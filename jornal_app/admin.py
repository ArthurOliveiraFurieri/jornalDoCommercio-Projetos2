from django.contrib import admin
from .models import Categoria, Noticia, Comentario  

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'data_publicacao', 'destaque')
    list_filter = ('categoria', 'data_publicacao', 'destaque')
    search_fields = ('titulo', 'conteudo')

# ADICIONE ESTE NOVO REGISTRO PARA COMENTÁRIOS
@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['autor', 'noticia', 'data_criacao', 'ativo']
    list_filter = ['ativo', 'data_criacao', 'noticia__categoria']
    search_fields = ['autor__username', 'noticia__titulo', 'texto']
    list_editable = ['ativo']  # Permite ativar/desativar diretamente na lista
    actions = ['aprovar_comentarios', 'rejeitar_comentarios']
    
    def aprovar_comentarios(self, request, queryset):
        queryset.update(ativo=True)
        self.message_user(request, f"{queryset.count()} comentário(s) aprovado(s) com sucesso!")
    aprovar_comentarios.short_description = "Aprovar comentários selecionados"
    
    def rejeitar_comentarios(self, request, queryset):
        queryset.update(ativo=False)
        self.message_user(request, f"{queryset.count()} comentário(s) rejeitado(s)!")
    rejeitar_comentarios.short_description = "Rejeitar comentários selecionados"