from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, CommandHandler
from ..models import Task

# Conversation bosqichlari uchun konstantalar
SELECT_TASK, CONFIRM_DELETE = range(2)

def start_delete_task(update: Update, context: CallbackContext):
    """Task o'chirishni boshlaydi."""
    tasks = Task.objects.all()

    if not tasks.exists():
        update.callback_query.edit_message_text("Hech qanday vazifa topilmadi.")
        return ConversationHandler.END

    # Vazifalar ro'yxatini inline tugmalar sifatida ko'rsatish
    keyboard = []
    row = []
    for i, task in enumerate(tasks, start=1):
        row.append(InlineKeyboardButton(task.name, callback_data=f"task_{task.id}"))
        if i % 2 == 0:  # Har 2 tadan keyin yangi qator
            keyboard.append(row)
            row = []
    if row:  # Qoldiq tugmalarni qo'shish
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text("Qaysi vazifani o'chirmoqchisiz?", reply_markup=reply_markup)
    return SELECT_TASK

def select_task(update: Update, context: CallbackContext):
    """Foydalanuvchi tanlagan vazifani ko'rsatadi."""
    query = update.callback_query
    query.answer()

    task_id = int(query.data.split("_")[1])
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        query.edit_message_text("Tanlangan vazifa topilmadi.")
        return ConversationHandler.END

    context.user_data['task_id'] = task_id
    
    task_info = (
        f"<b>Vazifa haqida ma'lumot:</b>\n\n"
        f"<b>Nom:</b> {task.name}\n"
        f"<b>URL:</b> {task.url}\n"
        f"<b>Mukofot:</b> {task.reward}\n"
        f"<b>Vazifa turi:</b> {task.get_task_type_display()}\n"
        f"<b>Ta'rif:</b> {task.description}\n"
    )

    keyboard = [
        [
            InlineKeyboardButton("Ha", callback_data="taskconfirm_yes"),
            InlineKeyboardButton("Yo'q", callback_data="taskconfirm_no")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        task_info + "\n\n<b>Rostdan ham o'chirmoqchimisiz</b>❓❓❓",
        parse_mode="HTML",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )
    return CONFIRM_DELETE

def confirm_delete(update: Update, context: CallbackContext):
    """Foydalanuvchi tasdiqlasa vazifani o'chiradi."""
    query = update.callback_query
    query.answer()

    if query.data == "taskconfirm_yes":
        task_id = context.user_data.get('task_id')
        try:
            task = Task.objects.get(id=task_id)
            task_name = task.name
            task.delete()
            query.edit_message_text(f"Vazifa '{task_name}' muvaffaqiyatli o'chirildi.")
        except Task.DoesNotExist:
            query.edit_message_text("Vazifa topilmadi yoki allaqachon o'chirilgan.")
    else:
        query.edit_message_text("Amal bekor qilindi.")

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    """Amalni bekor qilish."""
    update.message.reply_text("Amal bekor qilindi.")
    return ConversationHandler.END

# ConversationHandler yaratish
delete_task_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_delete_task, pattern=r'^delete_task$')],
    states={
        SELECT_TASK: [CallbackQueryHandler(select_task, pattern="^task_\\d+$")],
        CONFIRM_DELETE: [
            CallbackQueryHandler(confirm_delete, pattern="^taskconfirm_(yes|no)$")
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)
