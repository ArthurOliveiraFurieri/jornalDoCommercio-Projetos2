from django.db import models
from django.utils.text import slugify


class SiteConfiguration(models.Model):
    """Configurações gerais do site"""
    site_name = models.CharField('Nome do Site', max_length=200, default='Jornal do Commercio')
    site_description = models.TextField('Descrição', blank=True)
    logo = models.ImageField('Logo', upload_to='site/', blank=True, null=True)
    favicon = models.ImageField('Favicon', upload_to='site/', blank=True, null=True)
    contact_email = models.EmailField('Email de Contato', blank=True)
    contact_phone = models.CharField('Telefone', max_length=20, blank=True)
    facebook_url = models.URLField('Facebook', blank=True)
    twitter_url = models.URLField('Twitter', blank=True)
    instagram_url = models.URLField('Instagram', blank=True)

    class Meta:
        verbose_name = 'Configuração do Site'
        verbose_name_plural = 'Configurações do Site'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Garantir que só exista uma instância
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Menu(models.Model):
    """Itens do menu principal"""
    title = models.CharField('Título', max_length=100)
    url = models.CharField('URL', max_length=200, help_text='Pode ser um caminho relativo ou URL completa')
    order = models.IntegerField('Ordem', default=0)
    is_active = models.BooleanField('Ativo', default=True)
    open_in_new_tab = models.BooleanField('Abrir em nova aba', default=False)

    class Meta:
        verbose_name = 'Item do Menu'
        verbose_name_plural = 'Itens do Menu'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title
