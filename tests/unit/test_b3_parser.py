import pytest
from pathlib import Path
from src.data_loader.b3_parser import (
    parse_b3_file,
    parse_multiple_b3_files,
    _parse_numeric,
    _clean_ticker_from_product,
    _classify_asset,
)


def test_numeric_parsing():
    assert _parse_numeric("10,50") == 10.5
    assert _parse_numeric("1.250,75") == 1250.75
    assert _parse_numeric("1250.75") == 1250.75
    assert _parse_numeric("-") == 0.0
    assert _parse_numeric(None) == 0.0
    assert _parse_numeric(100) == 100.0


def test_ticker_cleaning():
    raw, clean, sa = _clean_ticker_from_product("PETR4 - PETROLEO BRASILEIRO S/A PETROBRAS")
    assert clean == "PETR4"
    assert sa == "PETR4.SA"

    raw, clean, sa = _clean_ticker_from_product("MXRF11 - MAXI RENDA FDO INV IMOB - FII")
    assert clean == "MXRF11"
    assert sa == "MXRF11.SA"

    raw, clean, sa = _clean_ticker_from_product("M1TA34 - META PLAT")
    assert clean == "M1TA34"
    assert sa == "M1TA34.SA"

    raw, clean, sa = _clean_ticker_from_product("AZTE3F")
    assert clean == "AZTE3"
    assert sa == "AZTE3.SA"


def test_asset_classification():
    assert _classify_asset("PETR4") == "Ações Brasil"
    assert _classify_asset("VALE3") == "Ações Brasil"
    assert _classify_asset("MXRF11") == "FIIs"
    assert _classify_asset("TGAR11") == "FIIs"
    assert _classify_asset("GOGL34") == "BDRs"
    assert _classify_asset("M1TA34") == "BDRs"


def test_real_b3_spreadsheet():
    """Validates the official B3 movement spreadsheet with 693 rows."""
    b3_path = Path("B3/movimentacao-2026-10-22-13-32-52.xlsx")
    if not b3_path.exists():
        pytest.skip("Planilha B3 não encontrada para teste local.")

    result = parse_b3_file(b3_path)
    assert result.total_movements == 693
    assert len(result.holdings) >= 20  # 23 active holdings
    assert result.total_invested > 2500.0  # R$ 4,085.12
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


def test_negociacao_and_multi_file_parsing():
    """Test parsing Negociação - Resumo and combining multiple B3 spreadsheets."""
    neg_path = Path("B3/negociacao desde 04-08-2026.xlsx")
    mov_path = Path("B3/movimentacao desde 04-08-2026.xlsx")

    if not neg_path.exists() or not mov_path.exists():
        pytest.skip("Arquivos de teste não encontrados em B3/.")

    # 1. Parse Negociação alone
    res_neg = parse_b3_file(neg_path)
    assert res_neg.total_movements > 0
    assert any(h.ticker == "TSLA34.SA" for h in res_neg.holdings)
    tsla = next(h for h in res_neg.holdings if h.ticker == "TSLA34.SA")
    assert tsla.shares == 1.0
    assert tsla.average_buy_price == 64.99

    # 2. Parse Multi-file combined
    f_neg = (neg_path.name, open(neg_path, "rb").read())
    f_mov = (mov_path.name, open(mov_path, "rb").read())
    res_multi = parse_multiple_b3_files([f_neg, f_mov])

    assert any(h.ticker == "TSLA34.SA" for h in res_multi.holdings)
    assert res_multi.total_income >= 26.0  # R$ 26.17 from movimentacao
    assert len(res_multi.monthly_income) > 0


def test_b3_api_multi_upload():
    """Test POST /api/b3/parse endpoint with multiple uploaded files via TestClient."""
    from fastapi.testclient import TestClient
    from src.api.server import app

    client = TestClient(app)

    neg_path = Path("B3/negociacao desde 04-08-2026.xlsx")
    mov_path = Path("B3/movimentacao desde 04-08-2026.xlsx")

    if neg_path.exists() and mov_path.exists():
        files = [
            ("files", (neg_path.name, open(neg_path, "rb"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
            ("files", (mov_path.name, open(mov_path, "rb"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
        ]
        res = client.post("/api/b3/parse", files=files)
        assert res.status_code == 200
        data = res.json()
        assert len(data["holdings"]) > 0
        assert data["total_income"] >= 26.0
