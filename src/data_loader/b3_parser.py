"""
B3 Official Movement Spreadsheet Parser and Tax Average Buy Price (Preço Médio) Engine.
Processes official .xlsx and .csv files from B3 Investor Portal.
Calculates chronological weighted average buy price (PM), net custody holdings,
and segregates passive income (Dividends, JCP, Rendimentos).
"""

import os
import io
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np

from ..api.schemas import B3MovementRecord, B3Holding, B3MonthlyIncome, B3ParseResult


def _normalize_str(text: Any) -> str:
    """Removes accents, trims, and normalizes unicode characters."""
    if text is None or pd.isna(text):
        return ""
    s = str(text).strip()
    n = unicodedata.normalize("NFKD", s)
    return "".join(c for c in n if not unicodedata.combining(c)).strip()


def _classify_asset(clean_ticker: str) -> str:
    """Classifies asset into Ações Brasil, FIIs, BDRs, or Outros."""
    t = clean_ticker.upper()
    if t.endswith("34") or t.endswith("35") or t.endswith("39"):
        return "BDRs"
    if t.endswith("11"):
        return "FIIs"
    if any(t.endswith(sfx) for sfx in ("3", "4", "5", "6")):
        return "Ações Brasil"
    return "Outros"


def _clean_ticker_from_product(product_val: Any) -> Tuple[str, str, str]:
    """
    Extracts raw, clean and .SA ticker from the Produto column.
    Example: 'PETR4 - PETROLEO BRASILEIRO S/A PETROBRAS' -> ('PETR4', 'PETR4', 'PETR4.SA')
    """
    prod = str(product_val or "").strip()
    raw = prod.split("-")[0].strip().upper()
    clean = raw
    # If ticker is valid B3 format, append .SA
    sa = f"{clean}.SA" if clean and not clean.endswith(".SA") else clean
    return raw, clean, sa


