from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from django.core.exceptions import ObjectDoesNotExist
from ..models import TelegramUser

def require_card_info(func):
    """
    Dekorator: Foydalanuvchining PassportInfo modelida ma'lumoti borligini tekshiradi.
    Agar ma'lumot topilmasa, tegishli xabarni qaytaradi.
    """
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        # Telegram foydalanuvchini aniqlash
        user_id = update.effective_user.id

        try:
            # `TelegramUser` va `PassportInfo` modelidagi ma'lumotlarni tekshirish
            telegram_user = TelegramUser.objects.get(user_id=user_id)
            if not hasattr(telegram_user, 'passport_info'):
                inline_btn = [
                        [
                            InlineKeyboardButton(text="📥 Ro'yxatdan o'tish", callback_data="full_registration")
                        ]
                    ]
                update.callback_query.edit_message_text(
                    "<b>Siz botdan pul yechishdan oldin pasport ma'lumotlaringizni to'ldirishingiz kerak</b>.\n<i>Bu malumotlar siz botdan faqat bitta akkount orqali foydalanayotganinggizga ishonch hosil qilish uchun kerak</i>\n<tg-spoiler><u>Malumotlar Admin tomonidan 100% himoyalangan</u></tg-spoiler>",
                    reply_markup=InlineKeyboardMarkup(inline_btn),
                    parse_mode="HTML"
                )
                return
        except TelegramUser.DoesNotExist:
            update.callback_query.edit_message_text(
                "Siz botimizga ro'yxatdan o'tmagansiz. Iltimos, oldin ro'yxatdan o'ting."
            )
            return

        # Agar ma'lumot mavjud bo'lsa, asosiy funksiyani bajaradi
        return func(update, context, *args, **kwargs)

    return wrapper

