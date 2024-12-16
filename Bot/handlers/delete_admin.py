from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, CommandHandler
from ..models import TelegramUser

# Conversation bosqichlari uchun konstantalar
SELECT_ADMIN, CONFIRM_DELETE = range(2)

def start_delete_admin(update: Update, context: CallbackContext):
    """Adminni o'chirishni boshlaydi."""
    query = update.callback_query
    query.answer()

    admins = TelegramUser.objects.filter(is_admin=True)

    if not admins.exists():
        query.edit_message_text("Hozircha adminlar mavjud emas.")
        return ConversationHandler.END

    # Adminlar ro'yxatini inline tugmalar sifatida ko'rsatish
    keyboard = []
    for admin in admins:
        keyboard.append([
            InlineKeyboardButton(
                f"{admin.first_name} ({admin.user_id})",
                callback_data=f"admin_{admin.id}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text("Qaysi adminni o'chirmoqchisiz?", reply_markup=reply_markup)
    return SELECT_ADMIN

def select_admin(update: Update, context: CallbackContext):
    """Tanlangan admin haqida ma'lumot chiqaradi."""
    query = update.callback_query
    query.answer()

    admin_id = int(query.data.split("_")[1])
    try:
        admin = TelegramUser.objects.get(id=admin_id, is_admin=True)
    except TelegramUser.DoesNotExist:
        query.edit_message_text("Tanlangan admin topilmadi yoki allaqachon o'chirilgan.")
        return ConversationHandler.END

    context.user_data['admin_id'] = admin_id

    admin_info = (
        f"<b>Admin haqida ma'lumot:</b>\n\n"
        f"<b>Ismi:</b> {admin.first_name}\n"
        f"<b>ID:</b> {admin.user_id}\n"
    )

    keyboard = [
        [
            InlineKeyboardButton("Ha", callback_data="adconfirm_yes"),
            InlineKeyboardButton("Yo'q", callback_data="adconfirm_no")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        admin_info + "\n\n<b>Rostdan ham adminlikdan o'chirmoqchimisiz?</b>",
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    return CONFIRM_DELETE

def confirm_delete(update: Update, context: CallbackContext):
    """Adminni o'chirishni tasdiqlaydi."""
    query = update.callback_query
    query.answer()

    if query.data == "adconfirm_yes":
        admin_id = context.user_data.get('admin_id')
        try:
            admin = TelegramUser.objects.get(id=admin_id, is_admin=True)
            admin.is_admin = False
            admin.save(update_fields=['is_admin'])

            query.edit_message_text(f"{admin.first_name} adminlikdan muvaffaqiyatli o'chirildi.")

            # Adminlikdan o'chirilgan userga ogohlantirish yuborish
            context.bot.send_message(
                chat_id=admin.user_id,
                text="Siz adminlikdan o'chirildingiz."
            )
        except TelegramUser.DoesNotExist:
            query.edit_message_text("Admin topilmadi yoki allaqachon o'chirilgan.")
    else:
        query.edit_message_text("Amal bekor qilindi.")

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    """Amalni bekor qilish."""
    update.message.reply_text("Amal bekor qilindi.")
    return ConversationHandler.END

# ConversationHandler yaratish
delete_admin_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_delete_admin, pattern=r'^delete_admin$')],
    states={
        SELECT_ADMIN: [CallbackQueryHandler(select_admin, pattern=r'^admin_\d+$')],
        CONFIRM_DELETE: [
            CallbackQueryHandler(confirm_delete, pattern=r'^adconfirm_(yes|no)$')
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)
