from django import forms
from .models import Categoria

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