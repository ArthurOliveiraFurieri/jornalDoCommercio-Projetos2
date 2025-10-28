from django.contrib import admin
from .models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'is_active', 'start_date', 'end_date', 'clicks']
    list_filter = ['is_active', 'position', 'start_date']
    list_editable = ['is_active']
    search_fields = ['title']
    readonly_fields = ['clicks']
