from django import forms
from .models import Categoria, Comentario

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']

        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Economia'}),
        }

        error_messages = {
            'nome': {
                'unique': "Nome já utilizado. Categorias devem ter nomes únicos.",
            },
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['texto'].widget = forms.Textarea(
            attrs={
                'placeholder': 'Escreva seu comentário aqui...',
                'rows': 4,
                'class': 'form-control-comentario' 
            }
        )