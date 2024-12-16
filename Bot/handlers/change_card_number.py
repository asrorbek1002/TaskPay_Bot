from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (CallbackQueryHandler, CommandHandler, ConversationHandler,
                          MessageHandler, Filters, CallbackContext)
from ..models import BotStats
from .admin_menu import admin_keyb

# Callback query handler for inline button
def change_card_number(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.delete_message()
    query.message.reply_text("<b>Yangi karta raqamini yuboring:</b>", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text="⛔️Bekor Qilmoq⛔️")]], one_time_keyboard=True, resize_keyboard=True), parse_mode="HTML")
    return 'CHANGE_CARD'

# Save the new card number
def save_card_number(update: Update, context: CallbackContext):
    new_card_number = update.message.text
    if new_card_number in "⛔️Bekor Qilmoq⛔️":
        update.message.reply_text("Bekor qilindi", reply_markup=InlineKeyboardMarkup(admin_keyb))
        return ConversationHandler.END

    if not new_card_number.isdigit() or len(new_card_number) > 20:
        update.message.reply_text("Noto'g'ri format! Iltimos, 20 ta raqamdan oshmaydigan to'g'ri karta raqamini yuboring.")
        return 'CHANGE_CARD'

    # Yangilash jarayoni
    bot_stats = BotStats.objects.first()
    if bot_stats:
        bot_stats.update_deposit_card_number(new_card_number)
        update.message.reply_text(f"<b>Karta raqami muvaffaqiyatli yangilandi:</b> <blockquote>{new_card_number}</blockquote>\n\n<b>Admin menyu</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(admin_keyb))
    else:
        update.message.reply_text("Bot statistikasi topilmadi. Dasturchi bilan bog'laning.")

    return ConversationHandler.END

# Cancel handler
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Bekor qilindi.",  reply_markup=InlineKeyboardMarkup(admin_keyb))
    return ConversationHandler.END

# Conversation handler setup
change_card_number_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(change_card_number, pattern="^change_card_number$")],
    states={
        'CHANGE_CARD': [MessageHandler(Filters.text & ~Filters.command, save_card_number)],
    },
    fallbacks=[MessageHandler(Filters.regex(r"^⛔️Bekor Qilmoq⛔️$"), cancel)],
)

