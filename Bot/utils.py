from .models import TelegramUser, Task
from django.core.exceptions import ObjectDoesNotExist


def save_telegram_user(data):
    """
    Telegram foydalanuvchi ma'lumotlarini bazaga saqlaydi yoki yangilaydi.
    :param data: Foydalanuvchining barcha kerakli ma'lumotlari (lug'at)
    """
    try:
        if data['user_id'] in "6194484795":
            telegram_user, created = TelegramUser.objects.update_or_create(
                user_id=data['user_id'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'phone_number': data['phone_number'],
                    'is_admin': False,  # Standart qiymat
                    'status': 'user',
                    'task_completed_count': f'0_{bugungi_kun()}_1'
                }
            )
            return telegram_user
        else:
            telegram_user, created = TelegramUser.objects.update_or_create(
                user_id=data['user_id'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'phone_number': data['phone_number'],
                    'is_admin': True,  # Standart qiymat
                    'status': 'user',
                    'task_completed_count': f'0_{bugungi_kun()}_1'
                }
            )
            return telegram_user
    except Exception as e:
        print(f"Error saving user: {e}")
        return None


def update_user_status(user_id, status):
    # Bu funksiya foydalanuvchi statusini yangilash uchun kerak bo'ladi.
    # Masalan, statusni DBga saqlash uchun.
    # Misol:
    user = TelegramUser.objects.get(user_id=user_id)
    user.status = status
    user.save()
    pass

def save_task_data(data):
    """
    PTB context.user_data dan olingan ma'lumotlarni Task modeliga saqlovchi funksiya.
    :param data: dictionary (context.user_data) formatida bo'lishi kerak.
    :return: Task obyekti yoki xatolik uchun ValueError.
    """
    try:
        # Kerakli maydonlar
        name = data.get("task_name")
        url = data.get("task_url")
        reward = data.get("reward")
        description = data.get("task_caption")
        task_type = data.get("task_type")  # Default "other"

        # Saqlashdan oldin tekshiruv
        if not name or not url or not reward or not description:
            raise ValueError("Kerakli ma'lumotlar to'liq emas. 'name', 'url', 'reward', 'description' kerak.")

        # task_type tekshiruvi
        if task_type not in [choice[0] for choice in Task.TASK_TYPES]:
            raise ValueError(f"Noto'g'ri task_type: {task_type}. Yaroqli qiymatlar: {', '.join([choice[0] for choice in Task.TASK_TYPES])}")
        reward = float(reward)
        # Task obyekti yaratish va saqlash
        task = Task(
            name=name,
            url=url,
            reward=reward,
            description=description,
            task_type=task_type
        )
        task.save()
        return task

    except Exception as e:
        raise ValueError(f"Xatolik yuz berdi: {e}")


def is_user_admin(user_id):
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        return user.is_admin
    except ObjectDoesNotExist:
        return False

from datetime import datetime

def bugungi_kun():
    kun = datetime.now().day
    return kun
