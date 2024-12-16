from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler, CommandHandler, MessageHandler, CallbackContext, Filters
)
from ..models import TelegramUser, MandatoryChannel, BotStats
from .user_interfase import menu_keyb


# ConversationHandler start command
def deposit_start(update: Update, context: CallbackContext):
    user = update.effective_user
    telegram_user = TelegramUser.objects.filter(user_id=user.id).first()
    if not telegram_user:
        update.message.reply_text("Avval ro'yxatdan o'ting.")
        return ConversationHandler.END

    update.message.reply_text(
        "<b>Depozit miqdorini kiriting</b> <i>(masalan, 150000):</i>",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("❌Bekor qilish❌")]], resize_keyboard=True
        ),
        parse_mode="HTML"
    )
    return 'DEPOSIT_AMOUNT'

# Amount input step
def deposit_amount(update: Update, context: CallbackContext):
    if update.message.text in "❌Bekor qilish❌":
        update.message.reply_text("Jarayon bekor qilindi.", reply_markup=ReplyKeyboardMarkup(menu_keyb, one_time_keyboard=True, resize_keyboard=True))
        return ConversationHandler.END
    try:
        deposit_amount = int(update.message.text.replace(" ", ""))
        context.user_data['deposit_amount'] = deposit_amount
        card_number = BotStats.objects.first().deposit_card_number # Bu yerda haqiqiy karta raqamini o'zgartiring

        update.message.reply_text(
            f"Quyidagi karta raqamga {deposit_amount:,} so'mni kiritib, screenshotni yuboring:\n"
            f"Karta raqam: {card_number}",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("❌Bekor qilish❌")]], resize_keyboard=True
            ),
        )
        return 'SEND_SCREENSHOT'
    except ValueError:
        update.message.reply_text(
            "Iltimos, depozit miqdorini to'g'ri formatda kiriting (masalan, 150000):"
        )
        return 'DEPOSIT_AMOUNT'

# Screenshot receiving step
def deposit_screenshot(update: Update, context: CallbackContext):
    deposit_amount = context.user_data['deposit_amount']
    screenshot = update.message.photo[-1]  # Eng yuqori sifatdagi rasmni oladi
    user = update.effective_user
    bot_username = (context.bot.get_me()).username
    # Majburiy kanalni olish
    deposit_channel = MandatoryChannel.objects.filter(purpose='deposit').first()
    card_number = BotStats.objects.first()
    if deposit_channel:
        caption = (
            f"<b><i>Foydalanuvchi:</i> <a href='tg://user?id={user.id}'>{user.first_name or 'No Name'} </a>\n"
            f"<i>Depozit miqdori:</i> {deposit_amount:,} so'm\n"
            f"<i>Karta raqam:</i> {card_number.deposit_card_number}</b>\n\n"
            "<blockquote>Hisobotni tasdiqlaysizmi?</blockquote>"
        )
        depo_key = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="Tasdiqlash✅", callback_data=f'depocheck_{deposit_amount}_{user.id}'),
                InlineKeyboardButton(text="Rad etish❌", callback_data=f"deponotcheck_0_{user.id}")
            ],
            [
                InlineKeyboardButton(text="Qo'lda kiritish🔢", url=f"https://t.me/{bot_username}?start=setuserd_{user.id}")
            ]
        ])
        try:
            context.bot.send_photo(
                chat_id=deposit_channel.channel_id,
                photo=screenshot.file_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=depo_key
            )
        except:
            print('Channel ID topilmadi yoki xatolik ro\'y berdi')

    update.message.reply_text("<b>Rahmat! Depozit tasdiqlangandan keyin sizga xabar beramiz.</b>👍", reply_markup=ReplyKeyboardMarkup(menu_keyb, one_time_keyboard=True, resize_keyboard=True), parse_mode="HTML")
    return ConversationHandler.END

# Cancel handler
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Jarayon bekor qilindi.", reply_markup=ReplyKeyboardMarkup(menu_keyb, one_time_keyboard=True, resize_keyboard=True))
    return ConversationHandler.END

# ConversationHandler initialization
deposit_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(r"^💸 Depozit kiritish$"), deposit_start)],
    states={
        'DEPOSIT_AMOUNT': [MessageHandler(Filters.text & ~Filters.command, deposit_amount)],
        'SEND_SCREENSHOT': [MessageHandler(Filters.photo, deposit_screenshot)],
    },
    fallbacks=[MessageHandler(Filters.regex("^❌Bekor qilish❌$"), cancel)],
)
