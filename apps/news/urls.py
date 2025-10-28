from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.NewsListView.as_view(), name='list'),
    path('buscar/', views.SearchNewsView.as_view(), name='search'),
    path('categoria/<slug:slug>/', views.CategoryNewsView.as_view(), name='category'),
    path('tag/<slug:slug>/', views.TagNewsView.as_view(), name='tag'),
    path('<slug:slug>/', views.NewsDetailView.as_view(), name='detail'),
    path('<slug:slug>/comentar/', views.add_comment, name='add_comment'),
]
