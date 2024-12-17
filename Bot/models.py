from django.db import models

STATUS_CHOICES = [
    ('user', 'User'),
    ('main_admin', 'Bosh Admin'),
    ('admin_request', 'Murojaat Admin'),
    ('payment_admin', 'To\'lo\'v Admin'),
    ('deposit_admin', 'Depozit Admin'),
]

class TelegramUser(models.Model):
    user_id = models.BigIntegerField(unique=True, verbose_name="Telegram User ID")
    first_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="First Name")
    last_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Last Name")
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number")
    card_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Card Number")  # Qo'shildi
    is_admin = models.BooleanField(default=False, verbose_name="Is Admin")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='user', 
        verbose_name="User Status"
    )
    balance = models.IntegerField(default=0, verbose_name="User Balance")
    depozite = models.IntegerField(default=0, verbose_name="User Deposit Price")
    reff = models.IntegerField(default=0, verbose_name="User Referral Count")
    withdraw = models.IntegerField(default=0, verbose_name="Money Withdraw")
    task_completed_count = models.CharField(max_length=10, default=0, verbose_name="Task Completed Count")  # Qo'shildi
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    date_updated = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    def __str__(self):
        return f"{self.first_name or 'No Name'} ({self.user_id})"

    class Meta:
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"
        ordering = ['-date_created']

    @property
    def total_referral_reward(self):
        referral_count = self.referred_users.count()  # Taklif qilingan foydalanuvchilar soni
        referral_price = BotStats.objects.first().referral_price  # Bir taklif narxi
        return referral_count * referral_price

    @staticmethod
    def get_admin_ids():
        """
        Barcha adminlarning `user_id` larini olish.
        """
        admin_users = TelegramUser.objects.filter(is_admin=True)
        return [user.user_id for user in admin_users]


class PassportInfo(models.Model):
    user = models.OneToOneField(
        TelegramUser, 
        on_delete=models.CASCADE, 
        related_name='passport_info', 
        verbose_name="Related User"
    )
    first_name = models.CharField(max_length=150, verbose_name="First Name")
    last_name = models.CharField(max_length=150, verbose_name="Last Name")
    birth_date = models.DateField(verbose_name="Date of Birth")
    passport_series = models.CharField(
        max_length=9, 
        verbose_name="Passport Series", 
        unique=True, 
        help_text="Format: AA1234567"
    )
    passport_image = models.ImageField(upload_to='passport_images/', verbose_name="Passport Image")

    def __str__(self):
        return f"Passport Info of {self.user.first_name or 'Unknown'}"

    class Meta:
        verbose_name = "Passport Information"
        verbose_name_plural = "Passport Informations"



TASK_TYPES = [
    ('telegram', 'Telegram'),
    ('instagram', 'Instagram'),
    ('youtube', 'YouTube'),
    ('tiktok', 'TikTok'),
    ('facebook', 'Facebook'),
    ('other', 'Other'),
]

class Task(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name="Task Name")
    url = models.CharField(max_length=200, verbose_name="Task Url")
    is_active = models.BooleanField(default=True)
    reward = models.IntegerField(verbose_name="Task reward")
    description = models.TextField(verbose_name="Description")

    TASK_TYPES = [
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('facebook', 'Facebook'),
        ('other', 'Other'),
    ]

    task_type = models.CharField(
        max_length=10,
        choices=TASK_TYPES,
        default='other',
        verbose_name="Task Type"
    )

    def get_channel_info(self):
        """
        Kanal URL va ID'ni ajratib oladi.
        """
        if 't.me/' in self.url:
            parts = self.url.split('/')  # URL'ni bo'lib chiqamiz
            return parts[-1]  # Username yoki kanal ID'si
        return None

    def __str__(self):
        return f"{self.description[:50]} ({self.get_task_type_display()})"

class TaskCompletion(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)  # Foydalanuvchi
    task = models.ForeignKey(Task, on_delete=models.CASCADE)  # Vazifa
    completion_date = models.DateTimeField(auto_now_add=True)  # Vazifa tugallangan vaqt
    amount_added = models.DecimalField(max_digits=10, decimal_places=2)  # Balansga qo'shilgan pul miqdori
    is_completed = models.BooleanField(default=False)  # Vazifa yakunlandi yoki yo'q
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',  # Boshlang'ich qiymat "kutilmoqda"
    )

    def __str__(self):
        return f"{self.user} - {self.task.name} - {self.amount_added} so'm - {self.status}"


class BotStats(models.Model):
    guide = models.TextField(verbose_name="Bot qo‘llanmasi", blank=True, null=True)
    deposit_card_number = models.CharField(
        verbose_name="Depozit uchun karta raqami",
        max_length=20,
        blank=True,
        null=True,
        help_text="Depozitlar uchun karta raqami saqlanadi"
    )
    daily_limit = models.IntegerField(default=0, verbose_name="Userlarning kunlik vazifa bajarish limiti")
    bonus_money = models.IntegerField(default=5000, verbose_name="Userni birinchi botga kirganda sovg'a puli")

    class Meta:
        verbose_name = "Bot statistikasi"
        verbose_name_plural = "Bot statistikasi"

    def __str__(self):
        return "Bot statistikasi"

    @property
    def mandatory_channel_count(self):
        return MandatoryChannel.objects.count()

    @property
    def user_count(self):
        return TelegramUser.objects.count()

    def update_deposit_card_number(self, new_card_number):
        """
        Depozit karta raqamini yangilash uchun funksiya.
        Faqat karta raqami yangilanadi, guide o'zgarmasdan qoladi.
        """
        self.deposit_card_number = new_card_number
        self.save(update_fields=['deposit_card_number'])

    def update_daily_limit(self, new_limit):
        """
        Kunlik vazifa bajarish limitini yangilash uchun funksiya.
        Faqat daily_limit ustuni yangilanadi.
        """
        self.daily_limit = new_limit
        self.save(update_fields=['daily_limit'])

    def update_bonus_money(self, new_bonus_money):
        """
        Kunlik vazifa bajarish limitini yangilash uchun funksiya.
        Faqat daily_limit ustuni yangilanadi.
        """
        self.bonus_money = new_bonus_money
        self.save(update_fields=['bonus_money'])



