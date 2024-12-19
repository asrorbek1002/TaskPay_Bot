from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext
from ..utils import is_user_admin

admin_keyb = [
    [
        InlineKeyboardButton(text='💬Xabar yuborish', callback_data='send_messages'),
        InlineKeyboardButton(text='📊Bot statistikasi', callback_data='botstats')
    ],
    [
        InlineKeyboardButton(text='👮‍♂️Admin qo\'shish', callback_data='add_admin'),
        InlineKeyboardButton(text='🗑Admin o\'chirish', callback_data='delete_admin')
    ],
    [
        InlineKeyboardButton(text='🔘Kanal qo\'shish', callback_data='add_channel'),
        InlineKeyboardButton(text='🗑Kanal o\'chirish', callback_data='delete_channel')
    ],
    [
        InlineKeyboardButton(text="🎯Vazifa qo'shish", callback_data="add_task"),
        InlineKeyboardButton(text="🗑Vazifani o'chirish", callback_data="delete_task")
    ],
    [
        InlineKeyboardButton(text="⚙️Bot sozlamalari", callback_data='bot_settings')
    ],
    [
        InlineKeyboardButton(text='🌐Web admin panel', url='https://taskpay-bot.onrender.com/admin/')
    ]
]
inline_admin_key = InlineKeyboardMarkup(admin_keyb)

def admin_menu(update, context):
    user_id = update.message.from_user.id
    if is_user_admin(user_id) is True:
        update.message.reply_text("<b>Assalomu alaykum bosh admin!</b>\n<blockquote>Kerakli bo'limni tanlang👇</blockquote>", reply_markup=inline_admin_key, parse_mode="HTML")
    

bot_settings_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text='🔁 Bot qo\'llanmasini o\'zgartirish', callback_data='change_guide'),
            InlineKeyboardButton(text='🔄 Karta raqamini o\'zgartirish', callback_data='change_card_number') 
        ],
        [
            InlineKeyboardButton(text="🔋 Kunlik limitni o'zgartirish", callback_data='set_dailiy_limit'),
            InlineKeyboardButton(text="💰 Bonus pulni o'zgartirish", callback_data='set_bonus_money')
        ]
    ]
)

def Bot_Settings_menu(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if is_user_admin(user_id) is True:
        update.callback_query.edit_message_text("<b>Botdagi nimani o'zgartiramiz!</b>\n<blockquote>Kerakli bo'limni tanlang👇</blockquote>", reply_markup=bot_settings_keyboard, parse_mode="HTML")
    
