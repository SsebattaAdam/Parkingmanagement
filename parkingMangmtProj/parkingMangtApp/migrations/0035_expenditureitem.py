# Generated by Django 5.0.6 on 2025-03-10 13:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkingMangtApp', '0034_cart_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenditureItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='parkingMangtApp.expenditurecategory')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items_created', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
