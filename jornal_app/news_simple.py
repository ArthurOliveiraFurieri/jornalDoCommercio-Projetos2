import requests
from django.utils import timezone
from jornal_app.models import Noticia, Categoria

def fetch_news_from_api():
    API_KEY = "387de40a5e9c49daafa9d5331e1f35c6"  # ✅ Sua key
    
    # 🔄 TENTE DIFERENTES URLs:
    
    # Opção 1: Notícias internacionais em inglês
    # Busca 20 notícias em vez de 5
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=20&apiKey={API_KEY}"
    
    # Opção 2: Buscar por palavra-chave
    # url = f"https://newsapi.org/v2/everything?q=technology&language=en&pageSize=5&apiKey={API_KEY}"
    
    # Opção 3: Notícias dos EUA
    # url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize=5&apiKey={API_KEY}"
    
    try:
        print("📡 Conectando com NewsAPI...")
        print(f"🔗 URL: {url}")
        response = requests.get(url)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📦 Total de resultados: {data.get('totalResults', 0)}")
            
            articles = data.get('articles', [])
            print(f"✅ API: {len(articles)} notícias recebidas")
            
            # Mostra os títulos das notícias recebidas
            for i, article in enumerate(articles):
                title = article.get('title', 'Sem título')
                print(f"   {i+1}. {title}")
            
            return articles
        else:
            print(f"❌ Erro na API: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"💥 Erro de conexão: {e}")
        return []

def importar_noticias_simples():
    print('🎯 INICIANDO IMPORTACAO DA NEWSAPI...')
    
    categoria, _ = Categoria.objects.get_or_create(nome='Geral')
    news_count = 0
    
    articles = fetch_news_from_api()
    
    if not articles:
        print("❌ Nenhuma notícia recebida da API")
        return 0
    
    for article in articles:
        # ✅ VERIFICAÇÃO EXTRA: Garante que article não é None
        if article is None:
            print("⏭️ Pulando - artigo None")
            continue
            
        # ✅ VERIFICAÇÃO DUPLA: Garante que tem title
        titulo = article.get('title') if article else None
        if not titulo:
            print("⏭️ Pulando - sem título")
            continue
            
        titulo = str(titulo)[:200]  # Converte para string e limita
        
        conteudo = article.get('description') or article.get('content')
        if not conteudo:
            conteudo = "Conteúdo não disponível."
        else:
            conteudo = str(conteudo)
        
        # Verifica se já existe
        if Noticia.objects.filter(titulo__icontains=titulo[:50]).exists():
            print(f'⏭️ JÁ EXISTE: {titulo[:50]}...')
            continue
        
        # Cria nova notícia
        try:
            noticia = Noticia(
                titulo=titulo,
                conteudo=conteudo,
                categoria=categoria,
            )
            noticia.save()
            news_count += 1
            print(f'✅ NOVA NOTÍCIA SALVA: {titulo[:50]}...')
        except Exception as e:
            print(f'❌ ERRO AO SALVAR: {e}')
            continue
    
    print(f'🎯 CONCLUÍDO: {news_count} notícias novas da NewsAPI')
    return news_count