# Generated by Django 3.2 on 2021-06-25 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20210625_1512'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='status',
            new_name='active',
        ),
    ]
