# Generated by Django 5.1.4 on 2024-12-06 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bot', '0003_telegramuser_status_alter_telegramuser_passport_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramuser',
            name='status',
            field=models.CharField(blank=True, max_length=15, verbose_name='User status'),
        ),
    ]