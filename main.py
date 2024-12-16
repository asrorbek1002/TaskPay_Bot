from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

def get_invite_link(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Iltimos, kanal yoki guruh ID sini yuboring.\nMisol: `/getlink -1001234567890`")
        return

    chat_id = context.args[0]

    try:
        # Kanal yoki guruh haqida ma'lumot olish
        chat = context.bot.get_chat(chat_id)

        # Taklif havolasini olish
        invite_link = chat.invite_link

        # Taklif havolasi mavjud bo'lmasa, admin huquqlar bilan avtomatik yaratiladi
        if not invite_link:
            invite_link = context.bot.export_chat_invite_link(chat_id)

        # Javobni foydalanuvchiga yuborish
        update.message.reply_text(
            f"📋 **Kanal/Guruh haqida ma'lumot:**\n"
            f"🔑 ID: `{chat.id}`\n"
            f"📛 Nomi: {chat.title}\n"
            f"🔗 Taklif havolasi: {invite_link}\n"
            f"Chat tyoe {chat.type}",
            parse_mode="Markdown",
        )

    except Exception as e:
        update.message.reply_text(f"Xatolik yuz berdi: {e}")

def check_membership(update: Update, context: CallbackContext):
    if len(context.args) != 2:
        update.message.reply_text("Iltimos, kanal/guruh ID sini va foydalanuvchi ID sini yuboring.\nMisol: `/checkmembership -1001234567890 123456789`")
        return


    chat_id = context.args[0]
    user_id = context.args[1]

    try:
        # Kanal/guruhda foydalanuvchining a'zolik holatini tekshirish
        member = context.bot.get_chat_member(chat_id, user_id)
        print(member)

        # A'zolik holatiga qarab javob
        if member.status in ["member", "administrator", "creator"]:
            update.message.reply_text(f"✅ Foydalanuvchi kanal yoki guruhga a'zo.")
        else:
            update.message.reply_text(f"❌ Foydalanuvchi kanal yoki guruhga a'zo emas.")

    except Exception as e:
        update.message.reply_text(f"Xatolik yuz berdi: {e}")

from telegram import Update
from telegram.ext import Updater, CallbackContext, ChatJoinRequestHandler

def handle_join_request(update: Update, context: CallbackContext):
    """Foydalanuvchining kanal/guruhga qo'shilish so'rovini boshqaradi."""
    join_request = update.chat_join_request
    print(join_request)
    # Foydalanuvchi haqida ma'lumot olish
    user = join_request.from_user
    chat = join_request.chat

    # Foydalanuvchi haqida ma'lumotni chiqarish
    message = (
        f"👤 Foydalanuvchi: {user.full_name} (@{user.username})\n"
        f"🔑 ID: {user.id}\n"
        f"📢 Kanal/Guruh: {chat.title} ({chat.id})"
    )
    print(message)








# Botni ishga tushirish
def main():
    updater = Updater("7045575392:AAFJCQgK50eNZFcLTVcfP09vgxKVwgapjH4")
    dispatcher = updater.dispatcher
    # Join Request handlerini qo'shish
    dispatcher.add_handler(ChatJoinRequestHandler(handle_join_request))

    # /getlink komandasini qo'shish
    dispatcher.add_handler(CommandHandler("getlink", get_invite_link))
    dispatcher.add_handler(CommandHandler('checkmembership', check_membership))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
