# Generated by Django 5.0.6 on 2025-03-10 11:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkingMangtApp', '0033_remove_cart_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='parkingMangtApp.expenditurecategory'),
        ),
    ]
