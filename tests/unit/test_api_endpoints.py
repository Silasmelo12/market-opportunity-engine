import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"


def test_api_strategies_catalog():
    res = client.get("/api/strategies")
    assert res.status_code == 200
    data = res.json()
    assert "proprietary" in data
    assert "price_action" in data
    assert "allocation" in data
    assert "mql5" in data
    assert len(data["mql5"]["strategies"]) == 14
    assert "quant_buy" in data
    assert "quant_sell" in data
    assert len(data["quant_buy"]["strategies"]) == 10
    assert len(data["quant_sell"]["strategies"]) == 10
    total_strategies = sum(len(g["strategies"]) for g in data.values())
    assert total_strategies == 70  # 50 previously + 20 quant strategies


def test_api_analyze_synthetic(monkeypatch):
    # Tests /api/analyze endpoint with standard parameters
    res = client.get("/api/analyze?ticker=PETR4.SA&interval=1d&period=1y&lookback_n=10&retest_m=5&horizon_x=20")
    assert res.status_code == 200
    data = res.json()
    assert "ticker" in data
    assert data["ticker"] == "PETR4.SA"
    assert "candles" in data
    assert len(data["candles"]) > 0
    assert "signals" in data
    assert "summaries" in data
    assert "current_state" in data


def test_api_radar():
    res = client.get("/api/radar?interval=1d&horizon_x=30")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_api_radar_categories():
    # Test specific category scan
    res = client.get("/api/radar?interval=1d&category=crypto")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    for item in data["items"]:
        assert item["category"] == "Criptomoedas"


def test_api_radar_direction_filters():
    # Test SELL direction filter
    res_sell = client.get("/api/radar?interval=1d&direction=SELL&category=featured")
    assert res_sell.status_code == 200
    data_sell = res_sell.json()
    assert "items" in data_sell
    assert data_sell["direction"] == "SELL"
    for item in data_sell["items"]:
        assert item["direction"] == "SELL"

    # Test BOTH direction filter
    res_both = client.get("/api/radar?interval=1d&direction=BOTH&category=featured")
    assert res_both.status_code == 200
    data_both = res_both.json()
    assert data_both["direction"] == "BOTH"


def test_api_tickers():
    res = client.get("/api/tickers")
    assert res.status_code == 200
    data = res.json()
    assert "featured" in data
    assert "acoes_br" in data
    assert "fiis" in data
    assert "usa" in data
    assert "commodities" in data
    assert "forex" in data
    assert "crypto" in data
    assert data["total"] == 153


def test_api_simulate():
    payload = {
        "ticker": "PETR4.SA",
        "interval": "1d",
        "period": "1y",
        "simulation_mode": "cycle_trade",
        "buy_strategy": "t1_open",
        "sell_strategy": "sell_t1_open",
        "contribution_amount": 1000.0,
        "lookback_n": 10,
        "retest_m": 5,
        "retest_tol": 0.005,
    }
    res = client.post("/api/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "curve" in data
    assert "trades" in data
    assert data["metrics"]["total_invested"] >= 0


def test_api_simulate_hourly_60m():
    payload = {
        "ticker": "PETR4.SA",
        "interval": "60m",
        "period": "2y",
        "simulation_mode": "cycle_trade",
        "buy_strategy": "t1_open",
        "sell_strategy": "sell_t1_open",
        "contribution_amount": 1000.0,
        "lookback_n": 10,
        "retest_m": 5,
        "retest_tol": 0.005,
    }
    res = client.post("/api/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "curve" in data
    assert data["period"] in ("2y", "730d")


def test_api_simulate_optimize():
    payload = {
        "ticker": "PETR4.SA",
        "interval": "1d",
        "period": "1y",
        "initial_capital": 1000.0,
        "min_trades": 2,
    }
    res = client.post("/api/simulate/optimize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "champion" in data
    assert "top_combinations" in data
    assert data["total_combinations_tested"] >= 0
    if data["champion"]:
        assert data["champion"]["rank"] == 1
        assert "buy_sub_id" in data["champion"]
        assert "sell_sub_id" in data["champion"]


def test_api_simulate_optimize_accumulation():
    payload = {
        "ticker": "PETR4.SA",
        "interval": "1d",
        "period": "1y",
        "simulation_mode": "accumulation",
        "contribution_amount": 1000.0,
        "initial_capital": 1000.0,
    }
    res = client.post("/api/simulate/optimize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["simulation_mode"] == "accumulation"
    assert "champion" in data
    assert "top_combinations" in data
    if data["champion"]:
        c = data["champion"]
        assert c["rank"] == 1
        assert c["buy_sub_id"] is not None
        assert c["sell_sub_id"] is None or c["sell_label"] == "-"
        assert c["simulation_mode"] == "accumulation"
        assert c["total_invested"] is not None
        assert c["final_equity"] is not None
        assert c["total_return_pct"] is not None
        assert c["closed_trades"] >= 1


def test_root_serves_spa():
    res = client.get("/")
    assert res.status_code == 200
    assert "Bottom Statistical Engine" in res.text


def test_asset_names_and_radar_items():
    from src.ui.theme import get_asset_name
    assert get_asset_name("GC=F") == "Gold (Ouro / XAUUSD)"
    assert get_asset_name("CL=F") == "Crude Oil WTI (Petróleo)"
    assert get_asset_name("EURUSD=X") == "EUR/USD"
    assert get_asset_name("BTC-USD") == "Bitcoin"
    assert get_asset_name("PETR4.SA") == "Petrobras PN"

    # Test /api/radar includes asset_name
    res = client.get("/api/radar?interval=1d&category=crypto")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) > 0
    for item in data["items"]:
        assert "asset_name" in item
        assert item["asset_name"] is not None
        assert len(item["asset_name"]) > 0



def test_api_portfolio_advise():
    payload = {
        "available_cash": 10000.0,
        "holdings": [
            {"ticker": "PETR4.SA", "shares": 50.0, "average_buy_price": 35.0}
        ],
        "universe_category": "custom",
        "custom_tickers": ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA"],
        "interval": "1d",
        "period": "1y",
        "max_weight_pct": 25.0,
        "rebalance_band_pct": 5.0,
        "min_rotation_score_delta": 15.0,
    }
    res = client.post("/api/portfolio/advise", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["current_cash"] == 10000.0
    assert data["total_portfolio_equity"] > 10000.0
    assert data["projected_cash_after"] >= 0.0
    assert "holdings_evaluated" in data
    assert len(data["holdings_evaluated"]) == 1
    assert data["holdings_evaluated"][0]["ticker"] == "PETR4.SA"
    assert "recommendations" in data
    assert "opportunity_ranking" in data
    assert len(data["opportunity_ranking"]) >= 3
