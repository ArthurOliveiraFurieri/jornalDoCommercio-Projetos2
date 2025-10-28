from django.db import models


class Advertisement(models.Model):
    """Anúncios publicitários"""
    POSITION_CHOICES = [
        ('header', 'Header'),
        ('sidebar', 'Sidebar'),
        ('footer', 'Footer'),
        ('between_content', 'Entre Conteúdo'),
    ]

    title = models.CharField('Título', max_length=200)
    image = models.ImageField('Imagem', upload_to='advertising/')
    link = models.URLField('Link', blank=True)
    position = models.CharField('Posição', max_length=20, choices=POSITION_CHOICES)
    is_active = models.BooleanField('Ativo', default=True)
    start_date = models.DateField('Data de Início')
    end_date = models.DateField('Data de Término')
    clicks = models.IntegerField('Cliques', default=0)

    class Meta:
        verbose_name = 'Anúncio'
        verbose_name_plural = 'Anúncios'
        ordering = ['-start_date']

    def __str__(self):
        return self.title
