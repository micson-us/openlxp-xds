# Generated by Django 3.1.7 on 2021-03-17 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='xdsconfiguration',
            name='target_xis_es_api',
        ),
        migrations.AddField(
            model_name='xdsconfiguration',
            name='search_results_per_page',
            field=models.IntegerField(default=10),
        ),
    ]