import io

import pytest
from pathlib import Path
import pandas as pd
from src.data_loader.b3_parser import (
    parse_b3_file,
    parse_multiple_b3_files,
    _parse_numeric,
    _clean_ticker_from_product,
    _classify_asset,
)


def _csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, sep=";").encode("utf-8")


def _detalhada(rows):
    return pd.DataFrame(rows, columns=[
        "Data do Negócio", "Tipo de Movimentação", "Mercado", "Prazo/Vencimento",
        "Instituição", "Código de Negociação", "Quantidade", "Preço", "Valor",
    ])


def _movimentacao(rows):
    return pd.DataFrame(rows, columns=[
        "Entrada/Saída", "Data", "Movimentação", "Produto", "Instituição",
        "Quantidade", "Preço unitário", "Valor da Operação",
    ])


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
    """Validates the official B3 movement spreadsheet (693-row or local movimentacao.xlsx fallback)."""
    b3_path = Path("B3/movimentacao-2026-10-22-13-32-52.xlsx")
    fallback_path = Path("B3/movimentacao.xlsx")
    if b3_path.exists():
        result = parse_b3_file(b3_path)
        assert result.total_movements == 693
        assert len(result.holdings) >= 20  # 23 active holdings
        assert result.total_invested > 2500.0  # R$ 4,085.12
        assert result.total_income >= 683.39  # Exactly R$ 683.39
        assert len(result.monthly_income) > 20
        tickers = [h.ticker for h in result.holdings]
        assert "PETR4.SA" in tickers
        assert "MXRF11.SA" in tickers
        assert "KLBN4.SA" in tickers
    elif fallback_path.exists():
        result = parse_b3_file(fallback_path)
        assert result.total_movements == 53
        assert len(result.holdings) == 18
        assert result.total_invested > 2500.0
        assert result.total_income >= 30.0
        assert len(result.monthly_income) >= 4
        tickers = [h.ticker for h in result.holdings]
        assert "KLBN4.SA" in tickers
        assert "TGAR11.SA" in tickers
    else:
        pytest.skip("Planilha B3 não encontrada para teste local.")

    for h in result.holdings:
        assert h.shares > 0
        assert h.average_buy_price > 0
        assert h.total_invested > 0


def test_negociacao_and_multi_file_parsing():
    """Test parsing Negociação - Resumo and combining multiple B3 spreadsheets."""
    neg_path = Path("B3/negociacao desde 04-08-2026.xlsx")
    mov_path = Path("B3/movimentacao desde 04-08-2026.xlsx")
    fallback_neg = Path("B3/julho 2026.xlsx")
    fallback_mov = Path("B3/movimentacao.xlsx")

    if neg_path.exists() and mov_path.exists():
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
    elif fallback_neg.exists() and fallback_mov.exists():
        res_neg = parse_b3_file(fallback_neg)
        assert res_neg.total_movements == 17
        assert any(h.ticker == "GOGL34.SA" for h in res_neg.holdings)

        f_neg = (fallback_neg.name, fallback_neg.read_bytes())
        f_mov = (fallback_mov.name, fallback_mov.read_bytes())
        res_multi = parse_multiple_b3_files([f_neg, f_mov])
        assert len(res_multi.holdings) >= 18
        assert res_multi.total_income >= 30.0
        assert len(res_multi.monthly_income) >= 4
    else:
        pytest.skip("Arquivos de teste não encontrados em B3/.")


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


