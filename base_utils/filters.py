import re
import sys

from django.conf import settings

try:
    import coreapi
except ImportError:
    coreapi = None

try:
    import coreschema
except ImportError:
    coreschema = None


class DeepFilterBackend(object):
    """ 深入查询参数过滤器
    在 Django Rest Framework 中，支持以 queryset 的直接参数查询进行列表集的筛选
    在 DEFAULT_FILTER_BACKENDS 或者 ViewSet 的 filter_backends 中使用这个 DeepFilterBackend：

    'DEFAULT_FILTER_BACKENDS': (
        // ...
        'django_base.base_utils.filters.DeepFilterBackend',
    ),

    然后，在所有的 ListModelMixin 中，所有带有双下划线 `__` 的 querystring 参数，
    都会尝试在 queryset 中进行筛选。

    例如：

    ?user__username__startswith=admin_

    特殊处理：

    * 所有的 value 值如果是 True/False/None，会被转换成对应的 python 值
    * 如果查询参数前面带有 !，例如 `!name__startswith=a`，将使用 exclude 排除筛选条件而不是 filter

    为了安全起见，所有被捕获的查询条件参数，必须显式注册在对应的 View Class 的
    'allowed_deep_params' 列表里面，否则条件会被忽略并且获得一条警告。

    例如是的上述的两个条件生效：

    class UserViewSet(viewsets.ModelViewSet):
        # ...
        allowed_deep_params = ['user__username__startswith', 'name__starts__with']

    TODO: 考虑支持全部参数开放或者正则表达式过滤参数或者用户级别的权限控制
    TODO: 考虑添加静默选项以防止生产环境过多输出警告参数
    """

    def filter_queryset(self, request, queryset, view):
        allowed_deep_params = getattr(view, 'allowed_deep_params', ())

        for key, val in request.query_params.items():

            if '__' not in key:
                continue
            if not re.match(r'^!?[A-Za-z0-9_]+$', key):
                continue
            exclude = key[0] == '!'
            key = key.strip('!')
            # 管理员登录可以豁免，否则所有的级联搜索必须显式放行
            if not (hasattr(settings, 'ALLOW_ALL_DEEP_PARAMS') and settings.ALLOW_ALL_DEEP_PARAMS) \
                    and not request.user.is_superuser and key not in allowed_deep_params:
                print(
                    '!!!! Deep filter param not registered: ' + key + '\n' +
                    'The param is skipped, to make it work, '
                    'add the params key name to `allowed_deep_params` list '
                    'in the View class.\n!!!!', file=sys.stderr)
                continue
            if val == 'False':
                val = False
            elif val == 'True':
                val = True
            elif val == 'None':
                val = None
            # 如果是 id 列表类的入参，按照逗号进行分割
            if key.endswith('__in') and re.match('^(?:\d+,)*\d+$', val):
                val = map(int, val.split(','))
            if exclude:
                queryset = queryset.exclude(**{key: val})
            else:
                queryset = queryset.filter(**{key: val})

        return queryset

    def get_schema_fields(self, view):
        # This is not compatible with widgets where the query param differs from the
        # filter's attribute name. Notably, this includes `MultiWidget`, where query
        # params will be of the format `<name>_0`, `<name>_1`, etc...
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'

        return [
            coreapi.Field(
                name=field,
                required=False,
                location='query',
                # schema=self.get_coreschema_field(field)
                schema=coreschema.String(description='* 注册的 DeepFilter 查询参数')
            ) for field in getattr(view, 'allowed_deep_params', [])
        ]
