# 📰 Jornal do Commercio - Portal Digital

Portal de notícias completo e moderno desenvolvido em Django 5.2 com arquitetura modular.

## 🚀 Características

### ✨ Funcionalidades Principais
- ✅ **Sistema de Notícias** completo com categorias e tags
- ✅ **Área Administrativa** personalizada com Django Admin
- ✅ **Sistema de Comentários** com moderação
- ✅ **Busca Avançada** de notícias
- ✅ **Design Responsivo** com CSS modular
- ✅ **JavaScript Modular** para interatividade
- ✅ **Upload de Imagens** para notícias
- ✅ **Sistema de Autenticação** integrado

### 🏗️ Arquitetura

```
jornalDoCommercio-Projetos2/
├── apps/
│   ├── core/          # Configurações gerais e homepage
│   ├── news/          # Sistema de notícias
│   ├── live/          # Transmissões ao vivo
│   └── advertising/   # Sistema de publicidade
├── templates/
│   ├── base/          # Templates base
│   ├── components/    # Componentes reutilizáveis
│   ├── pages/         # Páginas principais
│   └── news/          # Templates de notícias
├── static/
│   ├── css/           # Estilos organizados em camadas
│   ├── js/            # JavaScript modular
│   └── images/        # Imagens do site
└── media/             # Uploads de usuários
```

## 📋 Requisitos

- Python 3.11+
- Django 5.2.6
- Pillow 11.3.0 (para processamento de imagens)

## 🔧 Instalação

### 1️⃣ Clone o repositório

```bash
git clone <url-do-repositorio>
cd jornalDoCommercio-Projetos2
```

### 2️⃣ Crie um ambiente virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3️⃣ Instale as dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Execute as migrações

```bash
python manage.py migrate
```

### 5️⃣ Crie um superusuário (se necessário)

```bash
python manage.py createsuperuser
```

### 6️⃣ Popule o banco com dados de exemplo

```bash
python populate_db.py
```

### 7️⃣ Execute o servidor

```bash
python manage.py runserver
```

Acesse em: **http://127.0.0.1:8000**

## 🎨 Estrutura CSS

O CSS está organizado em camadas para melhor manutenção:

1. **variables.css** - Variáveis CSS (cores, fontes, espaçamentos)
2. **reset.css** - Reset de estilos padrão do navegador
3. **main.css** - Estilos principais e layout
4. **components.css** - Componentes específicos (header, footer, cards)
5. **responsive.css** - Estilos responsivos para mobile

## 🔌 Apps

### Core
Gerencia configurações gerais do site, menu e homepage.

**Models:**
- `SiteConfiguration` - Configurações do site
- `Menu` - Itens do menu principal

### News
Sistema completo de notícias.

**Models:**
- `Category` - Categorias de notícias
- `Tag` - Tags para classificação
- `News` - Notícias
- `Comment` - Comentários nas notícias

**Features:**
- Listagem de notícias
- Visualização detalhada
- Filtros por categoria e tag
- Sistema de busca
- Comentários com moderação
- Contador de visualizações

### Live
Sistema para transmissões ao vivo.

**Models:**
- `LiveEvent` - Eventos ao vivo

### Advertising
Sistema de gerenciamento de anúncios.

**Models:**
- `Advertisement` - Anúncios publicitários

## 👨‍💼 Admin

Acesse o painel administrativo em: **http://127.0.0.1:8000/admin**

**Funcionalidades:**
- Gerenciamento completo de notícias
- Moderação de comentários
- Gerenciamento de categorias e tags
- Configurações do site
- Gerenciamento de anúncios

## 🎯 URLs Principais

- `/` - Homepage
- `/noticias/` - Lista de todas as notícias
- `/noticias/<slug>/` - Detalhes de uma notícia
- `/noticias/categoria/<slug>/` - Notícias por categoria
- `/noticias/tag/<slug>/` - Notícias por tag
- `/noticias/buscar/?q=termo` - Busca de notícias
- `/admin/` - Painel administrativo

## 📱 Responsividade

O site é totalmente responsivo com breakpoints:
- Desktop: 1024px+
- Tablet: 768px - 1023px
- Mobile: até 767px

## 🔐 Autenticação

- Login de usuários via Django Admin
- Sistema de permissões integrado
- Comentários apenas para usuários autenticados

## 🛠️ Desenvolvimento

### Estrutura de Código

**Views:**
- Class-based views (ListView, DetailView)
- Function-based views para ações específicas

**Templates:**
- Herança de templates
- Componentização
- Template tags do Django

**JavaScript:**
- Organização modular
- Funções utilitárias separadas
- Componentes específicos

### Boas Práticas

- ✅ Código PEP 8 compliant
- ✅ Models com validações
- ✅ Views otimizadas com select_related
- ✅ Templates componentizados
- ✅ CSS organizado em camadas
- ✅ JavaScript modular

## 📝 Próximos Passos

- [ ] Implementar sistema de newsletter
- [ ] Adicionar RSS feeds
- [ ] Implementar cache com Redis
- [ ] Criar API REST com DRF
- [ ] Adicionar testes automatizados
- [ ] Implementar sistema de notificações
- [ ] Adicionar analytics
- [ ] Melhorar SEO

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 👥 Autores

- **Desenvolvedor Principal** - Implementação inicial

## 🙏 Agradecimentos

- Django Framework
- Font Awesome para ícones
- Comunidade Django Brasil

---

**Desenvolvido com ❤️ usando Django**
