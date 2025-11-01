from django.db import models
from django.contrib.auth.models import User

# --- Imports novos para o Profile ---
from django.db.models.signals import post_save
from django.dispatch import receiver


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class Noticia(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='noticias')
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)
    destaque = models.BooleanField(default=False)
    
    # --- CAMPO NOVO ADICIONADO ---
    exclusivo = models.BooleanField(default=False, help_text="Marque se esta notícia é apenas para assinantes")
    # --- FIM DA MODIFICAÇÃO ---

    class Meta:
        ordering = ['-data_publicacao']

    def __str__(self):
        return self.titulo

class Comentario(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=False)

    class Meta:
        ordering = ['data_criacao']

    def __str__(self):
        return f'Comentário de {self.autor} em {self.noticia.titulo}'


# --- NOVO MODELO DE PROFILE ---
class Profile(models.Model):
    """
    Modelo que extende o User, guardando se ele é assinante ou não.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_assinante = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Perfil de {self.user.username}"

# --- "SINAIS" PARA CRIAR O PROFILE AUTOMATICAMENTE ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ Cria um Profile automaticamente quando um User é criado """
    if created:
        Profile.objects.create(user=instance)

