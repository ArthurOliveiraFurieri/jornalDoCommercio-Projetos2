from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from jornal_app.models import Noticia, Categoria, Comentario
from datetime import datetime


class JornalAppViewsTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nome="Política")
        self.usuario = User.objects.create_user(username="joao", password="123456")
        self.noticia = Noticia.objects.create(
    titulo="Nova medida econômica é anunciada",
    conteudo="O governo anunciou uma nova política econômica...",
    categoria=self.categoria,
    data_publicacao=datetime.now()
)

        self.url_artigo = reverse("jornal_app:artigo", args=[self.noticia.pk])
        self.url_home = reverse("jornal_app:home")

    # Teste página artigo

    def test_exibe_artigo_com_titulo_e_conteudo(self):
        response = self.client.get(self.url_artigo)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.noticia.titulo)
        self.assertContains(response, self.noticia.conteudo)
        self.assertContains(response, self.categoria.nome)

    def test_mensagem_login_para_comentar(self):
        response = self.client.get(self.url_artigo)
        self.assertContains(response, "Faça login")
        self.assertContains(response, "para comentar")

    def test_usuario_autenticado_pode_comentar(self):
        self.client.login(username="joao", password="123456")
        response = self.client.post(self.url_artigo, {"texto": "Boa matéria"})
        self.assertEqual(response.status_code, 302)
        comentario = Comentario.objects.first()
        self.assertIsNotNone(comentario)
        self.assertEqual(comentario.texto, "Boa matéria")
        self.assertEqual(comentario.autor, self.usuario)

    def test_comentario_aparece_no_artigo(self):
        Comentario.objects.create(noticia=self.noticia, autor=self.usuario, texto="Teste")
        response = self.client.get(self.url_artigo)
        self.assertContains(response, "Teste")
        self.assertContains(response, self.usuario.username)

    # Teste página exclusão comentário

    def test_pagina_excluir_comentario_exibe_detalhes(self):
        comentario = Comentario.objects.create(
            noticia=self.noticia,
            autor=self.usuario,
            texto="Comentário para excluir"
        )
        self.client.login(username="joao", password="123456")
        url_delete = reverse("jornal_app:comentario_delete", args=[comentario.pk])
        response = self.client.get(url_delete)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Excluir Comentário")
        self.assertContains(response, comentario.texto)
        self.assertContains(response, comentario.autor.username)

    def test_autor_pode_excluir_comentario(self):
        comentario = Comentario.objects.create(
            noticia=self.noticia,
            autor=self.usuario,
            texto="Comentário a ser removido"
        )
        self.client.login(username="joao", password="123456")
        url_delete = reverse("jornal_app:comentario_delete", args=[comentario.pk])
        response = self.client.post(url_delete)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comentario.objects.filter(pk=comentario.pk).exists())

    # Teste página inicial

    def test_home_exibe_destaques(self):
        Noticia.objects.create(
        titulo="Segunda notícia",
        conteudo="Resumo da segunda notícia",
        categoria=self.categoria,
        data_publicacao=datetime.now()
    )
        Noticia.objects.create(
        titulo="Terceira notícia",
        conteudo="Resumo da terceira notícia",
        categoria=self.categoria,
        data_publicacao=datetime.now()
    )
    
        response = self.client.get(self.url_home)
        self.assertEqual(response.status_code, 200)
        self.assertIn("notícia", response.content.decode().lower())

    def test_home_sem_noticias_exibe_mensagem(self):
        Noticia.objects.all().delete()
        response = self.client.get(self.url_home)
        self.assertContains(response, "Bem-vindo ao Jornal do Commercio")
        self.assertContains(response, "Volte em breve")

    # Teste página procura

    def test_busca_retorna_resultados_corretos(self):
        url_search = reverse("jornal_app:noticia_search") + "?q=medida"
        response = self.client.get(url_search)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resultados da busca por")
        self.assertContains(response, self.noticia.titulo)
        self.assertContains(response, self.noticia.titulo)

    def test_busca_sem_resultados_exibe_mensagem(self):
        url_search = reverse("jornal_app:noticia_search") + "?q=Inexistente"
        response = self.client.get(url_search)
        self.assertContains(response, "Nenhum resultado encontrado")
        self.assertContains(response, "palavras-chave diferentes")

    # Teste página categoria

    def test_categoria_lista_noticias(self):
        url_categoria = reverse("jornal_app:noticias_por_categoria", args=[self.categoria.pk])
        response = self.client.get(url_categoria)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.categoria.nome)
        self.assertContains(response, self.noticia.titulo)
        self.assertContains(response, self.noticia.titulo)


    def test_categoria_sem_noticias_exibe_mensagem(self):
        outra_categoria = Categoria.objects.create(nome="Esportes")
        url_categoria = reverse("jornal_app:noticias_por_categoria", args=[outra_categoria.pk])
        response = self.client.get(url_categoria)
        self.assertContains(response, "Ainda não há notícias publicadas nesta categoria.")
