from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from ..models import BotStats
from .admin_menu import inline_admin_key

SET_DAILY_LIMIT = range(1)

def start_set_daily_limit(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    update.callback_query.message.reply_text(
        "Iltimos, userlarning kunlik vazifa bajarish limitini kiriting:"
    )
    return SET_DAILY_LIMIT

def save_daily_limit(update: Update, context: CallbackContext) -> int:
    try:
        new_limit = int(update.message.text)
        bot_stats = BotStats.objects.first()

        if bot_stats:
            bot_stats.update_daily_limit(new_limit)
            update.message.reply_text(f"Kunlik limit {new_limit} ga muvaffaqiyatli o'zgartirildi✅")
            update.message.reply_text("<b>Admin menyu</b>", reply_markup=inline_admin_key, parse_mode="HTML")
        else:
            update.message.reply_text("Bot statistikasi topilmadi.")
    except ValueError:
        update.message.reply_text("Iltimos, faqat raqam kiriting.")
        return SET_DAILY_LIMIT

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("O'zgartirish bekor qilindi.")
    return ConversationHandler.END

set_daily_limit_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_set_daily_limit, pattern='^set_dailiy_limit$')
    ],
    states={
        SET_DAILY_LIMIT: [MessageHandler(Filters.text & ~Filters.command, save_daily_limit)]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)
