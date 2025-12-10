"""
🚀 EXECUTAR TESTES E2E NO SITE DE PRODUÇÃO
==========================================

Este script executa os testes E2E no site deployado no Railway
com o navegador VISÍVEL para acompanhar os testes em tempo real.

Uso:
    python executar_testes_producao.py
"""

import subprocess
import sys

def main():
    print("\n" + "="*70)
    print("🎯 TESTES E2E - SITE DE PRODUÇÃO (RAILWAY)")
    print("="*70)
    print("\n📋 O que será testado:")
    print("  1. ✅ Carregamento da Homepage")
    print("  2. 🔍 Sistema de Busca")
    print("  3. 📰 Leitura de Notícia")
    print("  4. 📝 Página de Cadastro")
    print("  5. 🔐 Página de Login")
    print("  6. 📱 Responsividade (Desktop/Tablet/Mobile)")
    print("  7. 🎬 Jornada Completa do Usuário")
    
    print("\n⚠️  IMPORTANTE:")
    print("  • O navegador Chrome abrirá VISÍVEL")
    print("  • Você verá os testes acontecendo em tempo real")
    print("  • NÃO feche o navegador manualmente")
    print("  • O site precisa estar deployado no Railway")
    
    input("\n▶️  Pressione ENTER para começar os testes...")
    
    print("\n🚀 Executando testes...\n")
    
    # Executar testes de produção
    cmd = [
        sys.executable,
        "manage.py",
        "test",
        "jornal_app.tests.JornalProductionE2ETests",
        "--verbosity=2"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Testes concluídos com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Alguns testes falharam. Código de saída: {e.returncode}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
