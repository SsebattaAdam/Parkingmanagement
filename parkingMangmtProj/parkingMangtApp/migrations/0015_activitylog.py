# Generated by Django 5.0.6 on 2025-02-10 07:54

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkingMangtApp', '0014_alter_parkingticket_duration_accountbalance_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[('expenditure', 'Expenditure'), ('balance_update', 'Balance Update'), ('user_activity', 'User Activity'), ('other', 'Other')], max_length=50)),
                ('details', models.TextField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_logs', to='parkingMangtApp.branch')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activity_logs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
