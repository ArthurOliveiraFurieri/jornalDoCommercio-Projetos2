from django.contrib import admin
from .models import Category, Tag, News, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_published', 'is_featured', 'published_at', 'views_count']
    list_filter = ['is_published', 'is_featured', 'category', 'created_at', 'published_at']
    list_editable = ['is_published', 'is_featured']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    date_hierarchy = 'published_at'
    readonly_fields = ['views_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'slug', 'excerpt', 'category', 'tags')
        }),
        ('Conteúdo', {
            'fields': ('content', 'featured_image')
        }),
        ('Publicação', {
            'fields': ('author', 'is_published', 'is_featured', 'published_at')
        }),
        ('Estatísticas', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'news', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    list_editable = ['is_approved']
    search_fields = ['author_name', 'content', 'news__title']
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('news', 'author')
