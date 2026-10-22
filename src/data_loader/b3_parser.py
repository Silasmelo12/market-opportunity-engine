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

    return B3ParseResult(
        filename=filename,
        total_movements=len(df),
        holdings=active_holdings,
        total_invested=round(total_invested, 2),
        total_income=0.0,
        monthly_income=[],
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

    return B3ParseResult(
        filename=filename,
        total_movements=total_movements,
        holdings=active_holdings,
        total_invested=round(total_invested, 2),
        total_income=total_income,
        monthly_income=monthly_income,
    )


def parse_b3_file(
    file_source: Union[str, Path, bytes, io.BytesIO],
    filename: str = "movimentacao.xlsx"
) -> B3ParseResult:
    """Parses a single B3 file, automatically detecting sheet type."""
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

    sheet_type = _detect_b3_sheet_type(df)
    if sheet_type == "negociacao_detalhada":
        return parse_b3_negociacao_detalhada_df(df, filename=filename)
    if sheet_type == "negociacao_resumo":
        return parse_b3_negociacao_resumo_df(df, filename=filename)
    return parse_b3_movimentacao_df(df, filename=filename)


def parse_multiple_b3_files(files_data: List[Tuple[str, bytes]]) -> B3ParseResult:
    """
    Consolidates multiple B3 files (e.g. Negociação Detalhada de vários meses + Movimentação de proventos)
    into a single unified B3ParseResult.
    """
    if not files_data:
        return B3ParseResult(
            filename="nenhum_arquivo",
            total_movements=0,
            holdings=[],
            total_invested=0.0,
            total_income=0.0,
            monthly_income=[],
        )

    parsed_results = []
    for fname, content in files_data:
        try:
            res = parse_b3_file(content, filename=fname)
            parsed_results.append(res)
        except Exception as e:
            pass

    if not parsed_results:
        raise ValueError("Nenhum arquivo válido da B3 pôde ser processado.")

    combined_names = ", ".join(r.filename for r in parsed_results)
    total_movements = sum(r.total_movements for r in parsed_results)
    total_income = round(sum(r.total_income for r in parsed_results), 2)

    # 1. Consolidate monthly income
    monthly_dict: Dict[str, Dict[str, float]] = {}
    for r in parsed_results:
        for m in r.monthly_income:
            if m.month_year not in monthly_dict:
                monthly_dict[m.month_year] = {"dividendos": 0.0, "jcp": 0.0, "rendimentos": 0.0}
            monthly_dict[m.month_year]["dividendos"] += m.dividendos
            monthly_dict[m.month_year]["jcp"] += m.jcp
            monthly_dict[m.month_year]["rendimentos"] += m.rendimentos

    combined_monthly: List[B3MonthlyIncome] = []
    for my in sorted(monthly_dict.keys()):
        d = monthly_dict[my]
        tot = round(d["dividendos"] + d["jcp"] + d["rendimentos"], 2)
        combined_monthly.append(
            B3MonthlyIncome(
                month_year=my,
                dividendos=round(d["dividendos"], 2),
                jcp=round(d["jcp"], 2),
                rendimentos=round(d["rendimentos"], 2),
                total=tot,
            )
        )

    # 2. Consolidate holdings across files
    # We maintain weighted average price for cumulative purchases across separate monthly negotiation sheets
    holdings_map: Dict[str, B3Holding] = {}
    for r in parsed_results:
        for h in r.holdings:
            if h.shares <= 0 or h.average_buy_price <= 0:
                continue
            if h.ticker not in holdings_map:
                holdings_map[h.ticker] = h
            else:
                existing = holdings_map[h.ticker]
                tot_qty = existing.shares + h.shares
                if tot_qty > 0:
                    weighted_cost = (existing.shares * existing.average_buy_price) + (h.shares * h.average_buy_price)
                    new_pm = round(weighted_cost / tot_qty, 4)
                    holdings_map[h.ticker] = B3Holding(
                        ticker=existing.ticker,
                        ticker_clean=existing.ticker_clean,
                        shares=round(tot_qty, 4),
                        average_buy_price=new_pm,
                        total_invested=round(tot_qty * new_pm, 2),
                        asset_class=existing.asset_class,
                    )

    final_holdings = list(holdings_map.values())
    final_holdings.sort(key=lambda x: x.total_invested, reverse=True)
    total_invested = round(sum(h.total_invested for h in final_holdings), 2)

    return B3ParseResult(
        filename=combined_names,
        total_movements=total_movements,
        holdings=final_holdings,
        total_invested=total_invested,
        total_income=total_income,
        monthly_income=combined_monthly,
    )
