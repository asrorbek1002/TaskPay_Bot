from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..models import Task, TelegramUser, TaskCompletion, BotStats
from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime

def earn_money_menu(update, context):
    inline_keyb = [
        [
            InlineKeyboardButton(text="Vazifa bajarish", callback_data='with_task')
        ]
    ]
    update.message.reply_text("<b>Pul ishlash uchun quyidagi usullardan birini tanlang</b>\n👇👇👇", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyb))

def create_channel_url(channel_username):
    # Agar kanal nomi @ bilan boshlasa, @ ni olib tashlaymiz
    if channel_username.startswith('@'):
        channel_username = channel_username[1:]
    
    # URL formatini yaratish
    url = f"https://t.me/{channel_username}"
    return url



def with_task(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    today = datetime.now().day  # Bugungi kunni olish

    try:
        user = TelegramUser.objects.get(user_id=user_id)
        bot_stats = BotStats.objects.first()
        if not bot_stats:
            update.callback_query.message.reply_text("Bot stats sozlanmagan.", parse_mode="HTML")
            return

        daily_limit = bot_stats.daily_limit
        task_data = user.task_completed_count.split("_") if user.task_completed_count else ["0", "0", "0"]
        completed_count = int(task_data[0])
        last_date = int(task_data[1]) if len(task_data) > 1 else 0
        is_first_time = task_data[-1] == "1"

        if last_date != today and user.depozite == 0:
            update.callback_query.answer("Depozit kiriting")
            update.callback_query.delete_message()
            update.callback_query.message.reply_text("Botdan pul ishlashingiz uchun depozit kiritishingiz kerak")
            return

        print(f'Is first time>>> {is_first_time}')
        
        task = Task.objects.filter(is_active=True).exclude(
            id__in=TaskCompletion.objects.filter(user=user, status='completed').values_list('task_id', flat=True)
        ).first()
        if task is None:
            update.callback_query.message.reply_text("Hozircha vazifalar mavjud emas.", parse_mode="HTML")
            return 
        if last_date == today:
            if completed_count >= daily_limit:
                update.callback_query.message.reply_text(
                    f"Siz bugun {daily_limit} ta vazifa bajardingiz. Ertaga qayta urinib ko'ring.",
                    parse_mode="HTML"
                )
                return
            else:
                completed_count += 1
        else:
            completed_count = 1

        # Agar user birinchi marta bo'lsa va limitga yetgan bo'lsa
        if is_first_time:
            user.balance += bot_stats.bonus_money
            user.task_completed_count = f"{completed_count}_{today}"
            user.save()
            update.callback_query.message.reply_text(f"<b>🥳Tabriklaymiz siz {bot_stats.bonus_money} so'm yutib oldingiz</b>", parse_mode='HTML')

        # Yangi qiymatni yangilash
        user.task_completed_count = f"{completed_count}_{today}"
        user.save()

        # Avvaldan `pending` holatida vazifa bor-yo'qligini tekshirish
        pending_task = TaskCompletion.objects.filter(user=user, status='pending').first()
        if pending_task:
            update.callback_query.message.reply_text(
                "Sizda kutilayotgan vazifa mavjud. Keyinroq urinib ko'ring.",
                parse_mode="HTML"
            )
            return
        rejected_task = TaskCompletion.objects.filter(user=user, status='rejected').first()
        # Yangi vazifa olish jarayoni
        if rejected_task:
            rejected_task.status = 'pending'
            rejected_task.save()
            deposit_percentage = task.reward
            deposit_amount = (user.depozite * deposit_percentage) / 100
            if task.url.startswith('http'):
                keyboard = [
                    [InlineKeyboardButton("🔗Vazifa havolasi🔗", url=task.url),
                     InlineKeyboardButton(text="✅Bajardim✅", callback_data=f'cht_{task.id}_{user_id}')]
                ]
            elif task.url.startswith("@"):
                keyboard = [
                    [InlineKeyboardButton("🔗Vazifa havolasi🔗", url=create_channel_url(task.url)),
                     InlineKeyboardButton(text="✅Bajardim✅", callback_data=f'cht_{task.id}_{user_id}')]
                ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            message = (
                f"📛 <b>Vazifa nomi: {task.name}</b>\n"
                f"ℹ️ <b>Tavsifi</b>: <i>{task.description}</i>"
            )
            update.callback_query.message.reply_text(message, reply_markup=reply_markup, parse_mode="HTML")
           
        else:
            deposit_percentage = task.reward
            deposit_amount = (user.depozite * deposit_percentage) / 100

            task_completion = TaskCompletion.objects.create(
                user=user,
                task=task,
                amount_added=deposit_amount,
                is_completed=False,
                status='pending'
            )

            if task.url.startswith('http'):
                keyboard = [
                    [InlineKeyboardButton("🔗Vazifa havolasi🔗", url=task.url),
                     InlineKeyboardButton(text="✅Bajardim✅", callback_data=f'cht_{task.id}_{user_id}')]
                ]
            elif task.url.startswith("@"):
                keyboard = [
                    [InlineKeyboardButton("🔗Vazifa havolasi🔗", url=create_channel_url(task.url)),
                     InlineKeyboardButton(text="✅Bajardim✅", callback_data=f'cht_{task.id}_{user_id}')]
                ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            message = (
                f"📛 <b>Vazifa nomi: {task.name}</b>\n"
                f"ℹ️ <b>Tavsifi</b>: <i>{task.description}</i>"
            )
            update.callback_query.message.reply_text(message, reply_markup=reply_markup, parse_mode="HTML")

    except TelegramUser.DoesNotExist:
        update.callback_query.message.reply_text("Siz hali ro'yxatdan o'tmadingiz.", parse_mode="HTML")

def by_refferal(update, context):
    update.callback_query.answer("Hali bu funksiya qo'shilmadi")


