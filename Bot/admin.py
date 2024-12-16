# your_app/admin.py
from django.contrib import admin
from .models import TelegramUser, Task, TaskCompletion, Referral, UserMessage, PassportInfo
from django.db.models.functions import Now


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'user_id', 'last_name', 'phone_number', 'is_admin', 'is_active')
    list_filter = ('is_admin', 'is_active')  # Filtrlar
    search_fields = ('user_id', 'first_name', 'last_name', 'phone_number') 
    ordering = ['-date_created']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'task_type')
    list_filter = ('task_type',)



@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'completion_date', 'amount_added', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'task__name')


from .models import BotStats, MandatoryChannel, Channel, JoinRequest

@admin.register(BotStats)
class BotStatsAdmin(admin.ModelAdmin):
    list_display = ['guide', 'deposit_card_number', 'daily_limit', 'bonus_money','mandatory_channel_count', 'user_count']
    readonly_fields = ['mandatory_channel_count', 'user_count']  # Bu maydonlar faqat o‘qish uchun

    def save_model(self, request, obj, form, change):
        """Har safar yangi ma'lumot qo'shilganda eski ma'lumotni o'chirish"""
        # Avvalgi BotStats obyektlarini o‘chirish
        BotStats.objects.exclude(pk=obj.pk).delete()
        super().save_model(request, obj, form, change)


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referred_user', 'referral_price', 'created_at']
    list_editable = ['referral_price']  # Referral narxini to‘g‘ridan-to‘g‘ri admin paneldan o‘zgartirish
    list_filter = ['created_at']
    search_fields = ['referrer__username', 'referred_user__username']

class MandatoryChannelAdmin(admin.ModelAdmin):
    list_display = ('channel_id', 'channel_name', 'purpose', 'channel_type', 'channel_url')
    search_fields = ('channel_name', 'channel_id')
    list_filter = ('channel_type',)

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('channel_id', 'name', 'type', 'url')
    search_fields = ('name', 'channel_id')
    list_filter = ('type',)

class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'full_name', 'channel', 'request_date')
    search_fields = ('user_id', 'full_name', 'channel__name')
    list_filter = ('channel',)

admin.site.register(MandatoryChannel, MandatoryChannelAdmin)
admin.site.register(JoinRequest, JoinRequestAdmin)



@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'is_reviewed', 'created_at', 'reviewed_at']
    list_filter = ['is_reviewed', 'created_at']
    search_fields = ['user__username', 'subject', 'message']
    actions = ['mark_as_reviewed']

    def mark_as_reviewed(self, request, queryset):
        """Tanlangan murojaatlarni ko‘rib chiqilgan deb belgilash"""
        queryset.update(is_reviewed=True, reviewed_at=Now())
        self.message_user(request, "Murojaatlar ko‘rib chiqilgan deb belgilandi.")
    mark_as_reviewed.short_description = "Ko‘rib chiqilgan deb belgilash"


@admin.register(PassportInfo)
class PassportInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'birth_date', 'passport_series')  # Ko‘rinadigan ustunlar
    search_fields = ('first_name', 'last_name', 'passport_series', 'user__user_id')  # Qidiruv maydonlari
    list_filter = ('birth_date',)  # Filtrlash bo‘limi
    ordering = ('-birth_date',)  # Saralash
    readonly_fields = ('passport_image',)  # Rasmni faqat o‘qish uchun qoldirish
