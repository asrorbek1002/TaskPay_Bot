from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Boshqa yo'nalishlaringiz
]

# Media fayllar uchun URL yo'nalishi
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
