from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, DetailView, TemplateView
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Categoria, Noticia, Comentario
from .forms import CategoriaForm, ComentarioForm
from django.contrib.admin.views.decorators import staff_member_required
import requests
from django.conf import settings
import json
from datetime import datetime


class NoticiaDetailView(DetailView):
    """
    Exibe uma notícia completa.
    """
    model = Noticia
    template_name = 'jornal_app/artigo.html'
    context_object_name = 'noticia'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """
        Adiciona o formulário de comentários e a lista de comentários ao contexto.
        """
        context = super().get_context_data(**kwargs)
        noticia = self.get_object()
        
        # Comentários ativos desta notícia
        context['comentarios'] = noticia.comentarios.filter(ativo=True)
        
        # Formulário para novo comentário
        context['comentario_form'] = ComentarioForm()
        
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Processa o envio de novos comentários.
        """
        if not request.user.is_authenticated:
            messages.error(request, 'Você precisa estar logado para comentar.')
            return redirect('login')
            
        noticia = self.get_object()
        comentario_form = ComentarioForm(request.POST)
        
        if comentario_form.is_valid():
            novo_comentario = comentario_form.save(commit=False)
            novo_comentario.noticia = noticia
            novo_comentario.autor = request.user
            novo_comentario.save()
            messages.success(request, 'Comentário adicionado com sucesso!')
            return redirect('jornal_app:artigo', pk=noticia.pk)
        else:
            # Se o formulário for inválido, reexibe a página com os erros
            context = self.get_context_data()
            context['comentario_form'] = comentario_form
            return self.render_to_response(context)

class HomeView(TemplateView):
    """
    Página inicial do jornal 
    """
    template_name = 'jornal_app/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['destaques'] = Noticia.objects.filter(destaque=True).order_by('-data_publicacao')[:3]
        
        context['artigos_recentes'] = Noticia.objects.filter(destaque=False).order_by('-data_publicacao')[:3]
        
        # 4. Informações do Dia (Mantemos estático por enquanto)
        #    No futuro, isso pode vir de uma API de clima/finanças.
        context['informacoes_dia'] = {
            'temperatura_max': '30°C',
            'temperatura_min': '27°C',
            'dolar': 'R$ 5,351',
            'euro': 'R$ 7,431'
        }
        
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

# --- VIEWS PARA COMENTÁRIOS ---

@method_decorator(login_required, name='dispatch')
class ComentarioDeleteView(DeleteView):
    """
    Exclui um comentário.
    """
    model = Comentario
    template_name = 'jornal_app/comentario_confirm_delete.html'
    
    def get_success_url(self):
        """
        Redireciona para a notícia após excluir o comentário.
        """
        noticia_id = self.object.noticia.id
        return reverse_lazy('jornal_app:artigo', kwargs={'pk': noticia_id})
    
    def delete(self, request, *args, **kwargs):
        """
        Sobrescreve o método delete para verificar permissões e mostrar mensagens.
        """
        self.object = self.get_object()
        
        # Verifica se o usuário é o autor do comentário ou staff
        if request.user == self.object.autor or request.user.is_staff:
            noticia_id = self.object.noticia.id
            self.object.delete()
            messages.success(request, "Comentário excluído com sucesso!")
            return redirect(self.get_success_url())
        else:
            messages.error(request, "Você não tem permissão para excluir este comentário.")
            return redirect(self.get_success_url())

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

# === FUNÇÕES PARA IMPORTAR NOTÍCIAS DA NEWS DATA API ===

@staff_member_required
def importar_noticias(request):
    """
    View para importar notícias da NewsDataAPI - CORRIGIDA
    """
    # Verificar se a chave API está configurada
    api_key = getattr(settings, 'NEWSDATA_API_KEY', '')
    api_configurada = bool(api_key and api_key.strip() and api_key != 'sua_chave_api_aqui')
    
    if request.method == 'POST':
        if not api_configurada:
            messages.error(request, '❌ Chave API não configurada. Adicione NEWSDATA_API_KEY no settings.py')
            return redirect('jornal_app:importar_noticias')
            
        try:
            # Tenta usar requests primeiro, depois fallback para urllib
            try:
                quantidade_importada = importar_noticias_newsdata_requests()
            except ImportError:
                quantidade_importada = importar_noticias_newsdata_urllib()
                
            if quantidade_importada > 0:
                messages.success(request, f'✅ {quantidade_importada} notícias importadas com sucesso da NewsDataAPI!')
            else:
                messages.info(request, 'ℹ️ Nenhuma nova notícia foi importada. Todas as notícias já existem no banco de dados.')
                
        except Exception as e:
            messages.error(request, f'❌ Erro ao importar notícias: {str(e)}')
        
        return redirect('jornal_app:importar_noticias')
    
    context = {
        'api_configurada': api_configurada,
        'NEWSDATA_API_KEY': api_key
    }
    return render(request, 'admin/importar_noticias.html', context)

def importar_noticias_newsdata_requests():
    """
    Função para importar notícias usando requests - CORRIGIDA
    """
    # Configurações da API
    api_key = getattr(settings, 'NEWSDATA_API_KEY', '')
    
    if not api_key:
        raise Exception('Chave API não configurada. Adicione NEWSDATA_API_KEY no settings.py')
    
    base_url = "https://newsdata.io/api/1/news"
    
    # Parâmetros SIMPLIFICADOS - sem categoria múltipla
    params = {
        'apikey': api_key,
        'country': 'br',
        'language': 'pt',
        'size': 10  # Reduzindo para 10 para testar
    }
    
    print(f"🔍 Fazendo requisição para: {base_url}")
    print(f"🔍 Parâmetros: {params}")
    
    response = requests.get(base_url, params=params, timeout=30)
    
    print(f"🔍 Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"🔍 Erro detalhado: {response.text}")
        response.raise_for_status()
    
    data = response.json()
    print(f"🔍 Total de artigos recebidos: {len(data.get('results', []))}")
    
    articles = data.get('results', [])
    return processar_artigos(articles)

def importar_noticias_newsdata_urllib():
    """
    Função para importar notícias usando urllib (fallback) - CORRIGIDA
    """
    # Configurações da API
    api_key = getattr(settings, 'NEWSDATA_API_KEY', '')
    
    if not api_key:
        raise Exception('Chave API não configurada. Adicione NEWSDATA_API_KEY no settings.py')
    
    base_url = "https://newsdata.io/api/1/news"
    
    # Parâmetros SIMPLIFICADOS
    params = {
        'apikey': api_key,
        'country': 'br',
        'language': 'pt',
        'size': 10
    }
    
    # Construir URL com parâmetros
    from urllib.parse import urlencode
    query_string = urlencode(params)
    url = f"{base_url}?{query_string}"
    
    print(f"🔍 URL da requisição: {url}")
    
    # Criar request
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError
    import ssl
    import json
    
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    # Fazer a requisição
    context = ssl._create_unverified_context()
    
    try:
        with urlopen(req, timeout=30, context=context) as response:
            data = json.loads(response.read().decode())
            print(f"🔍 Status Code: {response.status}")
            articles = data.get('results', [])
            return processar_artigos(articles)
    except (URLError, HTTPError) as e:
        print(f"🔍 Erro detalhado: {e}")
        raise Exception(f"Erro na requisição para NewsDataAPI: {str(e)}")
def processar_artigos(articles):
    """
    Processa os artigos e salva no banco de dados
    """
    quantidade_importada = 0
    
    for article in articles:
        # Verificar se a notícia já existe pela URL
        url_fonte = article.get('link', '')
        if Noticia.objects.filter(url_fonte=url_fonte).exists():
            continue
        
        # Mapear categoria
        categoria_api = article.get('category', ['general'])[0] if isinstance(article.get('category'), list) else article.get('category', 'general')
        categoria_obj = mapear_categoria(categoria_api)
        
        # Converter data de publicação
        data_publicacao = parse_date(article.get('pubDate', ''))
        
        # Preparar conteúdo
        descricao = article.get('description', '') or ''
        conteudo = article.get('content', '') or descricao
        
        if not conteudo.strip():
            continue
            
        # Criar a notícia
        noticia = Noticia(
            titulo=article.get('title', '')[:200],
            conteudo=conteudo[:2000],
            categoria=categoria_obj,
            url_fonte=url_fonte[:500],
            imagem_url=article.get('image_url', '')[:500],
            autor_fonte=article.get('source_id', 'Fonte Externa')[:100],
            data_publicacao=data_publicacao,
            destaque=False
        )
        
        noticia.save()
        quantidade_importada += 1
    
    return quantidade_importada

def mapear_categoria(categoria_api):
    """
    Mapeia a categoria da API para uma categoria do sistema - CORRIGIDA
    """
    mapeamento = {
        'technology': 'Tecnologia',
        'politics': 'Política',
        'sports': 'Esportes',
        'health': 'Saúde',
        'entertainment': 'Entretenimento',
        'business': 'Negócios',
        'science': 'Ciência',
        'general': 'Geral'
    }
    
    nome_categoria = mapeamento.get(categoria_api, 'Geral')
    
    # Buscar ou criar a categoria SEM o campo descricao
    categoria, created = Categoria.objects.get_or_create(
        nome=nome_categoria
        # Remova a parte do 'defaults' se seu modelo não tem descricao
    )
    
    return categoria

def parse_date(date_string):
    """
    Converte a string de data da API para um objeto datetime
    """
    if not date_string:
        return datetime.now()
    
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        try:
            formats = [
                '%a, %d %b %Y %H:%M:%S %Z',
                '%a, %d %b %Y %H:%M:%S %z',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
        except:
            pass
        
        return datetime.now()