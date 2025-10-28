# 🧪 GUIA COMPLETO DE TESTES - Jornal do Commercio

## ✅ PRÉ-REQUISITOS

O servidor já está rodando em: **http://127.0.0.1:8000**

---

## 📋 CHECKLIST DE TESTES

### ✅ 1. HOMEPAGE

**URL:** http://127.0.0.1:8000/

**O que você deve ver:**
- ✅ Header com logo "Jornal do Commercio"
- ✅ Barra de busca funcional
- ✅ Barra de categorias (Política, Economia, Esportes, etc.)
- ✅ Seção "Destaques" com 3 notícias em destaque
- ✅ Seção "Notícias Recentes" com 6 notícias
- ✅ Info Bar com temperatura, dólar, euro e horário
- ✅ Footer com links e informações

**Como testar:**
1. Abra http://127.0.0.1:8000/ no navegador
2. Verifique se as 3 notícias em destaque aparecem
3. Verifique se as 6 notícias recentes aparecem
4. Clique em uma notícia para ver os detalhes

---

### ✅ 2. LISTA DE NOTÍCIAS

**URL:** http://127.0.0.1:8000/noticias/

**O que você deve ver:**
- ✅ Título "Todas as Notícias"
- ✅ Grid com todas as 6 notícias
- ✅ Cada card mostrando:
  - Imagem (se houver)
  - Categoria
  - Título
  - Resumo
  - Data de publicação
  - Autor
  - Link "Leia mais"

**Como testar:**
1. Acesse http://127.0.0.1:8000/noticias/
2. Verifique se todas as 6 notícias aparecem
3. Clique em "Leia mais" em qualquer notícia

---

### ✅ 3. DETALHE DA NOTÍCIA

**URL de exemplo:**
http://127.0.0.1:8000/noticias/nova-reforma-economica-e-aprovada-no-congresso/

**O que você deve ver:**
- ✅ Breadcrumb (Início / Categoria)
- ✅ Título completo da notícia
- ✅ Meta informações (data, autor, visualizações)
- ✅ Tags da notícia
- ✅ Imagem em destaque (se houver)
- ✅ Conteúdo completo
- ✅ Botões de compartilhamento (Facebook, Twitter, WhatsApp)
- ✅ Seção de comentários
- ✅ Formulário para adicionar comentário (se logado)
- ✅ Notícias relacionadas (mesma categoria)

**Como testar:**
1. Acesse qualquer notícia
2. Verifique se o contador de visualizações aumenta ao recarregar
3. Tente adicionar um comentário (precisa estar logado)
4. Clique nos botões de compartilhamento
5. Clique nas tags para ver outras notícias

---

### ✅ 4. NOTÍCIAS POR CATEGORIA

**URLs para testar:**
- http://127.0.0.1:8000/noticias/categoria/politica/
- http://127.0.0.1:8000/noticias/categoria/economia/
- http://127.0.0.1:8000/noticias/categoria/esportes/
- http://127.0.0.1:8000/noticias/categoria/tecnologia/
- http://127.0.0.1:8000/noticias/categoria/cultura/
- http://127.0.0.1:8000/noticias/categoria/saude/

**O que você deve ver:**
- ✅ Título com o nome da categoria
- ✅ Descrição da categoria
- ✅ Notícias filtradas por essa categoria
- ✅ Mensagem se não houver notícias

**Como testar:**
1. Clique em uma categoria na barra de navegação
2. Verifique se apenas notícias daquela categoria aparecem
3. Teste todas as 6 categorias

---

### ✅ 5. BUSCA DE NOTÍCIAS

**URL de exemplo:**
http://127.0.0.1:8000/noticias/buscar/?q=economia

**Termos para buscar:**
- economia
- tecnologia
- brasil
- saúde

**O que você deve ver:**
- ✅ Título "Resultados da busca"
- ✅ Termo buscado destacado
- ✅ Número de resultados encontrados
- ✅ Grid com notícias que correspondem à busca
- ✅ Mensagem se nada for encontrado

**Como testar:**
1. Use a barra de busca no header
2. Digite "economia" e pressione Enter
3. Verifique se encontra a notícia sobre economia
4. Tente buscar termos que não existem

---

### ✅ 6. PAINEL ADMINISTRATIVO

**URL:** http://127.0.0.1:8000/admin/

**Credenciais:**
- Username: `JoaoHB` ou `lucas`
- Senha: (a que foi criada)

**O que você deve ver:**
- ✅ Dashboard do Django Admin
- ✅ Seções:
  - **CORE**: Site Configuration, Menu
  - **NEWS**: Categories, Tags, News, Comments
  - **LIVE**: Live Events
  - **ADVERTISING**: Advertisements
  - **AUTHENTICATION**: Users, Groups

**Como testar:**

**6.1. Gerenciar Notícias:**
1. Acesse http://127.0.0.1:8000/admin/news/news/
2. Veja a lista de todas as notícias
3. Clique em uma notícia para editar
4. Tente marcar/desmarcar como "Destaque"
5. Tente publicar/despublicar uma notícia
6. Salve e veja as mudanças no frontend

