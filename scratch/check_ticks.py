import sys
sys.path.insert(0, '.')
import time
import uvicorn
import threading
from playwright.sync_api import sync_playwright
from src.api.server import app

MONTHS = [
    '2025-11-28', '2025-12-28', '2026-01-28', '2026-02-28',
    '2026-03-28', '2026-04-28', '2026-05-28', '2026-06-28',
    '2026-07-28', '2026-08-28', '2026-09-28', '2026-10-28'
]
TOTALS = [35.20, 142.50, 38.00, 45.10, 180.20, 46.00, 52.30, 220.40, 58.10, 61.40, 245.90, 68.20]
payload = {
    'availableCash': 10000,
    'holdings': [],
    'b3TotalIncome': sum(TOTALS),
    'b3Timeline': [],
    'b3MonthlyIncome': [{'month_year': m, 'dividendos': t, 'jcp': 0, 'rendimentos': 0, 'total': t} for m, t in zip(MONTHS, TOTALS)],
}

config = uvicorn.Config(app, host='127.0.0.1', port=59998, log_level='error')
server = uvicorn.Server(config)
t = threading.Thread(target=server.run, daemon=True)
t.start()
time.sleep(1.5)

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={'width': 1781, 'height': 702})
    page.goto('http://127.0.0.1:59998/#carteira/proventos')
    page.evaluate('(p) => { localStorage.setItem("mo_active_tab", "proventos"); localStorage.setItem("market_engine_portfolio_v1", JSON.stringify(p)); }', payload)
    page.reload(wait_until='load')
    page.wait_for_selector('#chart-proventos-detailed .barlayer .point path')
    print('Initial ticks:', page.eval_on_selector_all('#chart-proventos-detailed .xtick text', 'nodes => nodes.map(n => n.textContent)'))
    page.click('#btn-proventos-view-anual')
    time.sleep(1)
    res = page.evaluate('''() => {
        const c = document.getElementById('chart-proventos-detailed');
        return {
            bars: c.querySelectorAll('.barlayer .point path').length,
            xtick_text: [...c.querySelectorAll('.xtick text')].map(t => t.textContent),
            all_text: [...c.querySelectorAll('text')].map(t => t.textContent),
            trace_x: c.data ? c.data[0].x : null
        };
    }''')
    print('Result after click:', res)
    b.close()
server.should_exit = True
