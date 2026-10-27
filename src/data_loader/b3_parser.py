"""
B3 Official Movement and Negotiation Spreadsheet Parser and Tax Engine.
Processes official .xlsx and .csv files from B3 Investor Portal:
- 'Movimentação' sheets (cashflow, custody changes, dividends, JCP, rendimentos)
- 'Negociação Detalhada' sheets (e.g. junho.xlsx, julho.xlsx, agosto.xlsx with 'Data do Negócio', 'Tipo de Movimentação')
- 'Negociação - Resumo' sheets (trading executed orders summary)
- Supports multi-file combined processing and consolidation.
"""

import os
import io
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np

from ..api.schemas import B3MovementRecord, B3Holding, B3MonthlyIncome, B3ParseResult, B3TimelinePoint


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
    Extracts raw, clean and .SA ticker from the Produto column or code.
    Example: 'PETR4 - PETROLEO BRASILEIRO S/A PETROBRAS' -> ('PETR4', 'PETR4', 'PETR4.SA')
             'AZTE3F' -> ('AZTE3F', 'AZTE3', 'AZTE3.SA')
    """
    prod = str(product_val or "").strip()
    raw = prod.split("-")[0].strip().upper()
    clean = raw
    # Strip fractional 'F' suffix if it is a standard 4-character equity (e.g. AZTE3F -> AZTE3)
    if len(clean) >= 5 and clean.endswith("F") and clean[:-1][-1].isdigit():
        clean = clean[:-1]
    
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
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0


def _parse_date(date_val: Any) -> Optional[pd.Timestamp]:
    """Parses date string or Timestamp to pd.Timestamp."""
    if date_val is None or pd.isna(date_val):
        return None
    if isinstance(date_val, pd.Timestamp):
        return date_val
    try:
        return pd.to_datetime(date_val, format="%d/%m/%Y", errors="coerce")
    except Exception:
        return pd.to_datetime(date_val, errors="coerce")


def _detect_b3_sheet_type(df: pd.DataFrame) -> str:
    """Detects whether a DataFrame represents 'movimentacao', 'negociacao_detalhada', 'negociacao_resumo', or 'csv_legado'."""
    normalized_cols = [_normalize_str(c).lower() for c in df.columns]
    
    if any("data do negocio" in c for c in normalized_cols):
        return "negociacao_detalhada"
    if any("quantidade (liquida)" in c for c in normalized_cols) or any("preco medio (compra)" in c for c in normalized_cols):
        return "negociacao_resumo"
    if any("movimentacao" in c for c in normalized_cols) and any("entrada/saida" in c for c in normalized_cols):
        return "movimentacao"
    if len(df.columns) >= 2 and any("ticker" in c or "ativo" in c or "papel" in c for c in normalized_cols):
        return "csv_legado"
    
    col_str = " ".join(normalized_cols)
    if "negocio" in col_str or "codigo de negociacao" in col_str:
        return "negociacao_detalhada"
    if "liquida" in col_str:
        return "negociacao_resumo"
    if "produto" in col_str:
        return "movimentacao"
    return "desconhecido"


def parse_b3_negociacao_detalhada_df(df: pd.DataFrame, filename: str = "negociacao.xlsx") -> B3ParseResult:
    """
    Parses a 'Negociação Detalhada' DataFrame (e.g. junho.xlsx, julho.xlsx, agosto.xlsx)
    with columns: Data do Negócio, Tipo de Movimentação, Código de Negociação, Quantidade, Preço, Valor.
    """
    col_map = {}
    for col in df.columns:
        norm = _normalize_str(col).lower()
        if "data" in norm:
            col_map["data"] = col
        elif "tipo" in norm or "movimentacao" in norm:
            col_map["tipo"] = col
        elif "codigo" in norm or "negociacao" in norm or "ativo" in norm:
            col_map["codigo"] = col
        elif "quantidade" in norm or "qtd" in norm:
            col_map["quantidade"] = col
        elif "preco" in norm:
            col_map["preco"] = col
        elif "valor" in norm:
            col_map["valor"] = col

    if "codigo" not in col_map or "tipo" not in col_map or "quantidade" not in col_map:
        return B3ParseResult(
            filename=filename,
            total_movements=0,
            holdings=[],
            total_invested=0.0,
            total_income=0.0,
            monthly_income=[],
        )

    # Sort chronologically if data column is present
    if "data" in col_map:
        df["__parsed_date"] = df[col_map["data"]].apply(_parse_date)
        df_sorted = df.sort_values(by="__parsed_date", ascending=True, na_position="first")
    else:
        df_sorted = df

    holdings_dict: Dict[str, Dict[str, Any]] = {}

    for _, row in df_sorted.iterrows():
        raw_code = str(row.get(col_map["codigo"], "")).strip().upper()
        if not raw_code or "WIN" in raw_code or "WDO" in raw_code or "FUTURO" in raw_code or "DI1" in raw_code:
            continue

        raw_ticker, clean_ticker, sa_ticker = _clean_ticker_from_product(raw_code)
        mov_type = _normalize_str(row.get(col_map["tipo"], "")).lower()
        qty = _parse_numeric(row.get(col_map["quantidade"], 0))
        val = _parse_numeric(row.get(col_map.get("valor", 0)))
        price = _parse_numeric(row.get(col_map.get("preco", 0)))
        op_cost = val if val > 0 else (qty * price)

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
        if "compra" in mov_type:
            prev_cost = cur["shares"] * cur["average_buy_price"]
            new_qty = cur["shares"] + qty
            new_pm = (prev_cost + op_cost) / new_qty if new_qty > 0 else 0.0
            cur["shares"] = new_qty
            cur["average_buy_price"] = new_pm
            cur["total_invested"] = new_qty * new_pm
        elif "venda" in mov_type:
            new_qty = max(0.0, cur["shares"] - qty)
            if new_qty <= 1e-6:
                cur["shares"] = 0.0
                cur["average_buy_price"] = 0.0
                cur["total_invested"] = 0.0
            else:
                cur["shares"] = new_qty
                cur["total_invested"] = new_qty * cur["average_buy_price"]

    active_holdings: List[B3Holding] = []
    total_invested = 0.0

    for sa_ticker, h in holdings_dict.items():
        if h["shares"] > 1e-4 and h["average_buy_price"] > 0:
            holding = B3Holding(
                ticker=h["ticker"],
                ticker_clean=h["ticker_clean"],
                shares=round(h["shares"], 4),
                average_buy_price=round(h["average_buy_price"], 4),
                total_invested=round(h["total_invested"], 2),
                asset_class=h["asset_class"],
            )
            active_holdings.append(holding)
            total_invested += holding.total_invested

    active_holdings.sort(key=lambda x: x.total_invested, reverse=True)

    # Build timeline points from monthly flow
    monthly_flow: Dict[str, Dict[str, Any]] = {}
    if "data" in col_map:
        for _, row in df_sorted.iterrows():
            raw_code = str(row.get(col_map["codigo"], "")).strip().upper()
            if not raw_code or "WIN" in raw_code or "WDO" in raw_code or "FUTURO" in raw_code or "DI1" in raw_code:
                continue
            dt = row.get("__parsed_date")
            if pd.isna(dt):
                continue
            m_key = dt.strftime("%Y-%m")
            lbl = dt.strftime("%m/%y")
            mov_type = _normalize_str(row.get(col_map["tipo"], "")).lower()
            qty = _parse_numeric(row.get(col_map["quantidade"], 0))
            val = _parse_numeric(row.get(col_map.get("valor", 0)))
            price = _parse_numeric(row.get(col_map.get("preco", 0)))
            op_cost = val if val > 0 else (qty * price)

            if m_key not in monthly_flow:
                monthly_flow[m_key] = {"label": lbl, "cashflow": 0.0}
            if "compra" in mov_type:
                monthly_flow[m_key]["cashflow"] += op_cost
            elif "venda" in mov_type:
                monthly_flow[m_key]["cashflow"] -= op_cost

    timeline: List[B3TimelinePoint] = []
    cum_invested = 0.0
    for m in sorted(monthly_flow.keys()):
        flow = monthly_flow[m]["cashflow"]
        cum_invested = max(0.0, cum_invested + flow)
        timeline.append(
            B3TimelinePoint(
                date=m,
                label=monthly_flow[m]["label"],
                invested=round(cum_invested, 2),
                cashflow=round(flow, 2),
            )
        )

    return B3ParseResult(
        filename=filename,
        total_movements=len(df),
        holdings=active_holdings,
        total_invested=round(total_invested, 2),
        total_income=0.0,
        monthly_income=[],
        timeline=timeline,
    )


def parse_b3_negociacao_resumo_df(df: pd.DataFrame, filename: str = "negociacao.xlsx") -> B3ParseResult:
    """Parses a 'Negociação - Resumo' DataFrame."""
    norm_map = {_normalize_str(c).lower(): c for c in df.columns}
    col_ticker = next((norm_map[k] for k in norm_map if "codigo de negociacao" in k or "codigo" in k), None)
    col_qtd_liq = next((norm_map[k] for k in norm_map if "quantidade (liquida)" in k or "liquida" in k), None)
    col_pm_compra = next((norm_map[k] for k in norm_map if "preco medio (compra)" in k or "medio (compra)" in k), None)

    holdings: List[B3Holding] = []
    total_invested = 0.0

    if not col_ticker:
        return B3ParseResult(
            filename=filename,
            total_movements=0,
            holdings=[],
            total_invested=0.0,
            total_income=0.0,
            monthly_income=[],
        )

    for _, row in df.iterrows():
        raw_code = str(row.get(col_ticker, "")).strip().upper()
        if not raw_code or "FUTURO" in raw_code or "WIN" in raw_code or "WDO" in raw_code:
            continue

        raw_ticker, clean_ticker, sa_ticker = _clean_ticker_from_product(raw_code)
        qtd_liq = _parse_numeric(row.get(col_qtd_liq, 0)) if col_qtd_liq else 0.0
        pm_compra = _parse_numeric(row.get(col_pm_compra, 0)) if col_pm_compra else 0.0

        if qtd_liq > 1e-4 and pm_compra > 0:
            invested = round(qtd_liq * pm_compra, 2)
            asset_cls = _classify_asset(clean_ticker)
            holdings.append(
                B3Holding(
                    ticker=sa_ticker,
                    ticker_clean=clean_ticker,
                    shares=round(qtd_liq, 4),
                    average_buy_price=round(pm_compra, 4),
                    total_invested=invested,
                    asset_class=asset_cls,
                )
            )
            total_invested += invested

    holdings.sort(key=lambda x: x.total_invested, reverse=True)

    return B3ParseResult(
        filename=filename,
        total_movements=len(df),
        holdings=holdings,
        total_invested=round(total_invested, 2),
        total_income=0.0,
        monthly_income=[],
    )


def parse_b3_movimentacao_df(df: pd.DataFrame, filename: str = "movimentacao.xlsx") -> B3ParseResult:
    """Parses a standard 'Movimentação' DataFrame with chronological tax calculations."""
    col_map = {}
    for col in df.columns:
        norm = _normalize_str(col).lower()
        if "entrada/saida" in norm or "entrada" in norm:
            col_map["entrada_saida"] = col
        elif "data" in norm:
            col_map["data"] = col
        elif "movimentacao" in norm or "tipo" in norm:
            col_map["movimentacao"] = col
        elif "produto" in norm or "ativo" in norm or "titulo" in norm:
            col_map["produto"] = col
        elif "quantidade" in norm or "qtd" in norm:
            col_map["quantidade"] = col
        elif "preco unitario" in norm or "preco" in norm:
            col_map["preco_unitario"] = col
        elif "valor da operacao" in norm or "valor" in norm:
            col_map["valor_operacao"] = col

    for req in ("data", "movimentacao", "produto"):
        if req not in col_map:
            raise ValueError(f"Coluna obrigatória '{req}' ausente na planilha B3.")

    df["__parsed_date"] = df[col_map["data"]].apply(_parse_date)
    df_sorted = df.sort_values(by="__parsed_date", ascending=True, na_position="first")

    total_movements = len(df_sorted)
    holdings_dict: Dict[str, Dict[str, Any]] = {}
    monthly_map: Dict[str, Dict[str, float]] = {}

    total_dividends = 0.0
    total_jcp = 0.0
    total_rendimentos = 0.0

    for _, row in df_sorted.iterrows():
        prod = row.get(col_map["produto"])
        raw_ticker, clean_ticker, sa_ticker = _clean_ticker_from_product(prod)
        if not clean_ticker or "FUTURO" in clean_ticker or "DI1" in clean_ticker:
            continue

        mov_raw = str(row.get(col_map["movimentacao"], "") or "").strip()
        mov_norm = _normalize_str(mov_raw).lower()
        es_raw = str(row.get(col_map.get("entrada_saida", ""), "") or "").strip()
        es_norm = _normalize_str(es_raw).lower()

        qty = _parse_numeric(row.get(col_map.get("quantidade", 0)))
        price = _parse_numeric(row.get(col_map.get("preco_unitario", 0)))
        val = _parse_numeric(row.get(col_map.get("valor_operacao", 0)))

        dt = row["__parsed_date"]
        month_key = dt.strftime("%Y-%m") if pd.notna(dt) else "Outros"

        if month_key not in monthly_map:
            monthly_map[month_key] = {"dividendos": 0.0, "jcp": 0.0, "rendimentos": 0.0}

        # Track Passive Income
        income_val = val if val > 0 else (qty * price)
        if "dividendo" in mov_norm:
            total_dividends += income_val
            monthly_map[month_key]["dividendos"] += income_val
        elif "juros sobre capital" in mov_norm or "jcp" in mov_norm:
            total_jcp += income_val
            monthly_map[month_key]["jcp"] += income_val
        elif "rendimento" in mov_norm:
            total_rendimentos += income_val
            monthly_map[month_key]["rendimentos"] += income_val

        # Track Custody Changes
        is_buy = "compra" in mov_norm or (es_norm == "credito" and "transferencia" in mov_norm and qty > 0)
        is_sell = "venda" in mov_norm or (es_norm == "debito" and "transferencia" in mov_norm and qty > 0)

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
            new_pm = (prev_cost + op_cost) / new_qty if new_qty > 0 else 0.0
            cur["shares"] = new_qty
            cur["average_buy_price"] = new_pm
            cur["total_invested"] = new_qty * new_pm
        elif is_sell:
            new_qty = max(0.0, cur["shares"] - qty)
            if new_qty <= 1e-6:
                cur["shares"] = 0.0
                cur["average_buy_price"] = 0.0
                cur["total_invested"] = 0.0
            else:
                cur["shares"] = new_qty
                cur["total_invested"] = new_qty * cur["average_buy_price"]

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

    active_holdings.sort(key=lambda x: x.total_invested, reverse=True)

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

    # Build timeline points from custody movements
    monthly_flow_mov: Dict[str, Dict[str, Any]] = {}
    for _, row in df_sorted.iterrows():
        prod = row.get(col_map["produto"])
        raw_ticker, clean_ticker, sa_ticker = _clean_ticker_from_product(prod)
        if not clean_ticker or "FUTURO" in clean_ticker or "DI1" in clean_ticker:
            continue
        dt = row.get("__parsed_date")
        if pd.isna(dt):
            continue
        m_key = dt.strftime("%Y-%m")
        lbl = dt.strftime("%m/%y")
        mov_norm = _normalize_str(row.get(col_map["movimentacao"], "")).lower()
        es_norm = _normalize_str(row.get(col_map.get("entrada_saida", ""), "")).lower()
        qty = _parse_numeric(row.get(col_map.get("quantidade", 0)))
        price = _parse_numeric(row.get(col_map.get("preco_unitario", 0)))
        val = _parse_numeric(row.get(col_map.get("valor_operacao", 0)))
        op_cost = val if val > 0 else (qty * price)

        is_buy = "compra" in mov_norm or (es_norm == "credito" and "transferencia" in mov_norm and qty > 0)
        is_sell = "venda" in mov_norm or (es_norm == "debito" and "transferencia" in mov_norm and qty > 0)

        if is_buy or is_sell:
            if m_key not in monthly_flow_mov:
                monthly_flow_mov[m_key] = {"label": lbl, "cashflow": 0.0}
            if is_buy:
                monthly_flow_mov[m_key]["cashflow"] += op_cost
            elif is_sell:
                monthly_flow_mov[m_key]["cashflow"] -= op_cost

    timeline_mov: List[B3TimelinePoint] = []
    cum_inv_mov = 0.0
    for m in sorted(monthly_flow_mov.keys()):
        flow = monthly_flow_mov[m]["cashflow"]
        cum_inv_mov = max(0.0, cum_inv_mov + flow)
        timeline_mov.append(
            B3TimelinePoint(
                date=m,
                label=monthly_flow_mov[m]["label"],
                invested=round(cum_inv_mov, 2),
                cashflow=round(flow, 2),
            )
        )

    return B3ParseResult(
        filename=filename,
        total_movements=total_movements,
        holdings=active_holdings,
        total_invested=round(total_invested, 2),
        total_income=total_income,
        monthly_income=monthly_income,
        timeline=timeline_mov,
    )


def _empty_result(filename: str) -> B3ParseResult:
    return B3ParseResult(
        filename=filename,
        total_movements=0,
        holdings=[],
        total_invested=0.0,
        total_income=0.0,
        monthly_income=[],
        timeline=[],
    )


def _read_b3_dataframe(
    file_source: Union[str, Path, bytes, io.BytesIO],
    filename: str,
) -> pd.DataFrame:
    """Reads a B3 spreadsheet/CSV into a DataFrame, handling bytes and paths."""
    if isinstance(file_source, (str, Path)):
        file_path = Path(file_source)
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo B3 não encontrado: {file_path}")
        is_excel = file_path.suffix.lower() in (".xlsx", ".xls")
        if is_excel:
            return pd.read_excel(file_path)
        try:
            return pd.read_csv(file_path, sep=";", encoding="utf-8")
        except Exception:
            return pd.read_csv(file_path, sep=",", encoding="latin1")

    stream = file_source if isinstance(file_source, io.BytesIO) else io.BytesIO(file_source)
    is_excel = filename.lower().endswith((".xlsx", ".xls"))
    if is_excel:
        return pd.read_excel(stream)
    try:
        return pd.read_csv(stream, sep=";", encoding="utf-8")
    except Exception:
        stream.seek(0)
        return pd.read_csv(stream, sep=",", encoding="latin1")


def _parse_dataframe(df: pd.DataFrame, filename: str) -> B3ParseResult:
    if df.empty:
        return _empty_result(filename)

    sheet_type = _detect_b3_sheet_type(df)
    if sheet_type == "negociacao_detalhada":
        return parse_b3_negociacao_detalhada_df(df, filename=filename)
    if sheet_type == "negociacao_resumo":
        return parse_b3_negociacao_resumo_df(df, filename=filename)
    return parse_b3_movimentacao_df(df, filename=filename)


def _extract_detalhada_events(df: pd.DataFrame, filename: str) -> List[Dict[str, Any]]:
    """Extracts explicit Compra/Venda events from a 'Negociação Detalhada' sheet."""
    col_map: Dict[str, Any] = {}
    for col in df.columns:
        norm = _normalize_str(col).lower()
        if "data" in norm:
            col_map["data"] = col
        elif "tipo" in norm or "movimentacao" in norm:
            col_map["tipo"] = col
        elif "codigo" in norm or "negociacao" in norm or "ativo" in norm:
            col_map["codigo"] = col
        elif "quantidade" in norm or "qtd" in norm:
            col_map["quantidade"] = col
        elif "preco" in norm:
            col_map["preco"] = col
        elif "valor" in norm:
            col_map["valor"] = col

    if "codigo" not in col_map or "tipo" not in col_map or "quantidade" not in col_map:
        return []

    events: List[Dict[str, Any]] = []
    for order, (_, row) in enumerate(df.iterrows()):
        raw_code = str(row.get(col_map["codigo"], "") or "").strip().upper()
        if not raw_code or any(x in raw_code for x in ("WIN", "WDO", "FUTURO", "DI1")):
            continue

        mov_type = _normalize_str(row.get(col_map["tipo"], "")).lower()
        if "compra" in mov_type:
            side = "buy"
        elif "venda" in mov_type:
            side = "sell"
        else:
            continue

        qty = _parse_numeric(row.get(col_map["quantidade"], 0))
        if qty <= 0:
            continue
        price = _parse_numeric(row.get(col_map.get("preco", 0)))
        value = _parse_numeric(row.get(col_map.get("valor", 0)))
        op_value = value if value > 0 else (qty * price)
        raw_ticker, clean_ticker, sa_ticker = _clean_ticker_from_product(raw_code)

        events.append({
            "date": _parse_date(row.get(col_map.get("data"))) if "data" in col_map else None,
            "ticker": sa_ticker,
            "ticker_clean": clean_ticker,
            "side": side,
            "qty": qty,
            "price": price,
            "value": op_value,
            "kind": "trade",
            "file": filename,
            "order": order,
        })
    return events


def _extract_movimentacao_events(df: pd.DataFrame, filename: str) -> List[Dict[str, Any]]:
    """Extracts custody events from a 'Movimentação' sheet.

    Explicit Compra/Venda rows are trades. 'Transferência - Liquidação' rows are
    the settlement of a trade and are tagged as transfers so they can be
    de-duplicated against an explicit trade row for the same operation.
    """
    col_map: Dict[str, Any] = {}
    for col in df.columns:
        norm = _normalize_str(col).lower()
        if "entrada/saida" in norm or "entrada" in norm:
            col_map["entrada_saida"] = col
        elif "data" in norm:
            col_map["data"] = col
        elif "movimentacao" in norm or "tipo" in norm:
            col_map["movimentacao"] = col
        elif "produto" in norm or "ativo" in norm or "titulo" in norm:
            col_map["produto"] = col
        elif "quantidade" in norm or "qtd" in norm:
            col_map["quantidade"] = col
        elif "preco unitario" in norm or "preco" in norm:
            col_map["preco_unitario"] = col
        elif "valor da operacao" in norm or "valor" in norm:
            col_map["valor_operacao"] = col

    if "produto" not in col_map or "movimentacao" not in col_map:
        return []

    events: List[Dict[str, Any]] = []
    for order, (_, row) in enumerate(df.iterrows()):
        prod = row.get(col_map["produto"])
        raw_ticker, clean_ticker, sa_ticker = _clean_ticker_from_product(prod)
        if not clean_ticker or "FUTURO" in clean_ticker or "DI1" in clean_ticker:
            continue

        mov_norm = _normalize_str(row.get(col_map["movimentacao"], "")).lower()
        es_norm = _normalize_str(row.get(col_map.get("entrada_saida", ""), "")).lower()
        qty = _parse_numeric(row.get(col_map.get("quantidade", 0)))
        if qty <= 0:
            continue

        side = None
        kind = None
        if "compra" in mov_norm:
            side = "buy"
            kind = "trade"
        elif "venda" in mov_norm:
            side = "sell"
            kind = "trade"
        elif "transferencia" in mov_norm and "liquidacao" in mov_norm:
            if es_norm == "credito":
                side = "buy"
                kind = "transfer"
            elif es_norm == "debito":
                side = "sell"
                kind = "transfer"

        if side is None:
            continue

        price = _parse_numeric(row.get(col_map.get("preco_unitario", 0)))
        value = _parse_numeric(row.get(col_map.get("valor_operacao", 0)))
        op_value = value if value > 0 else (qty * price)

        events.append({
            "date": _parse_date(row.get(col_map.get("data"))) if "data" in col_map else None,
            "ticker": sa_ticker,
            "ticker_clean": clean_ticker,
            "side": side,
            "qty": qty,
            "price": price,
            "value": op_value,
            "kind": kind,
            "file": filename,
            "order": order,
        })
    return events


def _dedupe_custody_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Keeps explicit trades and removes settlement transfers that duplicate them.

    A 'Transferência - Liquidação' is normally the cash/custody settlement of a
    Compra/Venda already present in a Negociação Detalhada sheet. Without this
    step the same operation would be counted twice when both files are uploaded.
    """
    trades = [e for e in events if e["kind"] == "trade"]
    transfers = [e for e in events if e["kind"] == "transfer"]
    kept = list(trades)
    matched_trades = set()

    for transfer in transfers:
        match_idx = None
        for idx, trade in enumerate(trades):
            if idx in matched_trades:
                continue
            if trade["ticker"] != transfer["ticker"] or trade["side"] != transfer["side"]:
                continue
            if abs(trade["qty"] - transfer["qty"]) > 1e-6:
                continue
            if trade["price"] > 0 and transfer["price"] > 0:
                tolerance = max(0.05, trade["price"] * 0.02)
                if abs(trade["price"] - transfer["price"]) > tolerance:
                    continue
            if trade["date"] is not None and transfer["date"] is not None:
                if abs((trade["date"] - transfer["date"]).days) > 7:
                    continue
            match_idx = idx
            break

        if match_idx is None:
            kept.append(transfer)
        else:
            matched_trades.add(match_idx)

    return kept


