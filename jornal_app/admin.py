from django.contrib import admin
from .models import Categoria, Noticia, Comentario  

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'data_publicacao', 'destaque', 'autor_fonte')
    list_filter = ('categoria', 'data_publicacao', 'destaque')
    search_fields = ('titulo', 'conteudo', 'autor_fonte')
    list_editable = ('destaque',)
    readonly_fields = ('data_publicacao',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'conteudo', 'categoria')
        }),
        ('Configurações de Exibição', {
            'fields': ('destaque', 'data_publicacao')
        }),
        ('Informações da Fonte Externa', {
            'fields': ('url_fonte', 'imagem_url', 'autor_fonte'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marcar_como_destaque', 'remover_destaque']
    
    def marcar_como_destaque(self, request, queryset):
        queryset.update(destaque=True)
        self.message_user(request, f"{queryset.count()} notícia(s) marcada(s) como destaque!")
    marcar_como_destaque.short_description = "Marcar como destaque"
    
    def remover_destaque(self, request, queryset):
        queryset.update(destaque=False)
        self.message_user(request, f"{queryset.count()} notícia(s) removida(s) dos destaques!")
    remover_destaque.short_description = "Remover dos destaques"

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['autor', 'noticia', 'data_criacao', 'ativo']
    list_filter = ['ativo', 'data_criacao', 'noticia__categoria']
    search_fields = ['autor__username', 'noticia__titulo', 'texto']
    list_editable = ['ativo']
    actions = ['aprovar_comentarios', 'rejeitar_comentarios']
    
    def aprovar_comentarios(self, request, queryset):
        queryset.update(ativo=True)
        self.message_user(request, f"{queryset.count()} comentário(s) aprovado(s) com sucesso!")
    aprovar_comentarios.short_description = "Aprovar comentários selecionados"
    
    def rejeitar_comentarios(self, request, queryset):
        queryset.update(ativo=False)
        self.message_user(request, f"{queryset.count()} comentário(s) rejeitado(s)!")
    rejeitar_comentarios.short_description = "Rejeitar comentários selecionados"