import requests
from django.utils import timezone
from jornal_app.models import Noticia, Categoria

# 1. FUNÇÃO DE BUSCA NA API (PLANO B: Usando /everything)
def fetch_news_from_api():
    API_KEY = "387de40a5e9c49daafa9d5331e1f35c6" # Sua key
    
    # --- MUDANÇA DRÁSTICA AQUI ---
    # Trocamos /top-headlines por /everything
    # Adicionamos o termo de busca (q='brasil') e mantemos language=pt
    # Adicionamos sortBy=publishedAt para pegar os mais novos
    url = (
        "https://newsapi.org/v2/everything?"
        "q=brasil&"
        "language=pt&"
        "sortBy=publishedAt&"
        "pageSize=30&"
        f"apiKey={API_KEY}"
    )
    
    try:
        print(f"📡 Conectando com NewsAPI (PLANO B: /everything?q=brasil&language=pt)...")
        print(f"🔗 URL: {url}")
        response = requests.get(url)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            print(f"✅ API: {len(articles)} artigos recebidos sobre 'Brasil' em PT")
            return articles
        else:
            print(f"❌ Erro na API: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"💥 Erro de conexão: {e}")
        return []

# 2. FUNÇÃO DE IMPORTAÇÃO (Exatamente como antes)
def importar_noticias_simples():
    print('🎯 INICIANDO IMPORTACAO DA NEWSAPI...')
    news_count = 0
    
    categoria_db, criada = Categoria.objects.get_or_create(nome='Geral')
    if criada:
        print(f"ℹ️ Categoria 'Geral' criada no banco.")

    # 1. Chama a API
    articles = fetch_news_from_api()
    
    if not articles:
        print(f"❌ Nenhuma notícia recebida.")
        return 0
        
    # 2. Salva as notícias
    for article in articles:
        if article is None:
            continue
            
        titulo = article.get('title')
        if not titulo:
            continue
            
        titulo = str(titulo)[:200] 
        
        conteudo = article.get('description') or article.get('content')
        if not conteudo:
            conteudo = "Conteúdo não disponível."
        else:
            conteudo = str(conteudo).split(' [+')[0]
        
        # Verifica se já existe
        if Noticia.objects.filter(titulo__icontains=titulo[:50]).exists():
            print(f'⏭️ JÁ EXISTE: {titulo[:50]}...')
            continue
        
        # Cria nova notícia
        try:
            noticia = Noticia(
                titulo=titulo,
                conteudo=conteudo,
                categoria=categoria_db, 
            )
            noticia.save()
            news_count += 1
            print(f'✅ NOVA NOTÍCIA SALVA (Geral): {titulo[:50]}...')
        except Exception as e:
            print(f'❌ ERRO AO SALVAR ({titulo[:50]}...): {e}')
            continue
    
    print(f'🎯 CONCLUÍDO: {news_count} notícias novas da NewsAPI')
    return news_count