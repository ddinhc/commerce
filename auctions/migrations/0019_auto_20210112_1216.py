# Generated by Django 3.1.4 on 2021-01-12 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0018_auto_20210112_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlist',
            name='listings',
            field=models.ManyToManyField(blank=True, related_name='watchlist', to='auctions.Listing'),
        ),
    ]
