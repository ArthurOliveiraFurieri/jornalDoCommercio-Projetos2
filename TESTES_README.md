# 🧪 Guia de Testes E2E - Jornal do Commercio

## 📋 Sobre os Testes

Este projeto inclui **testes End-to-End (E2E)** completos que simulam a jornada real do usuário na aplicação web usando **Selenium WebDriver**.

## 🎯 Cenários de Teste Cobertos

### ✅ Testes Unitários (TestCase)
1. Exibição de artigos com título e conteúdo
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

## 🐛 Troubleshooting

### Erro: "chromedriver not found"
**Solução:** Instale o ChromeDriver e adicione ao PATH do sistema.

### Erro: "Chrome version mismatch"
**Solução:** Atualize o Chrome e o ChromeDriver para versões compatíveis.

### Erro: TimeoutException
**Solução:** Aumentar o `implicitly_wait` ou verificar se elemento existe na página.

### Testes muito lentos
**Solução:** Os testes E2E são naturalmente mais lentos. Para acelerar:
```python
# Reduzir time.sleep() no código de testes
# Usar headless mode (já configurado por padrão)
```

## 🔒 Modo Headless

Os testes rodam em **modo headless** por padrão (sem abrir janela do navegador). Para ver o navegador durante os testes:

```python
# Em tests.py, comentar estas linhas:
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
```

## 📈 Cobertura de Código

Para verificar cobertura de código:

```bash
pip install coverage
coverage run --source='.' manage.py test jornal_app.tests
coverage report
coverage html
```

Abra `htmlcov/index.html` no navegador para ver relatório detalhado.

## 🎓 Boas Práticas

1. **Execute os testes antes de cada commit**
2. **Mantenha os testes atualizados** conforme adiciona features
3. **Use dados de teste realistas** mas não sensíveis
4. **Limpe o banco de dados** entre testes (Django faz isso automaticamente)
5. **Documente novos cenários** de teste adicionados

## 📝 Adicionando Novos Testes

```python
def test_e2e_11_novo_cenario(self):
    """E2E: Descrição do cenário"""
    print("\n🧪 Teste E2E 11: Nome do teste")
    
    # 1. Setup
    self.selenium.get(f'{self.live_server_url}/caminho/')
    time.sleep(2)
    
    try:
        # 2. Ação
        elemento = self.selenium.find_element(By.NAME, 'campo')
        elemento.send_keys('valor')
        elemento.submit()
        time.sleep(2)
        
        # 3. Verificação
        body = self.selenium.find_element(By.TAG_NAME, 'body').text
        self.assertIn("texto esperado", body)
        print("✅ Teste passou")
    except Exception as e:
        print(f"⚠️ Erro: {str(e)}")
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

## 📞 Suporte

Em caso de dúvidas ou problemas, consulte:
- Documentação Django Testing: https://docs.djangoproject.com/en/5.2/topics/testing/
- Selenium Docs: https://www.selenium.dev/documentation/
