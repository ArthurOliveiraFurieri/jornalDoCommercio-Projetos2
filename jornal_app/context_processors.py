from .models import Categoria

def menu_categorias(request):
    """
    Disponibiliza a lista de categorias para todos os templates.
    """
    categorias = Categoria.objects.all().order_by('nome')
    return {
        'categorias': categorias
    }