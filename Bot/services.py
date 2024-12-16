from .models import BotStats, Referral, TelegramUser
from django.db.models.functions import Now


# 1. BotStats bilan ishlash
def get_bot_stats():
    """Bot statistikasi ma'lumotlarini olish"""
    return BotStats.objects.first()

def update_bot_stats_referral_price(price):
    """Referral narxini yangilash"""
    bot_stats = BotStats.objects.first()
    if bot_stats:
        bot_stats.referral_price = price
        bot_stats.save()
        return bot_stats
    return None


# 2. Referral bilan ishlash
def create_referral(referrer_id, referred_user_id):
    """Yangi referral ma'lumotini yaratish"""
    referrer = TelegramUser.objects.get(id=referrer_id)
    referred_user = TelegramUser.objects.get(id=referred_user_id)
    referral = Referral.objects.create(referrer=referrer, referred_user=referred_user)
    return referral

def delete_referral(referral_id):
    """Referral ma'lumotini o'chirish"""
    referral = Referral.objects.get(id=referral_id)
    referral.delete()

def get_referrals_for_user(user_id):
    """Foydalanuvchining referral ma'lumotlarini olish"""
    user = TelegramUser.objects.get(id=user_id)
    return user.referred_users.all()

def get_user_total_referral_reward(user_id):
    """Foydalanuvchining umumiy referral mukofotini hisoblash"""
    user = TelegramUser.objects.get(id=user_id)
    bot_stats = BotStats.objects.first()
    referral_price = bot_stats.referral_price if bot_stats else 0
    referral_count = user.referred_users.count()
    return referral_count * referral_price



def update_bot_guide(new_guide):
    """Bot qo‘llanmasini yangilash"""
    # Yagona `BotStats` obyektini olish yoki yangi yaratish
    bot_stats, created = BotStats.objects.get_or_create(id=1)
    bot_stats.guide = new_guide
    bot_stats.save()
    return bot_stats

from .models import UserMessage

def create_user_message(user, subject, message, message_id):
    """Foydalanuvchi murojaatini yaratish"""
    user_message = UserMessage.objects.create(user=user, subject=subject, message=message, message_id=message_id)
    return user_message


def get_user_messages(user):
    """Foydalanuvchining barcha murojaatlarini olish"""
    return UserMessage.objects.filter(user=user)

def mark_message_as_reviewed(message_id):
    """Murojaatni ko‘rib chiqilgan deb belgilash"""
    message = UserMessage.objects.get(id=message_id)
    message.is_reviewed = True
    message.reviewed_at = Now()
    message.save()
    return message