def _parse_numeric(val: Any) -> float:
    """Safely converts numeric or formatted string (e.g. '1.250,50' or '-') to float."""
    if val is None or pd.isna(val):
        return 0.0
    if isinstance(val, (int, float, np.integer, np.floating)):
        return float(val) if not np.isnan(val) else 0.0
    s = str(val).strip()
    if not s or s == "-":
        return 0.0
    # Handle Brazilian number format '1.234,56' or standard '1234.56'
    if "," in s and "." in s:
        # Check positions to determine thousands vs decimal
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_b3_file(
    file_source: Union[str, Path, bytes, io.BytesIO],
    filename: str = "movimentacao.xlsx"
) -> B3ParseResult:
    """
    Parses a B3 movement file (Excel .xlsx or CSV) and computes:
    - Net custody holdings with chronological weighted average buy price
    - Consolidated passive income (Dividends, JCP, Rendimentos)
    - Monthly income aggregation
    """
    if isinstance(file_source, (str, Path)):
        file_path = Path(file_source)
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo B3 não encontrado: {file_path}")
        is_excel = file_path.suffix.lower() in (".xlsx", ".xls")
        if is_excel:
            df = pd.read_excel(file_path)
        else:
            try:
                df = pd.read_csv(file_path, sep=";", encoding="utf-8")
            except Exception:
                df = pd.read_csv(file_path, sep=",", encoding="latin1")
    else:
        # In-memory bytes or BytesIO
        stream = file_source if isinstance(file_source, io.BytesIO) else io.BytesIO(file_source)
        is_excel = filename.lower().endswith((".xlsx", ".xls"))
        if is_excel:
            df = pd.read_excel(stream)
        else:
            try:
                df = pd.read_csv(stream, sep=";", encoding="utf-8")
            except Exception:
                stream.seek(0)
                df = pd.read_csv(stream, sep=",", encoding="latin1")

    if df.empty:
        return B3ParseResult(
            filename=filename,
            total_movements=0,
            holdings=[],
            total_invested=0.0,
            total_income=0.0,
            monthly_income=[],
        )

    # Standardize column names
    col_mapping = {}
    for col in df.columns:
        norm = _normalize_str(col).lower()
        if "entrada" in norm or "saida" in norm:
            col_mapping[col] = "entrada_saida"
        elif norm == "data":
            col_mapping[col] = "data"
        elif "movimentacao" in norm or "movimento" in norm or "tipo" in norm:
            col_mapping[col] = "movimentacao"
        elif "produto" in norm or "ativo" in norm or "ticker" in norm:
            col_mapping[col] = "produto"
        elif "instituicao" in norm or "corretora" in norm:
            col_mapping[col] = "instituicao"
        elif "quantidade" in norm or "qtd" in norm:
            col_mapping[col] = "quantidade"
        elif "preco" in norm or "unitario" in norm:
            col_mapping[col] = "preco_unitario"
        elif "valor" in norm or "total" in norm:
            col_mapping[col] = "valor_operacao"

    df = df.rename(columns=col_mapping)

    required_cols = ["data", "movimentacao", "produto"]
    for rc in required_cols:
        if rc not in df.columns:
            raise ValueError(f"Coluna obrigatória '{rc}' ausente na planilha B3.")

    # Parse dates and numeric columns
    df["data_dt"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce")
    # In case of alternative ISO date formats
    if df["data_dt"].isna().all():
        df["data_dt"] = pd.to_datetime(df["data"], errors="coerce")

    # Sort strictly chronological ascending for tax Preço Médio calculation
    df = df.sort_values(by=["data_dt"], ascending=[True], na_position="first").reset_index(drop=True)

    holdings_dict: Dict[str, Dict[str, Any]] = {}
    total_dividends = 0.0
    total_jcp = 0.0
    total_rendimentos = 0.0
    monthly_map: Dict[str, Dict[str, float]] = {}

    total_movements = len(df)

    for _, row in df.iterrows():
        prod_val = row.get("produto")
        raw_ticker, clean_ticker, sa_ticker = _clean_ticker_from_product(prod_val)

        # Ignore futures (e.g. WIN, WDO) or records without product
        if not clean_ticker or clean_ticker.upper() == "FUTURO":
            continue

        mov_norm = _normalize_str(row.get("movimentacao", "")).lower()
        es_norm = _normalize_str(row.get("entrada_saida", "")).lower()

        qty = _parse_numeric(row.get("quantidade"))
        price = _parse_numeric(row.get("preco_unitario"))
        val = _parse_numeric(row.get("valor_operacao"))
        dt_val = row.get("data_dt")
        dt_str = dt_val.strftime("%Y-%m-%d") if pd.notna(dt_val) else str(row.get("data", ""))
        month_key = dt_val.strftime("%Y-%m") if pd.notna(dt_val) else "Outros"

        # Initialize monthly bucket if needed
        if month_key not in monthly_map:
            monthly_map[month_key] = {"dividendos": 0.0, "jcp": 0.0, "rendimentos": 0.0}

        # 1. Check for passive income
        is_dividendo = "dividendo" in mov_norm
        is_jcp = "juros sobre capital" in mov_norm or "jcp" in mov_norm
        is_rendimento = "rendimento" in mov_norm

        if is_dividendo:
            income_amount = val if val > 0 else (qty * price)
            total_dividends += income_amount
            monthly_map[month_key]["dividendos"] += income_amount
            continue
        elif is_jcp:
            income_amount = val if val > 0 else (qty * price)
            total_jcp += income_amount
            monthly_map[month_key]["jcp"] += income_amount
            continue
        elif is_rendimento:
            income_amount = val if val > 0 else (qty * price)
            total_rendimentos += income_amount
            monthly_map[month_key]["rendimentos"] += income_amount
            continue

        # 2. Custody trades (Compra, Venda, Transferencia - Liquidacao with price)
        # Note: B3 exports trades as 'Transferência - Liquidação' or 'Compra' / 'Venda'
        is_trade = (
            "compra" in mov_norm
            or "venda" in mov_norm
            or ("liquidacao" in mov_norm and (price > 0 or val > 0))
        )

        if not is_trade:
            continue

        # Determine operation direction
        is_buy = (es_norm == "credito") or ("compra" in mov_norm)
        is_sell = (es_norm == "debito") or ("venda" in mov_norm)

        if not is_buy and not is_sell:
            continue

        if sa_ticker not in holdings_dict:
            holdings_dict[sa_ticker] = {
                "ticker": sa_ticker,
                "ticker_clean": clean_ticker,
                "shares": 0.0,
                "average_buy_price": 0.0,
                "total_invested": 0.0,
                "asset_class": _classify_asset(clean_ticker),
            }

        cur = holdings_dict[sa_ticker]

        if is_buy:
            op_cost = val if val > 0 else (qty * price)
            prev_cost = cur["shares"] * cur["average_buy_price"]
            new_qty = cur["shares"] + qty
            if new_qty > 0:
                new_pm = (prev_cost + op_cost) / new_qty
            else:
                new_pm = 0.0
            cur["shares"] = new_qty
            cur["average_buy_price"] = new_pm
            cur["total_invested"] = new_qty * new_pm
        elif is_sell:
            # Under Receita Federal rules, selling reduces quantity while unit PM remains unchanged.
            # If position drops to 0, PM resets to 0.
            new_qty = max(0.0, cur["shares"] - qty)
            if new_qty <= 1e-6:
                cur["shares"] = 0.0
                cur["average_buy_price"] = 0.0
                cur["total_invested"] = 0.0
            else:
                cur["shares"] = new_qty
                cur["total_invested"] = new_qty * cur["average_buy_price"]

    # Filter active holdings (shares > 0)
    active_holdings: List[B3Holding] = []
    total_invested = 0.0

    for sa_ticker, h_data in holdings_dict.items():
        if h_data["shares"] > 1e-4:
            holding = B3Holding(
                ticker=h_data["ticker"],
                ticker_clean=h_data["ticker_clean"],
                shares=round(h_data["shares"], 4),
                average_buy_price=round(h_data["average_buy_price"], 4),
                total_invested=round(h_data["total_invested"], 2),
                asset_class=h_data["asset_class"],
            )
            active_holdings.append(holding)
            total_invested += holding.total_invested

    # Sort holdings descending by total invested
    active_holdings.sort(key=lambda x: x.total_invested, reverse=True)

    # Monthly income list sorted chronologically
    monthly_income: List[B3MonthlyIncome] = []
    for m_key in sorted(monthly_map.keys()):
        if m_key == "Outros" and monthly_map[m_key]["dividendos"] == 0 and monthly_map[m_key]["jcp"] == 0 and monthly_map[m_key]["rendimentos"] == 0:
            continue
        vals = monthly_map[m_key]
        m_tot = vals["dividendos"] + vals["jcp"] + vals["rendimentos"]
        if m_tot > 0:
            monthly_income.append(
                B3MonthlyIncome(
                    month_year=m_key,
                    dividendos=round(vals["dividendos"], 2),
                    jcp=round(vals["jcp"], 2),
                    rendimentos=round(vals["rendimentos"], 2),
                    total=round(m_tot, 2),
                )
            )

    total_income = round(total_dividends + total_jcp + total_rendimentos, 2)

    return B3ParseResult(
        filename=filename,
        total_movements=total_movements,
        holdings=active_holdings,
        total_invested=round(total_invested, 2),
        total_income=total_income,
        monthly_income=monthly_income,
    )
