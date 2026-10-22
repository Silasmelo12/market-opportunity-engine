"""
Unit tests for B3 Official Spreadsheet Parser and tax PM calculation engine.
Tests purchases, partial sales, position liquidation, passive income,
and parsing of real B3 spreadsheets.
"""

import os
from pathlib import Path
import pandas as pd
import pytest

from src.data_loader.b3_parser import (
    parse_b3_file,
    _clean_ticker_from_product,
    _classify_asset,
    _parse_numeric,
)
from src.api.schemas import B3ParseResult


def test_clean_ticker_and_classification():
    raw, clean, sa = _clean_ticker_from_product("PETR4 - PETROLEO BRASILEIRO S/A PETROBRAS")
    assert clean == "PETR4"
    assert sa == "PETR4.SA"
    assert _classify_asset(clean) == "Ações Brasil"

    raw, clean, sa = _clean_ticker_from_product("MXRF11 - MAXI RENDA FDO INV IMOB - FII")
    assert clean == "MXRF11"
    assert sa == "MXRF11.SA"
    assert _classify_asset(clean) == "FIIs"

    raw, clean, sa = _clean_ticker_from_product("AMZO34 - AMAZON.COM, INC")
    assert clean == "AMZO34"
    assert sa == "AMZO34.SA"
    assert _classify_asset(clean) == "BDRs"


def test_parse_numeric():
    assert _parse_numeric("10") == 10.0
    assert _parse_numeric("10,50") == 10.5
    assert _parse_numeric("1.250,50") == 1250.50
    assert _parse_numeric("-") == 0.0
    assert _parse_numeric(None) == 0.0
    assert _parse_numeric(25.4) == 25.4


def test_synthetic_pm_calculation_chronological(tmp_path):
    """
    Test chronological purchase, additional purchase at different price,
    partial sale without PM change, and position zeroing.
    """
    csv_file = tmp_path / "test_mov.csv"
    data = [
        # Buy 10 @ 20.00 = 200.00
        {"Entrada/Saída": "Credito", "Data": "01/01/2026", "Movimentação": "Transferência - Liquidação", "Produto": "TEST3 - TESTE S/A", "Quantidade": "10", "Preço unitário": "20.00", "Valor da Operação": "200.00"},
        # Buy 10 @ 30.00 = 300.00 -> Total 20 shares, cost 500.00, PM = 25.00
        {"Entrada/Saída": "Credito", "Data": "05/01/2026", "Movimentação": "Transferência - Liquidação", "Produto": "TEST3 - TESTE S/A", "Quantidade": "10", "Preço unitário": "30.00", "Valor da Operação": "300.00"},
        # Partial Sell 5 @ 40.00 -> Remaining 15 shares, PM remains 25.00, Total invested = 375.00
        {"Entrada/Saída": "Debito", "Data": "10/01/2026", "Movimentação": "Transferência - Liquidação", "Produto": "TEST3 - TESTE S/A", "Quantidade": "5", "Preço unitário": "40.00", "Valor da Operação": "200.00"},
        # Dividend received 15.00
        {"Entrada/Saída": "Credito", "Data": "15/01/2026", "Movimentação": "Dividendo", "Produto": "TEST3 - TESTE S/A", "Quantidade": "15", "Preço unitário": "1.00", "Valor da Operação": "15.00"},
        # JCP received 5.00
        {"Entrada/Saída": "Credito", "Data": "20/01/2026", "Movimentação": "Juros Sobre Capital Próprio", "Produto": "TEST3 - TESTE S/A", "Quantidade": "15", "Preço unitário": "0.33", "Valor da Operação": "5.00"},
    ]
    df = pd.DataFrame(data)
    df.to_csv(csv_file, sep=";", index=False, encoding="utf-8")

    result = parse_b3_file(csv_file, filename="test_mov.csv")
    assert result.total_movements == 5
    assert len(result.holdings) == 1

    h = result.holdings[0]
    assert h.ticker == "TEST3.SA"
    assert h.shares == 15.0
    assert h.average_buy_price == 25.0
    assert h.total_invested == 375.0

    assert result.total_income == 20.0
    assert len(result.monthly_income) == 1
    assert result.monthly_income[0].month_year == "2026-01"
    assert result.monthly_income[0].dividendos == 15.0
    assert result.monthly_income[0].jcp == 5.0


def test_position_zeroing(tmp_path):
    """Sell entire position -> position should be 0 and excluded from active holdings."""
    csv_file = tmp_path / "zero_pos.csv"
    data = [
        {"Entrada/Saída": "Credito", "Data": "01/01/2026", "Movimentação": "Transferência - Liquidação", "Produto": "ZERO3 - ZERO S/A", "Quantidade": "10", "Preço unitário": "15.00", "Valor da Operação": "150.00"},
        {"Entrada/Saída": "Debito", "Data": "02/01/2026", "Movimentação": "Transferência - Liquidação", "Produto": "ZERO3 - ZERO S/A", "Quantidade": "10", "Preço unitário": "18.00", "Valor da Operação": "180.00"},
    ]
    df = pd.DataFrame(data)
    df.to_csv(csv_file, sep=";", index=False, encoding="utf-8")

    result = parse_b3_file(csv_file, filename="zero_pos.csv")
    assert result.total_movements == 2
    assert len(result.holdings) == 0
    assert result.total_invested == 0.0


def test_real_b3_spreadsheet():
    """Verify parsing against the official B3 file provided in the workspace."""
    b3_path = Path("B3/movimentacao-2026-10-22-13-32-52.xlsx")
    if not b3_path.exists():
        pytest.skip("Arquivo B3 oficial não encontrado no caminho local")

    result = parse_b3_file(b3_path, filename=b3_path.name)
    assert isinstance(result, B3ParseResult)
    assert result.total_movements == 693
    assert len(result.holdings) >= 20  # 23 active holdings
    assert result.total_invested > 4000.0  # R$ 4,085.12
    assert result.total_income >= 683.39  # Exactly R$ 683.39
    assert len(result.monthly_income) > 20

    # Validate that tickers have .SA and valid PM
    tickers = [h.ticker for h in result.holdings]
    assert "PETR4.SA" in tickers
    assert "MXRF11.SA" in tickers
    assert "KLBN4.SA" in tickers
    for h in result.holdings:
        assert h.shares > 0
        assert h.average_buy_price > 0
        assert h.total_invested > 0


def test_b3_api_endpoints():
    """Test GET /api/b3/sync-local and POST /api/b3/parse endpoints via FastAPI TestClient."""
    from fastapi.testclient import TestClient
    from src.api.server import app

    client = TestClient(app)

    # 1. Test GET /api/b3/sync-local
    res_sync = client.get("/api/b3/sync-local")
    assert res_sync.status_code == 200
    data_sync = res_sync.json()
    assert data_sync["total_movements"] == 693
    assert len(data_sync["holdings"]) >= 20
    assert data_sync["total_income"] >= 683.39

    # 2. Test POST /api/b3/parse with file upload
    b3_path = Path("B3/movimentacao-2026-10-22-13-32-52.xlsx")
    if b3_path.exists():
        with open(b3_path, "rb") as f:
            res_upload = client.post(
                "/api/b3/parse",
                files={"file": (b3_path.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )
        assert res_upload.status_code == 200
        data_upload = res_upload.json()
        assert data_upload["total_movements"] == 693
        assert len(data_upload["holdings"]) >= 20