def _build_holdings_from_events(events: List[Dict[str, Any]]) -> List[B3Holding]:
    """Replays the custody ledger chronologically across every uploaded file."""
    holdings: Dict[str, Dict[str, Any]] = {}

    for event in events:
        ticker = event["ticker"]
        if ticker not in holdings:
            holdings[ticker] = {
                "ticker": ticker,
                "ticker_clean": event["ticker_clean"],
                "shares": 0.0,
                "average_buy_price": 0.0,
                "total_invested": 0.0,
                "asset_class": _classify_asset(event["ticker_clean"]),
            }

        current = holdings[ticker]
        qty = float(event["qty"])
        value = float(event["value"])

        if event["side"] == "buy":
            prev_cost = current["shares"] * current["average_buy_price"]
            new_qty = current["shares"] + qty
            new_pm = (prev_cost + value) / new_qty if new_qty > 0 else 0.0
            current["shares"] = new_qty
            current["average_buy_price"] = new_pm
            current["total_invested"] = new_qty * new_pm
        elif event["side"] == "sell":
            new_qty = max(0.0, current["shares"] - qty)
            if new_qty <= 1e-6:
                current["shares"] = 0.0
                current["average_buy_price"] = 0.0
                current["total_invested"] = 0.0
            else:
                current["shares"] = new_qty
                current["total_invested"] = new_qty * current["average_buy_price"]

    active: List[B3Holding] = []
    for data in holdings.values():
        if data["shares"] <= 1e-4 or data["average_buy_price"] <= 0:
            continue
        active.append(
            B3Holding(
                ticker=data["ticker"],
                ticker_clean=data["ticker_clean"],
                shares=round(data["shares"], 4),
                average_buy_price=round(data["average_buy_price"], 4),
                total_invested=round(data["total_invested"], 2),
                asset_class=data["asset_class"],
            )
        )

    active.sort(key=lambda h: h.total_invested, reverse=True)
    return active


