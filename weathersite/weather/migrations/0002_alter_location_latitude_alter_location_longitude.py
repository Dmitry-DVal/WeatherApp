# Generated by Django 5.2 on 2025-05-02 09:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("weather", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="Latitude",
            field=models.DecimalField(decimal_places=7, max_digits=10, unique=True),
        ),
        migrations.AlterField(
            model_name="location",
            name="Longitude",
            field=models.DecimalField(decimal_places=7, max_digits=10, unique=True),
        ),
    ]
