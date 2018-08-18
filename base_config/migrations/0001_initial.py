# Generated by Django 2.0.5 on 2018-05-22 10:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=128, unique=True, verbose_name='选项关键字')),
                ('value', models.TextField(blank=True, default='', verbose_name='选项值')),
            ],
            options={
                'verbose_name': '系统选项',
                'verbose_name_plural': '系统选项',
                'db_table': 'base_config_option',
            },
        ),
        migrations.CreateModel(
            name='UserOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=128, verbose_name='选项名')),
                ('value', models.TextField(blank=True, default='', verbose_name='选项值')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '用户选项',
                'verbose_name_plural': '用户选项',
                'db_table': 'base_config_user_option',
            },
        ),
        migrations.AlterUniqueTogether(
            name='useroption',
            unique_together={('user', 'key')},
        ),
    ]
