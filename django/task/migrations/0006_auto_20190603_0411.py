# Generated by Django 2.1.7 on 2019-06-03 04:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0005_auto_20190403_0813'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['-creation_time']},
        ),
    ]
