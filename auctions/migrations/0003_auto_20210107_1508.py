# Generated by Django 3.1.4 on 2021-01-07 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_listing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='description',
            field=models.TextField(),
        ),
    ]
