from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = 'jornal_app'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'), 
    path('categorias/<int:pk>/', views.NoticiasPorCategoriaView.as_view(), name='noticias_por_categoria'),
    path('noticia/<int:pk>/', views.NoticiaDetailView.as_view(), name='artigo'),
    path('busca/', views.noticia_search, name='noticia_search'),
    path('editor/categorias/', views.CategoriaListView.as_view(), name='categoria_list'),
    path('editor/categorias/nova/', views.CategoriaCreateView.as_view(), name='categoria_create'),
    path('editor/categorias/<int:pk>/excluir/', views.CategoriaDeleteView.as_view(), name='categoria_delete'),
    path('feed/', views.MaisNoticiasView.as_view(), name='noticia_feed'),
    path('comentario/<int:pk>/excluir/', views.comentario_delete.as_view(), name='comentario_delete'),
    
    # ✅ URLs para API
    path('importar-noticias/', views.importar_noticias, name='importar_noticias'),
    path('criar-categorias-api/', views.criar_categorias_api, name='criar_categorias_api'),
    
    # ✅ URLs PARA RESET (USE APENAS ESTAS)
    path('reset-total/', views.reset_total, name='reset_total'),
    path('criar-categorias-definitivas/', views.criar_categorias_definitivas, name='criar_categorias_definitivas'),
    
    # ✅ URLs DE AUTENTICAÇÃO - CORRIGIDAS
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('jornal_app:home')), name='logout'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/profile/', views.profile, name='profile'),
    
    # ✅ INFINITE SCROLL PARA CATEGORIAS
    path('categorias/<int:pk>/feed/', views.MaisNoticiasCategoriaView.as_view(), name='categoria_feed'),
]