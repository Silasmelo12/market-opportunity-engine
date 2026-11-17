#!/usr/bin/env python3
"""
Script autônomo para escanear oportunidades e publicar no Telegram (e/ou X).
FILTRO ESTRITO: Apenas sinais gerados/confirmados no pregão de HOJE.
UNIVERSO COMPLETO: Rastreia absolutamente TODOS os ativos do sistema (194+ ativos:
Ações B3, FIIs, BDRs, Ações EUA, Commodities, Forex e Criptomoedas).

Uso:
    python scripts/publish_daily_radar.py                         # Simulação (dry-run, exibe no terminal)
    python scripts/publish_daily_radar.py --post --telegram       # Publica no Telegram
    python scripts/publish_daily_radar.py --refresh               # Força download das cotações mais recentes
    python scripts/publish_daily_radar.py --limit 8               # Limita aos Top 8 sinais
"""

import sys
import os
import argparse
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

# Garante raiz do projeto no path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.integrations.telegram_publisher import TelegramPublisher
from src.integrations.x_publisher import XPublisher
from src.api.server import (
    _scan_single_ticker,
    DEFAULT_SCANNER_BASKET,
    TICKERS_BR_ACOES,
    TICKERS_FIIS,
    TICKERS_BDRS,
    TICKERS_USA,
    TICKERS_COMMODITIES,
    TICKERS_FX,
    TICKERS_CRYPTO,
)


def resolve_basket(category_filter: str = "all") -> List[tuple]:
    """Retorna o universo de ativos baseado no filtro solicitado."""
    c = category_filter.lower().strip()
    if c in ("acoes_br", "acoes", "b3"):
        return [(t, "Ações Brasil") for t in TICKERS_BR_ACOES]
    if c in ("fiis", "fii"):
        return [(t, "FIIs Brasil") for t in TICKERS_FIIS]
    if c in ("bdrs", "bdr"):
        return [(t, "BDRs") for t in TICKERS_BDRS]
    if c in ("usa", "eua"):
        return [(t, "Ações EUA") for t in TICKERS_USA]
    if c in ("commodities", "commodity"):
        return [(t, "Commodities") for t in TICKERS_COMMODITIES]
    if c in ("fx", "forex"):
        return [(t, "Forex") for t in TICKERS_FX]
    if c in ("crypto", "cripto"):
        return [(t, "Criptomoedas") for t in TICKERS_CRYPTO]

    # Padrão: ABSOLUTAMENTE TODOS OS ATIVOS (194 ativos)
    return DEFAULT_SCANNER_BASKET


def find_today_opportunities(
    category_filter: str = "all",
    max_count: int = 8,
    min_win_rate: float = 60.0,
    refresh: bool = False,
    max_workers: int = 10,
) -> List[Dict[str, Any]]:
    """
    Executa a varredura em paralelo em todo o universo de ativos cadastrados no sistema
    e extrai ESTRITAMENTE os sinais de COMPRA que foram disparados no pregão de HOJE.
    """
    basket = resolve_basket(category_filter)
    print(f"🔎 Varrendo {len(basket)} ativos do sistema em paralelo (Mercado: {category_filter.upper()}, refresh={refresh})...")

    def _scan_worker(item):
        ticker, cat = item
        try:
            return _scan_single_ticker(ticker, cat, interval="1d", horizon_x=60, refresh=refresh)
        except Exception:
            return []

    all_radar_items = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for items in executor.map(_scan_worker, basket):
            all_radar_items.extend(items)

    best_by_ticker: Dict[str, Dict[str, Any]] = {}

    for it in all_radar_items:
        # Pula índices macro que não são ativos diretamente negociáveis (ex: ^BVSP)
        if it.ticker.startswith("^"):
            continue

        # REGRA CRUCIAL: Apenas sinal formado na barra de HOJE
        is_today_signal = it.status_signal in ("Formado na Barra", "Executado Hoje")

        if it.direction == "BUY" and is_today_signal and it.historical_win_rate >= min_win_rate:
            clean_ticker = it.ticker.replace(".SA", "")
            current_best = best_by_ticker.get(clean_ticker)

            # Se o mesmo ativo gerou mais de uma estratégia hoje, seleciona a com maior Win Rate
            if current_best is None or it.historical_win_rate > current_best["historical_win_rate"]:
                best_by_ticker[clean_ticker] = {
                    "ticker": it.ticker,
                    "category": it.category,
                    "current_price": it.current_price,
                    "historical_win_rate": it.historical_win_rate,
                    "timing_label": it.timing_label,
                    "strategy": it.strategy_label,
                    "status_signal": it.status_signal,
                    "distance_pct": it.distance_pct,
                }

    # Ordena pelo maior Win Rate histórico (e menor distância em caso de empate)
    sorted_opps = sorted(
        best_by_ticker.values(),
        key=lambda x: (x["historical_win_rate"], -abs(x.get("distance_pct", 0.0))),
        reverse=True,
    )
    return sorted_opps[:max_count]


