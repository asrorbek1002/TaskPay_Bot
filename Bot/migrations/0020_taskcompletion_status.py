# Generated by Django 5.1.4 on 2024-12-11 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bot', '0019_alter_task_reward'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskcompletion',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending', max_length=10),
        ),
    ]