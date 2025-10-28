from .models import SiteConfiguration, Menu
from apps.news.models import Category


def site_settings(request):
    """Adiciona configurações do site ao contexto de todos os templates"""
    return {
        'site_config': SiteConfiguration.get_config(),
        'menu_items': Menu.objects.filter(is_active=True),
        'categories': Category.objects.filter(is_active=True).order_by('order'),
    }
