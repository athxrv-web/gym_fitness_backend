"""
URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('fitness.urls')),
    path('api/members/', include('members.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/reminders/', include('reminders.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/whatsapp/', include('whatsapp.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Gym Fitness Backend"
admin.site.site_title = "Gym Admin"
admin.site.index_title = "Welcome to Gym Management"