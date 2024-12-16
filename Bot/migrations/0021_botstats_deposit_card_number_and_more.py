# Generated by Django 5.1.4 on 2024-12-11 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bot', '0020_taskcompletion_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='botstats',
            name='deposit_card_number',
            field=models.CharField(blank=True, help_text='Depozitlar uchun karta raqami saqlanadi', max_length=20, null=True, verbose_name='Depozit uchun karta raqami'),
        ),
        migrations.AlterField(
            model_name='mandatorychannel',
            name='purpose',
            field=models.CharField(choices=[('payments', 'To‘lovlar uchun'), ('check_task', 'Vazifalarni tekshirish uchun'), ('support', 'Foydalanuvchi murojaatlari uchun'), ('deposit', 'Depozitni tasdiqlash uchun'), ('user_verification', 'Foydalanuvchilarni tasdiqlash uchun'), ('admin_channel', 'Adminning kanali'), ('advertising_channel', 'Reklama kanali'), ('other', 'Boshqa maqsadlar')], default='other', max_length=20, verbose_name='Kanal/Guruh maqsadi'),
        ),
        migrations.AlterField(
            model_name='taskcompletion',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('rejected', 'Rejected'), ('completed', 'Completed')], default='pending', max_length=10),
        ),
    ]
