from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
from django.core.files.base import ContentFile
import re
from .user_interfase import main_menu, menu_keyb
from io import BytesIO
from ..models import TelegramUser, PassportInfo
import requests

# Bosqichlar uchun state-lar
FIRST_NAME, LAST_NAME, BIRTH_DATE, PASSPORT_SERIES, PASSPORT_IMAGE, CONFIRMATION = range(6)

Main_menukey = [
    [KeyboardButton(text="🏠Asosiy menyu")]
]
menu_main = ReplyKeyboardMarkup(Main_menukey, resize_keyboard=True)

# Boshlash funksiyasi
def start_passport(update: Update, context: CallbackContext):
    update.callback_query.edit_message_text("<b>Iltimos, pasportingiz ma'lumotlarini kiriting.</b> <u>Ismingizni kiriting:</u>", parse_mode="HTML")
    return 'FIRST_NAME'

# Ismni olish
def get_first_name(update: Update, context: CallbackContext):
    if update.message.text in "🏠Asosiy menyu":
        update.message.reply_text("<b>Asosiy menyu</b>", parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(menu_keyb, resize_keyboard=True, one_time_keyboard=True))
        return ConversationHandler.END
    context.user_data['first_name'] = update.message.text.strip()
    update.message.reply_text("<b>Familiyangizni kiriting</b>:", parse_mode="HTML", reply_markup=menu_main)
    return 'LAST_NAME'

# Familiyani olish
def get_last_name(update: Update, context: CallbackContext):
    if update.message.text in "🏠Asosiy menyu":
        update.message.reply_text("<b>Asosiy menyu</b>", parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(menu_keyb, resize_keyboard=True, one_time_keyboard=True))
        return ConversationHandler.END
    context.user_data['last_name'] = update.message.text.strip()
    update.message.reply_text("<b>Tug'ilgan sanangizni kiriting (Format: YYYY-MM-DD)</b>:", parse_mode="HTML", reply_markup=menu_main)
    return 'BIRTH_DATE'

# Tug'ilgan sanani olish
def get_birth_date(update: Update, context: CallbackContext):
    if update.message.text in "🏠Asosiy menyu":
        update.message.reply_text("<b>Asosiy menyu</b>", parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(menu_keyb, resize_keyboard=True, one_time_keyboard=True))
        return ConversationHandler.END
    birth_date = update.message.text.strip()
    if not re.match(r"\d{4}-\d{2}-\d{2}", birth_date):
        update.message.reply_text("<b>Iltimos, to'g'ri formatda sanani kiriting (YYYY-MM-DD):</b>", parse_mode="HTML", reply_markup=menu_main)
        return 'BIRTH_DATE'

    context.user_data['birth_date'] = birth_date
    update.message.reply_text("<b>Pasport seriyangizni kiriting (Format: AA1234567):</b>", parse_mode="HTML", reply_markup=menu_main)
    return 'PASSPORT_SERIES'

# Pasport seriyasini olish
def get_passport_series(update: Update, context: CallbackContext):
    if update.message.text in "🏠Asosiy menyu":
        update.message.reply_text("<b>Asosiy menyu</b>", parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(menu_keyb, resize_keyboard=True, one_time_keyboard=True))
        return ConversationHandler.END
    passport_series = update.message.text.strip()
    if not re.match(r"^[A-Z]{2}\d{7}$", passport_series):
        update.message.reply_text("<b>Iltimos, to'g'ri formatda pasport seriyasini kiriting (AA1234567):</b>", parse_mode="HTML")
        return 'PASSPORT_SERIES'

    context.user_data['passport_series'] = passport_series
    update.message.reply_text("<b>Pasportingizning rasm suratini yuboring:</b>", parse_mode="HTML", reply_markup=menu_main)
    return 'PASSPORT_IMAGE'

# Pasport rasmini olish
def get_passport_image(update: Update, context: CallbackContext):
    if not update.message.photo:
        update.message.reply_text("<b>Iltimos, pasportingizning haqiqiy rasm suratini yuboring:</b>", parse_mode="HTML", reply_markup=menu_main)
        return 'PASSPORT_IMAGE'

    photo_file = update.message.photo[-1].get_file()
    photo_data = BytesIO(photo_file.download_as_bytearray())
    context.user_data['passport_image'] = ContentFile(photo_data.read(), 'passport.jpg')
    update.message.reply_text(
        "<b>Hamma ma'lumot to'g'rimi?\n\n"
        f"<i>Ism:</i> {context.user_data['first_name']}\n"
        f"<i>Familiya:</i> {context.user_data['last_name']}\n"
        f"<i>Tug'ilgan sana:</i> {context.user_data['birth_date']}\n"
        f"<i>Pasport seriyasi:</i> {context.user_data['passport_series']}</b>\n",
        reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Ha"), KeyboardButton("Yo'q")]
        ], one_time_keyboard=True, resize_keyboard=True)
    )
    return 'CONFIRMATION'

# Tasdiqlash
def confirm_data(update: Update, context: CallbackContext):
    if update.message.text.strip().lower() == 'yoq':
        update.message.reply_text("Kiritishni qayta boshlaymiz. Ismingizni kiriting:")
        return 'FIRST_NAME'

    # Ma'lumotlarni bazaga saqlash
    user = TelegramUser.objects.get(user_id=update.effective_user.id)
    PassportInfo.objects.create(
        user=user,
        first_name=context.user_data['first_name'],
        last_name=context.user_data['last_name'],
        birth_date=context.user_data['birth_date'],
        passport_series=context.user_data['passport_series'],
        passport_image=context.user_data['passport_image']
    )
    update.message.reply_text("Pasport ma'lumotlaringiz saqlandi. Rahmat!")
    return ConversationHandler.END

# Bekor qilish
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Ma'lumot kiritish bekor qilindi.")
    return ConversationHandler.END

passport_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_passport, pattern='full_registration')],
    fallbacks=[MessageHandler(Filters.regex(r"^🏠Asosiy menyu$"), main_menu)],
    states={
        'FIRST_NAME': [MessageHandler(Filters.text & ~Filters.command, get_first_name)],
        'LAST_NAME': [MessageHandler(Filters.text & ~Filters.command, get_last_name)],
        'BIRTH_DATE': [MessageHandler(Filters.text & ~Filters.command, get_birth_date)],
        'PASSPORT_SERIES': [MessageHandler(Filters.text & ~Filters.command, get_passport_series)],
        'PASSPORT_IMAGE': [MessageHandler(Filters.photo, get_passport_image)],
        'CONFIRMATION': [MessageHandler(Filters.text & ~Filters.command, confirm_data)],
    }
)
