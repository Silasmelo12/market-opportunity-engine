#!/usr/bin/env python3
"""
Script para testar a conexão com o bot do Telegram.
Uso:
    python scripts/test_telegram_connection.py            # Valida as chaves no .env
    python scripts/test_telegram_connection.py --post     # Envia uma mensagem real de teste no Telegram
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.integrations.telegram_publisher import TelegramPublisher


def main():
    parser = argparse.ArgumentParser(description="Testa conexão com o Telegram")
    parser.add_argument(
        "--post",
        action="store_true",
        help="Envia uma mensagem real de teste no Telegram",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("🤖 Diagnóstico de Conexão com o Telegram")
    print("=" * 60)

    publisher = TelegramPublisher()

    try:
        publisher.validate_credentials()
        print("✅ Credenciais do Telegram encontradas no .env!")
        print(f"  • Bot Token: {publisher.bot_token[:10]}...{publisher.bot_token[-4:]}")
        print(f"  • Chat ID: {publisher.chat_id}")
    except ValueError as e:
        print(f"\n❌ {e}")
        print("\nComo resolver:")
        print("1. Abra o arquivo .env.")
        print("2. Adicione TELEGRAM_BOT_TOKEN=... e TELEGRAM_CHAT_ID=...")
        sys.exit(1)

    if not args.post:
        print("\n💡 Credenciais validadas localmente!")
        print("Para enviar uma mensagem real de teste para o seu Telegram, execute:")
        print("   python scripts/test_telegram_connection.py --post")
        print("=" * 60)
        return

    print("\n🚀 Enviando mensagem de teste para o Telegram...")
    msg = (
        "🤖 <b>Teste de Conexão do Market Opportunity Engine</b>\n\n"
        "Se você está lendo isso, a integração com o Telegram está <b>100% ativa e funcionando!</b> 🎉\n\n"
        "<i>Pronto para emitir os alertas diários de mercado.</i>"
    )

    try:
        res = publisher.send_message(msg)
        print("🎉 Mensagem enviada com sucesso!")
        print(f"  • Mensagem ID: {res['message_id']}")
        print(f"  • Chat: {res['chat_title']}")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Falha no envio: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
