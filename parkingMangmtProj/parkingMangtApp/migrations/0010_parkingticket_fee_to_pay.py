# Generated by Django 5.0.6 on 2025-01-25 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkingMangtApp', '0009_parkingticket_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkingticket',
            name='fee_to_pay',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
