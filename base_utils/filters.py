from __future__ import unicode_literals

import re
import sys

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models.sql.constants import ORDER_PATTERN
from django.template import loader
from django.utils import six
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from rest_framework.compat import coreapi, coreschema
from rest_framework.filters import BaseFilterBackend
from rest_framework.settings import api_settings

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


class OrderingFilter(BaseFilterBackend):
    """
    改编自 rest_framework.filters.OrderingFilter，由于过于严格的过滤，导致不能支持级联字段的排序，例如
    ordering=-related_item__name 的过滤，在这里将过滤的逻辑剔除，以使得功能增强。
    """
    # The URL query parameter used for the ordering.
    ordering_param = api_settings.ORDERING_PARAM
    ordering_fields = None
    ordering_title = _('Ordering')
    ordering_description = _('Which field to use when ordering the results.')
    template = 'rest_framework/filters/ordering.html'

    def get_ordering(self, request, queryset, view):
        """
        Ordering is set by a comma delimited ?ordering=... query parameter.

        The `ordering` query parameter can be overridden by setting
        the `ordering_param` value on the OrderingFilter or by
        specifying an `ORDERING_PARAM` value in the API settings.
        """
        params = request.query_params.get(self.ordering_param)
        if params:
            fields = [param.strip() for param in params.split(',')]
            return fields
            # ordering = self.remove_invalid_fields(queryset, fields, view, request)
            # if ordering:
            #     return ordering

        # No ordering was included, or all the ordering fields were invalid
        return self.get_default_ordering(view)

    # def get_default_ordering(self, view):
    #     ordering = getattr(view, 'ordering', None)
    #     if isinstance(ordering, six.string_types):
    #         return (ordering,)
    #     return ordering

    # def get_default_valid_fields(self, queryset, view, context={}):
    #     # If `ordering_fields` is not specified, then we determine a default
    #     # based on the serializer class, if one exists on the view.
    #     if hasattr(view, 'get_serializer_class'):
    #         try:
    #             serializer_class = view.get_serializer_class()
    #         except AssertionError:
    #             # Raised by the default implementation if
    #             # no serializer_class was found
    #             serializer_class = None
    #     else:
    #         serializer_class = getattr(view, 'serializer_class', None)
    #
    #     if serializer_class is None:
    #         msg = (
    #             "Cannot use %s on a view which does not have either a "
    #             "'serializer_class', an overriding 'get_serializer_class' "
    #             "or 'ordering_fields' attribute."
    #         )
    #         raise ImproperlyConfigured(msg % self.__class__.__name__)
    #
    #     return [
    #         (field.source.replace('.', '__') or field_name, field.label)
    #         for field_name, field in serializer_class(context=context).fields.items()
    #         if not getattr(field, 'write_only', False) and not field.source == '*'
    #     ]
    #
    # def get_valid_fields(self, queryset, view, context={}):
    #     valid_fields = getattr(view, 'ordering_fields', self.ordering_fields)
    #
    #     if valid_fields is None:
    #         # Default to allowing filtering on serializer fields
    #         return self.get_default_valid_fields(queryset, view, context)
    #
    #     elif valid_fields == '__all__':
    #         # View explicitly allows filtering on any model field
    #         valid_fields = [
    #             (field.name, field.verbose_name) for field in queryset.model._meta.fields
    #         ]
    #         valid_fields += [
    #             (key, key.title().split('__'))
    #             for key in queryset.query.annotations
    #         ]
    #     else:
    #         valid_fields = [
    #             (item, item) if isinstance(item, six.string_types) else item
    #             for item in valid_fields
    #         ]
    #
    #     return valid_fields

    # def remove_invalid_fields(self, queryset, fields, view, request):
    #     valid_fields = [item[0] for item in self.get_valid_fields(queryset, view, {'request': request})]
    #     return [term for term in fields if term.lstrip('-') in valid_fields and ORDER_PATTERN.match(term)]

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            return queryset.order_by(*ordering)

        return queryset

    def get_template_context(self, request, queryset, view):
        current = self.get_ordering(request, queryset, view)
        current = None if not current else current[0]
        options = []
        context = {
            'request': request,
            'current': current,
            'param': self.ordering_param,
        }
        for key, label in self.get_valid_fields(queryset, view, context):
            options.append((key, '%s - %s' % (label, _('ascending'))))
            options.append(('-' + key, '%s - %s' % (label, _('descending'))))
        context['options'] = options
        return context

    def to_html(self, request, queryset, view):
        template = loader.get_template(self.template)
        context = self.get_template_context(request, queryset, view)
        return template.render(context)

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name=self.ordering_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text(self.ordering_title),
                    description=force_text(self.ordering_description)
                )
            )
        ]
