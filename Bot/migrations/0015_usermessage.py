# Generated by Django 5.1.4 on 2024-12-08 19:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bot', '0014_alter_referral_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255, verbose_name='Murojaat mavzusi')),
                ('message', models.TextField(verbose_name='Murojaat matni')),
                ('is_reviewed', models.BooleanField(default=False, verbose_name='Ko‘rib chiqilganmi')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yuborilgan vaqt')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True, verbose_name='Ko‘rib chiqilgan vaqt')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='Bot.telegramuser', verbose_name='Foydalanuvchi')),
            ],
            options={
                'verbose_name': 'Foydalanuvchi murojaati',
                'verbose_name_plural': 'Foydalanuvchi murojaatlari',
                'ordering': ['-created_at'],
            },
        ),
    ]