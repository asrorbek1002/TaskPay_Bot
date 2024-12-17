
from telegram import ParseMode
from ..models import BotStats

def stats_command(update, context):
    # Bot statistikasi modelidan ma'lumotni olish
    bot_stats = BotStats.objects.first()  # Birinchi va yagona yozuvni olish
    update.callback_query.answer("Malumotlarni yuklayabman!!!")
    if bot_stats:
        # Ma'lumotni HTML formatida tayyorlash
        message = (
            "<b>📊 Bot Statistikasi:</b>\n\n"
            f"<b>👥 Foydalanuvchilar soni:</b> {bot_stats.user_count}\n"
            f"<b>🔗 Majburiy kanallar soni:</b> {bot_stats.mandatory_channel_count}\n"
        )
    else:
        # Agar modelda ma'lumot bo'lmasa
        message = "<b>📊 Bot Statistikasi:</b>\nMa'lumot mavjud emas."

    # Ma'lumotni foydalanuvchiga yuborish
    update.callback_query.edit_message_text(
        text=message,
        parse_mode=ParseMode.HTML
    )
