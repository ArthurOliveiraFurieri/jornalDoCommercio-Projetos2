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

class MaisNoticiasView(ListView):
    """
    Serve os artigos para o scroll infinito, de forma paginada.
    """
    model = Noticia
    template_name = 'jornal_app/partials/noticia_feed.html'
    context_object_name = 'noticias'
    paginate_by = 4

    def get_queryset(self):
        return Noticia.objects.all().order_by('-data_publicacao')[4:]


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
def criar_categorias_api(request):
    """
    Cria as categorias que a API realmente suporta
    """
    categorias_api = [
        'Política', 'Esportes', 'Economia', 'Tecnologia', 
        'Entretenimento', 'Saúde', 'Ciência', 'Geral'
    ]
    
    resultados = []
    for nome in categorias_api:
        cat, created = Categoria.objects.get_or_create(nome=nome)
        if created:
            resultados.append(f"✅ {nome} criada (ID: {cat.id})")
        else:
            resultados.append(f"⚠️ {nome} já existe (ID: {cat.id})")
    
    messages.success(request, "Categorias da API criadas/verificadas!")
    for resultado in resultados:
        messages.info(request, resultado)
    
    return redirect('jornal_app:importar_noticias')

@staff_member_required
def importar_noticias(request):
    """
    View para importar notícias da NewsDataAPI - COM FILTRO POR CATEGORIA
    """
    api_key = getattr(settings, 'NEWSDATA_API_KEY', '')
    api_configurada = bool(api_key and api_key.strip() and api_key != 'sua_chave_api_aqui')
    
    # Obter categorias disponíveis
    categorias = Categoria.objects.all()
    
    if request.method == 'POST':
        if not api_configurada:
            messages.error(request, '❌ Chave API não configurada. Adicione NEWSDATA_API_KEY no settings.py')
            return redirect('jornal_app:importar_noticias')
            
        try:
            # Obter categoria selecionada (ou importar para todas)
            categoria_id = request.POST.get('categoria')
            
            if categoria_id:
                # Importar para uma categoria específica
                categoria_filtro = get_object_or_404(Categoria, pk=categoria_id)
                quantidade_importada = importar_noticias_por_categoria(categoria_filtro)
                messages.success(request, f'✅ {quantidade_importada} notícias de {categoria_filtro.nome} importadas!')
            else:
                # Importar para TODAS as categorias
                total_importadas = 0
                for categoria in categorias:
                    quantidade = importar_noticias_por_categoria(categoria)
                    total_importadas += quantidade
                    print(f"📰 {quantidade} notícias importadas para {categoria.nome}")
                
                messages.success(request, f'✅ {total_importadas} notícias importadas para TODAS as categorias!')
                
        except Exception as e:
            messages.error(request, f'❌ Erro ao importar notícias: {str(e)}')
        
        return redirect('jornal_app:importar_noticias')
    
    context = {
        'api_configurada': api_configurada,
        'NEWSDATA_API_KEY': api_key,
        'categorias': categorias
    }
    return render(request, 'admin/importar_noticias.html', context)

