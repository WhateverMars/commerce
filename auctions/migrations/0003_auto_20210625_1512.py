# Generated by Django 3.2 on 2021-06-25 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auto_20210625_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='price',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='listing',
            name='st_price',
            field=models.FloatField(),
        ),
    ]