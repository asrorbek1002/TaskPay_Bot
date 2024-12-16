from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from .user_interfase import menu_keyb

def restart(update: Update, context: CallbackContext):
    update.message.reply_text("<blockquote>Asosiy menyu</blockquote>", reply_markup=ReplyKeyboardMarkup(menu_keyb, one_time_keyboard=True, resize_keyboard=True), parse_mode="HTML")
    return ConversationHandler.END