**6.2. Criar Nova Notícia:**
1. Clique em "Add News" (+ ao lado de News)
2. Preencha:
   - Título: "Minha Primeira Notícia de Teste"
   - Slug: (será gerado automaticamente)
   - Resumo: "Este é um resumo de teste"
   - Conteúdo: "Conteúdo completo da notícia..."
   - Categoria: Escolha uma
   - Tags: Selecione algumas
   - Marque "Publicado" e "Destaque"
3. Salve e veja no frontend

**6.3. Gerenciar Categorias:**
1. Acesse http://127.0.0.1:8000/admin/news/category/
2. Veja as 6 categorias criadas
3. Edite uma categoria
4. Mude a ordem ou descrição
5. Salve e veja as mudanças no menu

**6.4. Moderar Comentários:**
1. Acesse http://127.0.0.1:8000/admin/news/comment/
2. Veja comentários pendentes
3. Marque como "Aprovado" para aparecer no site

**6.5. Configurar Site:**
1. Acesse http://127.0.0.1:8000/admin/core/siteconfiguration/
2. Edite as configurações:
   - Nome do site
   - Email de contato
   - Telefone
   - Links de redes sociais
3. Salve e veja no footer

---

## 🎨 TESTE DE DESIGN RESPONSIVO

**Como testar:**
1. Abra http://127.0.0.1:8000/
2. Pressione F12 para abrir DevTools
3. Clique no ícone de responsividade (ou Ctrl+Shift+M)
4. Teste em diferentes tamanhos:
   - **Mobile**: 375px
   - **Tablet**: 768px
   - **Desktop**: 1200px
5. Verifique se o layout se adapta bem

**O que deve acontecer:**
- ✅ Menu hambúrguer aparece no mobile
- ✅ Grid de notícias muda de 3 colunas para 1
- ✅ Hero section se adapta
- ✅ Footer reorganiza as colunas
- ✅ Barra de busca ocupa toda a largura

---

## 🔍 TESTE DE FUNCIONALIDADES

### 📝 Comentários

1. **Fazer logout:**
   - Acesse http://127.0.0.1:8000/admin/logout/

2. **Tentar comentar sem login:**
   - Vá em uma notícia
   - Tente comentar
   - Deve pedir para fazer login

3. **Fazer login e comentar:**
   - Faça login em http://127.0.0.1:8000/admin/
   - Volte à notícia
   - Adicione um comentário
   - Mensagem deve aparecer: "Comentário enviado! Ele será publicado após moderação."

4. **Aprovar comentário:**
   - Vá ao admin: http://127.0.0.1:8000/admin/news/comment/
   - Marque seu comentário como "Aprovado"
   - Volte à notícia e veja o comentário publicado

### 📊 Contador de Visualizações

1. Acesse uma notícia
2. Veja o número de visualizações
3. Recarregue a página (F5)
4. O número deve aumentar em 1

### 🔖 Tags

1. Em uma notícia, clique em uma tag
2. Deve mostrar todas as notícias com aquela tag

### 🔗 Compartilhamento

1. Em uma notícia, clique nos botões de compartilhamento
2. Facebook: deve abrir janela do Facebook
3. Twitter: deve abrir janela do Twitter
4. WhatsApp: deve abrir WhatsApp Web

---

## ⚡ TESTE DE PERFORMANCE

### JavaScript funcionando:

**Relógio na Info Bar:**
- Deve atualizar a cada segundo

**Botão "Voltar ao Topo":**
- Scroll para baixo
- Botão deve aparecer
- Clique nele
- Deve voltar ao topo suavemente

**Mensagens de Alerta:**
- Devem fechar automaticamente após 5 segundos
- Ou ao clicar no X

---

## 📱 URLs RÁPIDAS PARA COPIAR E COLAR

```
# Homepage
http://127.0.0.1:8000/

# Todas as notícias
http://127.0.0.1:8000/noticias/

# Categorias
http://127.0.0.1:8000/noticias/categoria/economia/
http://127.0.0.1:8000/noticias/categoria/esportes/
http://127.0.0.1:8000/noticias/categoria/tecnologia/

# Busca
http://127.0.0.1:8000/noticias/buscar/?q=brasil

# Admin
http://127.0.0.1:8000/admin/
```

---

## 🐛 PROBLEMAS COMUNS

### Servidor não está rodando?
```bash
python manage.py runserver
```

### Página em branco?
1. Verifique o terminal por erros
2. Verifique se executou as migrations:
   ```bash
   python manage.py migrate
   ```

### Sem dados?
```bash
python populate_db.py
```

### CSS não carrega?
```bash
python manage.py collectstatic --noinput
```

---

## ✅ CHECKLIST FINAL

- [ ] Homepage carrega com notícias
- [ ] Lista de notícias funciona
- [ ] Detalhe da notícia mostra tudo
- [ ] Categorias filtram corretamente
- [ ] Busca encontra notícias
- [ ] Admin está acessível
- [ ] Pode criar/editar notícias no admin
- [ ] Comentários funcionam
- [ ] Design responsivo funciona
- [ ] JavaScript funciona (relógio, botão voltar ao topo)
- [ ] Compartilhamento social funciona

---

## 🎉 TUDO FUNCIONANDO?

**Próximos passos:**
1. Personalizar o CSS em `static/css/variables.css`
2. Adicionar seu logo em "Site Configuration" no admin
3. Adicionar imagens às notícias
4. Criar mais categorias e notícias
5. Configurar emails e redes sociais

**Divirta-se! 🚀**