def test_multi_file_ledger_nets_cross_file_sales():
    """A compra em julho e a venda em agosto devem resultar em saldo zero.

    Regressão do AMZO34/MSFT34/SSFO34/S2NA34: o parser antigo somava as
    holdings de cada arquivo e a venda do mês seguinte era descartada por não
    haver posição inicial dentro daquele arquivo.
    """
    julho = _detalhada([
        ["06/07/2026", "Compra", "Mercado à Vista", "-", "XP", "AMZO34", 1, 63.0, 63.0],
        ["06/07/2026", "Compra", "Mercado Fracionário", "-", "XP", "PETR4F", 5, 38.66, 193.30],
    ])
    agosto = _detalhada([
        ["05/08/2026", "Venda", "Mercado à Vista", "-", "XP", "AMZO34", 1, 69.76, 69.76],
    ])
    movimento = _movimentacao([
        ["Credito", "08/07/2026", "Transferência - Liquidação", "AMZO34 - AMAZON.COM, INC", "XP", 1, 63.0, 63.0],
        ["Debito", "07/08/2026", "Transferência - Liquidação", "AMZO34 - AMAZON.COM, INC", "XP", 1, 69.76, 69.76],
        ["Credito", "08/07/2026", "Transferência - Liquidação", "PETR4 - PETROLEO BRASILEIRO", "XP", 5, 38.66, 193.30],
        ["Credito", "15/09/2026", "Rendimento", "MXRF11 - MAXI RENDA FII", "XP", 1, 0.10, 0.10],
    ])

    files = [
        ("julho.csv", _csv_bytes(julho)),
        ("agosto.csv", _csv_bytes(agosto)),
        ("movimentacao.csv", _csv_bytes(movimento)),
    ]
    result = parse_multiple_b3_files(files)

    tickers = {h.ticker: h for h in result.holdings}
    assert "AMZO34.SA" not in tickers
    assert tickers["PETR4.SA"].shares == 5.0
    assert tickers["PETR4.SA"].average_buy_price == pytest.approx(38.66, abs=1e-4)
    assert result.total_income == pytest.approx(0.10, abs=1e-6)
    assert [(m.month_year, m.total) for m in result.monthly_income] == [("2026-09", 0.10)]


def test_detailed_only_multi_file_ledger_nets_cross_file_sales():
    """Mesmo sem o arquivo de movimentação, julho + agosto não podem deixar saldo."""
    julho = _detalhada([
        ["06/07/2026", "Compra", "Mercado à Vista", "-", "XP", "AMZO34", 1, 63.0, 63.0],
        ["06/07/2026", "Compra", "Mercado Fracionário", "-", "XP", "PETR4F", 5, 38.66, 193.30],
    ])
    agosto = _detalhada([
        ["05/08/2026", "Venda", "Mercado à Vista", "-", "XP", "AMZO34", 1, 69.76, 69.76],
    ])

    result = parse_multiple_b3_files([
        ("julho.csv", _csv_bytes(julho)),
        ("agosto.csv", _csv_bytes(agosto)),
    ])

    tickers = {h.ticker: h for h in result.holdings}
    assert "AMZO34.SA" not in tickers
    assert tickers["PETR4.SA"].shares == 5.0


def test_movement_file_takes_precedence_over_detailed_trades():
    """Movimentação já contém a liquidação; não pode duplicar a Compra detalhada."""
    julho = _detalhada([
        ["06/07/2026", "Compra", "Mercado à Vista", "-", "XP", "PETR4", 5, 38.66, 193.30],
    ])
    movimento = _movimentacao([
        ["Credito", "08/07/2026", "Transferência - Liquidação", "PETR4 - PETROLEO BRASILEIRO", "XP", 5, 38.66, 193.30],
    ])

    result = parse_multiple_b3_files([
        ("julho.csv", _csv_bytes(julho)),
        ("movimentacao.csv", _csv_bytes(movimento)),
    ])

    tickers = {h.ticker: h for h in result.holdings}
    assert tickers["PETR4.SA"].shares == 5.0
    assert tickers["PETR4.SA"].total_invested == pytest.approx(193.30, abs=1e-2)


def _movimentacao_completa() -> pd.DataFrame:
    """Movimentação sintética com custódia e as três categorias de renda."""
    return _movimentacao([
        ["Credito", "08/07/2026", "Transferência - Liquidação", "PETR4 - PETROLEO BRASILEIRO", "XP", 5, 38.66, 193.30],
        ["Credito", "10/08/2026", "Dividendo", "PETR4 - PETROLEO BRASILEIRO", "XP", 5, 0.50, 2.50],
        ["Credito", "10/08/2026", "Juros Sobre Capital Próprio", "PETR4 - PETROLEO BRASILEIRO", "XP", 5, 0.20, 1.00],
        ["Credito", "15/09/2026", "Rendimento", "MXRF11 - MAXI RENDA FII", "XP", 1, 0.10, 0.10],
    ])


