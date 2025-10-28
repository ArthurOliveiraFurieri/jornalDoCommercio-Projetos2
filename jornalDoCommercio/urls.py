from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Autenticação
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Apps do projeto (nova estrutura)
    path('', include('apps.core.urls')),
    path('noticias/', include('apps.news.urls')),
    path('ao-vivo/', include('apps.live.urls')),

    # App antigo (manter temporariamente para compatibilidade)
    # path('old/', include('jornal_app.urls')),
]

# Servir arquivos de media durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)