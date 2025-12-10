from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

class Categoria(models.Model):
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome da Categoria",
        help_text="O nome deve ser único para cada categoria."
    ) 

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Noticia(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    conteudo = models.TextField(verbose_name="Conteúdo")
    data_publicacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Publicação")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='noticias',
        verbose_name="Categoria"
    )
    
    destaque = models.BooleanField(
        default=False,
        verbose_name="Notícia em Destaque",
        help_text="Marque para que esta notícia apareça na seção de destaques da homepage."
    )
    
    url_fonte = models.URLField(
        max_length=500, 
        blank=True, 
        null=True,
        verbose_name="URL da Fonte Original"
    )
    
    imagem_url = models.URLField(
        max_length=500, 
        blank=True, 
        null=True,
        verbose_name="URL da Imagem"
    )
    
    autor_fonte = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Autor/Fonte Externa"
    )

    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"
        ordering = ['-data_publicacao']

    def __str__(self):
        return self.titulo
    
    def get_absolute_url(self):
        return reverse('jornal_app:artigo', kwargs={'pk': self.pk})

class Comentario(models.Model):
    noticia = models.ForeignKey(
        Noticia, 
        on_delete=models.CASCADE, 
        related_name='comentarios' 
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    texto = models.TextField(verbose_name="Seu Comentário")
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True) 

    class Meta:
        ordering = ['data_criacao'] 
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"

    def __str__(self):
        return f'Comentário de {self.autor.username} em {self.noticia.titulo}'

class UserProfile(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='userprofile'
    )
    pontos = models.IntegerField(default=0, verbose_name="Pontos")
    nivel = models.IntegerField(default=1, verbose_name="Nível")
    noticias_lidas = models.IntegerField(default=0, verbose_name="Notícias Lidas")
    comentarios_feitos = models.IntegerField(default=0, verbose_name="Comentários Feitos")
    categorias_visitadas = models.JSONField(default=list, blank=True, verbose_name="Categorias Visitadas")
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_atividade = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil do Usuário"
        verbose_name_plural = "Perfis dos Usuários"

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    def adicionar_pontos(self, quantidade, motivo=""):
        self.pontos += quantidade
        novo_nivel = (self.pontos // 100) + 1
        
        if novo_nivel > self.nivel:
            self.nivel = novo_nivel
            print(f"🎉 {self.usuario.username} subiu para o nível {self.nivel}!")
        
        self.save()
        return novo_nivel > self.nivel  # Retorna True se subiu de nível

    def marcar_noticia_lida(self, noticia_id):
        self.noticias_lidas += 1
        level_up = self.adicionar_pontos(5, f"Leitura da notícia {noticia_id}")
        return level_up

    def marcar_comentario_feito(self):
        self.comentarios_feitos += 1
        level_up = self.adicionar_pontos(10, "Comentário feito")
        return level_up

    def marcar_categoria_visitada(self, categoria_id):
        if categoria_id not in self.categorias_visitadas:
            self.categorias_visitadas.append(categoria_id)
            level_up = self.adicionar_pontos(15, f"Nova categoria visitada: {categoria_id}")
            return level_up
        return False

    def get_progresso_porcentagem(self):
        pontos_no_nivel = self.pontos % 100
        return min(100, (pontos_no_nivel / 100) * 100)

    def get_pontos_proximo_nivel(self):
        return 100 - (self.pontos % 100)

    def get_badges(self):
        badges = []
        
        if self.noticias_lidas >= 10:
            badges.append('📚  Leitor Iniciante')
        if self.noticias_lidas >= 50:
            badges.append('📖  Leitor Ávido')
        if self.comentarios_feitos >= 5:
            badges.append('💬  Comentarista')
        if self.comentarios_feitos >= 20:
            badges.append('🗣️  Debatedor')
        if len(self.categorias_visitadas) >= 3:
            badges.append('🧭  Explorador')
        if len(self.categorias_visitadas) >= Categoria.objects.count():
            badges.append('🌎  Navegador Completo')
        if self.nivel >= 5:
            badges.append('⭐  Estrela em Ascensão')
        if self.nivel >= 10:
            badges.append('🏆  Lenda do Jornal')
            
        return badges

    def get_estatisticas(self):
        return {
            'noticias_lidas': self.noticias_lidas,
            'comentarios_feitos': self.comentarios_feitos,
            'categorias_exploradas': len(self.categorias_visitadas),
            'total_categorias': Categoria.objects.count(),
            'progresso_porcentagem': self.get_progresso_porcentagem(),
            'pontos_proximo_nivel': self.get_pontos_proximo_nivel(),
            'badges': self.get_badges(),
        }

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def criar_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(usuario=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def salvar_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

# Mantenha a classe Perfil original se precisar para compatibilidade
class Perfil(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    
    def __str__(self):
        return f"Perfil (legado) de {self.usuario.username}"