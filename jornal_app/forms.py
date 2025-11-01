from django import forms
from .models import Categoria, Comentario
# Imports novos
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

# --- Seu CategoriaForm (sem modificações) ---
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

# --- Seu ComentarioForm (sem modificações) ---
class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Digite seu comentário...'
            }),
        }
        labels = {
            'texto': 'Seu comentário'
        }

# --- CustomUserCreationForm (Corrigido) ---
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
        
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Nome de usuário'
        self.fields['email'].widget.attrs['placeholder'] = 'Seu e-mail'
        self.fields['password1'].widget.attrs['placeholder'] = 'Digite sua senha'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirme sua senha'
        self.fields['username'].label = ''
        self.fields['email'].label = ''
        self.fields['password1'].label = ''
        self.fields['password2'].label = ''

# --- FORMULÁRIO DE LOGIN (NOVO) ---
class CustomAuthenticationForm(AuthenticationForm):
    """
    Adiciona placeholders ao formulário de login padrão.
    """
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Nome de usuário'
        self.fields['password'].widget.attrs['placeholder'] = 'Senha'
        self.fields['username'].label = ''
        self.fields['password'].label = ''