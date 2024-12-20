# Generated by Django 5.1.4 on 2024-12-08 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bot', '0011_alter_task_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='mandatorychannel',
            name='purpose',
            field=models.CharField(choices=[('payments', 'To‘lovlar uchun'), ('check_task', 'Vazifalarni tekshirish uchun'), ('user_verification', 'Foydalanuvchilarni tasdiqlash uchun'), ('admin_channel', 'Admin kanali'), ('advertising_channel', 'Reklama kanali'), ('other', 'Boshqa maqsadlar')], default='other', max_length=20, verbose_name='Kanal/Guruh maqsadi'),
        ),
    ]
