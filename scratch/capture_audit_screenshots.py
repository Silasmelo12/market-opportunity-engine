import sys
sys.path.insert(0, '.')
import time
import json
import pathlib
import uvicorn
import threading
from playwright.sync_api import sync_playwright
from src.api.server import app

OUTPUT_DIR = pathlib.Path(r"C:\Users\silas\.gemini\antigravity\brain\d0f3576a-db6a-41c4-aa36-5f7f1a92cb6f\screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HOLDINGS = [
    {"ticker": "PETR4.SA", "shares": 100, "average_buy_price": 32.50},
    {"ticker": "VALE3.SA", "shares": 50, "average_buy_price": 62.00},
    {"ticker": "WEGE3.SA", "shares": 80, "average_buy_price": 48.00},
    {"ticker": "HGLG11.SA", "shares": 30, "average_buy_price": 160.00},
    {"ticker": "BTC-USD", "shares": 0.05, "average_buy_price": 350000.00},
]

MONTHS = [
    "2025-11-28", "2025-12-28", "2026-01-28", "2026-02-28",
    "2026-03-28", "2026-04-28", "2026-05-28", "2026-06-28",
    "2026-07-28", "2026-08-28", "2026-09-28", "2026-10-28",
]

PORTFOLIO_PAYLOAD = {
    "availableCash": 5420.00,
    "holdings": HOLDINGS,
    "universeCategory": "featured",
    "interval": "1d",
    "period": "2y",
    "maxWeightPct": 25.0,
    "b3TotalIncome": 1450.80,
    "b3Timeline": [
        {"date": "2025-11", "invested": 22000.0, "profit": 1200.0, "total": 23200.0},
        {"date": "2026-02", "invested": 25000.0, "profit": 2100.0, "total": 27100.0},
        {"date": "2026-06", "invested": 29000.0, "profit": 3500.0, "total": 32500.0},
        {"date": "2026-10", "invested": 34000.0, "profit": 4800.0, "total": 38800.0},
    ],
    "b3MonthlyIncome": [
        {"month_year": m, "dividendos": 120.90, "jcp": 0.0, "rendimentos": 0.0, "total": 120.90}
        for m in MONTHS
    ],
}

SCREENS = [
    {"name": "visao_geral", "hash": "#carteira/visao-geral", "wait_sel": "#overview-total-equity"},
    {"name": "custodia", "hash": "#carteira/posicoes", "wait_sel": "#tab-portfolio"},
    {"name": "radar", "hash": "#quant/radar", "wait_sel": "#radar-table-body"},
    {"name": "grafico", "hash": "#quant/grafico?ticker=PETR4.SA", "wait_sel": "#active-asset-title"},
    {"name": "simulador", "hash": "#quant/simulador", "wait_sel": "#form-simulator"},
    {"name": "playbook", "hash": "#quant/playbook", "wait_sel": "#tab-playbook"},
]

PORT = 58888
config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="error")
server = uvicorn.Server(config)
t = threading.Thread(target=server.run, daemon=True)
t.start()
time.sleep(1.5)

print(f"Server started on port {PORT}. Launching Playwright...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    configs = [
        {"theme": "light", "width": 1600, "height": 1000, "label": "desktop_light"},
        {"theme": "dark", "width": 1600, "height": 1000, "label": "desktop_dark"},
        {"theme": "light", "width": 768, "height": 1024, "label": "tablet_light"},
        {"theme": "dark", "width": 768, "height": 1024, "label": "tablet_dark"},
    ]

    for cfg in configs:
        theme = cfg["theme"]
        w = cfg["width"]
        h = cfg["height"]
        lbl = cfg["label"]
        print(f"\n--- Capturing mode: {lbl} ({w}x{h}, {theme}) ---")

        context = browser.new_context(viewport={"width": w, "height": h})
        page = context.new_page()

        # Seed initial localStorage with portfolio data and theme
        page.goto(f"http://127.0.0.1:{PORT}/?e2e=1#carteira/visao-geral")
        page.evaluate(
            """({payload, theme}) => {
                localStorage.clear();
                localStorage.setItem('terminal_theme', theme);
                localStorage.setItem('market_engine_portfolio_v1', JSON.stringify(payload));
                document.documentElement.setAttribute('data-theme', theme);
            }""",
            {"payload": PORTFOLIO_PAYLOAD, "theme": theme}
        )

        for screen in SCREENS:
            sname = screen["name"]
            shash = screen["hash"]
            swait = screen["wait_sel"]

            target_url = f"http://127.0.0.1:{PORT}/?e2e=1{shash}"
            page.goto(target_url, wait_until="load")
            page.evaluate(f"document.documentElement.setAttribute('data-theme', '{theme}')")

            try:
                page.wait_for_selector(swait, state="visible", timeout=6000)
            except Exception as e:
                print(f"Warning: wait_for_selector {swait} timed out on {sname}: {e}")

            time.sleep(0.5)  # allow animations/plotly layout settling
            file_name = f"{sname}_{lbl}.png"
            out_path = OUTPUT_DIR / file_name
            page.screenshot(path=str(out_path), full_page=False)
            print(f"  Captured: {file_name} ({out_path.stat().st_size} bytes)")

        context.close()

    browser.close()

server.should_exit = True
print("\nAll screenshots captured successfully!")
