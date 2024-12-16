# Generated by Django 5.1.4 on 2024-12-06 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bot', '0002_alter_telegramuser_passport_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='status',
            field=models.BooleanField(default=True, verbose_name='User Status'),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='passport_pic',
            field=models.ImageField(upload_to='src/', verbose_name='User passport photo'),
        ),
    ]
