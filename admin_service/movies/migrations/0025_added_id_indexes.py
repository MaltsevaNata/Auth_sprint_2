# Generated by Django 3.1 on 2021-03-14 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0024_added_indexes'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='filmwork',
            name='movies_film_title_753e28_idx',
        ),
        migrations.RemoveIndex(
            model_name='genre',
            name='movies_genr_name_850734_idx',
        ),
        migrations.RemoveIndex(
            model_name='person',
            name='movies_pers_last_na_601cc4_idx',
        ),
        migrations.AddIndex(
            model_name='filmwork',
            index=models.Index(fields=['id'], name='movies_film_id_dd5b50_idx'),
        ),
        migrations.AddIndex(
            model_name='genre',
            index=models.Index(fields=['id'], name='movies_genr_id_7d5d87_idx'),
        ),
        migrations.AddIndex(
            model_name='person',
            index=models.Index(fields=['id'], name='movies_pers_id_9d3f96_idx'),
        ),
    ]