from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, DetailView, TemplateView
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.db.models import Q

from .models import Categoria, Noticia
from .forms import CategoriaForm

# --- VIEWS PARA O LEITOR ---

class HomeView(TemplateView):
    """
    Página inicial do jornal - para leitores
    """
    template_name = 'jornal_app/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dados para a página inicial
        context['destaques'] = [
            {
                'titulo': 'Brasileiros que ficaram presos em Israel são recebidos por apoiadores em SP',
                'resumo': 'Traca brasileiras, onde eles a circulação federal, utilizando fim (PT-CE), chegariam hoje ao Brasil...',
                'categoria': 'INTERNACIONAL'
            },
            {
                'titulo': 'Governo sofre derrota e vê caducar MP que traria R$ 17 bilhões aos cofres',
                'resumo': 'Foram 325 a 195 votos pelo Submetido. O governo não teve votos suficientes...',
                'categoria': 'POLÍTICA'
            },
            {
                'titulo': 'Maior desafio na transição energética no Brasil é substituir diesel, diz diretor da AMP',
                'resumo': 'O diretor da Agência Nacional do Perdoso, Olá-Natural e Biocombustíveis...',
                'categoria': 'ECONOMIA'
            }
        ]
        
        context['artigos_recentes'] = [
            {
                'titulo': 'Justiça Federal autoriza edital de Medicina da UFFE para assentados da reforma agrária',
                'categoria': 'POLÍTICA'
            },
            {
                'titulo': 'Lucro Real x Lucro Presumidor migrar de regime pode gerar economia milionária',
                'categoria': 'ECONOMIA'
            },
            {
                'titulo': 'Governo cria comitê de enfrentamento da crise do metanol',
                'categoria': 'BRASIL'
            }
        ]
        
        # Categorias para o menu de navegação
        context['categorias'] = Categoria.objects.all()
        
        # Dados mockados (substitua por dados reais quando tiver)
        context['informacoes_dia'] = {
            'temperatura_max': '30°C',
            'temperatura_min': '27°C',
            'dolar': 'R$ 5,351',
            'euro': 'R$ 7,431'
        }
        
        return context

class NoticiaDetailView(DetailView):
    """
    Detalhes de uma notícia específica
    """
    model = Noticia
    template_name = 'jornal_app/noticia_detail.html'
    context_object_name = 'noticia'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Notícias relacionadas (da mesma categoria)
        context['noticias_relacionadas'] = Noticia.objects.filter(
            categoria=self.object.categoria
        ).exclude(pk=self.object.pk).order_by('-data_publicacao')[:4]
        return context

class NoticiasPorCategoriaView(ListView):
    """
    Lista as notícias filtradas por uma categoria específica.
    """
    model = Noticia
    template_name = 'jornal_app/noticias_por_categoria.html'
    context_object_name = 'noticias'
    paginate_by = 10 

    def get_queryset(self):
        """
        Filtra as notícias pela categoria passada na URL.
        """
        self.categoria = get_object_or_404(Categoria, pk=self.kwargs['pk'])
        return Noticia.objects.filter(categoria=self.categoria).order_by('-data_publicacao')

    def get_context_data(self, **kwargs):
        """
        Adiciona o objeto 'categoria' ao contexto para ser usado no template.
        """
        context = super().get_context_data(**kwargs)
        context['categoria'] = self.categoria
        return context

# --- VIEWS PARA O EDITOR ---

class CategoriaListView(ListView):
    """
    Lista todas as categorias para o editor.
    """
    model = Categoria
    template_name = 'jornal_app/categoria_list.html'
    context_object_name = 'categorias'

class CategoriaCreateView(CreateView):
    """
    Cria uma nova categoria.
    """
    model = Categoria
    form_class = CategoriaForm
    template_name = 'jornal_app/categoria_form.html'
    success_url = reverse_lazy('jornal_app:categoria_list')

    def form_valid(self, form):
        messages.success(self.request, "Categoria criada com sucesso!")
        return super().form_valid(form)

class CategoriaDeleteView(DeleteView):
    """
    Exclui uma categoria.
    """
    model = Categoria
    template_name = 'jornal_app/categoria_confirm_delete.html'
    success_url = reverse_lazy('jornal_app:categoria_list')
    
    def post(self, request, *args, **kwargs):
        """
        Sobrescreve o método post para tratar o ProtectedError.
        """
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, f"Categoria '{self.object.nome}' excluída com sucesso.")
            return redirect(self.success_url)
        except ProtectedError:
            messages.error(
                request, 
                f"Não é possível excluir a categoria '{self.object.nome}' pois ela está vinculada a uma ou mais notícias."
            )
            return redirect(self.success_url)

# --- VIEWS EXTRAS (OPCIONAIS) ---

def noticia_search(request):
    """
    View function para busca de notícias
    """
    query = request.GET.get('q', '')
    noticias = Noticia.objects.all()
    
    if query:
        noticias = noticias.filter(
            Q(titulo__icontains=query) | 
            Q(conteudo__icontains=query)
        ).order_by('-data_publicacao')
    
    context = {
        'noticias': noticias,
        'query': query
    }
    return render(request, 'jornal_app/noticia_search.html', context)