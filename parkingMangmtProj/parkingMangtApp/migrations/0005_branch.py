# Generated by Django 5.0.6 on 2025-01-22 12:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkingMangtApp', '0004_business'),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch_name', models.CharField(max_length=255)),
                ('location', models.TextField()),
                ('contact_number', models.CharField(max_length=15)),
                ('is_active', models.BooleanField(default=True)),
                ('is_main_branch', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='branches', to='parkingMangtApp.business')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='branches_created', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
