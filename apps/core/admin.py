from django.contrib import admin
from .models import SiteConfiguration, Menu


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'contact_email', 'contact_phone']

    def has_add_permission(self, request):
        # Permite adicionar apenas se não existir nenhuma configuração
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Não permite deletar a configuração
        return False


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'order', 'is_active', 'open_in_new_tab']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'url']
