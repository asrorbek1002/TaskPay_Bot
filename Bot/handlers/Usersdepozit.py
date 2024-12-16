from telegram.ext import CallbackContext
from telegram import Update
from django.db.models import F
from ..models import TelegramUser
from ..utils import is_user_admin



def check_depozite(update: Update, context: CallbackContext):
    callback_data = update.callback_query.data
    calldeposite_price, calluser_id = callback_data.split("_")[1:]
    dprice = int(calldeposite_price)
    user_id = int(calluser_id)
    user = TelegramUser.objects.get(user_id=user_id)

    tasdiqlangan_message = f"""Foydalanuvchi: <a href='tg://user?id={user_id}'>{user.first_name}</a> 
<b>Depozit miqdori: 37,000 so'm
Karta raqam: 9860606747877300
</b>
<blockquote>Tasdiqlandi✅</blockquote>
"""
    radetilgan_message = f"""Foydalanuvchi: <a href='tg://user?id={user_id}'>{user.first_name}</a> 
<b>Depozit miqdori: 37,000 so'm
Karta raqam: 9860606747877300
</b>
<blockquote>Rad etildi❌</blockquote>
"""
    if callback_data.startswith("depocheck_"):
        user.depozite = F('depozite') + dprice
        user.save(update_fields=['depozite'])
        update.callback_query.edit_message_caption(caption=tasdiqlangan_message, parse_mode="HTML")
        update.callback_query.answer("Muvaffaqiyatli✅")
        context.bot.send_message(chat_id=user_id, text="<b>Tabriklaymiz siz kiritgan depozit miqdori tasdiqlandi <u>💰 Hisobim</u> bo'limidan tekshirib olishingiz mumkin</b>", parse_mode="HTML")
    else:
        update.callback_query.edit_message_caption(caption=radetilgan_message, parse_mode="HTML")
        context.bot.send_message(chat_id=user_id, text="<b>Siz kiritgan depozit tasdiqdan o'tmadi🙁</b>\nBuni xato deb bilsangiz adminlarga bog'laning", parse_mode="HTML")
   
def set_user_depozite(update: Update, context: CallbackContext):
    admin_id = update.message.from_user.id
    text = context.args
    text2 = text[0]
    print(f'text>> {text}')
    print(f'text2>> {text2}')
    userdepozit = text2.split("_")[1]
    context.user_data['user_id_for_depozit'] = userdepozit
    user = TelegramUser.objects.get(user_id=userdepozit)
    if is_user_admin(admin_id) is True:
        update.message.reply_text(f"<b><a href='tg://user?id={user.user_id}'>{user.first_name}</a> uchun <u>depozit</u> miqdorini kiriting<?b>", parse_mode="HTML")
        return 'SET_DEPOZIT'

def set_user_depozit_end(update: Update, context: CallbackContext):
    depozite_price = update.message.text
    user_id = context.user_data['user_id_for_depozit']
    user = TelegramUser.objects.get(user_id=user_id)
    depozite_price = int(depozite_price)

    user.depozite = F('depozite') + depozite_price
    user.save(update_fields=['depozite'])
    update.message.reply_text(f"<b>{user.first_name}ga {depozite_price} so'm depozit hisobiga qo'shildi</b>", parse_mode="HTML")