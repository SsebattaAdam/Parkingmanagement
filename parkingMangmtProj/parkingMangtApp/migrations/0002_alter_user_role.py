# Generated by Django 5.0.6 on 2025-01-22 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkingMangtApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('ADMIN', 'Admin'), ('USER', 'User'), ('STAFF', 'Staff')], default='USER', max_length=50),
        ),
    ]
