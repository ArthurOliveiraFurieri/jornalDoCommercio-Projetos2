from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, DetailView, TemplateView
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Categoria, Noticia, Comentario, UserProfile
from .forms import CategoriaForm, ComentarioForm, RegistroForm
from django.contrib.admin.views.decorators import staff_member_required
import requests
from django.conf import settings
import json
from datetime import datetime
from django.contrib.auth import login, authenticate

class MaisNoticiasView(ListView):
    model = Noticia
    template_name = 'jornal_app/partials/noticia_feed.html'
    context_object_name = 'noticias'
    paginate_by = 4

    def get_queryset(self):
        return Noticia.objects.all().order_by('-data_publicacao')[4:]

class NoticiaDetailView(DetailView):
    model = Noticia
    template_name = 'jornal_app/artigo.html'
    context_object_name = 'noticia'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        noticia = self.get_object()
        
        # Gamificação - marcar notícia lida e categoria visitada
        if self.request.user.is_authenticated:
            user_profile = self.request.user.userprofile
            level_up = user_profile.marcar_noticia_lida(noticia.pk)
            user_profile.marcar_categoria_visitada(noticia.categoria.pk)
            
            if level_up:
                messages.success(self.request, f'🎉 Parabéns! Você subiu para o nível {user_profile.nivel}!')
        
        context['comentarios'] = noticia.comentarios.filter(ativo=True)
        context['comentario_form'] = ComentarioForm()
        context['noticias_similares'] = Noticia.objects.filter(
            categoria=noticia.categoria  
        ).exclude(pk=noticia.pk).order_by('?')[:2]
        
        return context
    
    def post(self, request, *args, **kwargs):
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
            
            # Gamificação - marcar comentário feito
            user_profile = request.user.userprofile
            level_up = user_profile.marcar_comentario_feito()
            
            messages.success(request, 'Comentário adicionado com sucesso! +10 pontos!')
            
            if level_up:
                messages.success(request, f'🎉 Parabéns! Você subiu para o nível {user_profile.nivel}!')
                
            return redirect('jornal_app:artigo', pk=noticia.pk)
        else:
            context = self.get_context_data()
            context['comentario_form'] = comentario_form
            return self.render_to_response(context)

class HomeView(TemplateView):
    template_name = 'jornal_app/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['destaques'] = Noticia.objects.filter(destaque=True).order_by('-data_publicacao')[:3]
        context['artigos_recentes'] = Noticia.objects.filter(destaque=False).order_by('-data_publicacao')[:3]
        return context

class NoticiasPorCategoriaView(ListView):
    model = Noticia
    template_name = 'jornal_app/noticias_por_categoria.html'
    context_object_name = 'noticias'
    paginate_by = 10 

    def get_queryset(self):
        self.categoria = get_object_or_404(Categoria, pk=self.kwargs['pk'])
        return Noticia.objects.filter(categoria=self.categoria).order_by('-data_publicacao')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = self.categoria
        
        # Gamificação - marcar categoria visitada
        if self.request.user.is_authenticated:
            user_profile = self.request.user.userprofile
            user_profile.marcar_categoria_visitada(self.categoria.pk)
        
        return context

@method_decorator(login_required, name='dispatch')
class comentario_delete(DeleteView):
    model = Comentario
    template_name = 'jornal_app/comentario_confirm_delete.html'
    
    def get_success_url(self):
        noticia_id = self.object.noticia.id
        return reverse_lazy('jornal_app:artigo', kwargs={'pk': noticia_id})
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if request.user == self.object.autor or request.user.is_staff:
            noticia_id = self.object.noticia.id
            self.object.delete()
            messages.success(request, "Comentário excluído com sucesso!")
            return redirect(self.get_success_url())
        else:
            messages.error(request, "Você não tem permissão para excluir este comentário.")
            return redirect(self.get_success_url())

class CategoriaListView(ListView):
    model = Categoria
    template_name = 'jornal_app/categoria_list.html'
    context_object_name = 'categorias'

class CategoriaCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'jornal_app/categoria_form.html'
    success_url = reverse_lazy('jornal_app:categoria_list')

    def form_valid(self, form):
        messages.success(self.request, "Categoria criada com sucesso!")
        return super().form_valid(form)

class CategoriaDeleteView(DeleteView):
    model = Categoria
    template_name = 'jornal_app/categoria_confirm_delete.html'
    success_url = reverse_lazy('jornal_app:categoria_list')
    
    def post(self, request, *args, **kwargs):
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

