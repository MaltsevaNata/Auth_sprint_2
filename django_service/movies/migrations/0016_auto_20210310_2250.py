# Generated by Django 3.1 on 2021-03-10 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0015_convert_integer_to_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filmwork',
            name='file_path',
            field=models.FileField(blank=True, null=True, upload_to='film_works/', verbose_name='файл'),
        ),
    ]
