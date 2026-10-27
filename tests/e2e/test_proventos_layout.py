"""Regressão visual E2E da aba de Proventos (Playwright + Chromium).

Este teste cobre o que os testes estáticos não conseguem: geometria real do
Plotly depois do layout do navegador. Ele falha se o gráfico voltar a escapar
do card, se o toggle Mensal/Anual parar de funcionar ou se mojibake reaparecer.

Requisitos (fora da suíte unitária):
    pip install -r requirements-dev.txt
    python -m playwright install chromium
Execução:
    pytest tests/e2e -v
"""

from __future__ import annotations

import re

import pytest

playwright_sync = pytest.importorskip(
    "playwright.sync_api",
    reason="Playwright não instalado; rode 'pip install -r requirements-dev.txt'.",
)

MONTHS = [
    "2025-11-28", "2025-12-28", "2026-01-28", "2026-02-28",
    "2026-03-28", "2026-04-28", "2026-05-28", "2026-06-28",
    "2026-07-28", "2026-08-28", "2026-09-28", "2026-10-28",
]
TOTALS = [35.20, 142.50, 38.00, 45.10, 180.20, 46.00,
          52.30, 220.40, 58.10, 61.40, 245.90, 68.20]


@pytest.fixture(scope="module")
def proventos_page(server_url):
    payload = {
        "availableCash": 10000,
        "holdings": [],
        "b3TotalIncome": sum(TOTALS),
        "b3Timeline": [],
        "b3MonthlyIncome": [
            {"month_year": month, "dividendos": total, "jcp": 0, "rendimentos": 0, "total": total}
            for month, total in zip(MONTHS, TOTALS)
        ],
    }

    with playwright_sync.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as exc:  # noqa: BLE001 - ambiente sem navegador
            pytest.skip(f"Chromium indisponível para o teste E2E: {exc}")

        context = browser.new_context(viewport={"width": 1781, "height": 702})
        page = context.new_page()
        page.goto(server_url, wait_until="load")
        page.evaluate(
            """(payload) => {
                history.replaceState(null, '', '/' + location.search);
                localStorage.removeItem('mo_active_route');
                localStorage.setItem('mo_active_tab', 'proventos');
                localStorage.setItem('market_engine_portfolio_v1', JSON.stringify(payload));
            }""",
            payload,
        )
        page.reload(wait_until="load")
        page.wait_for_function(
            """() => document.querySelectorAll(
                '#chart-proventos-detailed .barlayer .point path').length === 12""",
            timeout=25000,
        )
        yield page
        browser.close()


def test_proventos_chart_stays_inside_its_card(proventos_page):
    page = proventos_page
    assert page.locator("#tab-pane-proventos").is_visible()
    assert page.locator("#tab-overview").is_hidden()
    assert page.evaluate("localStorage.getItem('mo_active_tab')") == "proventos"

    geometry = page.evaluate(
        """() => {
            const container = document.getElementById('chart-proventos-detailed');
            const card = container.closest('.bg-white');
            const svg = container.querySelector('svg.main-svg');
            const rect = (el) => {
                const r = el.getBoundingClientRect();
                return {x: r.x, y: r.y, width: r.width, height: r.height,
                        right: r.right, bottom: r.bottom};
            };
            return {
                container: rect(container),
                card: rect(card),
                svg: svg ? rect(svg) : null,
                display: getComputedStyle(container).display,
                scrollWidth: document.documentElement.scrollWidth,
                innerWidth: window.innerWidth,
                bars: container.querySelectorAll('.barlayer .point path').length,
            };
        }"""
    )

    container = geometry["container"]
    card = geometry["card"]
    svg = geometry["svg"]

    tolerance = 1.5
    assert container["x"] >= card["x"] - tolerance
    assert container["right"] <= card["right"] + tolerance
    assert container["y"] >= card["y"] - tolerance
    assert container["bottom"] <= card["bottom"] + tolerance
    assert container["width"] > 0 and container["height"] > 0

    # O SVG do Plotly deve ocupar exatamente o host, não flutuar deslocado.
    assert svg is not None, "SVG do Plotly não encontrado"
    assert abs(svg["x"] - container["x"]) <= 2
    assert abs(svg["y"] - container["y"]) <= 2
    assert abs(svg["width"] - container["width"]) <= 2
    assert abs(svg["height"] - container["height"]) <= 2

    # O guard-rail de CSS precisa manter a raiz do Plotly como block.
    assert geometry["display"] == "block"
    assert geometry["bars"] == 12
    assert geometry["scrollWidth"] <= geometry["innerWidth"] + 1, "Página com overflow horizontal"


def test_proventos_toggle_and_labels(proventos_page):
    page = proventos_page

    mensal_ticks = page.eval_on_selector_all(
        "#chart-proventos-detailed .xtick text", "nodes => nodes.map(n => n.textContent)"
    )
    assert mensal_ticks[0] == "11/25"
    assert mensal_ticks[-1] == "10/26"

    page.click("#btn-proventos-view-anual")
    page.wait_for_function(
        """() => [...document.querySelectorAll('#chart-proventos-detailed .xtick text')]
            .map(n => n.textContent).join(',') === '2025,2026'""",
        timeout=10000,
    )
    assert page.get_attribute("#btn-proventos-view-anual", "aria-pressed") == "true"
    assert page.eval_on_selector_all(
        "#chart-proventos-detailed .barlayer .point path", "nodes => nodes.length"
    ) == 2

    page.click("#btn-proventos-view-mensal")
    page.wait_for_function(
        """() => [...document.querySelectorAll('#chart-proventos-detailed .xtick text')]
            .map(n => n.textContent).join(',') === '11/25,12/25,01/26,02/26,03/26,04/26,05/26,06/26,07/26,08/26,09/26,10/26'""",
        timeout=10000,
    )


def test_no_mojibake_in_visible_text(proventos_page):
    text = proventos_page.locator("body").inner_text()
    match = re.search(r"(?:Ã|Â)[\u0080-\u00bf]|â€|ï¸", text)
    assert match is None, f"Mojibake visível na UI: {text[max(0, match.start() - 40):match.end() + 40]!r}"
    assert "Evolução de Proventos" in text
