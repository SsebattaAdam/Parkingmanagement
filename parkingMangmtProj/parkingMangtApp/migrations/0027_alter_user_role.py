# Generated by Django 5.0.6 on 2025-02-22 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkingMangtApp', '0026_alter_user_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('ADMIN', 'Admin'), ('USER', 'User'), ('MANAGER', 'Manager')], default='USER', max_length=50),
        ),
    ]
