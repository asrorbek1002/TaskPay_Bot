from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext, ConversationHandler
from ..models import MandatoryChannel, TelegramUser
from django.db.models import F
from decimal import Decimal
from .user_interfase import menu_keyb

def choosewithdrawtype(update, context):
    user=TelegramUser.objects.get(user_id=update.message.from_user.id)
    if user.is_active is True:
        inline_btn = [[
            InlineKeyboardButton(text='💳 Karta', callback_data='wto_card'),
        ]]
        reply_mak = InlineKeyboardMarkup(inline_btn)

        update.message.reply_text(
            "<b>☟ Quyidagi to'lov usulidan birini tanlang:</b>", 
            reply_markup=reply_mak, parse_mode="HTML"
        )
    else:
        update.message.reply_text("🚫🚫🚫<b>Siz adminlar tomonidan blocklangansiz</b>\n<i>Batafsil malumotni adminlardan so'rab olishingiz mumkin</i>🚫🚫🚫")

def handlerwithdrawtype(update, context):
    data = update.callback_query
    if data.data == "wto_card":
        data.edit_message_text("<b>Karta raqamingizni kiriting:</b>", parse_mode="HTML")
        return "START_WITHDRAW"


def get_withdraw_price(update: Update, context: CallbackContext):
    payments_number = update.message.text
    user_id = update.message.from_user.id

    try:
        # Karta raqamini bazadan qidirish
        card_user = TelegramUser.objects.filter(card_number=payments_number).first()
        user = TelegramUser.objects.get(user_id=user_id)
        if card_user:
            # Karta raqami boshqa foydalanuvchiga tegishli bo'lsa, is_active ni False qilish
            if card_user.user_id != user_id:
                user.is_active = False
                user.save()
                update.message.reply_text(
                    text="<b>🚫🚫Siz endi pul chiqara olmaysiz\nBuni xato deb o'ylasangiz adminga murojaat qiling!</b>",
                    parse_mode="HTML"
                )
                return ConversationHandler.END
            else:
                update.message.reply_text(
                    text="<b>Qancha pul chiqarmoqchisiz?</b>", parse_mode="HTML"
                )
                return "GET_WITHDRAW_PRICE"
        else:
            # Karta raqami bazada topilmadi, foydalanuvchining karta raqamini saqlash
            user = TelegramUser.objects.get(user_id=user_id)
            user.card_number = payments_number
            user.save()
            update.message.reply_text(
                text="<b>Qancha pul chiqarmoqchisiz?</b>", parse_mode="HTML"
            )
            return "GET_WITHDRAW_PRICE"

    except TelegramUser.DoesNotExist:
        update.message.reply_text(
            text="<b>Qandaydir xatolik ro'y berdi! Botni qaytadan ishga tushirib ko'ring.</b>",
            parse_mode="HTML"
        )
        return ConversationHandler.END


def endWithdraw(update: Update, context: CallbackContext):
    try:
        price = update.message.text
        user_id = update.message.from_user.id
        user = TelegramUser.objects.get(user_id=user_id)
        price = int(price)

        if user.balance >= price and user.balance > 100:
            channel_id = withdrawchannelid()
            bot_username = (context.bot.get_me()).username
            repl_inline = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(text="To'lov qilindi✅", callback_data=f'okm_{price}_{user_id}'),
                    InlineKeyboardButton(text="To'lov qilinmadi❌", callback_data=f"nokm_{price}_{user_id}")
                ]
            ])
            message = f"""
<b>Foydalanuvchi: <a href="tg://user?id={user.user_id}">{user.first_name}</a> pul yechmoqchi.</b>

• Pul miqdori: {price} so'm
• Hisob raqam: {user.card_number}

Bizning Bot: @{bot_username}
"""
            if channel_id:
                update.message.reply_text(
                    "Ma'lumotlaringiz adminga yuborildi. Tez orada pulni tashlab beramiz✅",
                    reply_markup=ReplyKeyboardMarkup(menu_keyb, one_time_keyboard=True, resize_keyboard=True)
                )
                context.bot.send_message(chat_id=channel_id, text=message, parse_mode="HTML", reply_markup=repl_inline)
                return ConversationHandler.END
        else:
            update.message.reply_text("Hisobingizda mablag' yetarli emas")
            return 'GET_WITHDRAW_PRICE'
    except Exception as e:
        update.message.reply_text(f"Qandaydir xatolik ro'y berdi: {e}")
        return 'GET_WITHDRAW_PRICE'

# Qo'shimcha yordamchi funksiya

def withdrawchannelid():
    channel = MandatoryChannel.objects.filter(purpose='payments').first()
    if channel:
        return channel.channel_id
    return None

def handler_check_paymen(update: Update, context: CallbackContext):
    callback_data = update.callback_query.data
    price, user_id = callback_data.split("_")[1:]
    bot_username = (context.bot.get_me()).username
    try:
        price = float(price)  # To'lov miqdorini float ga aylantiramiz
        user = TelegramUser.objects.get(user_id=user_id)  # Foydalanuvchini bazadan olamiz

        if callback_data.startswith("okm_"):
            # Balansdan to'lov miqdorini chiqarib tashlaymiz
            if user.balance >= price:
                user.balance = F('balance') - price
                user.withdraw = F('withdraw') + price
                user.save(update_fields=['balance', 'withdraw'])  # Faqat balansni yangilash

                context.bot.send_message(
                    chat_id=user_id,
                    text="To'lov muvaffaqiyatli amalga oshirildi!"
                )
                update.callback_query.answer("Muvaffaqiyatli✅")
                update.callback_query.edit_message_text(text=f"""
<b>Foydlanuvchi: <a href="tg://user?id={user.user_id}">{user.first_name}</a> pul yechib oldi✅.

    • <i>Pul miqdori:</i> {price} so'm
    • <i>To'lo'v holati:</i> Muvaffaqiyatli✅
                                                                                                              
Bizning Bot: @{bot_username}</b>
""", parse_mode="HTML")
            else:
                context.bot.send_message(
                    chat_id=user_id,
                    text="Balansingiz yetarli emas!"
                )
        elif callback_data.startswith("nokm_"):
            if user.balance >= price:
                user.balance = F('balance') - price
                user.save(update_fields=['balance'])  # Faqat balansni yangilash
            # To'lov amalga oshmagan xabarini yuboramiz
            context.bot.send_message(
                chat_id=user_id,
                text="To'lov amalga oshmadi!\nAdmin bilan bog'laning"
            )
    except TelegramUser.DoesNotExist:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Foydalanuvchi topilmadi!"
        )
    except Exception as e:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Xatolik yuz berdi: {e}"
        )
