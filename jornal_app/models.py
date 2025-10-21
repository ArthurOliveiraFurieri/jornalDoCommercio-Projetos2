from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone

class Categoria(models.Model):
    """
    Representa uma categoria de notícia, como 'Economia', 'Tecnologia', etc.
    """
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
    """
    Representa uma notícia publicada no site.
    """
    titulo = models.CharField(max_length=200, verbose_name="Título")
    conteudo = models.TextField(verbose_name="Conteúdo")
    data_publicacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Publicação")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='noticias',
        verbose_name="Categoria"
    )

    exclusiva = models.BooleanField(
        default=False, 
        verbose_name="Conteúdo Exclusivo",
        help_text="Marque se esta notícia é apenas para assinantes."
    )

    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"
        ordering = ['-data_publicacao']

    def __str__(self):
        return self.titulo
    
class Perfil(models.Model):
    """
    Estende o modelo de usuário padrão do Django para armazenar 
    informações adicionais, incluindo o status da assinatura.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='perfil'
    )


