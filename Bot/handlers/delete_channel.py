from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler
from .admin_menu import inline_admin_key
from ..models import MandatoryChannel

def start_remove_channel(update: Update, context: CallbackContext):
    """Kanal yoki guruhni o'chirishni boshlaydi."""
    update.callback_query.delete_message()

    # Bazadagi mavjud kanallarni olish
    channels = MandatoryChannel.objects.all()
    if not channels:
        update.callback_query.message.reply_text(
            "Hozircha hech qanday kanal yoki guruh qo'shilmagan.", reply_markup=inline_admin_key
        )
        return ConversationHandler.END

    # Inline tugmalar yaratish
    keyboard = []
    for channel in channels:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{channel.channel_name} ({channel.channel_type})",
                callback_data=f"remove_{channel.channel_id}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text(
        "O'chirmoqchi bo'lgan kanal yoki guruhni tanlang:",
        reply_markup=reply_markup
    )
    return 'CONFIRM_REMOVE'

def confirm_remove_channel(update: Update, context: CallbackContext):
    """Foydalanuvchidan tasdiq so'raydi."""
    query = update.callback_query
    query.answer()

    # Callback ma'lumotini olish
    channel_id = query.data.split('_')[1]
    context.user_data['channel_id'] = channel_id

    try:
        channel = MandatoryChannel.objects.get(channel_id=channel_id)
        context.user_data['channel_name'] = channel.channel_name

        # Tasdiq tugmalari
        keyboard = [
            [
                InlineKeyboardButton("Ha", callback_data="chaconfirm_yes"),
                InlineKeyboardButton("Yo'q", callback_data="chaconfirm_no")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            text=f"<b>{channel.channel_name}</b> ni o'chirishni tasdiqlaysizmi?",
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        return 'REMOVE_CHANNEL'
    except MandatoryChannel.DoesNotExist:
        query.edit_message_text("Tanlangan kanal topilmadi.")
        return ConversationHandler.END

def remove_channel(update: Update, context: CallbackContext):
    """Kanal yoki guruhni o'chiradi."""
    query = update.callback_query
    query.answer()

    if query.data == "chaconfirm_yes":
        channel_id = context.user_data.get('channel_id')
        channel_name = context.user_data.get('channel_name')

        try:
            # Kanalni bazadan o'chirish
            MandatoryChannel.objects.filter(channel_id=channel_id).delete()
            query.edit_message_text(
                text=f"✅ <b>{channel_name}</b> muvaffaqiyatli o'chirildi.",
                parse_mode="HTML"
            )
        except Exception as e:
            query.edit_message_text(f"Xatolik yuz berdi: {str(e)}")
    else:
        query.edit_message_text("Amal bekor qilindi.")

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    """ConversationHandler ni bekor qilish."""
    update.message.reply_text("Amal bekor qilindi.", reply_markup=inline_admin_key)
    return ConversationHandler.END

remove_channel_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_remove_channel, pattern='^delete_channel$')],
    states={
        'CONFIRM_REMOVE': [CallbackQueryHandler(confirm_remove_channel, pattern='^remove_\d+$')],
        'REMOVE_CHANNEL': [CallbackQueryHandler(remove_channel, pattern='^chaconfirm_(yes|no)$')],
    },
    fallbacks=[CallbackQueryHandler(cancel, pattern='^cancel$')],
)
