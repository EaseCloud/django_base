from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django_base.base_meta.models import UserOwnedModel


class UserMark(UserOwnedModel):
    """ 用于让用户对某类对象产生标记的
    例如：用户收藏商品
    UserMark.objects.create(author=user, object=goods, subject='collect')
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('content_type', 'object_id')

    # is_read = models.BooleanField(
    #     verbose_name='是否已读',
    #     default=False,
    # )

    date_created = models.DateTimeField(
        verbose_name='记录时间',
        auto_now_add=True,
    )

    subject = models.CharField(
        verbose_name='标记类型',
        max_length=20,
    )

    class Meta:
        verbose_name = '用户标记'
        verbose_name_plural = '用户标记'
        db_table = 'base_mark_user_mark'
        unique_together = [['author', 'content_type', 'object_id', 'subject']]

    def __str__(self):
        # zhangsan: [collect] Article(8)
        # lisi: [downvote] Goods(137)
        return '{}: [{}] {}({})'.format(
            self.author, self.subject, self.content_type, self.object_id)


class UserMarkModel(models.Model):
    """ 可被用户标记的模型
    例如商品模型 (Goods)，需要用户可以：
    收藏：collect
    赞：upvote
    踩：downvote
    这样我们就可以让 Goods 继承这个类
    """
    marks = GenericRelation(UserMark)

    class Meta:
        abstract = True

    def get_users_marked_with(self, subject):
        """ 获取已经标记此对象的用户 QuerySet
        例如：
        ```
        goods = Goods.objects.get(1)
        goods.get_users_marked_with('collect')
        ```
        :param subject:
        :return:
        """
        model = type(self)
        content_type = ContentType.objects.get(
            app_label=model._meta.app_label,
            model=model._meta.model_name,
        )
        return User.objects.filter(
            usermarks_owned__content_type=content_type,
            usermarks_owned__object_id=self.pk,
            usermarks_owned__subject=subject,
        )

    def is_marked_by(self, user, subject):
        """ 判断该对象是否被某个用户标记
        例如判断某个商品是否被用户收藏：
        ```
        goods = Goods.objects.get(1)
        user = User.objects.get(1)
        if goods.is_marked_by(user, 'collect'):
            print('已收藏')
        ```
        :param user:
        :param subject:
        :return:
        """
        return self.get_users_marked_with(subject).filter(id=user.id).exists()

    def set_marked_by(self, user, subject, is_marked=True):
        """ 添加标记
        例如：
        设置置顶
        ```
        goods = Goods.objects.get(1)
        user = User.objects.get(1)
        goods.set_marked_by(user, 'collect')
        ```
        取消置顶
        ```
        goods = Goods.objects.get(1)
        user = User.objects.get(1)
        goods.set_marked_by(user, 'collect', False)
        ```
        :param user:
        :param subject:
        :param is_marked:
        :return:
        """
        model = type(self)
        content_type = ContentType.objects.get(
            app_label=model._meta.app_label,
            model=model._meta.model_name,
        )
        fields = dict(
            author=user,
            content_type=content_type,
            object_id=self.pk,
            subject=subject,
        )
        mark = UserMark.objects.filter(**fields).first()
        if is_marked and not mark:
            UserMark.objects.create(**fields)
        elif not is_marked and mark:
            mark.delete()
        else:
            pass

    @classmethod
    def get_objects_marked_by(cls, user, subject):
        """ 获取被用户标记的对象列表
        例如获取用户收藏的所有商品
        ```
        user = User.objects.get(1)
        goods_list = Goods.get_objects_marked_by(user, 'collect')
        ```
        :param user:
        :param subject:
        :return:
        """
        content_type = ContentType.objects.get(
            app_label=cls._meta.app_label,
            model=cls._meta.model_name,
        )
        col = cls._meta.pk.db_column or cls._meta.pk.name + '_id' \
            if type(cls._meta.pk) == models.OneToOneField else cls._meta.pk.name
        # TODO: 此处实现环境兼容性并不完美，后期可以考虑修改一下写法
        qs = cls.objects.extra(
            where=["""
            exists(
                select *
                from base_mark_user_mark um, auth_user u
                where um.subject = '{subject}'
                  and um.author_id = {author_id}
                  and um.object_id = {table}.{col}
                  and um.content_type_id = {content_type_id}
            )
            """.format(subject=subject, author_id=user.id, table=cls._meta.db_table,
                       col=col, content_type_id=content_type.id)]
        )
        return qs
