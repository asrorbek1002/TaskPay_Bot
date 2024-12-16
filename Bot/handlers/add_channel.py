from telegram import Update
from ..models import MandatoryChannel, PURPOSE_TYPES

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from .admin_menu import inline_admin_key


def start_add_channel(update: Update, context: CallbackContext):
    """Kanal yoki guruhni qo‘shishni boshlaydi."""
    update.callback_query.delete_message()
    update.callback_query.message.reply_text(
        "Iltimos, kanal yoki guruhdan biror xabarni forward qiling.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text='🏠Asosiy menyu🏠')]], resize_keyboard=True)
    )
    return 'FORWARD_MESSAGE'


from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

# Taklif havolasi yaratish uchun yordamchi funksiya
def get_or_create_invite_link(context, chat_id):
    try:
        invite_link = context.bot.export_chat_invite_link(chat_id)
        return invite_link
    except Exception as e:
        return None

def handle_forwarded_message(update: Update, context: CallbackContext):
    """Kanal yoki guruh xabarini qayta ishlaydi va inline tugmalarni ko‘rsatadi."""
    if not update.message.forward_from_chat:
        update.message.reply_text("Iltimos, faqat kanal yoki guruhdan xabar forward qiling.")
        return 'FORWARD_MESSAGE'

    chat = update.message.forward_from_chat
    bot_id = (context.bot.get_me()).id

    # Kanal yoki guruh ma'lumotlarini olish
    context.user_data["channel_id"] = str(chat.id)
    context.user_data["channel_name"] = chat.title or "Noma'lum"
    context.user_data["channel_type"] = "channel" if chat.type == "channel" else "group"

    # Usernamesi bo‘lsa, to‘g‘ridan-to‘g‘ri URL ishlatiladi
    if chat.username:
        context.user_data["channel_url"] = f"https://t.me/{chat.username}"
    else:
        # Usernamesi yo'q bo'lsa, taklif havolasi yaratish
        invite_link = get_or_create_invite_link(context, chat.id)
        if invite_link:
            context.user_data["channel_url"] = invite_link
        else:
            update.message.reply_text("Taklif havolasini yaratib bo'lmadi. Bot adminligini tekshiring.")
            return ConversationHandler.END

    try:
        admins = context.bot.get_chat_administrators(chat.id)
        bot_is_admin = any(admin.user.id == bot_id for admin in admins)
        if not bot_is_admin:
            update.message.reply_text(f"Bot {chat.title} da admin emas. Iltimos, uni admin qiling.")
            return ConversationHandler.END

        # Inline tugmalar yaratish
        keyboard = [
            [InlineKeyboardButton(name, callback_data=value) for value, name in PURPOSE_TYPES[:2]],
            [InlineKeyboardButton(name, callback_data=value) for value, name in PURPOSE_TYPES[2:4]],
            [InlineKeyboardButton(name, callback_data=value) for value, name in PURPOSE_TYPES[4:]]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "Kanal yoki guruhning maqsadini tanlang:",
            reply_markup=reply_markup,
        )
        return 'CHOOSE_PURPOSE'
    except Exception as e:
        update.message.reply_text(f"Xatolik yuz berdi: {str(e)}")
        return ConversationHandler.END
    
def handle_purpose_selection(update: Update, context: CallbackContext):
    """User tomonidan maqsad tanlanganini qayta ishlaydi."""
    query = update.callback_query
    query.answer()

    purpose = query.data
    channel_id = context.user_data["channel_id"]
    channel_name = context.user_data["channel_name"]
    channel_type = context.user_data["channel_type"]
    channel_url = context.user_data["channel_url"]

    # Ma'lumotlarni bazaga saqlash
    try:
        obj, created = MandatoryChannel.objects.get_or_create(
            channel_id=channel_id,
            defaults={
                "channel_name": channel_name,
                "channel_type": channel_type,
                "channel_url": channel_url,
                "purpose": purpose,
            },
        )
        if created:
            query.edit_message_text(
                f"✅<b>{channel_name} {channel_type} muvaffaqiyatli qo‘shildi</b> \n(ID: <code>{channel_id}</code>)."
            , parse_mode="HTML")
        else:
            query.edit_message_text(
                f"<b>{channel_name} allaqachon bazaga qo‘shilgan</b>.\n(ID: <code>{channel_id}</code>)"
            , parse_mode="HTML")
    except Exception as e:
        query.edit_message_text(f"Xatolik yuz berdi: {str(e)}")
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    """ConversationHandler ni bekor qilish."""
    update.message.reply_text("Amal bekor qilindi.", reply_markup=inline_admin_key)
    return ConversationHandler.END

add_channel_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_add_channel, pattern='^add_channel$')],
    states={
        'FORWARD_MESSAGE': [MessageHandler(Filters.forwarded & ~Filters.command, handle_forwarded_message)],
        'CHOOSE_PURPOSE': [CallbackQueryHandler(handle_purpose_selection)],
    },
    fallbacks=[MessageHandler(Filters.regex("🏠Asosiy menyu🏠"), cancel)],
)