def importar_noticias_por_categoria(categoria):
    """
    Importa notícias específicas para uma categoria
    """
    api_key = getattr(settings, 'NEWSDATA_API_KEY', '')
    
    if not api_key:
        raise Exception('Chave API não configurada')
    
    base_url = "https://newsdata.io/api/1/news"
    
    # Mapear categoria do sistema para categoria da API
    mapeamento_para_api = {
        'Política': 'politics',
        'Esportes': 'sports', 
        'Economia': 'business',
        'Tecnologia': 'technology',
        'Entretenimento': 'entertainment',
        'Saúde': 'health',
        'Ciência': 'science',
        'Geral': 'general'
    }
    
    categoria_api = mapeamento_para_api.get(categoria.nome, 'general')
    print(f"🎯 Buscando notícias: {categoria.nome} → {categoria_api}")
    
    params = {
        'apikey': api_key,
        'country': 'br', 
        'language': 'pt',
        'category': categoria_api,
        'size': 5
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Erro na API para {categoria.nome}: {response.status_code}")
            return 0
        
        data = response.json()
        articles = data.get('results', [])
        
        print(f"📰 {len(articles)} notícias recebidas para {categoria.nome}")
        return processar_artigos_para_categoria(articles, categoria)
        
    except Exception as e:
        print(f"❌ Erro ao buscar notícias para {categoria.nome}: {str(e)}")
        return 0

def processar_artigos_para_categoria(articles, categoria):
    """
    Processa artigos para uma categoria específica
    """
    quantidade_importada = 0
    
    for article in articles:
        # Verificar se a notícia já existe pela URL
        url_fonte = article.get('link', '')
        if Noticia.objects.filter(url_fonte=url_fonte).exists():
            continue
        
        # Converter data de publicação
        data_publicacao = parse_date(article.get('pubDate', ''))
        
        # Preparar conteúdo
        descricao = article.get('description', '') or ''
        conteudo_final = article.get('description', '')

        # 2. Se a 'description' estiver vazIA, tente pegar o 'content'
        if not conteudo_final:
            conteudo_final = article.get('content', '')

        # 3. Se ambos falharem, use o título como último recurso
        if not conteudo_final:
            conteudo_final = article.get('title', 'Artigo sem conteúdo')
        
        if not conteudo_final.strip():
            continue
            
        # Criar a notícia
        noticia = Noticia(
            titulo=article.get('title', '')[:200],
            conteudo=conteudo_final[:2000],
            categoria=categoria,  # Usa a categoria específica
            url_fonte=url_fonte[:500],
            imagem_url=article.get('image_url', '')[:500],
            autor_fonte=article.get('source_id', 'Fonte Externa')[:100],
            data_publicacao=data_publicacao,
            destaque=(categoria.nome == 'Política')  # Destaque só para Política
        )
        
        noticia.save()
        quantidade_importada += 1
        print(f"✅ Notícia salva: {noticia.titulo[:50]}...")
    
    return quantidade_importada

def mapear_categoria(categoria_api):
    """
    Mapeia a categoria da API para uma categoria do sistema
    """
    mapeamento = {
        'politics': 'Política',
        'sports': 'Esportes',
        'business': 'Economia', 
        'technology': 'Tecnologia',
        'entertainment': 'Entretenimento',
        'health': 'Saúde',
        'science': 'Ciência',
        'general': 'Geral'
    }
    
    nome_categoria = mapeamento.get(categoria_api, 'Geral')
    
    # Buscar ou criar a categoria
    categoria, created = Categoria.objects.get_or_create(nome=nome_categoria)
    print(f"🔧 Categoria mapeada: {categoria_api} → {nome_categoria} (ID: {categoria.id})")
    
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
    
# === FUNÇÕES PARA RESET E CONFIGURAÇÃO ===

@staff_member_required
def reset_total(request):
    """
    LIMPA TUDO e começa do zero
    """
    # Deletar tudo
    Noticia.objects.all().delete()
    Categoria.objects.all().delete()
    
    messages.success(request, "🗑️ Banco limpo! Pronto para começar do zero.")
    return redirect('jornal_app:criar_categorias_definitivas')

@staff_member_required
def criar_categorias_definitivas(request):
    """
    Cria as 7 categorias DEFINITIVAS na ordem correta
    """
    categorias_definitivas = [
        'Política',      # ID 1
        'Esportes',      # ID 2  
        'Economia',      # ID 3
        'Tecnologia',    # ID 4
        'Saúde',         # ID 5
        'Ciência',       # ID 6
        'Geral'          # ID 7
    ]
    
    for nome in categorias_definitivas:
        cat, created = Categoria.objects.get_or_create(nome=nome)
        print(f"🎯 {nome} → ID: {cat.id}")
    
    messages.success(request, "✅ 7 categorias criadas na ordem DEFINITIVA!")
    
    # Mostrar os IDs criados
    categorias = Categoria.objects.all().order_by('id')
    for cat in categorias:
        messages.info(request, f"ID {cat.id}: {cat.nome}")
    
    return redirect('jornal_app:importar_noticias')