CHANNEL_TYPES = [
    ('channel', 'Kanal'),
    ('group', 'Guruh'),
]

PURPOSE_TYPES = [
    ('payments', 'To‘lovlar uchun'),
    ('check_task', 'Vazifalarni tekshirish uchun'),
    ('support', 'Foydalanuvchi murojaatlari uchun'),
    ('deposit', 'Depozitni tasdiqlash uchun'),
    ('user_verification', 'Foydalanuvchilarni tasdiqlash uchun')
]


class MandatoryChannel(models.Model):
    CHANNEL_TYPES = [
        ('channel', 'Kanal'),
        ('group', 'Guruh'),
    ]
    PURPOSE_TYPES = [
        ('payments', 'To‘lovlar uchun'),
        ('check_task', 'Vazifalarni tekshirish uchun'),
        ('support', 'Foydalanuvchi murojaatlari uchun'),
        ('deposit', 'Depozitni tasdiqlash uchun'),
        ('user_verification', 'Foydalanuvchilarni tasdiqlash uchun')
    ]


    channel_id = models.CharField(max_length=100, unique=True, verbose_name="Kanal/Guruh ID")
    channel_name = models.CharField(max_length=255, verbose_name="Kanal/Guruh nomi")
    channel_type = models.CharField(
        max_length=10,
        choices=CHANNEL_TYPES,
        verbose_name="Kanal turi"
    )
    purpose = models.CharField(
        max_length=20,
        choices=PURPOSE_TYPES,
        verbose_name="Kanal/Guruh maqsadi",
        default='other'  # Standart qiymat
    )
    channel_url = models.URLField(verbose_name="Kanal/Guruh URL manzili", blank=True, null=True)

    class Meta:
        verbose_name = "Majburiy kanal/guruh"
        verbose_name_plural = "Majburiy kanallar/guruhlar"

    def __str__(self):
        return f"{self.channel_name} ({dict(self.CHANNEL_TYPES).get(self.channel_type)}) - {dict(self.PURPOSE_TYPES).get(self.purpose)}"


class Channel(models.Model):
    """Kanal yoki guruh haqida ma'lumotlarni saqlash uchun model."""
    CHANNEL_TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('group', 'Group'),
    ]

    channel_id = models.CharField(max_length=255, unique=True)  # Kanal ID
    name = models.CharField(max_length=255)  # Kanal nomi
    type = models.CharField(max_length=10, choices=CHANNEL_TYPE_CHOICES)  # Kanal turi
    url = models.URLField(null=True, blank=True)  # Kanalning URL manzili (agar mavjud bo'lsa)

    def __str__(self):
        return self.name


class JoinRequest(models.Model):
    """Kanalga qo'shilish so'rovi yuborgan foydalanuvchilarni saqlash uchun model."""
    user_id = models.BigIntegerField()  # Foydalanuvchi IDsi
    username = models.CharField(max_length=255, null=True, blank=True)  # Foydalanuvchi username (agar mavjud bo'lsa)
    full_name = models.CharField(max_length=255)  # Foydalanuvchi to'liq ismi
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)  # Kanalga bog'lanish (kanalga oid ma'lumot)
    request_date = models.DateTimeField(auto_now_add=True)  # So'rov yuborilgan sana va vaqt

    def __str__(self):
        return f"{self.full_name} ({self.user_id}) - {self.channel.name}"


class Referral(models.Model):
    referrer = models.ForeignKey(
        "TelegramUser", on_delete=models.CASCADE, related_name="referred_users", verbose_name="Taklif qiluvchi foydalanuvchi"
    )
    referred_user = models.ForeignKey(
        "TelegramUser", on_delete=models.CASCADE, related_name="referrals", verbose_name="Taklif qilingan foydalanuvchi"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Taklif qilingan sana")
    referral_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Referral narxi", default=0.0
    )

    class Meta:
        verbose_name = "Referral"
        verbose_name_plural = "Referral"

    def __str__(self):
        return f"{self.referrer} → {self.referred_user}"

  # Agar foydalanuvchilarni User modeli bilan bog‘lamoqchi bo‘lsangiz

class UserMessage(models.Model):
    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="messages", verbose_name="Foydalanuvchi"
    )
    subject = models.CharField(max_length=255, verbose_name="Murojaat mavzusi")
    message = models.TextField(verbose_name="Murojaat matni")
    is_reviewed = models.BooleanField(default=False, verbose_name="Ko‘rib chiqilganmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqt")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Ko‘rib chiqilgan vaqt")
    message_id = models.PositiveIntegerField(verbose_name="Xabar ID", null=True, blank=True)  # Yangi ustun

    class Meta:
        verbose_name = "Foydalanuvchi murojaati"
        verbose_name_plural = "Foydalanuvchi murojaatlari"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.first_name} - {self.subject}"