def _build_timeline_from_events(events: List[Dict[str, Any]]) -> List[B3TimelinePoint]:
    monthly: Dict[str, Dict[str, Any]] = {}
    for event in events:
        date = event.get("date")
        if date is None or pd.isna(date):
            continue
        key = date.strftime("%Y-%m")
        if key not in monthly:
            monthly[key] = {"label": date.strftime("%m/%y"), "cashflow": 0.0}
        if event["side"] == "buy":
            monthly[key]["cashflow"] += float(event["value"])
        else:
            monthly[key]["cashflow"] -= float(event["value"])

    timeline: List[B3TimelinePoint] = []
    cumulative = 0.0
    for key in sorted(monthly.keys()):
        flow = monthly[key]["cashflow"]
        cumulative = max(0.0, cumulative + flow)
        timeline.append(
            B3TimelinePoint(
                date=key,
                label=monthly[key]["label"],
                invested=round(cumulative, 2),
                cashflow=round(flow, 2),
            )
        )
    return timeline


def _dedupe_exact_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Removes identical custody events repeated across overlapping files."""
    seen = set()
    unique: List[Dict[str, Any]] = []
    for event in events:
        date_key = event["date"].isoformat() if event["date"] is not None else None
        key = (
            event["ticker"],
            event["side"],
            event["kind"],
            date_key,
            round(float(event["qty"]), 6),
            round(float(event["price"]), 4),
            round(float(event["value"]), 2),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(event)
    return unique


def parse_b3_file(
    file_source: Union[str, Path, bytes, io.BytesIO],
    filename: str = "movimentacao.xlsx"
) -> B3ParseResult:
    """Parses a single B3 file, automatically detecting sheet type."""
    df = _read_b3_dataframe(file_source, filename)
    return _parse_dataframe(df, filename)


def parse_multiple_b3_files(files_data: List[Tuple[str, bytes]]) -> B3ParseResult:
    """Consolidates multiple B3 files into one chronological custody ledger.

    The previous implementation parsed each file independently and summed the
    resulting holdings. That lost cross-file sells: a share bought in July and
    sold in August stayed in the portfolio because the August file, parsed
    alone, had no opening position and clamped the sale to zero. Settlements
    ('Transferência - Liquidação') could also duplicate explicit trades.

    This implementation extracts every custody event from every file, removes
    settlement duplicates, sorts by date and replays one single ledger.
    """
    if not files_data:
        return _empty_result("nenhum_arquivo")

    loaded: List[Tuple[str, pd.DataFrame, str, B3ParseResult]] = []
    for fname, content in files_data:
        try:
            df = _read_b3_dataframe(content, fname)
            if df.empty:
                continue
            sheet_type = _detect_b3_sheet_type(df)
            result = _parse_dataframe(df, fname)
            loaded.append((fname, df, sheet_type, result))
        except Exception:
            continue

    if not loaded:
        raise ValueError("Nenhum arquivo válido da B3 pôde ser processado.")

    combined_names = ", ".join(item[0] for item in loaded)
    total_movements = sum(item[3].total_movements for item in loaded)
    total_income = round(sum(item[3].total_income for item in loaded), 2)

    # 1. Income is always additive across files.
    monthly_dict: Dict[str, Dict[str, float]] = {}
    for _, _, _, result in loaded:
        for month in result.monthly_income:
            if month.month_year not in monthly_dict:
                monthly_dict[month.month_year] = {"dividendos": 0.0, "jcp": 0.0, "rendimentos": 0.0}
            monthly_dict[month.month_year]["dividendos"] += month.dividendos
            monthly_dict[month.month_year]["jcp"] += month.jcp
            monthly_dict[month.month_year]["rendimentos"] += month.rendimentos

    combined_monthly: List[B3MonthlyIncome] = []
    for month_year in sorted(monthly_dict.keys()):
        values = monthly_dict[month_year]
        combined_monthly.append(
            B3MonthlyIncome(
                month_year=month_year,
                dividendos=round(values["dividendos"], 2),
                jcp=round(values["jcp"], 2),
                rendimentos=round(values["rendimentos"], 2),
                total=round(values["dividendos"] + values["jcp"] + values["rendimentos"], 2),
            )
        )

    # 2. Custody source policy:
    #    - 'Negociação - Resumo' is already a custody snapshot: authoritative.
    #    - 'Movimentação' is the official custody/cash ledger: authoritative
    #      over detailed trade confirmations, because it already contains the
    #      settlement of every trade. Replaying both would double-count.
    #    - Detailed-only uploads are replayed as one chronological ledger.
    resumo_results = [item[3] for item in loaded if item[2] == "negociacao_resumo"]
    movement_sources = [item for item in loaded if item[2] == "movimentacao"]
    detailed_sources = [item for item in loaded if item[2] == "negociacao_detalhada"]

    if resumo_results:
        final_holdings = list(resumo_results[-1].holdings)
        timeline = list(resumo_results[-1].timeline or [])
    else:
        movement_events: List[Dict[str, Any]] = []
        for fname, df, _, _ in movement_sources:
            movement_events.extend(_extract_movimentacao_events(df, fname))
        movement_events = _dedupe_exact_events(movement_events)
        movement_events = _dedupe_custody_events(movement_events)

        if movement_events:
            events = movement_events
        else:
            events = []
            for fname, df, _, _ in detailed_sources:
                events.extend(_extract_detalhada_events(df, fname))
            events = _dedupe_custody_events(events)

        events.sort(key=lambda e: (
            e["date"] is None,
            e["date"] if e["date"] is not None else pd.Timestamp("2100-01-01"),
            0 if e["kind"] == "trade" else 1,
            0 if e["side"] == "buy" else 1,
            e["file"],
            e["order"],
        ))

        final_holdings = _build_holdings_from_events(events)
        timeline = _build_timeline_from_events(events)

    final_holdings.sort(key=lambda h: h.total_invested, reverse=True)
    total_invested = round(sum(h.total_invested for h in final_holdings), 2)

    return B3ParseResult(
        filename=combined_names,
        total_movements=total_movements,
        holdings=final_holdings,
        total_invested=total_invested,
        total_income=total_income,
        monthly_income=combined_monthly,
        timeline=timeline,
    )
