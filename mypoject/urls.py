from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Встроенные маршруты авторизации Django (логин)
    path('accounts/', include('django.contrib.auth.urls')), 
    
    # Главные маршруты приложения сотрудников
    path('', include('employees.urls')), 
]

# Раздача медиафайлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
