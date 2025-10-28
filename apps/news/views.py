from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import News, Category, Tag, Comment


class NewsListView(ListView):
    """Lista todas as notícias publicadas"""
    model = News
    template_name = 'news/list.html'
    context_object_name = 'news_list'
    paginate_by = 12

    def get_queryset(self):
        return News.objects.filter(is_published=True).select_related('category', 'author')


class NewsDetailView(DetailView):
    """Detalhe de uma notícia"""
    model = News
    template_name = 'news/detail.html'
    context_object_name = 'news'

    def get_queryset(self):
        return News.objects.filter(is_published=True).select_related('category', 'author')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Incrementa visualizações
        obj.increment_views()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        news = self.get_object()

        # Comentários aprovados
        context['comments'] = news.comments.filter(is_approved=True).select_related('author')

        # Notícias relacionadas (mesma categoria)
        context['related_news'] = News.objects.filter(
            is_published=True,
            category=news.category
        ).exclude(id=news.id)[:4]

        return context


class CategoryNewsView(ListView):
    """Lista notícias por categoria"""
    model = News
    template_name = 'news/category.html'
    context_object_name = 'news_list'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return News.objects.filter(
            is_published=True,
            category=self.category
        ).select_related('category', 'author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class TagNewsView(ListView):
    """Lista notícias por tag"""
    model = News
    template_name = 'news/tag.html'
    context_object_name = 'news_list'
    paginate_by = 12

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return News.objects.filter(
            is_published=True,
            tags=self.tag
        ).select_related('category', 'author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class SearchNewsView(ListView):
    """Busca de notícias"""
    model = News
    template_name = 'news/search.html'
    context_object_name = 'news_list'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return News.objects.filter(
                Q(title__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(content__icontains=query),
                is_published=True
            ).select_related('category', 'author')
        return News.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


@login_required
def add_comment(request, slug):
    """Adiciona um comentário a uma notícia"""
    news = get_object_or_404(News, slug=slug, is_published=True)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()

        if content:
            Comment.objects.create(
                news=news,
                author=request.user,
                content=content,
                is_approved=False  # Comentários precisam de aprovação
            )
            messages.success(request, 'Comentário enviado! Ele será publicado após moderação.')
        else:
            messages.error(request, 'O comentário não pode estar vazio.')

    return redirect('news:detail', slug=slug)
