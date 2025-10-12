from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView
from django.contrib import messages
from django.db.models.deletion import ProtectedError

from .models import Categoria, Noticia
from .forms import CategoriaForm

# --- Views para o Editor ---

class CategoriaListView(ListView):
    """
    Lista todas as categorias para o editor.
    """
    model = Categoria
    template_name = 'seu_app/categoria_list.html'
    context_object_name = 'categorias'
    # Futuramente, você pode adicionar um mixin de permissão aqui 
    # para garantir que só editores acessem:
    # permission_required = 'seu_app.view_categoria'

class CategoriaCreateView(CreateView):
    """
    Cria uma nova categoria.
    """
    model = Categoria
    form_class = CategoriaForm
    template_name = 'seu_app/categoria_form.html'
    success_url = reverse_lazy('categoria_list') # Redireciona para a lista após sucesso

    def form_valid(self, form):
        messages.success(self.request, "Categoria criada com sucesso!")
        return super().form_valid(form)
        
    # O form_invalid é tratado automaticamente pelo CreateView,
    # que irá renderizar o formulário novamente com a mensagem de erro
    # definida no nosso CategoriaForm.

class CategoriaDeleteView(DeleteView):
    """
    Exclui uma categoria.
    """
    model = Categoria
    template_name = 'seu_app/categoria_confirm_delete.html'
    success_url = reverse_lazy('categoria_list')
    
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

# --- View para o Leitor ---

class NoticiasPorCategoriaView(ListView):
    """
    Lista as notícias filtradas por uma categoria específica.
    """
    model = Noticia
    template_name = 'seu_app/noticias_por_categoria.html'
    context_object_name = 'noticias'
    paginate_by = 10 

    def get_queryset(self):
        """
        Filtra as notícias pela categoria passada na URL.
        """
        self.categoria = Categoria.objects.get(pk=self.kwargs['pk'])
        return Noticia.objects.filter(categoria=self.categoria).order_by('-data_publicacao')

    def get_context_data(self, **kwargs):
        """
        Adiciona o objeto 'categoria' ao contexto para ser usado no template.
        """
        context = super().get_context_data(**kwargs)
        context['categoria'] = self.categoria
        return context