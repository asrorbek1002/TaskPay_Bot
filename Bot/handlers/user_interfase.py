from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ConversationHandler

menu_keyb = [
    [
        KeyboardButton(text="💵 Pul ishlash"),
        KeyboardButton(text="🏦 Pulni yechish")
    ],
    [
        KeyboardButton(text="💰 Hisobim"),
        KeyboardButton(text="💸 Depozit kiritish")
    ],
    [
        KeyboardButton(text="📨 Murojaat"),
        KeyboardButton(text="📚 Qo'llanma")
    ]
]

def main_menu(update, context):
    update.message.reply_text("<b>Asosiy menyu</b>", parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(menu_keyb, one_time_keyboard=True, resize_keyboard=True))
    return ConversationHandler.END