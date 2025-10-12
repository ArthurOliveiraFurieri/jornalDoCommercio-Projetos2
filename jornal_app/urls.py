from django.urls import path
from .views import (
    CategoriaListView,
    CategoriaCreateView,
    CategoriaDeleteView,
    NoticiasPorCategoriaView,
)

urlpatterns = [
    # URLs para o leitor
    path('categorias/<int:pk>/', NoticiasPorCategoriaView.as_view(), name='noticias_por_categoria'),
    
    # URLs para o painel do editor
    path('editor/categorias/', CategoriaListView.as_view(), name='categoria_list'),
    path('editor/categorias/nova/', CategoriaCreateView.as_view(), name='categoria_create'),
    path('editor/categorias/<int:pk>/excluir/', CategoriaDeleteView.as_view(), name='categoria_delete'),
]