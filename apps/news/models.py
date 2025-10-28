from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    """Categorias de notícias"""
    name = models.CharField('Nome', max_length=100, unique=True)
    slug = models.SlugField('Slug', max_length=100, unique=True, blank=True)
    description = models.TextField('Descrição', blank=True)
    order = models.IntegerField('Ordem', default=0, help_text='Ordem de exibição no menu')
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:category', kwargs={'slug': self.slug})


class Tag(models.Model):
    """Tags para classificação de notícias"""
    name = models.CharField('Nome', max_length=50, unique=True)
    slug = models.SlugField('Slug', max_length=50, unique=True, blank=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:tag', kwargs={'slug': self.slug})


class News(models.Model):
    """Modelo principal de notícias"""
    title = models.CharField('Título', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True, blank=True)
    excerpt = models.TextField('Resumo', max_length=300, help_text='Breve descrição da notícia')
    content = models.TextField('Conteúdo')
    featured_image = models.ImageField('Imagem Destaque', upload_to='news/%Y/%m/', blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='news',
        verbose_name='Categoria'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Tags', blank=True, related_name='news')
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Autor',
        related_name='news'
    )
    is_published = models.BooleanField('Publicado', default=False)
    is_featured = models.BooleanField('Destaque', default=False, help_text='Aparecer na página inicial')
    views_count = models.IntegerField('Visualizações', default=0)
    published_at = models.DateTimeField('Publicado em', blank=True, null=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Notícia'
        verbose_name_plural = 'Notícias'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Se está sendo publicado agora, define a data de publicação
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:detail', kwargs={'slug': self.slug})

    def increment_views(self):
        """Incrementa o contador de visualizações"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class Comment(models.Model):
    """Comentários nas notícias"""
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Notícia'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Autor'
    )
    author_name = models.CharField('Nome', max_length=100, blank=True)
    author_email = models.EmailField('Email', blank=True)
    content = models.TextField('Comentário')
    is_approved = models.BooleanField('Aprovado', default=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering = ['created_at']

    def __str__(self):
        return f'Comentário de {self.author_name or self.author.username} em {self.news.title}'

    def save(self, *args, **kwargs):
        # Se não tiver nome, usa o username do autor
        if not self.author_name and self.author:
            self.author_name = self.author.get_full_name() or self.author.username
        # Se não tiver email, usa o email do autor
        if not self.author_email and self.author:
            self.author_email = self.author.email
        super().save(*args, **kwargs)