def main():
    parser = argparse.ArgumentParser(description="Publica sinais quantitativos de HOJE de todo o sistema")
    parser.add_argument(
        "--post",
        action="store_true",
        help="Publica de verdade. Sem este argumento, roda apenas simulação (dry-run).",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Força download das cotações mais recentes do pregão de hoje.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=8,
        help="Quantidade máxima de sinais no relatório (Padrão: 8).",
    )
    parser.add_argument(
        "--category",
        type=str,
        default="all",
        help="Filtrar por categoria (all, acoes_br, fiis, bdrs, usa, commodities, fx, crypto). Padrão: all (todos).",
    )
    parser.add_argument(
        "--min-win-rate",
        type=float,
        default=60.0,
        help="Taxa de acerto mínima histórica (Padrão: 60%%).",
    )
    parser.add_argument(
        "--telegram",
        action="store_true",
        default=True,
        help="Publica no Telegram (Padrão: True).",
    )
    parser.add_argument(
        "--x",
        action="store_true",
        help="Publica também no X.",
    )
    args = parser.parse_args()

    today_str = datetime.now().strftime("%d/%m/%Y")
    print("=" * 60)
    print(f"🤖 Market Opportunity Engine • MULTI-MERCADO TOTAL ({today_str})")
    print("=" * 60)

    # 1. Encontra sinais exclusivamente de HOJE varrendo todo o universo
    today_opps = find_today_opportunities(
        category_filter=args.category,
        max_count=args.limit,
        min_win_rate=args.min_win_rate,
        refresh=args.refresh,
    )

    if not today_opps:
        print(f"\nℹ️ Nenhum sinal de compra com Win Rate >= {args.min_win_rate:.0f}% foi disparado no pregão de hoje ({today_str}).")
        print("Nenhuma recomendação/post forçado será emitido.")
        print("=" * 60)
        return

    print(f"\n🎯 Foram encontrados {len(today_opps)} sinais de compra disparados HOJE entre todos os ativos:")

    # 2. Formata a mensagem para o Telegram
    telegram_pub = TelegramPublisher()
    telegram_msg = telegram_pub.format_opportunities_html(today_opps, date_str=today_str, max_items=args.limit)

    print("\n📱 Prévia da mensagem para o Telegram:")
    print("-" * 50)
    print(telegram_msg)
    print("-" * 50)

    # 3. Modo Dry-Run vs Envio Real
    if not args.post:
        print("\n💡 Modo DRY-RUN (simulação). Nenhuma mensagem foi enviada.")
        print("Para enviar de verdade para o Telegram, execute:")
        print("   python scripts/publish_daily_radar.py --post --telegram")
        print("=" * 60)
        return

    if args.telegram:
        print("\n🚀 Enviando para o Telegram...")
        try:
            res = telegram_pub.send_message(telegram_msg)
            print(f"✅ Telegram: Mensagem enviada com sucesso para '{res['chat_title']}' (ID: {res['message_id']})")
        except Exception as e:
            print(f"❌ Telegram erro: {e}")

    if args.x:
        print("\n🚀 Enviando para o X...")
        try:
            x_pub = XPublisher()
            x_text = x_pub.format_opportunities_tweet(today_opps, max_items=3)
            res = x_pub.post_tweet(x_text)
            print(f"✅ X: Post publicado com sucesso! {res['url']}")
        except Exception as e:
            print(f"❌ X erro: {e}")

    print("=" * 60)


if __name__ == "__main__":
    main()
