"""
Módulo de integração com a API do X (antigo Twitter) para postagens autônomas.
Utiliza Tweepy com autenticação OAuth 1.0a User Context (API v2).
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import tweepy
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env local se existir
load_dotenv()


class XPublisher:
    """Gerencia autenticação e publicação de tweets no X."""

    def __init__(
        self,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
    ):
        self.consumer_key = (
            consumer_key
            if consumer_key is not None
            else (os.getenv("X_CONSUMER_KEY") or os.getenv("X_API_KEY"))
        )
        self.consumer_secret = (
            consumer_secret
            if consumer_secret is not None
            else (os.getenv("X_CONSUMER_SECRET") or os.getenv("X_API_SECRET"))
        )
        self.access_token = (
            access_token
            if access_token is not None
            else os.getenv("X_ACCESS_TOKEN")
        )
        self.access_token_secret = (
            access_token_secret
            if access_token_secret is not None
            else os.getenv("X_ACCESS_TOKEN_SECRET")
        )

        self._client: Optional[tweepy.Client] = None

    def validate_credentials(self) -> None:
        """Verifica se todas as 4 credenciais essenciais foram fornecidas."""
        missing = []
        if not self.consumer_key:
            missing.append("X_CONSUMER_KEY / X_API_KEY")
        if not self.consumer_secret:
            missing.append("X_CONSUMER_SECRET / X_API_SECRET")
        if not self.access_token:
            missing.append("X_ACCESS_TOKEN")
        if not self.access_token_secret:
            missing.append("X_ACCESS_TOKEN_SECRET")

        if missing:
            raise ValueError(
                f"Credenciais do X incompletas. Faltando no .env: {', '.join(missing)}"
            )

    @property
    def client(self) -> tweepy.Client:
        """Retorna instância autenticada do cliente v2 da API do X."""
        if self._client is None:
            self.validate_credentials()
            self._client = tweepy.Client(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
            )
        return self._client

    def post_tweet(self, text: str) -> Dict[str, Any]:
        """
        Publica um novo tweet na conta vinculada.
        
        Args:
            text: Conteúdo textual do tweet (até 280 caracteres).
            
        Returns:
            Dict com 'id', 'text' e status.
        """
        if not text or not text.strip():
            raise ValueError("O conteúdo do tweet não pode ser vazio.")

        if len(text) > 280:
            raise ValueError(
                f"O tweet ultrapassa o limite de 280 caracteres (comprimento atual: {len(text)})."
            )

        try:
            response = self.client.create_tweet(text=text)
            tweet_id = response.data["id"]
            return {
                "success": True,
                "tweet_id": tweet_id,
                "url": f"https://x.com/i/web/status/{tweet_id}",
                "text": text,
            }
        except tweepy.errors.Forbidden as e:
            raise PermissionError(
                "Erro de permissão do X (403 Forbidden). Verifique se o seu App no X Developer Portal "
                "está configurado com permissão 'Read and Write' e se os Access Tokens foram gerados "
                "APÓS essa alteração de permissão."
            ) from e
        except tweepy.errors.TweepyException as e:
            raise RuntimeError(f"Falha ao publicar tweet no X: {e}") from e

    @staticmethod
    def format_opportunities_tweet(
        opportunities: List[Dict[str, Any]],
        date_str: Optional[str] = None,
        max_items: int = 3,
    ) -> str:
        """
        Formata uma lista de oportunidades do Radar em um tweet conciso (< 280 caracteres).
        
        Args:
            opportunities: Lista de dicionários com 'ticker', 'current_price', 'historical_win_rate', etc.
            date_str: Data formatada (opcional, padrão: data atual dd/mm).
            max_items: Quantidade máxima de ativos para incluir no tweet (padrão: 3).
        """
        if not date_str:
            date_str = datetime.now().strftime("%d/%m")

        header = f"📊 Radar Quantitativo ({date_str})\n"
        header += "Oportunidades estatísticas identificadas pelo motor:\n\n"

        disclaimer = "\n\n⚠️ Estudo puramente quantitativo. Não é recomendação."

        # Monta os itens até o limite de caracteres
        items_text = []
        for opp in opportunities[:max_items]:
            ticker = opp.get("ticker", "").strip()
            price = opp.get("current_price", 0.0)
            win_rate = opp.get("historical_win_rate", 0.0)
            timing = opp.get("timing_label", "Zona de Compra")

            line = f"• ${ticker}: R$ {price:.2f} | Win Rate: {win_rate:.0f}% ({timing})"
            items_text.append(line)

        body = "\n".join(items_text)
        tweet = header + body + disclaimer

        # Ajuste de segurança caso ultrapasse 280 chars
        if len(tweet) > 280 and len(items_text) > 2:
            # Tenta com 2 itens
            body = "\n".join(items_text[:2])
            tweet = header + body + disclaimer

        if len(tweet) > 280:
            # Versão ultra-compacta
            compact_items = [
                f"• ${o.get('ticker')}: R$ {o.get('current_price', 0.0):.2f}"
                for o in opportunities[:max_items]
            ]
            tweet = f"📊 Radar Quantitativo ({date_str}):\n" + "\n".join(compact_items) + "\n\nEstudo quantitativo. Não é recomendação."

        return tweet
