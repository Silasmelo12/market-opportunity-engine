"""
Módulo de integração com a API de Bots do Telegram.
Utiliza httpx (100% nativo e assíncrono/síncrono, sem dependências externas adicionais).
"""

import os
import html
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

CATEGORY_ICONS = {
    "Ações Brasil": "🇧🇷 Ações B3",
    "FIIs Brasil": "🏢 FIIs Brasil",
    "BDRs": "🌎 BDRs Globais",
    "Ações EUA": "🇺🇸 Ações EUA",
    "Commodities": "⛏️ Commodities",
    "Forex": "💱 Câmbio / FX",
    "Criptomoedas": "🪙 Criptomoedas",
}


class TelegramPublisher:
    """Gerencia autenticação e envio de mensagens e relatórios para o Telegram."""

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
    ):
        self.bot_token = bot_token if bot_token is not None else os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id if chat_id is not None else os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else ""

    def validate_credentials(self) -> None:
        """Verifica se o token e o chat_id foram configurados."""
        missing = []
        if not self.bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not self.chat_id:
            missing.append("TELEGRAM_CHAT_ID")

        if missing:
            raise ValueError(
                f"Credenciais do Telegram ausentes no .env: {', '.join(missing)}"
            )

    def send_message(self, text: str, parse_mode: str = "HTML") -> Dict[str, Any]:
        """
        Envia uma mensagem de texto (com formatação HTML ou Markdown) para o chat ou canal.
        """
        self.validate_credentials()
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }

        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, json=payload)
            data = response.json()

            if not data.get("ok"):
                error_desc = data.get("description", "Erro desconhecido")
                raise RuntimeError(f"Erro na API do Telegram ({data.get('error_code')}): {error_desc}")

            return {
                "success": True,
                "message_id": data["result"]["message_id"],
                "chat_title": data["result"]["chat"].get("title", data["result"]["chat"].get("first_name", "")),
            }

    @staticmethod
    def format_opportunities_html(
        opportunities: List[Dict[str, Any]],
        date_str: Optional[str] = None,
        max_items: int = 8,
    ) -> str:
        """
        Formata as oportunidades em uma mensagem visual elegante com tags HTML para o Telegram,
        com suporte multi-mercado (B3, FIIs, BDRs, EUA, Cripto, Commodities, FX).
        """
        if not date_str:
            date_str = datetime.now().strftime("%d/%m/%Y")

        lines = [
            f"⚡ <b>SINAIS DE COMPRA DISPARADOS HOJE • {date_str}</b>",
            "<i>Varredura completa em todos os ativos do sistema (B3, FIIs, BDRs, EUA & Cripto):</i>\n",
        ]

        for i, opp in enumerate(opportunities[:max_items], 1):
            raw_ticker = opp.get("ticker", "").strip()
            clean_ticker = raw_ticker.replace(".SA", "")
            ticker = html.escape(clean_ticker)
            category = opp.get("category", "")
            cat_badge = CATEGORY_ICONS.get(category, category)

            price = opp.get("current_price", 0.0)
            win_rate = opp.get("historical_win_rate", 0.0)
            timing = html.escape(opp.get("timing_label", "Zona de Compra").strip())
            strategy = html.escape(opp.get("strategy", "Estatística").strip())

            # Formatação de moeda adaptativa
            if category in ("Ações Brasil", "FIIs Brasil", "BDRs") or not category or ".SA" in raw_ticker:
                price_str = f"R$ {price:.2f}"
            elif category == "Forex":
                price_str = f"{price:.4f}"
            elif category == "Criptomoedas":
                price_str = f"US$ {price:,.2f}" if price >= 1.0 else f"US$ {price:.4f}"
            else:
                price_str = f"US$ {price:.2f}"

            lines.append(f"<b>{i}. #{ticker}</b> • <i>{html.escape(cat_badge)}</i>")
            lines.append(f"   💰 Preço: <code>{price_str}</code>")
            lines.append(f"   🎯 Win Rate Histórico: <b>{win_rate:.1f}%</b>")
            lines.append(f"   📍 Status: <b>{timing}</b>")
            lines.append(f"   ⚙️ Setup de Hoje: <i>{strategy}</i>\n")

        lines.append("─────────────────────")
        lines.append("⚠️ <b>Aviso Regulatório:</b>")
        lines.append("<i>Estudo quantitativo automatizado com base em modelos matemáticos. Não constitui recomendação de investimento ou compra.</i>")

        return "\n".join(lines)
