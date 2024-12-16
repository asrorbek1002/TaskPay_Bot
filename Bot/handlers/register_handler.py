import os
from django.conf import settings
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext
)
from Bot.models import TelegramUser
from .user_interfase import menu_keyb
from ..utils import save_telegram_user, update_user_status

# Bosqichlarning holatlari
FIRST_NAME, LAST_NAME, PHONE_NUMBER, PASSPORT_PIC = range(4)
END = ConversationHandler.END

# Statusni tasdiqlash va bekor qilish tugmalari
def get_confirmation_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Tasdiqlash", callback_data=f'confirm_{user_id}')],
        [InlineKeyboardButton("Rad etish", callback_data=f'cancel_{user_id}')]
    ])

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    context.user_data['user_id'] = user.id

    # Foydalanuvchini bazada qidirish
    try:
        telegram_user = TelegramUser.objects.get(user_id=user.id)
        update.message.reply_text(f"<b>Asosiy menyu.</b>", parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(menu_keyb, one_time_keyboard=True, resize_keyboard=True))
        return ConversationHandler.END  # Muloqotni to'xtatadi
    except TelegramUser.DoesNotExist:
        # Agar foydalanuvchi bazada bo'lmasa, muloqotni boshlaydi
        update.message.reply_text("Salom! Iltimos, ismingizni kiriting:")
        return FIRST_NAME

# Bot ismini so'rash
def ask_user_name(update: Update, context: CallbackContext):
    context.user_data['first_name'] = update.message.text
    update.message.reply_text("Rahmat! Endi familiyangizni kiriting:")
    return LAST_NAME

# Familiyasini so'rash
def ask_last_name(update: Update, context: CallbackContext):
    context.user_data['last_name'] = update.message.text
    update.message.reply_text("Rahmat! Endi telefon raqamingizni yuboring.",
                              reply_markup=ReplyKeyboardMarkup(
                                  [[KeyboardButton("📲Telefon raqamni ulashish", request_contact=True)]],
                                  resize_keyboard=True, one_time_keyboard=True
                              ))
    return PHONE_NUMBER



def end_registration(update: Update, context: CallbackContext):
    # Foydalanuvchi telefon raqamini yuborsa
    if update.message.contact:
        context.user_data['phone_number'] = update.message.contact.phone_number
    else:
        update.message.reply_text(
            "Iltimos, telefon raqamingizni yuborish uchun 📲Telefon raqamni ulashish tugmasini bosing."
        )
        return PHONE_NUMBER
    save_telegram_user(data=context.user_data)

    update.message.reply_text("<b>Ajoyib👍 \nSiz botdan foydalanishingiz mumkin✅</b>", reply_markup=ReplyKeyboardMarkup(menu_keyb, one_time_keyboard=True, resize_keyboard=True), parse_mode="HTML")

    return END

# Admin tomonidan tasdiqlash yoki bekor qilishni boshqarish
def handle_admin_confirmation(update: Update, context: CallbackContext):
    query = update.callback_query
    user_data = context.user_data
    data = query.data
    if data.startswith("confirm"):
        confirm, user_id = data.split('_')
        # Statusni "chekked" qilib o'zgartirish
        update_user_status(user_id, 'confirm')
        query.answer("Ma'lumot tasdiqlandi.")
        query.delete_message()
    elif data.startswith("cancel"):
        # Statusni "not chekked" qilish
        notconfirm, user_id = data.split('_')
        update_user_status(user_id, 'not chekked')
        query.answer("Ma'lumotlar tasdiqlanmadi.")
        query.delete_message()

    return ConversationHandler.END

# Foydalanuvchi ma'lumotlarini saqlash
def save_user(update: Update, context: CallbackContext):
    tg_user = update.effective_user
    user_data = context.user_data
    user_data['user_id'] = tg_user.id

    saved_user = save_telegram_user(user_data)
    if saved_user:
        update.message.reply_text(f"Ma'lumotlaringiz saqlandi: {saved_user.first_name} {saved_user.last_name}")
    else:
        update.message.reply_text("Ma'lumotlaringizni saqlashda xatolik yuz berdi.")
    
    return ConversationHandler.END

# Cancel (Jarayonni bekor qilish)
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Jarayon bekor qilindi. Xayr!")
    return ConversationHandler.END


