from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton,InlineKeyboardMarkup
from ..models import TASK_TYPES
from ..utils import save_task_data

def start_add_task(update, context):
    update.callback_query.edit_message_text("Vazifaning nomini kiriting")
    return "START_ADD_TASK"

def get_task_name(update, context):
    context.user_data['task_name'] = update.message.text
    update.message.reply_text("Yaxshi. Endi vazifaning URL linkini yuboring")
    return "GET_TASK_NAME"

def get_task_url(update, context):
    context.user_data['task_url'] = update.message.text
    update.message.reply_text("Qabul qildim. Endi vazifani foydalanuvchilar yaxshi tushunish uchun u haqida tavsif yozing...")
    return "GET_TASK_URL"

def get_task_caption(update, context):
    context.user_data['task_caption'] = update.message.text
    update.message.reply_text("<b>Topshiriq qiymatini kiriting</b>\n<i>(Misol: 5) - bu foydalnuvchi kiritgan pulning 5 foizi hisoblanadi</i>", parse_mode="HTML")
    return "GET_TASK_CAPTION"

def get_task_price(update, context):
    context.user_data['reward'] = update.message.text
    keyboard = [
        [InlineKeyboardButton(TASK_TYPES[i][1], callback_data=TASK_TYPES[i][0]),
         InlineKeyboardButton(TASK_TYPES[i+1][1], callback_data=TASK_TYPES[i+1][0])]
        for i in range(0, len(TASK_TYPES) - 1, 2)
    ]
    
    # Tugmalar soni toq bo'lsa, oxirgi tugmachani alohida qo'shish
    if len(TASK_TYPES) % 2 != 0:
        keyboard.append([InlineKeyboardButton(TASK_TYPES[-1][1], callback_data=TASK_TYPES[-1][0])])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "<b>😍 Ajoyib! Endigi navbatda bu vazifa qaysi ijtimoiy tarmoqda ekanini tanlang:</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return "GET_TASK_PRICE"

def end_task_add(update, context):
    task_types = update.callback_query.data
    context.user_data['task_type'] = task_types
    save_task_data(context.user_data)
    if task_types == "telegram":
        update.callback_query.message.reply_text("<b>Vazifa salandi!✅</b>\n<i>Unutmang bot vazifani tekshirish uchun Telegram kanalga admin bo'lishi kerak!!!</i>", parse_mode="HTML")
    else:
        update.callback_query.message.reply_text("Vazifa salandi!")
    update.callback_query.answer("Muvaffaqiyatli✅")
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text("Vazifa qo'shish bekor qilindi")
    return ConversationHandler.END

