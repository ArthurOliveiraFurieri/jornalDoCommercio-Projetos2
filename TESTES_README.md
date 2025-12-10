# 🧪 Guia de Testes E2E - Jornal do Commercio

## 📋 Sobre os Testes

Este projeto inclui **testes End-to-End (E2E)** completos que simulam a jornada real do usuário na aplicação web usando **Selenium WebDriver**.

## 🎯 Tipos de Testes Disponíveis

### 1. ✅ Testes Unitários (TestCase) - 11 testes
Testes rápidos que verificam funcionalidades individuais sem navegador.

### 2. 🚀 Testes E2E Local (LiveServerTestCase + Selenium) - 10 testes
Testes com servidor Django local, navegador em modo headless (sem janela).

### 3. 🌐 **NOVO! Testes E2E Produção (Site ao Vivo)** - 10 testes
**Testa o site DEPLOYADO no Railway com navegador VISÍVEL!**
- ✅ Você vê os testes acontecendo na tela
- ✅ Testa o site real em produção
- ✅ Verifica responsividade em diferentes resoluções
- ✅ Simula jornada completa do usuário
- ✅ Testa criação de conta e autenticação
- ✅ Verifica sistema de comentários
- ✅ Visualiza perfil e gamificação

## 🎬 Como Executar Testes de Produção (Navegador Visível)

### Método 1: Script Automatizado (Recomendado)

```bash
python executar_testes_producao.py
```

### Método 2: Comando Django Direto

```bash
python manage.py test jornal_app.tests.JornalProductionE2ETests --verbosity=2
```

### O que você verá:

1. 🌐 Navegador Chrome abre automaticamente
2. 📍 Acessa o site no Railway
3. 🎬 Executa ações como um usuário real:
   - Navega pela homepage
   - Usa o sistema de busca
   - Clica em notícias
   - Testa páginas de login/cadastro
   - Muda tamanho da janela (responsividade)
4. ✅ Mostra resultados em tempo real no terminal
5. ⏰ Pausa 5 segundos antes de fechar

## 🧪 Cenários de Teste de Produção
## 🧪 Cenários de Teste de Produção

1. **test_prod_01_homepage_carrega** - Verifica carregamento da homepage
2. **test_prod_02_navegacao_busca** - Testa sistema de busca
3. **test_prod_03_clicar_noticia** - Clica e lê uma notícia
4. **test_prod_04_acessar_cadastro** - Verifica formulário de cadastro
5. **test_prod_05_acessar_login** - Verifica formulário de login
6. **test_prod_06_verificar_responsividade** - Testa Desktop/Tablet/Mobile
7. **test_prod_07_navegacao_completa** - Simula jornada completa
8. **test_prod_08_criar_conta_aleatoria** - Cria conta com dados aleatórios
9. **test_prod_09_comentar_noticia** - Faz login e comenta em notícia
10. **test_prod_10_visualizar_perfil_gamificacao** - Visualiza perfil e elementos de gamificação

## 📊 Cenários de Teste Local (E2E)
2. Mensagem de login para comentar
3. Comentários de usuários autenticados
4. Exclusão de comentários pelo autor
5. Homepage com notícias em destaque
6. Sistema de busca de notícias
7. Listagem por categoria

### 🚀 Testes E2E (LiveServerTestCase + Selenium)
1. **test_e2e_01_navegacao_homepage** - Acesso e visualização da homepage
2. **test_e2e_02_navegacao_por_categorias** - Navegação entre categorias
3. **test_e2e_03_leitura_noticia_completa** - Leitura de notícia completa
4. **test_e2e_04_busca_noticias** - Sistema de busca
5. **test_e2e_05_registro_novo_usuario** - Cadastro de novo usuário
6. **test_e2e_06_login_usuario** - Login na plataforma
7. **test_e2e_07_comentar_noticia** - Adicionar comentário
8. **test_e2e_08_excluir_comentario** - Excluir comentário próprio
9. **test_e2e_09_perfil_gamificacao** - Acesso ao perfil de gamificação
10. **test_e2e_10_logout** - Logout do sistema

## 🔧 Pré-requisitos

### 1. Instalar dependências Python
```bash
pip install -r requirements.txt
```

### 2. Instalar ChromeDriver

**Windows:**
```bash
# Via Chocolatey
choco install chromedriver

# Ou baixe manualmente de:
# https://googlechromelabs.github.io/chrome-for-testing/
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install -y chromium-chromedriver
```

**macOS:**
```bash
brew install chromedriver
```

### 3. Verificar instalação
```bash
chromedriver --version
```

## ▶️ Como Executar os Testes

### Executar TODOS os testes
```bash
python manage.py test jornal_app.tests
```

### Executar apenas testes unitários
```bash
python manage.py test jornal_app.tests.JornalAppViewsTests
```

### Executar apenas testes E2E
```bash
python manage.py test jornal_app.tests.JornalE2ETests
```

### Executar teste específico
```bash
python manage.py test jornal_app.tests.JornalE2ETests.test_e2e_05_registro_novo_usuario
```

### Executar com verbose (mais detalhes)
```bash
python manage.py test jornal_app.tests --verbosity=2
```

## 📊 Saída Esperada

```
🧪 Teste E2E 01: Navegação na homepage
✅ Título da página verificado
✅ Notícias exibidas na homepage
.
🧪 Teste E2E 02: Navegação por categorias
✅ Navegação para categoria Política funcionou
.
🧪 Teste E2E 03: Leitura de notícia completa
✅ Notícia completa exibida corretamente
.
...

----------------------------------------------------------------------
Ran 20 tests in 45.234s

OK
```
## 🔒 Modo Headless

Os testes rodam em **modo headless** por padrão (sem abrir janela do navegador). Para ver o navegador durante os testes:

```python
# Em tests.py, comentar estas linhas:
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
```

## 🚀 CI/CD

Para integrar com CI/CD (GitHub Actions, GitLab CI):

```yaml
# .github/workflows/tests.yml
name: Django Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: sudo apt-get install -y chromium-chromedriver
      - run: python manage.py test
```
