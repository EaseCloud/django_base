import json
from datetime import datetime, timedelta
from django.db import models


class PlannedTaskBase(models.Model):
    """ 计划任务抽象模型
    如果要使用，请在主模块的模型内实现静态方法，然后通过
    PlannedTask.make 方法将任务加入队列
    然后将 python manage.py runcrons 定时执行（1分钟），即可按期自动触发任务
    """
    method = models.CharField(verbose_name='任务', max_length=100)
    args = models.TextField(verbose_name='参数', blank=True, default='',
                            help_text='JSON 表示的参数列表')
    kwargs = models.TextField(verbose_name='字典参数', blank=True,
                              default='', help_text='JSON 表示的参数字典')
    date_planned = models.DateTimeField(verbose_name='计划时间')
    date_execute = models.DateTimeField(verbose_name='执行时间', blank=True, null=True)
    traceback = models.TextField(verbose_name='错误信息', blank=True, default='')

    STATUS_PLANNED = 'PLANNED'
    STATUS_DONE = 'DONE'
    STATUS_FAIL = 'FAIL'
    STATUS_CHOICES = (
        (STATUS_PLANNED, '计划中'),
        (STATUS_DONE, '执行成功'),
        (STATUS_FAIL, '失败'),
    )
    status = models.CharField(verbose_name='状态', max_length=20, default=STATUS_PLANNED)

    class Meta:
        abstract = True
        # verbose_name = '计划任务'
        # verbose_name_plural = '计划任务'
        # db_table = 'core_cron_planned_task'

    @classmethod
    def make(cls, method, date_planned, *args, **kwargs):
        cls.objects.create(
            method=method,
            date_planned=date_planned,
            args=json.dumps(args),
            kwargs=json.dumps(kwargs),
        )

    @classmethod
    def trigger_all(cls):
        tasks = cls.objects.filter(
            status=cls.STATUS_PLANNED,
            date_planned__lte=datetime.now(),
        )
        for task in tasks:
            task.exec()

    def exec(self):
        if self.status == self.STATUS_DONE or self.date_planned > datetime.now():
            return False
        try:
            args = json.loads(self.args or '[]')
            kwargs = json.loads(self.kwargs or '{}')
            method = getattr(self, self.method)
            method(*args, **kwargs)
            self.status = self.STATUS_DONE
        except Exception as e:
            import traceback
            self.status = self.STATUS_FAIL
            self.traceback = traceback.format_exc()
        self.date_execute = datetime.now()
        self.save()

    # 具体注册的方法
    # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓

    # @staticmethod
    # def update_user_payment_password(user_id, hashed_password):
    #     """ 更新用户的支付密码
    #     :param user_id: 对应的用户
    #     :param hashed_password: 加密的密码
    #     :return:
    #     """
    #     UserPreference.set(User.objects.get(id=user_id), 'payment_password', hashed_password)
