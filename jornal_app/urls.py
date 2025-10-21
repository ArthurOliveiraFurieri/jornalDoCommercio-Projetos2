from django.urls import path
from .views import (
    HomeView, 
    noticia_search,
    CategoriaListView,
    CategoriaCreateView,
    CategoriaDeleteView,
    NoticiasPorCategoriaView,

    NoticiaDetailView,
)

urlpatterns = [
    # --- URL DA HOME ---
    path('', HomeView.as_view(), name='home'), 
    
    # URLs para o leitor
    path('categorias/<int:pk>/', NoticiasPorCategoriaView.as_view(), name='noticias_por_categoria'),
    path('noticia/<int:pk>/', NoticiaDetailView.as_view(), name='noticia_detail'),

    # URL da Busca (NOVA)
    path('busca/', noticia_search, name='noticia_search'),

    # URLs para o painel do editor
    path('editor/categorias/', CategoriaListView.as_view(), name='categoria_list'),
    path('editor/categorias/nova/', CategoriaCreateView.as_view(), name='categoria_create'),
    path('editor/categorias/<int:pk>/excluir/', CategoriaDeleteView.as_view(), name='categoria_delete'),
]