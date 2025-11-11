from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone

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
    
    # ⭐⭐ CAMPOS OBRIGATÓRIOS PARA A API ⭐⭐
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

class Comentario(models.Model):
    """
    Representa um comentário em uma notícia.
    """
    noticia = models.ForeignKey(
        Noticia, 
        on_delete=models.CASCADE, 
        related_name='comentarios',
        verbose_name="Notícia"
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Autor"
    )
    texto = models.TextField(verbose_name="Comentário")
    data_criacao = models.DateTimeField(default=timezone.now, verbose_name="Data de Criação")
    ativo = models.BooleanField(
        default=True, 
        verbose_name="Ativo",
        help_text="Desmarque para ocultar este comentário."
    )
    
    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ['data_criacao']
    
    def __str__(self):
        return f'Comentário de {self.autor} em {self.noticia}'

class Perfil(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='perfil'
    )