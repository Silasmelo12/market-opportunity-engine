#!/usr/bin/env python3
"""
Script de diagnóstico e teste de conexão com o X (Twitter).
Uso:
    python scripts/test_x_connection.py            # Apenas valida chaves locais
    python scripts/test_x_connection.py --post     # Envia um tweet real de teste
"""

import sys
import os
import argparse

# Garante que o diretório raiz do projeto esteja no sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.integrations.x_publisher import XPublisher


def main():
    parser = argparse.ArgumentParser(description="Testa conexão com a API do X")
    parser.add_argument(
        "--post",
        action="store_true",
        help="Publica um tweet de teste real se as credenciais forem válidas",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("🔍 Diagnóstico de Conexão com o X (Twitter API v2)")
    print("=" * 60)

    publisher = XPublisher()

    try:
        publisher.validate_credentials()
        print("✅ Todas as 4 variáveis de autenticação foram encontradas!")
        print(f"  • Consumer Key: {publisher.consumer_key[:6]}...{publisher.consumer_key[-4:]}")
        print(f"  • Access Token: {publisher.access_token[:8]}...{publisher.access_token[-4:]}")
    except ValueError as e:
        print(f"\n❌ Erro de Configuração: {e}")
        print("\nComo resolver:")
        print("1. Abra o arquivo .env na raiz do projeto.")
        print("2. Preencha as chaves: X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN e X_ACCESS_TOKEN_SECRET.")
        print("3. Consulte o arquivo .env.example para ver o modelo.")
        sys.exit(1)

    if not args.post:
        print("\n💡 Credenciais validadas localmente!")
        print("Para enviar um tweet real de teste para sua conta, execute:")
        print("   python scripts/test_x_connection.py --post")
        print("=" * 60)
        return

    print("\n🚀 Tentando publicar tweet de teste...")
    test_text = "🤖 Teste de integração do Market Opportunity Engine no X concluído com sucesso! #quant #b3"

    try:
        res = publisher.post_tweet(test_text)
        print("🎉 Tweet publicado com sucesso!")
        print(f"  • ID: {res['tweet_id']}")
        print(f"  • Link: {res['url']}")
        print("=" * 60)
    except PermissionError as e:
        print(f"\n❌ Erro 403 (Permissão): {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Falha na publicação: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
