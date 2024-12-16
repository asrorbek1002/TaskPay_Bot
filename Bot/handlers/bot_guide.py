from telegram import Update, ReplyKeyboardMarkup
from .user_interfase import menu_keyb
from telegram.ext import CallbackContext, ConversationHandler
from ..models import BotStats
from ..services import update_bot_guide

def start_change_guide(update: Update, context: CallbackContext):
    update.callback_query.edit_message_text(text="<b>Yaxshi botning yangi qo'llanmasini kiritng.</b> \n<i>Iloji bo'lsa userga tushunarli qilib shriftlar bian emojilar qo'shsangiz user yaxshi tushunadi</i>", parse_mode="HTML")
    return 'START_CHANGE_GUIDE'

def save_guide(update: Update, context: CallbackContext):
    guide = update.message.text_html
    try:
        update_bot_guide(guide)
        update.message.reply_text("Yangi qo'llanma saqlandi!")
    except:
        update.message.reply_text("Xatolik ro'y berdi")
    return ConversationHandler.END



def get_bot_guide(update: Update, context: CallbackContext):
    bot_stats = BotStats.objects.first()
    print(bot_stats)
    update.message.reply_text(text=bot_stats.guide, parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(menu_keyb, one_time_keyboard=True, resize_keyboard=True))
