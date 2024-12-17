from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from ..models import BotStats
from .admin_menu import inline_admin_key

SET_BOUCE_MONEY = range(1)

def start_set_bonus_money(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    update.callback_query.message.reply_text(
        "<b>Endi kirgan foydalanuvchilarga beriladigan <u>bonus pul</u> miqdorini kiriting:</b>",
        parse_mode="HTML"
    )
    return SET_BOUCE_MONEY

def save_bonus_money(update: Update, context: CallbackContext) -> int:
    try:
        new_limit = int(update.message.text)
        bot_stats = BotStats.objects.first()

        if bot_stats:
            bot_stats.update_bonus_money(new_limit)
            update.message.reply_text(f"Bonus pul {new_limit} so'm ga muvaffaqiyatli o'zgartirildi✅")
            update.message.reply_text("<b>Admin menyu</b>", reply_markup=inline_admin_key, parse_mode="HTML")
        else:
            update.message.reply_text("Bot statistikasi topilmadi.")
    except ValueError:
        update.message.reply_text("Iltimos, faqat raqam kiriting.")
        return SET_BOUCE_MONEY

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("O'zgartirish bekor qilindi.")
    return ConversationHandler.END

set_daily_limit_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_set_bonus_money, pattern='^set_bonus_money$')
    ],
    states={
        SET_BOUCE_MONEY: [MessageHandler(Filters.text & ~Filters.command, save_bonus_money)]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)
