from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from ..models import TelegramUser

# Bosqichlarning boshlanish holati
FIRST_NAME = 0

def start(update: Update, context: CallbackContext):
    user = update.effective_user

    # Foydalanuvchini bazada qidirish
    try:
        telegram_user = TelegramUser.objects.get(user_id=user.id)
        update.message.reply_text(f"Salom, {telegram_user.first_name}!\nAhvollaringiz yaxshimi.")
        return ConversationHandler.END  # Muloqotni to'xtatadi
    except TelegramUser.DoesNotExist:
        # Agar foydalanuvchi bazada bo'lmasa, muloqotni boshlaydi
        update.message.reply_text("Salom! Iltimos, ismingizni kiriting:")
        return 'FIRST_NAME'

