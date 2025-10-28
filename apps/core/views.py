from django.shortcuts import render
from django.views.generic import TemplateView
from apps.news.models import News


class HomeView(TemplateView):
    """Página inicial do jornal"""
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Notícias em destaque
        context['featured_news'] = News.objects.filter(
            is_published=True,
            is_featured=True
        ).order_by('-published_at')[:3]

        # Notícias recentes
        context['recent_news'] = News.objects.filter(
            is_published=True
        ).order_by('-published_at')[:6]

        # Informações do dia (estático por enquanto)
        context['info_bar'] = {
            'temperature_max': '30°C',
            'temperature_min': '27°C',
            'dolar': 'R$ 5,35',
            'euro': 'R$ 7,43'
        }

        return context
