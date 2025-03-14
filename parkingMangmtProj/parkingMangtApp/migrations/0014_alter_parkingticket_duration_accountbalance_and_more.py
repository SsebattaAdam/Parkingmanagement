# Generated by Django 5.0.6 on 2025-02-09 19:26

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkingMangtApp', '0013_remove_client_contact_info_remove_client_driver_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parkingticket',
            name='duration',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='AccountBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('bank', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('mobile_money', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='account_balance', to='parkingMangtApp.branch')),
            ],
        ),
        migrations.CreateModel(
            name='ExpenditureCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='categories_created', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Expenditure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('bank', 'Bank'), ('mobile_money', 'Mobile Money')], max_length=20)),
                ('proof_of_payment', models.FileField(blank=True, null=True, upload_to='proof_of_payments/')),
                ('description', models.TextField(blank=True, null=True)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenditures', to='parkingMangtApp.branch')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenditures_created', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenditures', to='parkingMangtApp.expenditurecategory')),
            ],
        ),
    ]
