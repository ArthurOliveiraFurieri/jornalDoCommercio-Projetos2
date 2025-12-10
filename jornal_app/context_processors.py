from .models import Categoria

def menu_categorias(request):
    categorias = Categoria.objects.all().order_by('nome')
    return {
        'categorias': categorias
    }