from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
from ..models import TelegramUser, MandatoryChannel, UserMessage
from ..services import create_user_message
from ..utils import is_user_admin

def supportchannelid():
    channel = MandatoryChannel.objects.filter(purpose='support').first()
    if channel:
        channel_id = channel.channel_id
        print(f"Kanal ID: {channel_id}")
        return channel_id
    else:
        print("Murojaat uchun kanal topilmadi.")

def start_get_appeal(update: Update, context: CallbackContext):
    if supportchannelid():
        channel = MandatoryChannel.objects.filter(purpose='support').first()
        update.message.reply_text(f"Quyidagi guruhga qo'shilib adminlardan to'liq mallumot olishingiz mumkin\n\n{channel.channel_url}")
        return ConversationHandler.END
    back = [[InlineKeyboardButton(text="🔙Bekor qilish", callback_data="back_appeal")]]
    update.message.reply_text("<b>Iltimos murojaat mavzusini kiriting...</b>", reply_markup=InlineKeyboardMarkup(back), parse_mode="HTML")
    return "START_GET_APPEAL"

def get_appeal_text(update: Update, context: CallbackContext):
    appeal_name = update.message.text
    context.user_data['murojaat_mavzusi'] = appeal_name
    back = [[InlineKeyboardButton(text="🔙Bekor qilish", callback_data="back_appeal")]]
    update.message.reply_text("<b>Yaxshi endi murojaat matnini kiritng...</b>", reply_markup=InlineKeyboardMarkup(back), parse_mode="HTML")
    return "GET_APPEAL_TEXT"


def end_appeal(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    subject = context.user_data['murojaat_mavzusi']
    message = update.message.text_html
    user_instance = TelegramUser.objects.get(user_id=user_id)  
    
    # Foydalanuvchidan kelgan xabarni olish va message_id ni saqlash
    message_id = update.message.message_id  # Foydalanuvchidan kelgan xabar ID sini olish
    
    # Foydalanuvchi murojaatini yaratish
    create_user_message(user=user_instance, subject=subject, message=message, message_id=message_id)
    
    user = TelegramUser.objects.get(user_id=user_id)
    messages = f"""
<b>Yangi murojaat📬
                             
<i>Foydalanuvchi:</i> <a href="tg://user?id={user_id}">{user.first_name}</a>
<i>Murojaat mavzusi:</i> {subject}

<i>Murojaat matni:</i> </b>{message}
"""

    reply_btn = [
        [InlineKeyboardButton(text='💬Javob yozish', callback_data=f"replyappeal_{message_id}_{user_id}")]
    ]
    
    # Murojaatni kanalga yoki adminlarga yuborish
    # if appealchannelid():
    #     channel_ids = appealchannelid()
    #     context.bot.send_message(chat_id=channel_ids, text=messages, reply_markup=InlineKeyboardMarkup(reply_btn), parse_mode="HTML")
    # else:
    admin_ids = TelegramUser.get_admin_ids()
    for admin_id in admin_ids:
        context.bot.send_message(chat_id=admin_id, text=messages, reply_markup=InlineKeyboardMarkup(reply_btn), parse_mode="HTML")

    update.message.reply_text(text="Murojaatingizni qabul qildim, tez orada admin javob yozadi.")
    return ConversationHandler.END


  
def reply_appeal_to_user(update: Update, context: CallbackContext):
    admin_id = update.callback_query.from_user.id
    callback_data = update.callback_query.data
    message_id, user_id = callback_data.split('_')[1:]
    context.user_data['message_id'] = int(message_id)
    context.user_data['reply_user_id'] = int(user_id)
    print(user_id)
    print(message_id)
    if is_user_admin(admin_id) is True:
        context.bot.send_message(chat_id=admin_id, text="Foydalanuvchiga yubormoqchi bo'lgan xabarni kiritng...")
        return "START_REPLY"

def mark_as_reviewed(message_id):
    try:
        # message_id bo'yicha UserMessage obyektini qidirmoqda
        user_message = UserMessage.objects.get(message_id=message_id)
        
        # Agar xabar topilsa, is_reviewed ni True ga o'zgartiradi
        user_message.is_reviewed = True
        user_message.save()  # O'zgartirishlarni saqlash
        
        return f"Xabar (ID: {message_id}) ko'rib chiqildi."
    
    except UserMessage.DoesNotExist:
        # Agar xabar topilmasa
        return f"Xabar (ID: {message_id}) topilmadi."



def send_reply(update: Update, context: CallbackContext):
    message = update.message.text_html
    user_id = context.user_data['reply_user_id']
    message_id = context.user_data['message_id']
    mark_as_reviewed(message_id)
    context.bot.send_message(
        chat_id=user_id,
        text=message,
        reply_to_message_id=message_id,
        parse_mode="HTML"
    )
    return ConversationHandler.END
