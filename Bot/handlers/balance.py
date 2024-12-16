from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..models import TelegramUser
from decimal import Decimal, ROUND_DOWN


blance_inline_menu = [
    [
        InlineKeyboardButton(text="Referal taklif qilish", callback_data='by_referral')
    ]
]

def balance_menu(update, context):
    user_id = update.message.from_user.id
    user = TelegramUser.objects.get(user_id=user_id)
    print(user.first_name, user.balance)
    user_balance = Decimal(user.balance)
    format_balance = user_balance.quantize(Decimal("1"))
    message = f"""
🆔 <b>Sizning ID raqamingiz</b>:
<blockquote>{user_id}</blockquote>


💵 <b>Asosiy balans</b>: {format_balance} so'm
💸 <b>Yechib olingan pullar</b>: {user.withdraw} so'm
💳 <b>Depozit pullar</b>: {user.depozite} so'm
👥 <b>Referalllar soni</b>: {user.reff} ta
"""
    update.message.reply_text(message, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(blance_inline_menu))


