from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from django.db.models import F
from ..models import TelegramUser  # O'zingizning modelingizni import qiling
from .user_interfase import menu_keyb

def handle_add_admin(update: Update, context: CallbackContext):
    """Admin qo'shish jarayonini boshlaydi."""
    query = update.callback_query
    query.answer()
    query.edit_message_text("Qaysi foydalanuvchini admin qilmoqchisiz? Iltimos, foydalanuvchi ID sini kiriting:", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text='🏠Asosiy menyu🏠')]], resize_keyboard=True))
    return 'ENTER_USER_ID'

def handle_user_id(update: Update, context: CallbackContext):
    """Foydalanuvchi ID sini tekshirish va admin qilish."""
    if update.message.text in "🏠Asosiy menyu🏠":
        update.message.reply_text("<b>Jarayon bekor qilindi</b>", parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(menu_keyb, resize_keyboard=True, one_time_keyboard=True))
        return ConversationHandler.END
    user_id = update.message.text.strip()
    current_user_id = update.effective_user.id

    # O'zini admin qilmaslik uchun tekshirish
    if int(user_id) == current_user_id:
        update.message.reply_text("Bu foydalanuvchi ID sizga tegishli!")
        return ConversationHandler.END

    try:
        user = TelegramUser.objects.get(user_id=user_id)
    except TelegramUser.DoesNotExist:
        update.message.reply_text("Bunday foydalanuvchi mavjud emas.")
        return ConversationHandler.END

    if user.is_admin:
        update.message.reply_text("Bu foydalanuvchi avvaldan admin!")
        return ConversationHandler.END

    # Foydalanuvchini admin qilish
    user.is_admin = True
    user.status = "main_admin"
    user.save(update_fields=["is_admin", "status"])
    update.message.reply_text(f"{user.first_name or 'No Name'} ({user_id}) admin qilindi!✅")
    context.bot.send_message(chat_id=user_id, text="🥳<b>Tabriklayman siz hozirgina Botga admin bo'ldingiz</b>", parse_mode="HTML")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    """Amalni bekor qilish."""
    update.message.reply_text("<b>Jarayon bekor qilindi</b>", parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(menu_keyb, resize_keyboard=True, one_time_keyboard=True))
    return ConversationHandler.END

# ConversationHandler yarating
admin_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_add_admin, pattern="^add_admin$")],
    states={
        'ENTER_USER_ID': [
            MessageHandler(Filters.text & ~Filters.command, handle_user_id)
        ]
    },
    fallbacks=[MessageHandler(Filters.regex("^🏠Asosiy menyu🏠$"), cancel)]
)
