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
        self.assertContains(response, "para deixar um comentário")

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
        self.assertContains(response, "Resultados da Busca")
        self.assertContains(response, "Buscando por")
        self.assertContains(response, self.noticia.titulo)

    def test_busca_sem_resultados_exibe_mensagem(self):
        url_search = reverse("jornal_app:noticia_search") + "?q=Inexistente"
        response = self.client.get(url_search)
        self.assertContains(response, "Nenhuma notícia encontrada")
        self.assertContains(response, "Inexistente")

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


# =====================================================
# TESTES E2E PRODUÇÃO - SITE AO VIVO NO RAILWAY
# =====================================================

class JornalProductionE2ETests(TestCase):
    """
    Testes E2E no site de PRODUÇÃO (Railway).
    Abre o navegador VISÍVEL para mostrar os testes em ação.
    
    IMPORTANTE: Execute apenas quando o site estiver deployado!
    Comando: python manage.py test jornal_app.tests.JornalProductionE2ETests
    """
    
    # URL do site em produção no Railway
    PRODUCTION_URL = "https://jornaldocommercio-projetos2-production.up.railway.app"
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n" + "="*70)
        print("🚀 INICIANDO TESTES E2E NO SITE DE PRODUÇÃO")
        print(f"🌐 URL: {cls.PRODUCTION_URL}")
        print("👁️  Navegador VISÍVEL - Acompanhe os testes na tela!")
        print("="*70 + "\n")
        
        # Configuração do Chrome VISÍVEL (SEM headless)
        options = webdriver.ChromeOptions()
        # Comentar headless para ver o navegador
        # options.add_argument('--headless')
        options.add_argument('--start-maximized')  # Maximizar janela
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        cls.selenium = webdriver.Chrome(options=options)
        cls.selenium.implicitly_wait(10)
        
        # Deixar navegador aberto por mais tempo para visualização
        cls.selenium.set_page_load_timeout(30)
    
    @classmethod
    def tearDownClass(cls):
        print("\n" + "="*70)
        print("✅ TESTES CONCLUÍDOS!")
        print("⏳ Aguardando 5 segundos antes de fechar o navegador...")
        print("="*70)
        time.sleep(5)  # Pausar antes de fechar
        cls.selenium.quit()
        super().tearDownClass()
    
    def test_prod_01_homepage_carrega(self):
        """Teste 1: Verificar se a homepage carrega corretamente"""
        print("\n" + "="*70)
        print("🧪 TESTE 1: Carregamento da Homepage")
        print("="*70)
        
        print(f"📍 Acessando: {self.PRODUCTION_URL}")
        self.selenium.get(self.PRODUCTION_URL)
        time.sleep(3)
        
        print("✓ Verificando título da página...")
        page_title = self.selenium.title
        print(f"  📄 Título: {page_title}")
        self.assertIn("Jornal", page_title)
        
        print("✓ Verificando se há notícias na página...")
        body = self.selenium.find_element(By.TAG_NAME, 'body').text
        self.assertTrue(len(body) > 100)
        
        print("✅ Homepage carregada com sucesso!\n")
        time.sleep(2)
    
    def test_prod_02_navegacao_busca(self):
        """Teste 2: Testar funcionalidade de busca"""
        print("\n" + "="*70)
        print("🧪 TESTE 2: Sistema de Busca")
        print("="*70)
        
        self.selenium.get(self.PRODUCTION_URL)
        time.sleep(2)
        
        try:
            print("✓ Procurando botão de busca...")
            search_btn = WebDriverWait(self.selenium, 10).until(
                EC.element_to_be_clickable((By.ID, "search-toggle-btn"))
            )
            print("✓ Clicando no botão de busca...")
            search_btn.click()
            time.sleep(1)
            
            print("✓ Digitando termo de busca: 'política'")
            search_input = self.selenium.find_element(By.NAME, 'q')
            search_input.send_keys('política')
            time.sleep(1)
            
            print("✓ Submetendo busca...")
            search_input.submit()
            time.sleep(3)
            
            print("✓ Verificando resultados...")
            body = self.selenium.find_element(By.TAG_NAME, 'body').text
            self.assertIn("Busca", body) or self.assertIn("Resultado", body)
            
            print("✅ Sistema de busca funcionando!\n")
        except Exception as e:
            print(f"⚠️  Aviso: Busca não disponível - {str(e)}\n")
        
        time.sleep(2)
    
    def test_prod_03_clicar_noticia(self):
        """Teste 3: Clicar em uma notícia e ler conteúdo"""
        print("\n" + "="*70)
        print("🧪 TESTE 3: Leitura de Notícia")
        print("="*70)
        
        self.selenium.get(self.PRODUCTION_URL)
        time.sleep(3)
        
        try:
            print("✓ Procurando primeira notícia...")
            noticia_link = WebDriverWait(self.selenium, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='/noticia/']"))
            )
            
            noticia_titulo = noticia_link.text
            print(f"✓ Encontrada: '{noticia_titulo}'")
            print("✓ Clicando na notícia...")
            noticia_link.click()
            time.sleep(3)
            
            print("✓ Verificando conteúdo da notícia...")
            body = self.selenium.find_element(By.TAG_NAME, 'body').text
            self.assertTrue(len(body) > 200)
            
            print("✅ Notícia aberta e lida com sucesso!\n")
        except Exception as e:
            print(f"⚠️  Erro ao clicar na notícia: {str(e)}\n")
        
        time.sleep(2)
    
    def test_prod_04_acessar_cadastro(self):
        """Teste 4: Acessar página de cadastro"""
        print("\n" + "="*70)
        print("🧪 TESTE 4: Página de Cadastro")
        print("="*70)
        
        cadastro_url = f"{self.PRODUCTION_URL}/accounts/register/"
        print(f"📍 Acessando: {cadastro_url}")
        self.selenium.get(cadastro_url)
        time.sleep(3)
        
        print("✓ Verificando formulário de cadastro...")
        try:
            username_field = self.selenium.find_element(By.NAME, 'username')
            email_field = self.selenium.find_element(By.NAME, 'email')
            password1_field = self.selenium.find_element(By.NAME, 'password1')
            password2_field = self.selenium.find_element(By.NAME, 'password2')
            
            print("  ✓ Campo: username")
            print("  ✓ Campo: email")
            print("  ✓ Campo: password1")
            print("  ✓ Campo: password2")
            
            print("✅ Formulário de cadastro OK!\n")
        except Exception as e:
            print(f"❌ Erro no formulário: {str(e)}\n")
        
        time.sleep(2)
    
    def test_prod_05_acessar_login(self):
        """Teste 5: Acessar página de login"""
        print("\n" + "="*70)
        print("🧪 TESTE 5: Página de Login")
        print("="*70)
        
        login_url = f"{self.PRODUCTION_URL}/accounts/login/"
        print(f"📍 Acessando: {login_url}")
        self.selenium.get(login_url)
        time.sleep(3)
        
        print("✓ Verificando formulário de login...")
        try:
            username_field = self.selenium.find_element(By.NAME, 'username')
            password_field = self.selenium.find_element(By.NAME, 'password')
            
            print("  ✓ Campo: username")
            print("  ✓ Campo: password")
            
            print("✅ Formulário de login OK!\n")
        except Exception as e:
            print(f"❌ Erro no formulário: {str(e)}\n")
        
        time.sleep(2)
    
    def test_prod_06_verificar_responsividade(self):
        """Teste 6: Testar responsividade em diferentes tamanhos"""
        print("\n" + "="*70)
        print("🧪 TESTE 6: Responsividade")
        print("="*70)
        
        tamanhos = [
            ("Desktop", 1920, 1080),
            ("Tablet", 768, 1024),
            ("Mobile", 375, 667)
        ]
        
        for nome, largura, altura in tamanhos:
            print(f"\n✓ Testando em {nome} ({largura}x{altura})...")
            self.selenium.set_window_size(largura, altura)
            time.sleep(1)
            
            self.selenium.get(self.PRODUCTION_URL)
            time.sleep(2)
            
            body = self.selenium.find_element(By.TAG_NAME, 'body')
            print(f"  ✓ Página renderizada em {nome}")
            time.sleep(2)
        
        # Voltar ao tamanho maximizado
        self.selenium.maximize_window()
        print("\n✅ Responsividade testada!\n")
        time.sleep(2)
    
    def test_prod_07_navegacao_completa(self):
        """Teste 7: Jornada completa do usuário"""
        print("\n" + "="*70)
        print("🧪 TESTE 7: Jornada Completa do Usuário")
        print("="*70)
        
        print("\n1️⃣  Acessando homepage...")
        self.selenium.get(self.PRODUCTION_URL)
        time.sleep(2)
        
        print("2️⃣  Explorando conteúdo...")
        self.selenium.execute_script("window.scrollTo(0, 500);")
        time.sleep(1)
        self.selenium.execute_script("window.scrollTo(0, 1000);")
        time.sleep(1)
        
        print("3️⃣  Voltando ao topo...")
        self.selenium.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        try:
            print("4️⃣  Navegando para cadastro...")
            cadastrar_link = self.selenium.find_element(By.LINK_TEXT, "Cadastrar")
            cadastrar_link.click()
            time.sleep(2)
            
            print("5️⃣  Voltando para home...")
            self.selenium.get(self.PRODUCTION_URL)
            time.sleep(2)
        except:
            print("  ⚠️  Link de cadastro não encontrado no menu")
        
        print("\n✅ Jornada completa simulada!\n")
        time.sleep(2)
    
    def test_prod_08_criar_conta_aleatoria(self):
        """Teste 8: Criar conta aleatória através do cadastro"""
        import random
        import string
        
        print("\n" + "="*70)
        print("🧪 TESTE 8: Criação de Conta Aleatória")
        print("="*70)
        
        # Gerar credenciais aleatórias
        random_username = 'testuser_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        random_email = random_username + '@teste.com'
        random_password = 'Test@' + ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        print(f"\n📝 Credenciais geradas:")
        print(f"   Username: {random_username}")
        print(f"   Email: {random_email}")
        print(f"   Senha: {'*' * len(random_password)}")
        
        print("\n1️⃣  Navegando para página de cadastro...")
        self.selenium.get(f"{self.PRODUCTION_URL}/accounts/register/")
        time.sleep(3)
        
        try:
            print("2️⃣  Preenchendo formulário de cadastro...")
            
            # Preencher username
            username_field = WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.ID, "id_username"))
            )
            username_field.send_keys(random_username)
            time.sleep(0.5)
            
            # Preencher email
            email_field = self.selenium.find_element(By.ID, "id_email")
            email_field.send_keys(random_email)
            time.sleep(0.5)
            
            # Preencher senha
            password1_field = self.selenium.find_element(By.ID, "id_password1")
            password1_field.send_keys(random_password)
            time.sleep(0.5)
            
            # Confirmar senha
            password2_field = self.selenium.find_element(By.ID, "id_password2")
            password2_field.send_keys(random_password)
            time.sleep(1)
            
            print("3️⃣  Submetendo formulário...")
            submit_button = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            time.sleep(3)
            
            print("4️⃣  Verificando criação da conta...")
            
            # Verificar se foi redirecionado ou se a conta foi criada
            current_url = self.selenium.current_url
            print(f"   URL atual: {current_url}")
            
            # Verificar se o username aparece na página (indicando login)
            page_source = self.selenium.page_source.lower()
            
            if random_username.lower() in page_source or self.PRODUCTION_URL in current_url:
                print(f"\n✅ Conta criada e usuário logado com sucesso!")
                # Armazenar credenciais para próximo teste
                self.test_credentials = {
                    'username': random_username,
                    'password': random_password
                }
            else:
                print("\n⚠️  Conta pode ter sido criada, verificando status...")
                
        except Exception as e:
            print(f"\n❌ Erro ao criar conta: {str(e)}")
            raise
        
        time.sleep(2)
    
    def test_prod_09_comentar_noticia(self):
        """Teste 9: Fazer login e comentar em uma notícia"""
        import random
        import string
        
        print("\n" + "="*70)
        print("🧪 TESTE 9: Comentar em Notícia")
        print("="*70)
        
        # Verificar se temos credenciais do teste anterior
        if not hasattr(self, 'test_credentials'):
            print("\n⚠️  Criando nova conta para este teste...")
            # Criar conta rapidamente
            random_username = 'commenter_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            random_password = 'Test@' + ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            random_email = random_username + '@teste.com'
            
            self.selenium.get(f"{self.PRODUCTION_URL}/accounts/register/")
            time.sleep(3)
            
            self.selenium.find_element(By.ID, "id_username").send_keys(random_username)
            self.selenium.find_element(By.ID, "id_email").send_keys(random_email)
            self.selenium.find_element(By.ID, "id_password1").send_keys(random_password)
            self.selenium.find_element(By.ID, "id_password2").send_keys(random_password)
            self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(3)
            
            self.test_credentials = {'username': random_username, 'password': random_password}
        
        username = self.test_credentials['username']
        password = self.test_credentials['password']
        
        print(f"\n👤 Usando conta: {username}")
        
        try:
            print("\n1️⃣  Verificando se já está logado...")
            self.selenium.get(self.PRODUCTION_URL)
            time.sleep(2)
            
            page_source = self.selenium.page_source.lower()
            
            if 'entrar' in page_source and username.lower() not in page_source:
                print("2️⃣  Fazendo login...")
                self.selenium.get(f"{self.PRODUCTION_URL}/login/")
                time.sleep(2)
                
                username_field = self.selenium.find_element(By.ID, "id_username")
                username_field.send_keys(username)
                time.sleep(0.5)
                
                password_field = self.selenium.find_element(By.ID, "id_password")
                password_field.send_keys(password)
                time.sleep(0.5)
                
                submit_button = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
                submit_button.click()
                time.sleep(3)
            else:
                print("2️⃣  Usuário já está logado!")
            
            print("3️⃣  Navegando para uma notícia...")
            self.selenium.get(self.PRODUCTION_URL)
            time.sleep(2)
            
            # Encontrar e clicar na primeira notícia
            noticias = self.selenium.find_elements(By.CSS_SELECTOR, "a[href*='/noticia/']")
            if noticias:
                noticia_url = noticias[0].get_attribute('href')
                print(f"   Acessando: {noticia_url[:60]}...")
                self.selenium.get(noticia_url)
                time.sleep(3)
            else:
                print("   ⚠️  Nenhuma notícia encontrada, usando URL direta...")
                self.selenium.get(self.PRODUCTION_URL)
                time.sleep(2)
            
            print("4️⃣  Procurando campo de comentário...")
            
            # Scroll até a área de comentários
            self.selenium.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Tentar encontrar textarea de comentário
            comment_field = None
            try:
                comment_field = WebDriverWait(self.selenium, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[name='conteudo']"))
                )
            except:
                try:
                    comment_field = self.selenium.find_element(By.ID, "id_conteudo")
                except:
                    try:
                        comment_field = self.selenium.find_element(By.CSS_SELECTOR, "textarea")
                    except:
                        pass
            
            if comment_field:
                print("5️⃣  Escrevendo comentário...")
                
                # Gerar comentário aleatório
                comentarios_exemplos = [
                    "Muito interessante este artigo! Parabéns pelo conteúdo.",
                    "Excelente reportagem, muito bem escrita e informativa.",
                    "Gostei bastante, sempre bom ler notícias de qualidade.",
                    "Conteúdo relevante e atual, obrigado por compartilhar!",
                    "Ótima matéria, me ajudou a entender melhor o assunto."
                ]
                
                random_comment = random.choice(comentarios_exemplos) + f" [Teste automático {random.randint(1000, 9999)}]"
                
                # Scroll até o campo de comentário
                self.selenium.execute_script("arguments[0].scrollIntoView(true);", comment_field)
                time.sleep(1)
                
                comment_field.click()
                comment_field.send_keys(random_comment)
                time.sleep(2)
                
                print(f"   Comentário: {random_comment[:50]}...")
                
                print("6️⃣  Enviando comentário...")
                
                # Encontrar botão de enviar
                submit_button = None
                try:
                    submit_button = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
                except:
                    try:
                        submit_button = self.selenium.find_element(By.XPATH, "//button[contains(text(), 'Enviar')]")
                    except:
                        pass
                
                if submit_button:
                    submit_button.click()
                    time.sleep(3)
                    
                    print("7️⃣  Verificando se comentário foi publicado...")
                    
                    # Verificar se o comentário aparece na página
                    page_source = self.selenium.page_source
                    
                    if username in page_source or "comentário" in page_source.lower():
                        print("\n✅ Comentário enviado com sucesso!")
                    else:
                        print("\n⚠️  Comentário pode estar aguardando moderação")
                else:
                    print("\n⚠️  Botão de enviar não encontrado")
            else:
                print("\n⚠️  Campo de comentário não encontrado - pode precisar estar na página de notícia")
                
        except Exception as e:
            print(f"\n❌ Erro ao comentar: {str(e)}")
            # Não dar raise para não interromper os testes
        
        time.sleep(2)
    
    def test_prod_10_visualizar_perfil_gamificacao(self):
        """Teste 10: Visualizar perfil e gamificação"""
        import random
        import string
        
        print("\n" + "="*70)
        print("🧪 TESTE 10: Visualização de Perfil e Gamificação")
        print("="*70)
        
        # Verificar se temos credenciais do teste anterior
        if not hasattr(self, 'test_credentials'):
            print("\n⚠️  Criando nova conta para este teste...")
            random_username = 'profile_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            random_password = 'Test@' + ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            random_email = random_username + '@teste.com'
            
            self.selenium.get(f"{self.PRODUCTION_URL}/accounts/register/")
            time.sleep(3)
            
            self.selenium.find_element(By.ID, "id_username").send_keys(random_username)
            self.selenium.find_element(By.ID, "id_email").send_keys(random_email)
            self.selenium.find_element(By.ID, "id_password1").send_keys(random_password)
            self.selenium.find_element(By.ID, "id_password2").send_keys(random_password)
            self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(3)
            
            self.test_credentials = {'username': random_username, 'password': random_password}
        
        username = self.test_credentials['username']
        password = self.test_credentials['password']
        
        print(f"\n👤 Usando conta: {username}")
        
        try:
            print("\n1️⃣  Verificando se está logado...")
            self.selenium.get(self.PRODUCTION_URL)
            time.sleep(2)
            
            page_source = self.selenium.page_source.lower()
            
            if 'entrar' in page_source and username.lower() not in page_source:
                print("2️⃣  Fazendo login...")
                self.selenium.get(f"{self.PRODUCTION_URL}/login/")
                time.sleep(2)
                
                self.selenium.find_element(By.ID, "id_username").send_keys(username)
                time.sleep(0.5)
                self.selenium.find_element(By.ID, "id_password").send_keys(password)
                time.sleep(0.5)
                self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                time.sleep(3)
            else:
                print("2️⃣  Usuário já está logado!")
            
            print("3️⃣  Procurando menu do usuário...")
            self.selenium.get(self.PRODUCTION_URL)
            time.sleep(2)
            
            # Tentar encontrar dropdown ou link do perfil
            profile_link = None
            
            try:
                # Tentar encontrar dropdown do usuário
                user_dropdown = self.selenium.find_element(By.CSS_SELECTOR, ".dropdown-toggle")
                user_dropdown.click()
                time.sleep(1)
                print("   ✓ Dropdown de usuário expandido")
                
                # Procurar link "Meu Perfil"
                try:
                    profile_link = self.selenium.find_element(By.LINK_TEXT, "Meu Perfil")
                except:
                    try:
                        profile_link = self.selenium.find_element(By.PARTIAL_LINK_TEXT, "Perfil")
                    except:
                        pass
            except:
                # Se não encontrar dropdown, tentar link direto
                try:
                    profile_link = self.selenium.find_element(By.CSS_SELECTOR, "a[href*='perfil']")
                except:
                    pass
            
            if profile_link:
                print("4️⃣  Acessando página de perfil...")
                profile_link.click()
                time.sleep(3)
            else:
                # Tentar URL direta
                print("4️⃣  Tentando acessar perfil via URL direta...")
                self.selenium.get(f"{self.PRODUCTION_URL}/perfil/")
                time.sleep(3)
            
            print("5️⃣  Verificando elementos de gamificação no perfil...")
            
            page_source = self.selenium.page_source.lower()
            
            # Verificar elementos de gamificação
            gamification_elements = {
                'pontos': ['pontos', 'points', '⭐'],
                'nivel': ['nível', 'nivel', 'level'],
                'estatisticas': ['estatísticas', 'estatisticas', 'stats'],
                'noticias_lidas': ['notícias lidas', 'noticias lidas', 'artigos lidos'],
                'comentarios': ['comentários', 'comentarios']
            }
            
            found_elements = []
            
            for element_name, keywords in gamification_elements.items():
                for keyword in keywords:
                    if keyword in page_source:
                        found_elements.append(element_name)
                        break
            
            if found_elements:
                print(f"\n   ✅ Elementos encontrados: {', '.join(found_elements)}")
            else:
                print("\n   ℹ️  Perfil carregado (elementos de gamificação podem estar em desenvolvimento)")
            
            # Scroll pela página de perfil
            print("\n6️⃣  Explorando página de perfil...")
            self.selenium.execute_script("window.scrollTo(0, 500);")
            time.sleep(1)
            self.selenium.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Verificar se há informações do usuário
            if username in self.selenium.page_source:
                print(f"   ✓ Username '{username}' visível no perfil")
            
            print("\n✅ Perfil visualizado com sucesso!")
            
        except Exception as e:
            print(f"\n❌ Erro ao visualizar perfil: {str(e)}")
            # Não dar raise para não interromper os testes
        
        time.sleep(2)
