from django.db import models
from django.contrib.auth.models import User


class LiveEvent(models.Model):
    """Eventos de transmissão ao vivo"""
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descrição')
    stream_url = models.URLField('URL da Transmissão', blank=True)
    is_active = models.BooleanField('Ao Vivo', default=False)
    scheduled_at = models.DateTimeField('Agendado para')
    ended_at = models.DateTimeField('Finalizado em', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Criado por')

    class Meta:
        verbose_name = 'Evento ao Vivo'
        verbose_name_plural = 'Eventos ao Vivo'
        ordering = ['-scheduled_at']

    def __str__(self):
        return self.title
