from django_cron import CronJobBase, Schedule
from datetime import datetime, timedelta
from time import time

from . import models as m

# TODO: 示例文件，请将此 cron.py 移到主模块中实现

class MinuteCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'core.MinuteCronJob'  # a unique code

    def do(self):
        pass
        # print('MinuteCronJob: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'), flush=True)
        #
        # # 执行所有延时命令
        # t0 = time()
        # m.PlannedTask.trigger_all()
        # print('PlannedTask.trigger_all: {}s elapsed'.format(time() - t0), flush=True)
        #
        # # 推送所有计划的推送消息
        # t0 = time()
        # m.MessageBroadcast.push_all()
        # print('m.MessageBroadcast.push_all: {}s elapsed'.format(time() - t0), flush=True)


class HourCronJob(CronJobBase):
    ALLOW_PARALLEL_RUNS = False
    RUN_EVERY_MINS = 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'core.HourCronJob'  # a unique code

    def do(self):
        pass
        # print('HourCronJob: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'), flush=True)
        #
        # # 统计报表自动统计
        # t0 = time()
        # m.Statistic.make()
        # print('Statistic.make: {}s elapsed'.format(time() - t0), flush=True)
        #
        # # 为了不漏掉昨天的某些记录，总是补算一次昨天的记录
        # t0 = time()
        # m.Statistic.make(datetime.now() - timedelta(days=1))
        # print('Statistic.make (yesterday): {}s elapsed'.format(time() - t0), flush=True)
        #
        # # 同步所有微信消息模板
        # t0 = time()
        # m.WechatPushTemplate.sync_all()
        # print('WechatPushTemplate.sync_all: {}s elapsed'.format(time() - t0), flush=True)


class DailyCronJob(CronJobBase):
    # > crontab -e  */5 * * * *
    ALLOW_PARALLEL_RUNS = False
    RUN_EVERY_MINS = 24 * 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'core.DailyCronJob'  # a unique code

    def do(self):
        pass
        # 执行所有提成的补刀计算（耗时较长）
        # t0 = time()
        # m.CompetitionEntry.maintain_commissions_all()
        # print('maintain_commissions_all: {}s elapsed'.format(time() - t0), flush=True)

