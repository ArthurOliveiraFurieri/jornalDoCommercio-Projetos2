from django.contrib import admin
from .models import LiveEvent


@admin.register(LiveEvent)
class LiveEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'scheduled_at', 'is_active', 'created_by']
    list_filter = ['is_active', 'scheduled_at']
    search_fields = ['title', 'description']
