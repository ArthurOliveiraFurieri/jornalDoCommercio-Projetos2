import os
import sys

# 1. ADICIONE O CAMINHO PARA O DIRETÓRIO DO SEU PROJETO
# Este é o diretório principal que contém o 'manage.py'
path = '/home/oliveira2307/jornalDoCommercio-Projetos2'
if path not in sys.path:
    sys.path.insert(0, path)

# 2. DEFINA A VARIÁVEL DE AMBIENTE PARA SEUS SETTINGS
# O formato é 'nome_da_pasta_de_configuracao.settings'
# Assumindo que seu arquivo está em:
# /home/oliveira2307/jornalDoCommercio-Projetos2/jornalDoCommercio/settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jornalDoCommercio.settings')

# 3. CARREGUE A APLICAÇÃO WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
