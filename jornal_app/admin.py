from django.contrib import admin
# --- Importe os 4 modelos ---
from .models import Categoria, Noticia, Comentario, Profile

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    # --- MODIFICADO AQUI ---
    list_display = ('titulo', 'categoria', 'data_publicacao', 'destaque', 'exclusivo')
    list_filter = ('categoria', 'data_publicacao', 'destaque', 'exclusivo')
    # --- FIM DA MODIFICAÇÃO ---
    
    search_fields = ('titulo', 'conteudo')

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    # (Seu código foi mantido, está perfeito)
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

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Permite ver e editar quem é assinante pelo Admin.
    """
    list_display = ('user', 'is_assinante')
    list_editable = ('is_assinante',)
    search_fields = ('user__username',)