#!/usr/bin/env python
"""
Script para popular o banco de dados com dados de exemplo
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jornalDoCommercio.settings')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import SiteConfiguration, Menu
from apps.news.models import Category, Tag, News
from django.utils import timezone


def populate():
    print("Populando banco de dados com dados de exemplo...")

    # 1. Configuração do Site
    print("1. Criando configuração do site...")
    site_config, created = SiteConfiguration.objects.get_or_create(
        pk=1,
        defaults={
            'site_name': 'Jornal do Commercio',
            'site_description': 'Portal de notícias completo e moderno',
            'contact_email': 'contato@jornaldocommercio.com',
            'contact_phone': '(11) 1234-5678',
        }
    )
    print(f"   {'Criado' if created else 'Já existe'}: {site_config.site_name}")

    # 2. Menu Items
    print("\n2. Criando itens do menu...")
    menu_items = [
        {'title': 'Sobre', 'url': '/sobre/', 'order': 1},
        {'title': 'Contato', 'url': '/contato/', 'order': 2},
        {'title': 'Assine', 'url': '/assine/', 'order': 3},
    ]
    for item_data in menu_items:
        item, created = Menu.objects.get_or_create(
            title=item_data['title'],
            defaults=item_data
        )
        print(f"   {'Criado' if created else 'Já existe'}: {item.title}")

    # 3. Categorias
    print("\n3. Criando categorias...")
    categories_data = [
        {'name': 'Política', 'description': 'Notícias sobre política nacional e internacional', 'order': 1},
        {'name': 'Economia', 'description': 'Economia, negócios e mercado financeiro', 'order': 2},
        {'name': 'Esportes', 'description': 'O melhor do esporte nacional e mundial', 'order': 3},
        {'name': 'Tecnologia', 'description': 'Inovação, gadgets e tecnologia', 'order': 4},
        {'name': 'Cultura', 'description': 'Arte, música, cinema e entretenimento', 'order': 5},
        {'name': 'Saúde', 'description': 'Saúde, bem-estar e medicina', 'order': 6},
    ]
    categories = {}
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories[cat.name] = cat
        print(f"   {'Criada' if created else 'Já existe'}: {cat.name}")

    # 4. Tags
    print("\n4. Criando tags...")
    tags_data = ['Brasil', 'Internacional', 'Urgente', 'Análise', 'Entrevista', 'Especial']
    tags = {}
    for tag_name in tags_data:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        tags[tag_name] = tag
        print(f"   {'Criada' if created else 'Já existe'}: {tag.name}")

    # 5. Obter usuário para autor
    print("\n5. Obtendo usuário para autor...")
    try:
        author = User.objects.filter(is_staff=True).first()
        if not author:
            author = User.objects.first()
        print(f"   Autor: {author.username}")
    except:
        print("   ERRO: Nenhum usuário encontrado!")
        return

    # 6. Notícias
    print("\n6. Criando notícias de exemplo...")
    news_data = [
        {
            'title': 'Nova reforma econômica é aprovada no Congresso',
            'excerpt': 'Após meses de debate, projeto que modifica regras fiscais é aprovado por ampla maioria.',
            'content': '''A nova reforma econômica foi aprovada hoje no Congresso Nacional com ampla maioria de votos.

            O projeto, que vinha sendo debatido há meses, traz mudanças significativas nas regras fiscais do país e promete impactar positivamente a economia nos próximos anos.

            Entre as principais mudanças estão a simplificação tributária, novos incentivos para empresas e medidas de controle de gastos públicos. Economistas preveem que as mudanças podem gerar até 2 milhões de novos empregos nos próximos 3 anos.

            A reforma entra em vigor a partir do próximo ano fiscal.''',
            'category': categories['Economia'],
            'tags': [tags['Brasil'], tags['Urgente']],
            'is_featured': True,
        },
        {
            'title': 'Seleção Brasileira vence amistoso por 3 a 1',
            'excerpt': 'Em jogo emocionante, Brasil domina adversário e conquista importante vitória.',
            'content': '''A Seleção Brasileira conquistou uma importante vitória no amistoso internacional disputado nesta noite.

            Com gols de três jogadores diferentes, o time brasileiro mostrou entrosamento e dominou o jogo do início ao fim. O técnico elogiou a atuação dos atletas e destacou a importância da preparação para os próximos desafios.

            O próximo jogo da seleção está marcado para daqui a duas semanas.''',
            'category': categories['Esportes'],
            'tags': [tags['Brasil'], tags['Especial']],
            'is_featured': True,
        },
        {
            'title': 'Novas tecnologias prometem revolucionar o mercado',
            'excerpt': 'Inteligência Artificial e computação quântica lideram inovações do setor.',
            'content': '''O setor de tecnologia está passando por uma revolução sem precedentes, com o avanço da Inteligência Artificial e da computação quântica.

            Especialistas afirmam que essas tecnologias irão transformar completamente a forma como vivemos e trabalhamos nos próximos anos. Empresas do mundo todo já estão investindo bilhões nessas áreas.

            As aplicações vão desde medicina de precisão até automação industrial avançada.''',
            'category': categories['Tecnologia'],
            'tags': [tags['Internacional'], tags['Análise']],
            'is_featured': True,
        },
        {
            'title': 'Festival de Cinema reúne grandes produções nacionais',
            'excerpt': 'Evento cultural traz o melhor do cinema brasileiro para as telas.',
            'content': '''O tradicional Festival de Cinema Brasileiro começa hoje com uma programação repleta de grandes produções nacionais.

            Durante uma semana, o público poderá conferir filmes inéditos, participar de debates com cineastas e prestigiar a cerimônia de premiação. Este ano, mais de 100 filmes foram inscritos nas diversas categorias.

            O festival é considerado um dos mais importantes da América Latina.''',
            'category': categories['Cultura'],
            'tags': [tags['Brasil'], tags['Especial']],
            'is_featured': False,
        },
        {
            'title': 'Pesquisa revela novos avanços no tratamento de doenças',
            'excerpt': 'Estudo científico apresenta resultados promissores na área médica.',
            'content': '''Uma pesquisa recente apresentou resultados promissores para o tratamento de diversas doenças.

            Os cientistas responsáveis pelo estudo afirmam que a nova abordagem pode revolucionar a medicina moderna. Os testes clínicos já começaram e os primeiros resultados são animadores.

            A pesquisa foi publicada em renomadas revistas científicas internacionais.''',
            'category': categories['Saúde'],
            'tags': [tags['Internacional'], tags['Análise']],
            'is_featured': False,
        },
        {
            'title': 'Governo anuncia novo plano de infraestrutura',
            'excerpt': 'Investimentos previstos superam R$ 100 bilhões em obras pelo país.',
            'content': '''O governo federal anunciou hoje um ambicioso plano de infraestrutura que prevê investimentos de mais de R$ 100 bilhões em obras pelo país.

            O plano inclui construção e modernização de rodovias, ferrovias, portos e aeroportos. A previsão é que as obras gerem milhares de empregos e impulsionem o crescimento econômico nas regiões beneficiadas.

            As primeiras licitações devem ser lançadas ainda este semestre.''',
            'category': categories['Política'],
            'tags': [tags['Brasil'], tags['Urgente']],
            'is_featured': False,
        },
    ]

    for news_item in news_data:
        tags_list = news_item.pop('tags')
        news, created = News.objects.get_or_create(
            title=news_item['title'],
            defaults={
                **news_item,
                'author': author,
                'is_published': True,
                'published_at': timezone.now(),
            }
        )
        if created:
            news.tags.set(tags_list)
        print(f"   {'Criada' if created else 'Já existe'}: {news.title}")

    print("\n✅ Banco de dados populado com sucesso!")
    print("\n📊 Resumo:")
    print(f"   - Categorias: {Category.objects.count()}")
    print(f"   - Tags: {Tag.objects.count()}")
    print(f"   - Notícias: {News.objects.count()}")
    print(f"   - Notícias em destaque: {News.objects.filter(is_featured=True).count()}")


if __name__ == '__main__':
    populate()
