from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from django.db.models import F
from ..models import Task, TelegramUser, TaskCompletion, MandatoryChannel
from ..utils import is_user_admin, bugungi_kun
from .user_interfase import menu_keyb


def convert_to_username(url: str) -> str:
    """
    Telegram URL manzilini @username formatiga o'zgartiradi.
    
    Args:
        url (str): Telegram URL manzili (masalan, https://t.me/username).
    
    Returns:
        str: @username formatidagi string.
    """
    if url.startswith("https://t.me/"):
        return f"@{url.split('https://t.me/')[-1]}"
    elif url.startswith('@'):
        return url
    else:
        raise ValueError("URL noto'g'ri formatda. Iltimos, https://t.me/ bilan boshlanadigan URL kiriting.")

def checktaskchannelid():
    channel = MandatoryChannel.objects.filter(purpose='check_task').first()
    if channel:
        channel_id = channel.channel_id
        print(f"Kanal ID: {channel_id}")
        return channel_id
    else:
        print("Vazifani tekshirish uchun kanal topilmadi.")


def handle_task_completion(update, context: CallbackContext):
    # Callback data (masalan: "cht_5_6194484795")ni ajratish
    callback_data = update.callback_query.data
    task_id_str, user_id_str = callback_data.split('_')[1:]  # "5" va "6194484795"
    context.user_data['callback_data'] = callback_data
    # Task va User IDlarni integerga aylantirish
    task_id = int(task_id_str)
    user_id = int(user_id_str)

 
    update.callback_query.delete_message()
    update.callback_query.message.reply_text("<b>⚠️⚠️⚠️Vazifani bajarganligingizni adminlar tekshirishi uchun vazifa bajarilganligi haqidagi hisobotni menga yuboring.(ya’ni skrinshot)</b>", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    return 'TGCHEKSCREEN'


def handler_task_chek_with_screnshot(update, context):
    photo = update.message.photo[-1]  # Eng yuqori sifatli rasmni tanlash
    file_id = photo.file_id
    callback_data = context.user_data['callback_data']
    task_id_str, user_id_str = callback_data.split('_')[1:]  # "5" va "6194484795"
    bot_username = (context.bot.get_me()).username
    task_id = int(task_id_str)
    user_id = int(user_id_str)
    task = Task.objects.get(id=task_id)  # Taskni id orqali olish
    user = TelegramUser.objects.get(user_id=user_id) 
    deposit_percentage = task.reward  # Task.reward foizni ifodalaydi
    deposit_amount = (user.depozite * deposit_percentage) / 100  # Depozitdan foizni hisoblash
    message = f"""
<i>Vazifani tasdiqlash uchun screenshot👆</i>

<b>Foydalanvchi: <a href="tg://user?id={user.user_id}">{user.first_name}</a>
<i>Vazifa:</i> <a href="https://t.me/{bot_username}?start=task_{task.id}">{task.name}</a>.
<i>Vazifa url:</i> <a href="{task.url}">URL</a>
<i>Vazifa turi:</i> {task.task_type}
<i>Vazifa narxi:</i> {deposit_amount} so'm

Tasdiqlaysizmi?</b>
"""
    inline_tgma = [
        [
            InlineKeyboardButton(text="Tasdiqlash✅", callback_data=f'chkad_{task.id}_{user.user_id}'),
            InlineKeyboardButton(text="Rad etish❌", callback_data=f"ntchkd_{task.id}_{user.user_id}")
        ]
    ]
    print(checktaskchannelid())
    context.bot.send_photo(checktaskchannelid(), photo=file_id, caption=message, reply_markup=InlineKeyboardMarkup(inline_tgma), parse_mode="HTML")
    update.message.reply_text("<b>Hisobot yuborildi\nTez orada adminlar tekshiradi</b>", parse_mode='HTML')
    return ConversationHandler.END

def create_channel_url(channel_username):
    # Agar kanal nomi @ bilan boshlasa, @ ni olib tashlaymiz
    if channel_username.startswith('@'):
        channel_username = channel_username[1:]
    
    # URL formatini yaratish
    url = f"https://t.me/{channel_username}"
    return url

def check_notcheck_btn(update: Update, context: CallbackContext):
    admin_id = update.effective_user.id
    callback_data = update.callback_query.data
    task_id_str, user_id_str = callback_data.split('_')[1:]
    context.user_data['callback_data'] = callback_data
    task_id = int(task_id_str)
    user_id = int(user_id_str)

    task = Task.objects.get(id=task_id)
    user = TelegramUser.objects.get(user_id=user_id)
    deposit_percentage = task.reward  # Task.reward foizni ifodalaydi
    deposit_amount = (user.depozite * deposit_percentage) / 100  # Depozitdan foizni hisoblash
    bot_username = (context.bot.get_me()).username  # Bot username'ni bir marta olish

    if is_user_admin(admin_id):
        if callback_data.startswith("chkad_"):
            # Foizni hisoblash


            # Foydalanuvchi balansiga foiz qiymatni qo'shish
            user.balance = F('balance') + deposit_amount
            user.save()

            # Taskni bajarilgan deb belgilash
            try:
                task_completion = TaskCompletion.objects.get(user=user, task=task)
                task_completion.is_completed = True
                task_completion.status = 'completed'
                task_completion.save()
                deposit_percentage = task.reward  # Task.reward foizni ifodalaydi
                deposit_amount = (user.depozite * deposit_percentage) / 100  # Depozitdan foizni hisoblash
                update.callback_query.edit_message_caption(caption=f"""
Vazifani tasdiqlash uchun screenshot👆

<b>Foydalanvchi:<i> <a href="tg://user?id={user_id}">{user.first_name}</a></i>
 • Vazifa:<i> <a href="https://t.me/{bot_username}?start=task_{task.id}">{task.name}</a>.</i>
 • Vazifa url:<i> <a href="{task.url}">URL</a> </i>
 • Vazifa turi:<i> {task.task_type}</i>
 • Vazifa narxi:<i> {deposit_amount} so'm</i>
</b>
<blockquote>Tasdiqlandi✅</blockquote>
                """, parse_mode="HTML")
                update.callback_query.answer("Muvaffaqiyatli tasdiqlandi✅")
                context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"🥳Tabriklaymiz siz '{task.name}' nomli vazifani bajarganingiz tasdiqlandi.\n"
                        f"👝Hisobingizga {deposit_amount} so'm qo'shildi."
                    )
                )

                # Yangi vazifani yuborish
                try:
                    completed_task_ids = TaskCompletion.objects.filter(user=user).values_list('task_id', flat=True)
                    next_task = Task.objects.filter(is_active=True).exclude(id__in=completed_task_ids).first()

                    if next_task:
                        next_deposit_percentage = next_task.reward
                        next_deposit_amount = (user.depozite * next_deposit_percentage) / 100
                        keyboard = [[InlineKeyboardButton(text='Ha', callback_data='with_task')]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        message = (
                            "<b>🆕Sizda yangi vazifa mavjud\n\n<u>Vazifani bajarasizmi?</u></b>"
                        )
                        context.bot.send_message(chat_id=user_id, text=message, reply_markup=reply_markup, parse_mode="HTML")
                    else:
                        context.bot.send_message(
                            chat_id=user_id, text="Siz bugungi barcha vazifani bajardingiz.", parse_mode="HTML"
                        )
                except TelegramUser.DoesNotExist:
                    update.callback_query.message.reply_text("Nomalum xatolik qayta urining", parse_mode="HTML")

            except TaskCompletion.DoesNotExist:
                update.callback_query.answer("Vazifa topilmadi yoki xatolik yuz berdi.")

        elif callback_data.startswith("ntchkd_"):
            try:
                # TaskCompletion obyektini topamiz, bu yerda filter() ishlatamiz
                task_completion = TaskCompletion.objects.filter(user=user, task=task).first()

                if task_completion:
                    task_data = user.task_completed_count.split("_") if user.task_completed_count else ["0", "0", "0"]
                    completed_count = int(task_data[0])
                    user.task_completed_count = f"{completed_count - 1}_{bugungi_kun()}"
                    user.save()
                    # Agar status rejected bo'lsa, uni qayta tasdiqlash
                    if task_completion.status == 'pending':
                        task_completion.status = 'rejected'  
                        print(task_completion.status)
                        task_completion.save()
                        
                        update.callback_query.edit_message_caption(caption=f"""
Vazifani tasdiqlash uchun screenshot👆
<b>
Foydalanvchi: <i><a href="tg://user?id={user_id}">{user.first_name}</a></i>
• Vazifa: <i><a href="https://t.me/{bot_username}?start=task_{task.id}">{task.name}</a>.</i>
• Vazifa url: <i><a href="{task.url}">URL</a> </i>
• Vazifa turi:<i> {task.task_type}</i>
• Vazifa narxi:<i> {deposit_amount} so'm</i>
</b>
<blockquote>Rad etildi❌</blockquote>
                        """, parse_mode="HTML")
                        
                        context.bot.send_message(
                            chat_id=user_id,
                            text=(
                                f"⚠️Sizning '{task.name}' nomli vazifani tasdiqlash rad etildi\n"
                                "Iltimos, vazifani qayta bajarib, tasdiqlash uchun yuboring."
                            ),
                            reply_markup=ReplyKeyboardMarkup(menu_keyb, resize_keyboard=True)
                        )

                    
                    else:
                        update.callback_query.answer("Vazifa holati allaqachon tasdiqlangan yoki boshqa holatda.")
                else:
                    update.callback_query.answer("Vazifa topilmadi yoki xatolik yuz berdi.")
                
            except TaskCompletion.DoesNotExist:
                update.callback_query.answer("Vazifa topilmadi yoki xatolik yuz berdi.")

    else:
        update.callback_query.answer("Sizni bu tugmani bosishga haqqingiz yo'q😠")