def test_duplicate_identical_b3_upload_is_not_counted_twice():
    """US1/T006: o mesmo arquivo enviado duas vezes não duplica custódia nem renda."""
    payload = _csv_bytes(_movimentacao_completa())
    # Objeto distinto com o mesmo conteúdo: a deduplicação deve ser por conteúdo, não por identidade.
    payload_copy = bytes(bytearray(payload))

    single = parse_multiple_b3_files([("movimentacao.csv", payload)])
    duplicated = parse_multiple_b3_files([
        ("movimentacao.csv", payload),
        ("movimentacao.csv", payload_copy),
    ])
    aliased = parse_multiple_b3_files([
        ("movimentacao.csv", payload),
        ("movimentacao-copia.csv", payload_copy),
    ])

    # O nome consolidado lista cada arquivo uma única vez.
    assert single.filename == "movimentacao.csv"
    assert duplicated.filename == "movimentacao.csv"
    assert duplicated.filename.count("movimentacao.csv") == 1
    assert "," not in aliased.filename

    assert single.total_movements == 4
    assert [h.ticker for h in single.holdings] == ["PETR4.SA"]
    assert [(m.month_year, m.total) for m in single.monthly_income] == [
        ("2026-08", 3.50),
        ("2026-09", 0.10),
    ]
    assert [(t.date, t.invested) for t in single.timeline] == [("2026-07", 193.30)]

    for result in (duplicated, aliased):
        assert result.total_movements == single.total_movements
        assert result.total_income == single.total_income == pytest.approx(3.60, abs=1e-9)
        assert result.monthly_income == single.monthly_income
        assert result.holdings == single.holdings
        assert result.timeline == single.timeline
        assert result.total_invested == single.total_invested == pytest.approx(193.30, abs=1e-2)


def test_distinct_b3_files_are_both_consolidated():
    """Arquivos com conteúdos diferentes continuam sendo somados, sem deduplicação indevida."""
    arquivo_a = _movimentacao([
        ["Credito", "08/07/2026", "Transferência - Liquidação", "PETR4 - PETROLEO BRASILEIRO", "XP", 5, 38.66, 193.30],
        ["Credito", "15/09/2026", "Rendimento", "MXRF11 - MAXI RENDA FII", "XP", 1, 0.10, 0.10],
    ])
    arquivo_b = _movimentacao([
        ["Credito", "10/08/2026", "Transferência - Liquidação", "VALE3 - VALE S.A.", "XP", 10, 60.00, 600.00],
        ["Credito", "10/10/2026", "Dividendo", "VALE3 - VALE S.A.", "XP", 10, 0.10, 1.00],
    ])

    result = parse_multiple_b3_files([
        ("movimentacao_a.csv", _csv_bytes(arquivo_a)),
        ("movimentacao_b.csv", _csv_bytes(arquivo_b)),
    ])

    assert result.filename == "movimentacao_a.csv, movimentacao_b.csv"
    assert result.total_movements == 4

    tickers = {h.ticker: h for h in result.holdings}
    assert set(tickers) == {"PETR4.SA", "VALE3.SA"}
    assert tickers["PETR4.SA"].shares == 5.0
    assert tickers["VALE3.SA"].shares == 10.0
    assert result.total_income == pytest.approx(1.10, abs=1e-9)
    assert [(m.month_year, m.total) for m in result.monthly_income] == [
        ("2026-09", 0.10),
        ("2026-10", 1.00),
    ]
    assert [(t.date, t.invested) for t in result.timeline] == [
        ("2026-07", 193.30),
        ("2026-08", 793.30),
    ]


def test_parse_b3_xlsx_from_bytesio():
    """US1/T008: lê um .xlsx real gerado em memória, sem depender de fixture local."""
    pytest.importorskip("openpyxl")

    buffer = io.BytesIO()
    _movimentacao_completa().to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    result = parse_b3_file(buffer, filename="movimentacao.xlsx")

    assert result.filename == "movimentacao.xlsx"
    assert result.total_movements == 4
    assert result.total_income == pytest.approx(3.60, abs=1e-9)
    assert [h.ticker for h in result.holdings] == ["PETR4.SA"]
    assert result.holdings[0].shares == 5.0
    assert result.holdings[0].average_buy_price == pytest.approx(38.66, abs=1e-4)
    assert [(m.month_year, m.total) for m in result.monthly_income] == [
        ("2026-08", 3.50),
        ("2026-09", 0.10),
    ]
    assert [(t.date, t.invested) for t in result.timeline] == [("2026-07", 193.30)]
