# Generated by Django 3.1.4 on 2021-01-13 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0024_remove_user_watchlist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='user',
        ),
    ]
