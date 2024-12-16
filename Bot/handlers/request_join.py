from telegram import Update
from telegram.ext import CallbackContext
from ..models import Channel, JoinRequest

def handle_join_request(update: Update, context: CallbackContext):
    """Foydalanuvchining kanal/guruhga qo'shilish so'rovini loglash."""
    join_request = update.chat_join_request
    user = join_request.from_user
    chat = join_request.chat

    # Kanalni bazada izlash yoki yaratish
    channel, created = Channel.objects.get_or_create(
        channel_id=chat.id,
        defaults={'name': chat.title, 'type': 'group' if chat.type == 'group' else 'public'}
    )

    # Foydalanuvchini JoinRequest modeliga qo'shish
    JoinRequest.objects.create(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        channel=channel
    )

    print(f"Foydalanuvchi {user.full_name} so'rov yubordi!")
