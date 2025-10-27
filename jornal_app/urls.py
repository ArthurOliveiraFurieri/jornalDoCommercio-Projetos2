from django.urls import path
from . import views

app_name = 'jornal_app'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'), 
    path('categorias/<int:pk>/', views.NoticiasPorCategoriaView.as_view(), name='noticias_por_categoria'),
    path('noticia/<int:pk>/', views.NoticiaDetailView.as_view(), name='artigo'),
    path('busca/', views.noticia_search, name='noticia_search'),
    path('editor/categorias/', views.CategoriaListView.as_view(), name='categoria_list'),
    path('editor/categorias/nova/', views.CategoriaCreateView.as_view(), name='categoria_create'),
    path('editor/categorias/<int:pk>/excluir/', views.CategoriaDeleteView.as_view(), name='categoria_delete'),
    path('comentario/<int:pk>/excluir/', views.ComentarioDeleteView.as_view(), name='comentario_delete'),
    
    # ✅ URL simplificada - sem importação complexa
    path('importar-noticias/', views.importar_noticias, name='importar_noticias'),
]