@staff_member_required
def criar_categorias_api(request):
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
    api_key = getattr(settings, 'NEWSDATA_API_KEY', '')
    api_configurada = bool(api_key and api_key.strip() and api_key != 'sua_chave_api_aqui')
    
    categorias = Categoria.objects.all()
    
    if request.method == 'POST':
        if not api_configurada:
            messages.error(request, '❌ Chave API não configurada. Adicione NEWSDATA_API_KEY no settings.py')
            return redirect('jornal_app:importar_noticias')
            
        try:
            categoria_id = request.POST.get('categoria')
            
            if categoria_id:
                categoria_filtro = get_object_or_404(Categoria, pk=categoria_id)
                quantidade_importada = importar_noticias_por_categoria(categoria_filtro)
                messages.success(request, f'✅ {quantidade_importada} notícias de {categoria_filtro.nome} importadas!')
            else:
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
    api_key = getattr(settings, 'NEWSDATA_API_KEY', '')
    
    if not api_key:
        raise Exception('Chave API não configurada')
    
    base_url = "https://newsdata.io/api/1/news"
    
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
    quantidade_importada = 0
    
    for article in articles:
        url_fonte = article.get('link', '')
        if Noticia.objects.filter(url_fonte=url_fonte).exists():
            continue
        
        data_publicacao = parse_date(article.get('pubDate', ''))
        
        conteudo_final = article.get('description', '')
        if not conteudo_final:
            conteudo_final = article.get('content', '')
        if not conteudo_final:
            conteudo_final = article.get('title', 'Artigo sem conteúdo')
        
        if not conteudo_final.strip():
            continue
            
        noticia = Noticia(
            titulo=article.get('title', '')[:200],
            conteudo=conteudo_final[:2000],
            categoria=categoria,
            url_fonte=url_fonte[:500],
            imagem_url=article.get('image_url', '')[:500],
            autor_fonte=article.get('source_id', 'Fonte Externa')[:100],
            data_publicacao=data_publicacao,
            destaque=(categoria.nome == 'Política')
        )
        
        noticia.save()
        quantidade_importada += 1
        print(f"✅ Notícia salva: {noticia.titulo[:50]}...")
    
    return quantidade_importada

def parse_date(date_string):
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

@staff_member_required
def reset_total(request):
    Noticia.objects.all().delete()
    Categoria.objects.all().delete()
    
    messages.success(request, "🗑️ Banco limpo! Pronto para começar do zero.")
    return redirect('jornal_app:criar_categorias_definitivas')

@staff_member_required
def criar_categorias_definitivas(request):
    categorias_definitivas = [
        'Política', 'Esportes', 'Economia', 'Tecnologia', 
        'Saúde', 'Ciência', 'Geral'
    ]
    
    for nome in categorias_definitivas:
        cat, created = Categoria.objects.get_or_create(nome=nome)
        print(f"🎯 {nome} → ID: {cat.id}")
    
    messages.success(request, "✅ 7 categorias criadas na ordem DEFINITIVA!")
    
    categorias = Categoria.objects.all().order_by('id')
    for cat in categorias:
        messages.info(request, f"ID {cat.id}: {cat.nome}")
    
    return redirect('jornal_app:importar_noticias')

def register(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                
                # Garante que o UserProfile existe
                UserProfile.objects.get_or_create(usuario=user)
                
                messages.success(request, f'Conta criada com sucesso para {username}!')
                
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('jornal_app:home')
            except Exception as e:
                messages.error(request, f'Erro ao criar conta: {str(e)}')
        else:
            # Mostra os erros do formulário
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = RegistroForm()
    
    return render(request, 'jornal_app/register.html', {'form': form})

@login_required
def profile(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Se não existir, cria um
        user_profile = UserProfile.objects.create(usuario=request.user)
        messages.info(request, "Perfil de gamificação criado! 🎮")
    
    context = {
        'user_profile': user_profile,
        'stats': user_profile.get_estatisticas(),
    }
    
    return render(request, 'jornal_app/profile.html', context)

class MaisNoticiasCategoriaView(ListView):
    """
    Serve os artigos para o scroll infinito NAS CATEGORIAS - 3 em 3
    """
    model = Noticia
    template_name = 'jornal_app/partials/categoria_feed.html'
    context_object_name = 'noticias'
    paginate_by = 3

    def get_queryset(self):
        categoria_id = self.kwargs['pk']
        categoria = get_object_or_404(Categoria, pk=categoria_id)
        return Noticia.objects.filter(categoria=categoria).order_by('-data_publicacao')