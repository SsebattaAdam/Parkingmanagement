# Generated by Django 5.0.6 on 2025-03-10 10:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parkingMangtApp', '0030_remove_client_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='category',
        ),
    ]
