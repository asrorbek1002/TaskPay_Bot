# Generated by Django 5.1.4 on 2024-12-07 16:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bot', '0007_botstats_mandatorychannel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('public', 'Public'), ('private', 'Private'), ('group', 'Group')], max_length=10)),
                ('url', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='JoinRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField()),
                ('username', models.CharField(blank=True, max_length=255, null=True)),
                ('full_name', models.CharField(max_length=255)),
                ('request_date', models.DateTimeField(auto_now_add=True)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bot.channel')),
            ],
        ),
    ]
