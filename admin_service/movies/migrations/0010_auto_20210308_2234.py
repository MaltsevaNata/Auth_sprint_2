# Generated by Django 3.1 on 2021-03-08 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0009_auto_20210308_2224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personrole',
            name='role',
            field=models.CharField(choices=[('actor', 'актер'), ('director', 'режиссер'), ('scriptwriter', 'сценарист')], max_length=255, verbose_name='роль'),
        ),
    ]