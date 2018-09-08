# Generated by Django 2.0.5 on 2018-09-08 11:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_media', '0003_auto_20180908_1152'),
        ('base_config', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=20, verbose_name='版本号')),
                ('alias', models.CharField(blank=True, default='', max_length=100, verbose_name='版本别名')),
                ('platform', models.CharField(blank=True, default='', max_length=20, verbose_name='平台')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
                ('is_master', models.BooleanField(default=True, help_text='建议实践：如果是主要版本，所有低版本的客户端必须要升级到此版本才能使用，否则为建议版本，只作提醒，不强制升级。', verbose_name='是否主要版本')),
                ('description', models.TextField(blank=True, default='', verbose_name='版本描述')),
                ('link', models.CharField(blank=True, default='', max_length=255, verbose_name='下载链接')),
                ('attachment', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='version', to='base_media.Attachment', verbose_name='安装包附件')),
            ],
            options={
                'verbose_name': '版本',
                'verbose_name_plural': '版本',
                'db_table': 'base_version',
            },
        ),
    ]
