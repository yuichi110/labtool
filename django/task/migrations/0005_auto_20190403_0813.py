# Generated by Django 2.1.7 on 2019-04-03 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0004_auto_20190403_0813'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='updated_at',
            new_name='update_time',
        ),
    ]
