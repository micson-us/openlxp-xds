# Generated by Django 3.1.8 on 2021-04-27 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20210421_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='xdsuiconfiguration',
            name='course_img_fallback',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]