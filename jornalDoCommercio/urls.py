from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

# Importa o novo formulário de login
from jornal_app.forms import CustomAuthenticationForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jornal_app.urls')),  
    
    # Linha de login MODIFICADA
    path('login/', auth_views.LoginView.as_view(
            template_name='registration/login.html',
            authentication_form=CustomAuthenticationForm # Diz ao Django para usar nosso form
        ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]