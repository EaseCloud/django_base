# Generated by Django 2.2.1 on 2019-08-23 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_media', '0003_auto_20180908_1152'),
    ]

    operations = [
        migrations.CreateModel(
            name='Audio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=255, verbose_name='名称')),
                ('ext_url', models.URLField(blank=True, default='', verbose_name='外部附件链接')),
                ('audio', models.FileField(upload_to='audio/', verbose_name='音频')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
            ],
            options={
                'verbose_name': '音频',
                'verbose_name_plural': '音频',
                'db_table': 'base_media_audio',
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=255, verbose_name='名称')),
                ('ext_url', models.URLField(blank=True, default='', verbose_name='外部附件链接')),
                ('video', models.FileField(upload_to='video/', verbose_name='视频')),
            ],
            options={
                'verbose_name': '视频',
                'verbose_name_plural': '视频',
                'db_table': 'base_media_video',
            },
        ),
    ]
