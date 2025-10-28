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

        #Recomendação de notícias similares
        context['noticias_similares'] = noticia.noticias_similares()
        
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
@staff_member_required
def importar_noticias(request):
    if request.method == 'POST':
        try:
            from .news_simple import importar_noticias_simples
            quantidade = importar_noticias_simples()
            if quantidade > 0:
                messages.success(request, f'{quantidade} notícias importadas com sucesso!')
            else:
                messages.info(request, 'Nenhuma nova notícia foi importada.')
        except Exception as e:
            messages.error(request, f'Erro ao importar notícias: {str(e)}')
        
        return redirect('admin:index')
    
    return render(request, 'admin/importar_noticias.html')
