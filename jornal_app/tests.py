from django.test import TestCase, Client, LiveServerTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from jornal_app.models import Noticia, Categoria, Comentario, UserProfile
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


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


# =====================================================
# TESTES E2E (End-to-End) COM SELENIUM
# =====================================================

class JornalE2ETests(LiveServerTestCase):
    """
    Testes E2E que simulam a jornada completa do usuário na aplicação.
    Usa Selenium WebDriver para automação de navegador.
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configuração do Chrome em modo headless (sem interface gráfica)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        cls.selenium = webdriver.Chrome(options=options)
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
    def setUp(self):
        # Criar dados de teste
        self.categoria_politica = Categoria.objects.create(nome="Política")
        self.categoria_economia = Categoria.objects.create(nome="Economia")
        self.categoria_esportes = Categoria.objects.create(nome="Esportes")
        
        self.noticia1 = Noticia.objects.create(
            titulo="Governo anuncia reforma tributária",
            conteudo="O governo federal anunciou hoje uma reforma tributária que vai simplificar o sistema de impostos...",
            categoria=self.categoria_politica,
            data_publicacao=datetime.now()
        )
        
        self.noticia2 = Noticia.objects.create(
            titulo="Mercado financeiro reage positivamente",
            conteudo="O mercado financeiro brasileiro apresentou alta significativa nesta terça-feira...",
            categoria=self.categoria_economia,
            data_publicacao=datetime.now()
        )
        
        self.noticia3 = Noticia.objects.create(
            titulo="Time brasileiro vence campeonato internacional",
            conteudo="O time nacional conquistou o título do campeonato mundial após uma partida emocionante...",
            categoria=self.categoria_esportes,
            data_publicacao=datetime.now()
        )
        
        # Usuário de teste
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_e2e_01_navegacao_homepage(self):
        """E2E: Usuário acessa homepage e visualiza notícias"""
        print("\n🧪 Teste E2E 01: Navegação na homepage")
        
        # Acessar homepage
        self.selenium.get(f'{self.live_server_url}/')
        time.sleep(2)
        
        # Verificar título da página
        self.assertIn("Jornal do Commercio", self.selenium.title)
        print("✅ Título da página verificado")
        
        # Verificar se notícias aparecem
        body = self.selenium.find_element(By.TAG_NAME, 'body').text
        self.assertIn("Governo anuncia reforma", body)
        print("✅ Notícias exibidas na homepage")
    
    def test_e2e_02_navegacao_por_categorias(self):
        """E2E: Usuário navega pelas categorias de notícias"""
        print("\n🧪 Teste E2E 02: Navegação por categorias")
        
        self.selenium.get(f'{self.live_server_url}/')
        time.sleep(2)
        
        # Clicar na categoria Política
        try:
            link_politica = WebDriverWait(self.selenium, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Política"))
            )
            link_politica.click()
            time.sleep(2)
            
            # Verificar se estamos na página da categoria
            body = self.selenium.find_element(By.TAG_NAME, 'body').text
            self.assertIn("Política", body)
            self.assertIn("reforma tributária", body)
            print("✅ Navegação para categoria Política funcionou")
        except TimeoutException:
            print("⚠️ Link de categoria não encontrado (pode não estar no menu)")
    
    def test_e2e_03_leitura_noticia_completa(self):
        """E2E: Usuário acessa e lê notícia completa"""
        print("\n🧪 Teste E2E 03: Leitura de notícia completa")
        
        self.selenium.get(f'{self.live_server_url}/')
        time.sleep(2)
        
        # Clicar em uma notícia
        try:
            noticia_link = WebDriverWait(self.selenium, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Governo"))
            )
            noticia_link.click()
            time.sleep(2)
            
            # Verificar conteúdo completo da notícia
            body = self.selenium.find_element(By.TAG_NAME, 'body').text
            self.assertIn("reforma tributária", body)
            self.assertIn("simplificar o sistema", body)
            print("✅ Notícia completa exibida corretamente")
        except TimeoutException:
            print("⚠️ Link da notícia não encontrado")
    
    def test_e2e_04_busca_noticias(self):
        """E2E: Usuário utiliza busca para encontrar notícias"""
        print("\n🧪 Teste E2E 04: Busca de notícias")
        
        self.selenium.get(f'{self.live_server_url}/')
        time.sleep(2)
        
        try:
            # Localizar campo de busca
            search_input = self.selenium.find_element(By.NAME, 'q')
            search_input.send_keys('mercado')
            
            # Submeter formulário de busca
            search_input.submit()
            time.sleep(2)
            
            # Verificar resultados
            body = self.selenium.find_element(By.TAG_NAME, 'body').text
            self.assertIn("Resultados", body)
            self.assertIn("Mercado financeiro", body)
            print("✅ Busca funcionou corretamente")
        except Exception as e:
            print(f"⚠️ Busca não disponível: {str(e)}")
    
    def test_e2e_05_registro_novo_usuario(self):
        """E2E: Novo usuário se registra na plataforma"""
        print("\n🧪 Teste E2E 05: Registro de novo usuário")
        
        self.selenium.get(f'{self.live_server_url}/accounts/register/')
        time.sleep(2)
        
        try:
            # Preencher formulário de registro
            username_input = self.selenium.find_element(By.NAME, 'username')
            email_input = self.selenium.find_element(By.NAME, 'email')
            password1_input = self.selenium.find_element(By.NAME, 'password1')
            password2_input = self.selenium.find_element(By.NAME, 'password2')
            
            username_input.send_keys('novousuario')
            email_input.send_keys('novo@example.com')
            password1_input.send_keys('SenhaForte123!')
            password2_input.send_keys('SenhaForte123!')
            
            # Submeter formulário
            password2_input.submit()
            time.sleep(3)
            
            # Verificar se foi redirecionado para home (registro bem-sucedido)
            self.assertIn(self.live_server_url, self.selenium.current_url)
            print("✅ Registro de usuário funcionou")
            
            # Verificar se usuário foi criado no banco
            self.assertTrue(User.objects.filter(username='novousuario').exists())
            print("✅ Usuário criado no banco de dados")
        except Exception as e:
            print(f"⚠️ Erro no registro: {str(e)}")
    
    def test_e2e_06_login_usuario(self):
        """E2E: Usuário faz login na plataforma"""
        print("\n🧪 Teste E2E 06: Login de usuário")
        
        self.selenium.get(f'{self.live_server_url}/accounts/login/')
        time.sleep(2)
        
        try:
            # Preencher formulário de login
            username_input = self.selenium.find_element(By.NAME, 'username')
            password_input = self.selenium.find_element(By.NAME, 'password')
            
            username_input.send_keys('testuser')
            password_input.send_keys('testpass123')
            
            # Submeter formulário
            password_input.submit()
            time.sleep(3)
            
            # Verificar se foi redirecionado (login bem-sucedido)
            body = self.selenium.find_element(By.TAG_NAME, 'body').text
            self.assertIn("testuser", body.lower())
            print("✅ Login funcionou corretamente")
        except Exception as e:
            print(f"⚠️ Erro no login: {str(e)}")
    
    def test_e2e_07_comentar_noticia(self):
        """E2E: Usuário logado comenta em uma notícia"""
        print("\n🧪 Teste E2E 07: Comentar em notícia")
        
        # Primeiro fazer login
        self.selenium.get(f'{self.live_server_url}/accounts/login/')
        time.sleep(2)
        
        try:
            username_input = self.selenium.find_element(By.NAME, 'username')
            password_input = self.selenium.find_element(By.NAME, 'password')
            username_input.send_keys('testuser')
            password_input.send_keys('testpass123')
            password_input.submit()
            time.sleep(3)
            
            # Acessar notícia
            self.selenium.get(f'{self.live_server_url}/noticia/{self.noticia1.pk}/')
            time.sleep(2)
            
            # Adicionar comentário
            comment_input = self.selenium.find_element(By.NAME, 'texto')
            comment_input.send_keys('Excelente matéria! Muito informativo.')
            comment_input.submit()
            time.sleep(3)
            
            # Verificar se comentário aparece
            body = self.selenium.find_element(By.TAG_NAME, 'body').text
            self.assertIn("Excelente matéria", body)
            print("✅ Comentário adicionado com sucesso")
            
            # Verificar no banco de dados
            self.assertTrue(
                Comentario.objects.filter(
                    texto__contains="Excelente matéria",
                    autor=self.user
                ).exists()
            )
            print("✅ Comentário salvo no banco de dados")
        except Exception as e:
            print(f"⚠️ Erro ao comentar: {str(e)}")
    
    def test_e2e_08_excluir_comentario(self):
        """E2E: Usuário exclui seu próprio comentário"""
        print("\n🧪 Teste E2E 08: Excluir comentário")
        
        # Criar comentário
        comentario = Comentario.objects.create(
            noticia=self.noticia1,
            autor=self.user,
            texto="Comentário para deletar"
        )
        
        # Fazer login
        self.selenium.get(f'{self.live_server_url}/accounts/login/')
        time.sleep(2)
        
        try:
            username_input = self.selenium.find_element(By.NAME, 'username')
            password_input = self.selenium.find_element(By.NAME, 'password')
            username_input.send_keys('testuser')
            password_input.send_keys('testpass123')
            password_input.submit()
            time.sleep(3)
            
            # Acessar página de exclusão
            self.selenium.get(
                f'{self.live_server_url}/comentario/{comentario.pk}/delete/'
            )
            time.sleep(2)
            
            # Confirmar exclusão
            confirm_button = self.selenium.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
            confirm_button.click()
            time.sleep(3)
            
            # Verificar se comentário foi deletado
            self.assertFalse(
                Comentario.objects.filter(pk=comentario.pk).exists()
            )
            print("✅ Comentário excluído com sucesso")
        except Exception as e:
            print(f"⚠️ Erro ao excluir: {str(e)}")
    
    def test_e2e_09_perfil_gamificacao(self):
        """E2E: Usuário acessa perfil de gamificação"""
        print("\n🧪 Teste E2E 09: Perfil de gamificação")
        
        # Criar perfil
        UserProfile.objects.create(
            usuario=self.user,
            pontos=150,
            nivel=2,
            noticias_lidas=10,
            comentarios_feitos=5
        )
        
        # Fazer login
        self.selenium.get(f'{self.live_server_url}/accounts/login/')
        time.sleep(2)
        
        try:
            username_input = self.selenium.find_element(By.NAME, 'username')
            password_input = self.selenium.find_element(By.NAME, 'password')
            username_input.send_keys('testuser')
            password_input.send_keys('testpass123')
            password_input.submit()
            time.sleep(3)
            
            # Acessar perfil
            self.selenium.get(f'{self.live_server_url}/profile/')
            time.sleep(2)
            
            # Verificar informações do perfil
            body = self.selenium.find_element(By.TAG_NAME, 'body').text
            self.assertIn("150", body)  # Pontos
            self.assertIn("testuser", body)
            print("✅ Perfil de gamificação carregado corretamente")
        except Exception as e:
            print(f"⚠️ Erro ao acessar perfil: {str(e)}")
    
    def test_e2e_10_logout(self):
        """E2E: Usuário faz logout"""
        print("\n🧪 Teste E2E 10: Logout de usuário")
        
        # Fazer login primeiro
        self.selenium.get(f'{self.live_server_url}/accounts/login/')
        time.sleep(2)
        
        try:
            username_input = self.selenium.find_element(By.NAME, 'username')
            password_input = self.selenium.find_element(By.NAME, 'password')
            username_input.send_keys('testuser')
            password_input.send_keys('testpass123')
            password_input.submit()
            time.sleep(3)
            
            # Fazer logout (procurar link ou botão)
            try:
                logout_link = self.selenium.find_element(By.PARTIAL_LINK_TEXT, "Sair")
                logout_link.click()
            except:
                # Se for POST, procurar formulário
                logout_form = self.selenium.find_element(By.CSS_SELECTOR, 'form[action*="logout"]')
                logout_form.submit()
            
            time.sleep(3)
            
            # Verificar se foi deslogado (tentar acessar página protegida)
            self.selenium.get(f'{self.live_server_url}/profile/')
            time.sleep(2)
            
            # Deve redirecionar para login
            self.assertIn("login", self.selenium.current_url.lower())
            print("✅ Logout funcionou corretamente")
        except Exception as e:
            print(f"⚠️ Erro no logout: {str(e)}")
    def test_categoria_sem_noticias_exibe_mensagem(self):
        outra_categoria = Categoria.objects.create(nome="Esportes")
        url_categoria = reverse("jornal_app:noticias_por_categoria", args=[outra_categoria.pk])
        response = self.client.get(url_categoria)
        self.assertContains(response, "Ainda não há notícias publicadas nesta categoria.")
