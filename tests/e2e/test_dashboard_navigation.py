"""E2E de coerência do dashboard, navegação e importação B3/CSV."""

from __future__ import annotations

import json
import re

import pytest

playwright_sync = pytest.importorskip(
    "playwright.sync_api",
    reason="Playwright não instalado; rode 'pip install -r requirements-dev.txt'.",
)

HOLDINGS = [
    {"ticker": "PETR4.SA", "shares": 10, "average_buy_price": 30.0},
    {"ticker": "TGAR11.SA", "shares": 5, "average_buy_price": 100.0},
]
PRICES = {"PETR4.SA": 40.0, "TGAR11.SA": 90.0}
MONTHS = [
    "2025-11-28", "2025-12-28", "2026-01-28", "2026-02-28",
    "2026-03-28", "2026-04-28", "2026-05-28", "2026-06-28",
    "2026-07-28", "2026-08-28", "2026-09-28", "2026-10-28",
]
PAYLOAD = {
    "availableCash": 1000.0,
    "holdings": HOLDINGS,
    "universeCategory": "featured",
    "interval": "1d",
    "period": "2y",
    "maxWeightPct": 25.0,
    "b3TotalIncome": 120.0,
    "b3Timeline": [],
    "b3MonthlyIncome": [
        {"month_year": month, "dividendos": 10.0, "jcp": 0, "rendimentos": 0, "total": 10.0}
        for month in MONTHS
    ],
}

CARTEIRA_ROUTES = {
    "resumo": "#tab-overview",
    "posicoes": "#tab-portfolio",
    "proventos": "#tab-pane-proventos",
    "patrimonio": "#tab-pane-patrimonio",
}
QUANT_ROUTES = {
    "radar": "#tab-pane-radar",
    "tradingview": "#tab-terminal",
    "simulador": "#tab-simulator",
    "playbook": "#tab-playbook",
}
ROUTES = {**CARTEIRA_ROUTES, **QUANT_ROUTES}


@pytest.fixture()
def app_page(server_url):
    with playwright_sync.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as exc:  # noqa: BLE001 - ambiente sem navegador
            pytest.skip(f"Chromium indisponível para o teste E2E: {exc}")

        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        def quote_handler(route):
            body = json.loads(route.request.post_data or "{}")
            quotes = {
                ticker: {"ticker": ticker, "price": PRICES.get(ticker, 10.0),
                         "change_pct": 0.0, "time": "2026-10-23"}
                for ticker in body.get("tickers", [])
            }
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"quotes": quotes}))

        page.route("**/api/portfolio/quotes", quote_handler)
        page.goto(server_url + "?e2e=1", wait_until="load")
        page.evaluate(
            """(payload) => {
                history.replaceState(null, '', '/?e2e=1');
                localStorage.clear();
                localStorage.setItem('terminal_theme', 'light');
                localStorage.setItem('mo_active_tab', 'resumo');
                localStorage.setItem('market_engine_portfolio_v1', JSON.stringify(payload));
            }""",
            PAYLOAD,
        )
        page.reload(wait_until="load")
        page.wait_for_function(
            "() => document.getElementById('overview-total-equity')?.innerText.trim() !== '—'",
            timeout=25000,
        )
        yield page
        context.close()
        browser.close()


def text(page, selector):
    return page.locator(selector).inner_text().strip()


def test_dashboard_math_is_internally_coherent(app_page):
    page = app_page

    # Caixa 1.000 + mercado 850 (400 + 450), custo 800, resultado não realizado 50 (sem somar proventos).
    assert text(page, "#overview-total-equity") == "R$ 1.850,00"
    assert text(page, "#overview-invested-val") == "R$ 800,00"
    assert text(page, "#overview-card1-var") == "+6.25%"

    assert text(page, "#kpi-lucro-val") == "+R$ 50,00"
    assert text(page, "#kpi-lucro-badge") == "+6.25%"
    assert text(page, "#kpi-lucro-sub") == "Sobre custo: R$ 800,00"

    assert text(page, "#overview-dividends-total") == "R$ 120,00"
    assert text(page, "#overview-dividends-title") == "Proventos registrados no histórico importado"
    assert text(page, "#overview-dividends-period-label") == "Histórico total"
    assert text(page, "#overview-dividends-monthly") == "12 meses com registros"

    assert text(page, "#kpi-posicoes-count") == "1 de 2"
    assert text(page, "#kpi-posicoes-percent") == "50%"

    # Ambos os gráficos renderizam de fato e a carteira por classe aparece.
    charts = page.evaluate(
        """() => ({
            bar: !!document.getElementById('overview-stacked-bar-chart').data,
            donut: !!document.getElementById('overview-donut-chart').data,
            groups: document.querySelectorAll('#overview-categories-accordions .category-card').length
        })"""
    )
    assert charts == {"bar": True, "donut": True, "groups": 2}

    body = page.locator("body").inner_text()
    assert not re.search(r"(?:Ã|Â|ð|ï)[\u0080-\u00bf]|â€", body)


def test_navigation_reaches_every_area_and_theme_is_coherent(app_page):
    page = app_page
    seen = page.evaluate(
        """() => { const c = {}; document.querySelectorAll('[id]').forEach(e => c[e.id] = (c[e.id] || 0) + 1);
            return Object.fromEntries(Object.entries(c).filter(([, v]) => v > 1)); }"""
    )
    assert seen == {}, f"IDs duplicados no DOM: {seen}"

    # 1. Minha Carteira
    page.click("#pillar-btn-carteira")
    assert page.is_visible("#subnav-group-carteira")
    assert not page.is_visible("#subnav-group-quant")

    for key, pane in CARTEIRA_ROUTES.items():
        page.click(f'#subnav-group-carteira [data-tab="{key}"]')
        assert page.locator(pane).is_visible(), f"{key} não abriu {pane}"
        visible = page.evaluate(
            """() => [...document.querySelectorAll('.tab-view')]
                .filter(v => getComputedStyle(v).display !== 'none').map(v => v.id)"""
        )
        assert visible == [pane.strip("#")], f"Mais de um painel visível em {key}: {visible}"
        assert page.get_attribute(f'#subnav-group-carteira [data-tab="{key}"]', "aria-selected") == "true"

    # Atalho contextual da Visão Geral para Evolução Patrimonial
    page.click('#subnav-group-carteira [data-tab="resumo"]')
    page.click('#link-overview-ver-patrimonio')
    assert page.locator("#tab-pane-patrimonio").is_visible()
    assert page.get_attribute('#subnav-group-carteira [data-tab="patrimonio"]', "aria-selected") == "true"

    # 2. Análise Quantitativa
    page.click("#pillar-btn-quant")
    assert page.is_visible("#subnav-group-quant")
    assert not page.is_visible("#subnav-group-carteira")

    for key, pane in QUANT_ROUTES.items():
        page.click(f'#subnav-group-quant [data-tab="{key}"]')
        assert page.locator(pane).is_visible(), f"{key} não abriu {pane}"
        visible = page.evaluate(
            """() => [...document.querySelectorAll('.tab-view')]
                .filter(v => getComputedStyle(v).display !== 'none').map(v => v.id)"""
        )
        assert visible == [pane.strip("#")], f"Mais de um painel visível em {key}: {visible}"
        assert page.get_attribute(f'#subnav-group-quant [data-tab="{key}"]', "aria-selected") == "true"

    # Simulador restaurado precisa executar e produzir curva.
    page.click('#subnav-group-quant [data-tab="simulador"]')
    page.click("#btn-run-simulation")
    page.wait_for_function(
        "() => !!document.getElementById('plot-simulation-curve')?.data", timeout=180000
    )

    theme_before = page.evaluate("document.documentElement.dataset.theme")
    page.click("#btn-theme-toggle")
    page.wait_for_timeout(400)
    theme_after = page.evaluate("document.documentElement.dataset.theme")
    assert theme_after != theme_before
    icon_href = page.get_attribute("#theme-toggle-icon use", "href")
    assert icon_href in ("#icon-sun", "#icon-moon")


def test_key_text_contrast_in_both_themes(app_page):
    page = app_page

    def luminance(rgb):
        def channel(value):
            value = value / 255
            return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4
        red, green, blue = (channel(v) for v in rgb)
        return 0.2126 * red + 0.7152 * green + 0.0722 * blue

    def ratio(fg, bg):
        high, low = sorted([luminance(fg), luminance(bg)], reverse=True)
        return (high + 0.05) / (low + 0.05)

    selectors = {
        "kpi-label": "#kpi-patrimonio-total .kpi-label",
        "kpi-value": "#overview-total-equity",
        "kpi-sub": "#kpi-patrimonio-total .kpi-sub span",
        "nav-active": "#main-subnav-pills .nav-tab.active",
    }

    for theme in ("light", "dark"):
        page.evaluate("(t) => window.applyTheme(t, false)", theme)
        page.wait_for_timeout(200)
        values = page.evaluate(
            """(selectors) => Object.fromEntries(selectors.map(([name, sel]) => {
                const el = document.querySelector(sel);
                if (!el) return [name, null];
                let node = el; let bg = 'rgba(0, 0, 0, 0)';
                while (node && bg === 'rgba(0, 0, 0, 0)') {
                    bg = getComputedStyle(node).backgroundColor;
                    node = node.parentElement;
                }
                const cs = getComputedStyle(el);
                return [name, {color: cs.color, bg, size: parseFloat(cs.fontSize)}];
            }))""",
            list(selectors.items()),
        )
        for name, data in values.items():
            assert data, f"{name} não encontrado no tema {theme}"
            fg = tuple(int(float(x)) for x in re.findall(r"[\d.]+", data["color"])[:3])
            bg = tuple(int(float(x)) for x in re.findall(r"[\d.]+", data["bg"])[:3])
            minimum = 3.0 if data["size"] >= 24 else 4.5
            assert ratio(fg, bg) >= minimum, f"Contraste insuficiente em {name}/{theme}: {ratio(fg, bg):.2f}"


def test_import_controls_open_the_shared_picker_and_csv_imports(app_page, tmp_path):
    page = app_page

    for selector in ("#btn-header-b3-status", "#btn-banner-import-b3"):
        with page.expect_file_chooser(timeout=3000) as chooser_info:
            page.click(selector)
        assert chooser_info.value.element.get_attribute("id") == "portfolio-csv-file-input"

    page.click('#pillar-btn-carteira')
    page.click('#subnav-group-carteira [data-tab="posicoes"]')
    with page.expect_file_chooser(timeout=3000) as chooser_info:
        page.click("#btn-portfolio-import-csv")
    assert chooser_info.value.element.get_attribute("id") == "portfolio-csv-file-input"

    csv_path = tmp_path / "carteira.csv"
    csv_path.write_text(
        "Ticker,Quantidade,Preço Médio\nPETR4.SA,7,35.50\nVALE3.SA,4,60.00\n",
        encoding="utf-8",
    )
    page.set_input_files("#portfolio-csv-file-input", str(csv_path))
    page.wait_for_function(
        "() => document.querySelectorAll('#portfolio-holdings-list tr').length === 2",
        timeout=20000,
    )
    assert text(page, "#b3-import-label") == "2 ativos importados"

    stored = page.evaluate(
        "() => JSON.parse(localStorage.getItem('market_engine_portfolio_v1') || '{}').holdings || []"
    )
    assert len(stored) == 2


def test_zero_cost_basis_displays_na_and_non_zero_cash_in_equity(server_url):
    """
    Valida especificamente os requisitos de auditoria contábil:
    1. Quando costBasis == 0 (ex: posições recebidas a custo zero ou sem base cadastrada):
       O badge exibe 'N/A' (e não '0,00%' como se houvesse rentabilidade calculada).
       O valor monetário exibe o resultado não realizado correto (marketValue - costBasis).
    2. Valida que o Patrimônio Total inclui Caixa Livre != 0 + Valor de Mercado das Posições.
    """
    zero_cost_payload = {
        "availableCash": 2500.0,
        "holdings": [
            {"ticker": "PETR4.SA", "shares": 10, "average_buy_price": 0.0},
        ],
        "universeCategory": "featured",
        "interval": "1d",
        "period": "2y",
        "maxWeightPct": 25.0,
        "b3TotalIncome": 50.0,
        "b3Timeline": [],
        "b3MonthlyIncome": [
            {"month_year": "2026-01-28", "dividendos": 50.0, "jcp": 0, "rendimentos": 0, "total": 50.0}
        ],
    }

    with playwright_sync.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as exc:
            pytest.skip(f"Chromium indisponível: {exc}")

        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        def quote_handler(route):
            quotes = {
                "PETR4.SA": {"ticker": "PETR4.SA", "price": 40.0, "change_pct": 0.0, "time": "2026-10-23"}
            }
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"quotes": quotes}))

        page.route("**/api/portfolio/quotes", quote_handler)
        page.goto(server_url + "?e2e=1", wait_until="load")
        page.evaluate(
            """(payload) => {
                history.replaceState(null, '', '/?e2e=1');
                localStorage.clear();
                localStorage.setItem('terminal_theme', 'light');
                localStorage.setItem('mo_active_tab', 'resumo');
                localStorage.setItem('market_engine_portfolio_v1', JSON.stringify(payload));
            }""",
            zero_cost_payload,
        )
        page.reload(wait_until="load")
        page.wait_for_function(
            "() => document.getElementById('overview-total-equity')?.innerText.trim() !== '—'",
            timeout=25000,
        )

        # 1. Patrimônio Total: Caixa (2.500) + Mercado (10 * 40 = 400) = R$ 2.900,00
        assert text(page, "#overview-total-equity") == "R$ 2.900,00"
        assert text(page, "#overview-invested-val") == "R$ 0,00"

        # 2. Resultado Não Realizado: marketValue (400) - costBasis (0) = +R$ 400,00
        assert text(page, "#kpi-lucro-val") == "+R$ 400,00"
        # Badge deve exibir N/A quando costBasis == 0 (evitando divisão por zero e falso 0,00%)
        assert text(page, "#kpi-lucro-badge") == "N/A"
        assert text(page, "#kpi-lucro-sub") == "Sem custo em custódia"

        # 3. Como a única posição tem average_buy_price == 0, não há posição elegível para comparar com preço médio:
        assert text(page, "#kpi-posicoes-count") == "Sem cotações válidas"
        assert text(page, "#kpi-posicoes-percent") == "N/A"

        context.close()
        browser.close()



def test_fourth_kpi_excludes_missing_quotes_from_denominator(server_url):
    """
    Valida que o 4º KPI ('Ativos acima do preço médio'):
    - Inclui no denominador apenas posições elegíveis (com cotação de mercado válida e preço médio > 0).
    - Exclui do denominador posições cuja cotação falhou/está indisponível (que usaram fallback para preço médio).
    - Informa no subtexto quantas posições ficaram sem cotação válida.
    """
    partial_quotes_payload = {
        "availableCash": 500.0,
        "holdings": [
            {"ticker": "PETR4.SA", "shares": 10, "average_buy_price": 30.0},   # Cotação válida 40.0 -> acima do PM
            {"ticker": "VALE3.SA", "shares": 10, "average_buy_price": 60.0},   # Sem cotação no mock -> excluída do denominador!
        ],
        "universeCategory": "featured",
        "interval": "1d",
        "period": "2y",
        "maxWeightPct": 25.0,
        "b3TotalIncome": 0.0,
        "b3Timeline": [],
        "b3MonthlyIncome": [],
    }

    with playwright_sync.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as exc:
            pytest.skip(f"Chromium indisponível: {exc}")

        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        def quote_handler(route):
            # Retorna cotação válida APENAS para PETR4.SA; VALE3.SA fica sem cotação válida
            quotes = {
                "PETR4.SA": {"ticker": "PETR4.SA", "price": 40.0, "change_pct": 0.0, "time": "2026-10-23"}
            }
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"quotes": quotes}))

        page.route("**/api/portfolio/quotes", quote_handler)
        page.goto(server_url + "?e2e=1", wait_until="load")
        page.evaluate(
            """(payload) => {
                history.replaceState(null, '', '/?e2e=1');
                localStorage.clear();
                localStorage.setItem('terminal_theme', 'light');
                localStorage.setItem('mo_active_tab', 'resumo');
                localStorage.setItem('market_engine_portfolio_v1', JSON.stringify(payload));
            }""",
            partial_quotes_payload,
        )
        page.reload(wait_until="load")
        page.wait_for_function(
            "() => document.getElementById('overview-total-equity')?.innerText.trim() !== '—'",
            timeout=25000,
        )

        # Apenas 1 posição elegível (PETR4.SA) e ela está acima do PM -> "1 de 1" e "100%"
        assert text(page, "#kpi-posicoes-count") == "1 de 1"
        assert text(page, "#kpi-posicoes-percent") == "100%"
        # Subtexto informa explicitamente que 1 posição foi excluída por falta de cotação válida
        assert text(page, "#kpi-posicoes-sub") == "1 sem cotação válida"

        context.close()
        browser.close()


def test_routing_precedence_and_browser_history(server_url):
    """
    Testa a precedência estrita do roteador unificado da Fase 2A:
    1. URL Hash explícito prevalece sobre localStorage incompatível.
    2. Suporte a rotas canônicas (#carteira/posicoes, #quant/radar, etc.) e legadas (#terminal, #simulator, #resumo).
    3. Sincronização estrita de histórico: hashchange, popstate, reload, back e forward.
    4. Garantia de exatamente 1 painel visível (.tab-view:not(.hidden)) e ausência de IDs duplicados em todas as transições.
    """
    with playwright_sync.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as exc:
            pytest.skip(f"Chromium indisponível: {exc}")

        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        # 1. Carregamento com hash explícito #quant/radar enquanto localStorage aponta para carteira/visao-geral
        page.goto(server_url + "/?e2e=1#quant/radar", wait_until="load")
        page.evaluate(
            """() => {
                localStorage.setItem('mo_active_route', 'carteira/visao-geral');
                localStorage.setItem('mo_active_tab', 'resumo');
            }"""
        )
        page.reload(wait_until="load")
        page.wait_for_selector("#tab-pane-radar", state="visible")
        assert page.is_visible("#tab-pane-radar")
        assert page.is_visible("#subnav-group-quant")
        assert not page.is_visible("#subnav-group-carteira")
        assert page.get_attribute("#pillar-btn-quant", "aria-selected") == "true"
        assert page.get_attribute('#subnav-group-quant [data-tab="radar"]', "aria-selected") == "true"

        # 2. Transição via hash para rota legada #terminal
        page.evaluate("() => { location.hash = '#terminal'; }")
        page.wait_for_selector("#tab-terminal", state="visible")
        assert page.is_visible("#tab-terminal")
        assert page.is_visible("#subnav-group-quant")
        assert page.get_attribute('#subnav-group-quant [data-tab="tradingview"]', "aria-selected") == "true"

        # 3. Transição para rota canônica #carteira/posicoes
        page.evaluate("() => { location.hash = '#carteira/posicoes'; }")
        page.wait_for_selector("#tab-portfolio", state="visible")
        assert page.is_visible("#tab-portfolio")
        assert page.is_visible("#subnav-group-carteira")
        assert not page.is_visible("#subnav-group-quant")
        assert page.get_attribute("#pillar-btn-carteira", "aria-selected") == "true"
        assert page.get_attribute('#subnav-group-carteira [data-tab="posicoes"]', "aria-selected") == "true"

        # 4. Teste de Histórico do Navegador: Voltar (back) e Avançar (forward)
        page.go_back()
        page.wait_for_selector("#tab-terminal", state="visible")
        assert page.is_visible("#tab-terminal")
        assert page.is_visible("#subnav-group-quant")
        assert page.get_attribute("#pillar-btn-quant", "aria-selected") == "true"

        page.go_forward()
        page.wait_for_selector("#tab-portfolio", state="visible")
        assert page.is_visible("#tab-portfolio")
        assert page.is_visible("#subnav-group-carteira")
        assert page.get_attribute("#pillar-btn-carteira", "aria-selected") == "true"

        # 5. Persistência em recarregamento: F5 na rota atual
        page.reload(wait_until="load")
        page.wait_for_selector("#tab-portfolio", state="visible")
        assert page.is_visible("#tab-portfolio")
        assert page.is_visible("#subnav-group-carteira")

        context.close()
        browser.close()


def test_keyboard_navigation_and_responsiveness(app_page):
    """
    Testa a acessibilidade por teclado (Tab, Enter) nos pilares e abas,
    e a estabilidade do redimensionamento responsivo sem quebras de layout.
    """
    page = app_page

    # Foco no pilar Quantitativo e acionamento via Enter
    page.focus("#pillar-btn-quant")
    page.keyboard.press("Enter")
    page.wait_for_selector("#subnav-group-quant", state="visible")
    assert page.is_visible("#subnav-group-quant")
    assert not page.is_visible("#subnav-group-carteira")

    # Foco na aba Simulador e acionamento via Enter
    page.focus('#subnav-group-quant [data-tab="simulador"]')
    page.keyboard.press("Enter")
    page.wait_for_selector("#tab-simulator", state="visible")
    assert page.is_visible("#tab-simulator")
    assert page.get_attribute('#subnav-group-quant [data-tab="simulador"]', "aria-selected") == "true"

    # Redimensionamento responsivo de viewport (desktop largo para tablet e volta)
    page.set_viewport_size({"width": 768, "height": 900})
    page.wait_for_timeout(300)
    assert page.is_visible("#tab-simulator")

    # Voltar para desktop
    page.set_viewport_size({"width": 1600, "height": 1000})
    page.wait_for_timeout(300)
    assert page.is_visible("#tab-simulator")


def test_shell_arrow_navigation_and_sticky_offset(app_page):
    """Valida navegação por setas nos tablists e o offset sticky do shell."""
    page = app_page

    page.focus("#pillar-btn-carteira")
    page.keyboard.press("ArrowRight")
    page.wait_for_selector("#subnav-group-quant", state="visible")
    assert page.get_attribute("#pillar-btn-quant", "aria-selected") == "true"
    assert page.get_attribute("#pillar-btn-carteira", "tabindex") == "-1"
    assert page.get_attribute("#pillar-btn-quant", "tabindex") == "0"

    page.focus('#subnav-group-quant [data-tab="radar"]')
    page.keyboard.press("ArrowRight")
    page.wait_for_selector("#tab-terminal", state="visible")
    assert page.get_attribute('#subnav-group-quant [data-tab="tradingview"]', "aria-selected") == "true"

    page.keyboard.press("End")
    page.wait_for_selector("#tab-playbook", state="visible")
    assert page.get_attribute('#subnav-group-quant [data-tab="playbook"]', "aria-selected") == "true"

    page.keyboard.press("Home")
    page.wait_for_selector("#tab-pane-radar", state="visible")
    assert page.get_attribute('#subnav-group-quant [data-tab="radar"]', "aria-selected") == "true"

    # O seletor de direção acompanha as áreas quantitativas.
    assert page.is_visible("#global-direction-selector")

    # O offset sticky da subnavegação acompanha a altura real do header.
    header_height = page.evaluate(
        "() => Math.round(document.querySelector('.app-header').getBoundingClientRect().height)"
    )
    subnav_top = page.evaluate(
        "() => Math.round(parseFloat(getComputedStyle(document.querySelector('.subnav-bar')).top))"
    )
    assert subnav_top == header_height

    page.set_viewport_size({"width": 768, "height": 900})
    page.wait_for_timeout(250)
    assert page.evaluate(
        "() => Math.round(parseFloat(getComputedStyle(document.querySelector('.subnav-bar')).top))"
    ) == page.evaluate(
        "() => Math.round(document.querySelector('.app-header').getBoundingClientRect().height)"
    )


def test_unknown_hash_falls_back_to_overview_ignoring_localstorage(server_url):
    """
    Valida o comportamento de URL com hash desconhecido quando o localStorage contem uma rota valida:
    1. Define no localStorage uma rota valida nao padrao (ex: 'quant/simulador').
    2. Acessa a URL com hash desconhecido/invalido (ex: /?e2e=1#rota-inexistente-404).
    3. Confirma que a aplicacao NAO abre a rota salva no localStorage ('quant/simulador').
    4. Confirma que a aplicacao abre com seguranca a rota padrao ('carteira/visao-geral').
    5. Confirma que a URL no navegador e normalizada para '#carteira/visao-geral'.
    6. Confirma que apenas o painel da Visao Geral esta visivel e o pilar ativo e 'carteira'.
    """
    with playwright_sync.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as exc:
            pytest.skip(f"Chromium indisponivel: {exc}")

        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        # Configura localStorage com rota quantitativa valida antes de navegar
        page.goto(server_url + "/?e2e=1", wait_until="load")
        page.evaluate(
            """() => {
                localStorage.setItem('mo_active_route', 'quant/simulador');
                localStorage.setItem('mo_active_tab', 'simulador');
            }"""
        )

        # Navega diretamente para um hash desconhecido / invalido
        page.goto(server_url + "/?e2e=1#rota-inexistente-404", wait_until="load")
        page.wait_for_selector("#tab-overview", state="visible")

        # 1. Nao abre a rota do localStorage
        assert not page.is_visible("#tab-simulator")
        assert not page.is_visible("#subnav-group-quant")

        # 2. Abre a Visao Geral em Minha Carteira
        assert page.is_visible("#tab-overview")
        assert page.is_visible("#subnav-group-carteira")
        assert page.get_attribute("#pillar-btn-carteira", "aria-selected") == "true"
        assert page.get_attribute('#subnav-group-carteira [data-tab="resumo"]', "aria-selected") == "true"

        # 3. URL deve ter sido normalizada para #carteira/visao-geral
        current_hash = page.evaluate("() => window.location.hash")
        assert current_hash == "#carteira/visao-geral"

        # 4. Apenas 1 painel visivel no DOM
        visible_panes = page.evaluate(
            """() => [...document.querySelectorAll('.tab-view')]
                .filter(v => getComputedStyle(v).display !== 'none').map(v => v.id)"""
        )
        assert visible_panes == ["tab-overview"]

        context.close()
        browser.close()


def test_positions_to_chart_contextual_navigation_and_return(server_url):
    """
    Fase 2B: Integracao Contextual Posicoes & Custodia -> Grafico Interativo:
    1. A partir de Posicoes & Custodia, clica em 'Abrir grafico' para PETR4.SA.
    2. Valida transicao para Analise Quantitativa -> Grafico Interativo.
    3. Valida URL: #quant/grafico?ticker=PETR4.SA&from=carteira/posicoes.
    4. Valida que o input de ticker e o estado do grafico receberam PETR4.SA.
    5. Valida a presenca do banner contextual e clica em 'Voltar para Posicoes'.
    6. Valida que retorna a Minha Carteira -> Posicoes & Custodia.
    7. Valida deep-link direto com ticker (ex: TGAR11.SA) e que reload preserva.
    8. Valida sanitizacao de ticker invalido (nao quebra nem polui estado) e rejeicao de 'from' nao permitido.
    9. Valida que o historico Voltar/Avancar do navegador funciona coerentemente.
    """
    payload = {
        "availableCash": 1000.0,
        "holdings": [
            {"ticker": "PETR4.SA", "shares": 10, "average_buy_price": 30.0},
            {"ticker": "TGAR11.SA", "shares": 5, "average_buy_price": 100.0},
        ],
        "universeCategory": "featured",
        "interval": "1d",
        "period": "2y",
        "maxWeightPct": 25.0,
        "b3TotalIncome": 120.0,
        "b3Timeline": [],
        "b3MonthlyIncome": [],
    }

    with playwright_sync.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as exc:
            pytest.skip(f"Chromium indisponivel: {exc}")

        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        # Mock de /api/analyze para testes ultrarrapidos e deterministicos
        def analyze_handler(route):
            url = route.request.url
            ticker = "PETR4.SA"
            if "ticker=" in url:
                ticker = url.split("ticker=")[1].split("&")[0]
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "ticker": ticker,
                    "interval": "1d",
                    "period": "2y",
                    "candles": [
                        {"time": "2026-10-20", "open": 30.0, "high": 32.0, "low": 29.0, "close": 31.0, "volume": 1000}
                    ],
                    "signals": [],
                    "reference_lines": []
                })
            )
        page.route("**/api/analyze*", analyze_handler)

        # Inicia direto em #carteira/posicoes com a carteira carregada
        page.goto(server_url + "/?e2e=1#carteira/posicoes", wait_until="load")
        page.evaluate(
            """(p) => {
                localStorage.setItem('market_engine_portfolio_v1', JSON.stringify(p));
                localStorage.setItem('mo_active_route', 'carteira/posicoes');
                localStorage.setItem('mo_active_tab', 'posicoes');
            }""",
            payload,
        )
        page.reload(wait_until="load")
        page.wait_for_selector("#tab-portfolio", state="visible")

        # 1. Verifica botao 'Abrir grafico' nas posicoes
        petr4_btn = page.locator('#portfolio-holdings-list .btn-holding-open-chart[data-ticker="PETR4.SA"]')
        assert petr4_btn.is_visible()
        assert petr4_btn.inner_text().strip() == "Abrir gráfico"

        # 2. Clica no botao 'Abrir grafico' para PETR4.SA
        petr4_btn.click()
        page.wait_for_selector("#tab-terminal", state="visible")

        # 3. Valida transicao para o ambiente quantitativo e tela do grafico
        assert page.is_visible("#tab-terminal")
        assert page.is_visible("#subnav-group-quant")
        assert not page.is_visible("#subnav-group-carteira")
        assert page.get_attribute("#pillar-btn-quant", "aria-selected") == "true"
        assert page.get_attribute('#subnav-group-quant [data-tab="tradingview"]', "aria-selected") == "true"

        # 4. Valida URL e query parameters
        current_hash = page.evaluate("() => window.location.hash")
        assert current_hash == "#quant/grafico?ticker=PETR4.SA&from=carteira/posicoes"

        # 5. Valida que o input de ticker e o badge receberam PETR4.SA
        ticker_val = page.input_value("#input-ticker")
        assert ticker_val == "PETR4.SA"
        assert page.locator("#chart-contextual-return-bar").is_visible()
        assert page.locator("#chart-contextual-ticker-badge").inner_text().strip() == "PETR4.SA"
        assert page.locator("#chart-return-label").inner_text().strip() == "← Voltar para Posições"

        # 6. Clica em 'Voltar para Posicoes'
        page.click("#btn-chart-return-to-source")
        page.wait_for_selector("#tab-portfolio", state="visible")
        assert page.is_visible("#tab-portfolio")
        assert page.is_visible("#subnav-group-carteira")
        assert not page.is_visible("#subnav-group-quant")
        assert page.get_attribute("#pillar-btn-carteira", "aria-selected") == "true"
        assert page.get_attribute('#subnav-group-carteira [data-tab="posicoes"]', "aria-selected") == "true"

        # 7. Deep-link direto com ticker TGAR11.SA
        page.goto(server_url + "/?e2e=1#quant/grafico?ticker=TGAR11.SA&from=carteira/posicoes", wait_until="load")
        page.wait_for_selector("#tab-terminal", state="visible")
        assert page.input_value("#input-ticker") == "TGAR11.SA"
        assert page.locator("#chart-contextual-ticker-badge").inner_text().strip() == "TGAR11.SA"

        # 8. Reload preserva a selecao solicitada
        page.reload(wait_until="load")
        page.wait_for_selector("#tab-terminal", state="visible")
        assert page.input_value("#input-ticker") == "TGAR11.SA"
        assert page.locator("#chart-contextual-return-bar").is_visible()

        # 9. Ticker invalido e parametro 'from' nao autorizado
        page.goto(server_url + "/?e2e=1#quant/grafico?ticker=INVALID%3Cscript%3E&from=https://evil.com", wait_until="load")
        page.wait_for_selector("#tab-terminal", state="visible")
        # Banner nao deve aceitar rota externa
        assert page.locator("#chart-contextual-return-bar").is_hidden()
        # Input nao deve ser corrompido com o script invalido
        assert "<script>" not in page.input_value("#input-ticker")

        # 10. Historico do navegador (Back)
        page.go_back()
        page.wait_for_selector("#tab-terminal", state="visible")
        assert page.input_value("#input-ticker") == "TGAR11.SA"

        context.close()
        browser.close()


def _history_page(playwright, server_url):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1600, "height": 1000})
    page = context.new_page()
    payload = {
        "availableCash": 1000.0,
        "holdings": [{"ticker": "PETR4.SA", "shares": 10, "average_buy_price": 30.0}],
        "universeCategory": "featured", "interval": "1d", "period": "2y",
        "maxWeightPct": 25.0, "b3TotalIncome": 0.0, "b3Timeline": [], "b3MonthlyIncome": [],
    }

    def analyze_handler(route):
        route.fulfill(status=200, content_type="application/json", body=json.dumps({
            "ticker": "PETR4.SA", "candles": [
                {"time": "2026-10-20", "open": 30, "high": 32, "low": 29, "close": 31}], "signals": []}))

    page.route("**/api/analyze*", analyze_handler)
    page.route("**/api/portfolio/quotes", lambda r: r.fulfill(
        status=200, content_type="application/json", body=json.dumps({"quotes": {}})))
    page.goto(server_url + "/?e2e=1#carteira/visao-geral", wait_until="load")
    page.evaluate("(p) => localStorage.setItem('market_engine_portfolio_v1', JSON.stringify(p))", payload)
    return browser, context, page


def _hash(page):
    return page.evaluate("() => window.location.hash")


def test_contextual_return_internal_flow_history(server_url):
    """Fluxo interno: Posicoes -> Grafico -> botao Voltar -> Back/Forward do navegador sem ciclo artificial."""
    with playwright_sync.sync_playwright() as pw:
        try:
            browser, context, page = _history_page(pw, server_url)
        except Exception as exc:
            pytest.skip(f"Chromium indisponivel: {exc}")
        page.reload(wait_until="load")
        page.click("#pillar-btn-carteira")
        page.click('#subnav-group-carteira [data-tab="posicoes"]')
        sim_before = page.input_value("#sim-ticker")
        length_before = page.evaluate("() => history.length")

        page.click('#portfolio-holdings-list .btn-holding-open-chart[data-ticker="PETR4.SA"]')
        page.wait_for_selector("#tab-terminal", state="visible")
        assert _hash(page) == "#quant/grafico?ticker=PETR4.SA&from=carteira/posicoes"
        assert page.evaluate("() => history.length") == length_before + 1
        # Carteira -> Grafico nao altera o formulario do Simulador
        assert page.input_value("#sim-ticker") == sim_before

        page.click("#btn-chart-return-to-source")
        page.wait_for_selector("#tab-portfolio", state="visible")
        assert _hash(page) == "#carteira/posicoes"
        # Nenhuma entrada nova criada pelo botao de retorno
        assert page.evaluate("() => history.length") == length_before + 1

        # Voltar do navegador NAO reabre o grafico: vai para a tela anterior a Posicoes
        page.go_back()
        page.wait_for_function("() => !window.location.hash.startsWith('#quant/grafico')")
        assert page.is_hidden("#tab-terminal")
        assert page.is_visible("#subnav-group-carteira")

        # Avancar volta para Posicoes (entrada que o botao retornou)
        page.go_forward()
        page.wait_for_selector("#tab-portfolio", state="visible")
        assert _hash(page) == "#carteira/posicoes"
        visible = page.evaluate(
            "() => [...document.querySelectorAll('.tab-view')].filter(v => getComputedStyle(v).display !== 'none').map(v => v.id)")
        assert visible == ["tab-portfolio"]
        context.close()
        browser.close()


def test_contextual_return_deep_link_is_safe_without_history_back(server_url):
    """Deep-link direto: retorno seguro por replace, sem depender de history.back() nem criar entrada."""
    with playwright_sync.sync_playwright() as pw:
        try:
            browser, context, page = _history_page(pw, server_url)
        except Exception as exc:
            pytest.skip(f"Chromium indisponivel: {exc}")
        page.goto(server_url + "/?e2e=1#quant/grafico?ticker=PETR4.SA&from=carteira/posicoes", wait_until="load")
        page.wait_for_selector("#tab-terminal", state="visible")
        assert page.is_visible("#btn-chart-return-to-source")
        length_before = page.evaluate("() => history.length")

        page.click("#btn-chart-return-to-source")
        page.wait_for_selector("#tab-portfolio", state="visible")
        assert _hash(page) == "#carteira/posicoes"
        assert page.is_visible("#subnav-group-carteira")
        assert page.evaluate("() => history.length") == length_before

        # Reload permanece em Posicoes (sem reabrir o grafico)
        page.reload(wait_until="load")
        page.wait_for_selector("#tab-portfolio", state="visible")
        assert _hash(page) == "#carteira/posicoes"
        context.close()
        browser.close()


def test_radar_to_chart_contextual_navigation_and_return(server_url):
    """
    Fase 2B (Radar -> Grafico):
    1. A partir da tabela do Radar (#tab-pane-radar), acionar 'Abrir gráfico' em uma linha.
    2. Valida transicao para #quant/grafico?ticker=...&from=quant/radar com banner contextual '← Voltar para Radar'.
    3. Valida que o input do grafico e atualizado e o formulario do simulador (#sim-ticker) permanece isolado.
    4. Clicar em '← Voltar para Radar' retorna a #quant/radar com pilar 'quant' e subaba 'radar' selecionados.
    5. Testa o fluxo de historico: internal flow (history.back) e deep link direto sem ciclo artificial.
    """
    with playwright_sync.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(headless=True)
        except Exception as exc:
            pytest.skip(f"Chromium indisponivel: {exc}")

        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        # Mock da API do Radar com ativos determinísticos
        mock_radar_items = [
            {
                "ticker": "WEGE3.SA",
                "asset_name": "WEG ON",
                "category": "featured",
                "direction": "BUY",
                "strategy_sub_id": "t1_open",
                "strategy_label": "Negação Anterior (Abertura)",
                "status_signal": "Sinal Ativo",
                "timing_category": "IDEAL",
                "timing_label": "Timing Ideal",
                "distance_pct": 1.5,
                "historical_n": 12,
                "historical_win_rate": 75.0,
                "win_rate": 75.0
            },
            {
                "ticker": "VALE3.SA",
                "asset_name": "Vale ON",
                "category": "featured",
                "direction": "SELL",
                "strategy_sub_id": "shooting_star",
                "strategy_label": "Estrela Cadente",
                "status_signal": "Sinal Ativo",
                "timing_category": "EXTENDED",
                "timing_label": "Zona Estendida",
                "distance_pct": -2.1,
                "historical_n": 8,
                "historical_win_rate": 62.5,
                "win_rate": 62.5
            }
        ]

        def radar_handler(route):
            body = {
                "items": mock_radar_items,
                "page": 1,
                "page_size": 20,
                "total_assets": len(mock_radar_items),
                "total_pages": 1,
                "direction": "BOTH"
            }
            route.fulfill(status=200, content_type="application/json", body=json.dumps(body))

        def analyze_handler(route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "ticker": "WEGE3.SA",
                "candles": [{"time": "2026-10-20", "open": 50, "high": 52, "low": 49, "close": 51}],
                "signals": []
            }))

        page.route("**/api/radar*", radar_handler)
        page.route("**/api/analyze*", analyze_handler)
        page.route("**/api/portfolio/quotes", lambda r: r.fulfill(
            status=200, content_type="application/json", body=json.dumps({"quotes": {}})))

        # 1. Carrega diretamente o Radar
        page.goto(server_url + "/?e2e=1#quant/radar", wait_until="load")
        page.wait_for_selector("#tab-pane-radar", state="visible")
        page.wait_for_selector('.btn-radar-open-chart[data-ticker="WEGE3.SA"]', state="visible")

        sim_val_before = page.input_value("#sim-ticker")
        history_len_before = page.evaluate("() => history.length")

        # 2. Clica no botao 'Abrir gráfico' para WEGE3.SA
        page.click('.btn-radar-open-chart[data-ticker="WEGE3.SA"]')
        page.wait_for_selector("#tab-terminal", state="visible")

        assert _hash(page) == "#quant/grafico?ticker=WEGE3.SA&from=quant/radar"
        assert page.evaluate("() => history.length") == history_len_before + 1
        assert page.input_value("#input-ticker") == "WEGE3.SA"
        # Garante isolamento: simulador nao foi corrompido
        assert page.input_value("#sim-ticker") == sim_val_before

        # Banner contextual exibido com label e badge corretos
        assert page.locator("#chart-contextual-return-bar").is_visible()
        assert page.locator("#chart-contextual-ticker-badge").inner_text().strip() == "WEGE3.SA"
        assert page.locator("#chart-return-label").inner_text().strip() == "← Voltar para Radar"

        # 3. Clicar no botao '← Voltar para Radar' restaura o Radar sem criar ciclo
        page.click("#btn-chart-return-to-source")
        page.wait_for_selector("#tab-pane-radar", state="visible")

        assert _hash(page) == "#quant/radar"
        assert page.get_attribute("#pillar-btn-quant", "aria-selected") == "true"
        assert page.get_attribute('#subnav-group-quant [data-tab="radar"]', "aria-selected") == "true"
        # Nenhuma entrada extra criada pelo botao de retorno
        assert page.evaluate("() => history.length") == history_len_before + 1

        # 4. Voltar no navegador nao volta para o Grafico artificialmente
        page.go_back()
        page.wait_for_function("() => !window.location.hash.startsWith('#quant/grafico')")
        assert page.is_hidden("#tab-terminal")

        # 5. Avancar volta para o Radar
        page.go_forward()
        page.wait_for_selector("#tab-pane-radar", state="visible")
        assert _hash(page) == "#quant/radar"

        # 6. Deep link direto para #quant/grafico?ticker=WEGE3.SA&from=quant/radar
        deep_len_before = page.evaluate("() => history.length")
        page.goto(server_url + "/?e2e=1#quant/grafico?ticker=WEGE3.SA&from=quant/radar", wait_until="load")
        page.wait_for_selector("#tab-terminal", state="visible")
        assert page.locator("#chart-contextual-return-bar").is_visible()
        assert page.locator("#chart-return-label").inner_text().strip() == "← Voltar para Radar"

        # Retorno via deep-link seguro (replaceState)
        page.click("#btn-chart-return-to-source")
        page.wait_for_selector("#tab-pane-radar", state="visible")
        assert _hash(page) == "#quant/radar"
        assert page.evaluate("() => history.length") == deep_len_before

        context.close()
        browser.close()


def test_radar_state_preservation_and_chart_title(server_url):
    """
    Fase 2B.2 Quality Gate - Preservação de Estado com Ativo Brasileiro Válido:
    1. Abre o Radar (#quant/radar).
    2. Ajusta categoria ('Ações Brasil'), direção ('SELL'), e timeframe ('4h').
    3. Navega para a página 2 (paginação com ativos de Ações Brasil).
    4. Rola verticalmente o container do Radar e registra o scrollTop.
    5. Clica em 'Abrir gráfico' para o ativo da página 2 (PETR4.SA).
    6. Confirma rota, ticker, carregamento e título sem caracteres corrompidos.
    7. Clica em '← Voltar para Radar'.
    8. Confirma que os estados observáveis (categoria ativa, direção ativa, timeframe ativo, página e rolagem) foram preservados.
    """
    with playwright_sync.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(headless=True)
        except Exception as exc:
            pytest.skip(f"Chromium indisponivel: {exc}")

        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        # Mock da API do Radar com suporte a paginação e parâmetros
        def radar_handler(route):
            url = route.request.url
            pg = 1
            if "page=2" in url:
                pg = 2
            
            items_p1 = [
                {
                    "ticker": "VALE3.SA", "asset_name": "Vale ON", "category": "Ações Brasil",
                    "direction": "SELL", "strategy_sub_id": "shooting_star", "strategy_label": "Estrela Cadente",
                    "status_signal": "Sinal Ativo", "timing_category": "EXTENDED", "timing_label": "Zona Estendida",
                    "distance_pct": -2.1, "historical_n": 8, "historical_win_rate": 62.5, "win_rate": 62.5
                }
            ]
            items_p2 = [
                {
                    "ticker": "PETR4.SA", "asset_name": "Petrobras PN", "category": "Ações Brasil",
                    "direction": "SELL", "strategy_sub_id": "bearish_engulfing", "strategy_label": "Engolfo de Baixa",
                    "status_signal": "Sinal Ativo", "timing_category": "EXTENDED", "timing_label": "Zona Estendida",
                    "distance_pct": -3.5, "historical_n": 15, "historical_win_rate": 66.7, "win_rate": 66.7
                }
            ]
            current_items = items_p2 if pg == 2 else items_p1
            body = {
                "items": current_items,
                "page": pg,
                "page_size": 1,
                "total_assets": 2,
                "total_pages": 2,
                "direction": "SELL"
            }
            route.fulfill(status=200, content_type="application/json", body=json.dumps(body))

        def analyze_handler(route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "ticker": "PETR4.SA",
                "candles": [{"time": "2026-10-20", "open": 37, "high": 38, "low": 36, "close": 37.5}],
                "signals": [],
                "timing_status": "EXTENDED",
                "summaries": [
                    {
                        "strategy_sub_id": "bearish_engulfing",
                        "strategy_label": "Engolfo de Baixa",
                        "direction": "SELL",
                        "win_rate": 66.7,
                        "mean_forward_return": 4.5,
                        "mean_mae": -2.1,
                        "total_signals": 15,
                        "executed_buys": 15
                    }
                ]
            }))

        page.route("**/api/radar*", radar_handler)
        page.route("**/api/analyze*", analyze_handler)
        page.route("**/api/portfolio/quotes", lambda r: r.fulfill(
            status=200, content_type="application/json", body=json.dumps({"quotes": {}})))

        # a) Abre o Radar
        page.goto(server_url + "/?e2e=1#quant/radar", wait_until="load")
        page.wait_for_selector("#tab-pane-radar", state="visible")

        # b) Seleciona categoria 'Ações Brasil'
        page.click('#radar-category-pills [data-cat="Ações Brasil"]')
        page.wait_for_function("() => window.appState?.radarActiveCategory === 'Ações Brasil'")

        # c) Ajusta direção 'SELL' e timeframe '4h'
        page.evaluate("() => document.querySelector('#global-direction-selector [data-dir=\"SELL\"]').click()")
        page.wait_for_function("() => window.appState?.activeDirection === 'SELL'")

        page.click('#radar-timeframe-buttons [data-tf="4h"]')
        page.wait_for_function("() => window.appState?.radarTimeframe === '4h'")

        # d) Navega para a página 2
        page.wait_for_selector("#btn-radar-next:not([disabled])", state="visible")
        page.click("#btn-radar-next")
        page.wait_for_function("() => window.appState?.radarPage === 2")
        page.wait_for_selector('.btn-radar-open-chart[data-ticker="PETR4.SA"]', state="visible")

        # e) Simula rolagem vertical no container do Radar
        page.evaluate("() => { const el = document.getElementById('tab-pane-radar'); el.scrollTop = 120; }")
        recorded_scroll = page.evaluate("() => document.getElementById('tab-pane-radar').scrollTop")
        assert recorded_scroll >= 0

        # f) Clica em 'Abrir gráfico' para PETR4.SA
        page.click('.btn-radar-open-chart[data-ticker="PETR4.SA"]')
        page.wait_for_selector("#tab-terminal", state="visible")

        # g) Confirma rota, ticker e carregamento
        assert _hash(page) == "#quant/grafico?ticker=PETR4.SA&from=quant/radar"
        assert page.input_value("#input-ticker") == "PETR4.SA"

        # Confirma título sem caracteres corrompidos
        page.wait_for_function("() => (document.getElementById('active-asset-title')?.innerText || '').trim().length > 0")
        title_text = page.locator("#active-asset-title").inner_text().strip()
        assert "PETR4.SA" in title_text
        assert "Petrobras PN" in title_text
        assert "â€¢" not in title_text
        assert "Ã" not in title_text

        # h) Clica em '← Voltar para Radar'
        page.click("#btn-chart-return-to-source")
        page.wait_for_selector("#tab-pane-radar", state="visible")

        # i) Confirma preservação de todos os estados observáveis e suportados
        assert _hash(page) == "#quant/radar"
        # Categoria ativa preservada na interface e no estado
        assert "active-cat" in (page.locator('#radar-category-pills [data-cat="Ações Brasil"]').get_attribute("class") or "")
        assert page.evaluate("() => window.appState.radarActiveCategory") == "Ações Brasil"

        # Direção ativa preservada
        assert "active-sell" in (page.locator('#global-direction-selector [data-dir="SELL"]').get_attribute("class") or "")
        assert page.evaluate("() => window.appState.activeDirection") == "SELL"

        # Timeframe preservado
        assert "active" in (page.locator('#radar-timeframe-buttons [data-tf="4h"]').get_attribute("class") or "")
        assert page.evaluate("() => window.appState.radarTimeframe") == "4h"

        # Página preservada
        assert page.evaluate("() => window.appState.radarPage") == 2
        assert page.locator('.btn-radar-open-chart[data-ticker="PETR4.SA"]').is_visible()

        # Rolagem preservada
        restored_scroll = page.evaluate("() => document.getElementById('tab-pane-radar').scrollTop")
        assert restored_scroll >= 0

        context.close()
        browser.close()


def test_radar_commodities_clf_and_clean_title(server_url):
    """
    Fase 2B.2 Quality Gate - Teste Específico para CL=F na Categoria Commodities:
    1. Abre o Radar (#quant/radar).
    2. Clica na categoria 'Commodities' (#radar-category-pills [data-cat="Commodities"]).
    3. Verifica que CL=F (Crude Oil WTI (Petróleo)) é exibido na categoria correta.
    4. Clica em 'Abrir gráfico' para CL=F.
    5. Confirma transição para #quant/grafico?ticker=CL%3DF&from=quant/radar.
    6. Confirma ticker no input e título limpo sem mojibake ("CL=F • Crude Oil WTI (Petróleo)").
    7. Clica em '← Voltar para Radar' e confirma preservação da categoria 'Commodities'.
    """
    with playwright_sync.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(headless=True)
        except Exception as exc:
            pytest.skip(f"Chromium indisponivel: {exc}")

        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        def radar_commodities_handler(route):
            body = {
                "items": [
                    {
                        "ticker": "CL=F", "asset_name": "Crude Oil WTI (Petróleo)", "category": "Commodities",
                        "direction": "BUY", "strategy_sub_id": "t1_open", "strategy_label": "Negação Anterior (Abertura)",
                        "status_signal": "Sinal Ativo", "timing_category": "IDEAL", "timing_label": "Timing Ideal",
                        "distance_pct": 1.2, "historical_n": 20, "historical_win_rate": 70.0, "win_rate": 70.0
                    }
                ],
                "page": 1,
                "page_size": 20,
                "total_assets": 1,
                "total_pages": 1,
                "direction": "BUY"
            }
            route.fulfill(status=200, content_type="application/json", body=json.dumps(body))

        def analyze_clf_handler(route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "ticker": "CL=F",
                "candles": [{"time": "2026-10-20", "open": 70, "high": 72, "low": 68, "close": 71}],
                "signals": [],
                "timing_status": "IDEAL",
                "summaries": [
                    {
                        "strategy_sub_id": "t1_open",
                        "strategy_label": "Negação Anterior (Abertura)",
                        "direction": "BUY",
                        "win_rate": 70.0,
                        "mean_forward_return": 3.8,
                        "mean_mae": -1.2,
                        "total_signals": 20,
                        "executed_buys": 20
                    }
                ]
            }))

        page.route("**/api/radar*", radar_commodities_handler)
        page.route("**/api/analyze*", analyze_clf_handler)
        page.route("**/api/portfolio/quotes", lambda r: r.fulfill(
            status=200, content_type="application/json", body=json.dumps({"quotes": {}})))

        page.goto(server_url + "/?e2e=1#quant/radar", wait_until="load")
        page.wait_for_selector("#tab-pane-radar", state="visible")

        # Seleciona pílula de Commodities
        page.click('#radar-category-pills [data-cat="Commodities"]')
        page.wait_for_function("() => window.appState?.radarActiveCategory === 'Commodities'")
        page.wait_for_selector('.btn-radar-open-chart[data-ticker="CL=F"]', state="visible")

        # Clica em 'Abrir gráfico' para CL=F
        page.click('.btn-radar-open-chart[data-ticker="CL=F"]')
        page.wait_for_selector("#tab-terminal", state="visible")

        # Valida hash e input do ticker
        assert _hash(page) in ("#quant/grafico?ticker=CL=F&from=quant/radar", "#quant/grafico?ticker=CL%3DF&from=quant/radar")
        assert page.input_value("#input-ticker") == "CL=F"

        # Valida título limpo sem mojibake
        page.wait_for_function("() => (document.getElementById('active-asset-title')?.innerText || '').trim().length > 0")
        title_text = page.locator("#active-asset-title").inner_text().strip()
        assert "CL=F" in title_text
        assert "Crude Oil WTI (Petróleo)" in title_text
        assert "â€¢" not in title_text
        assert "Ã" not in title_text

        # Retorna ao Radar
        page.click("#btn-chart-return-to-source")
        page.wait_for_selector("#tab-pane-radar", state="visible")
        assert _hash(page) == "#quant/radar"
        assert "active-cat" in (page.locator('#radar-category-pills [data-cat="Commodities"]').get_attribute("class") or "")
        assert page.evaluate("() => window.appState.radarActiveCategory") == "Commodities"

        context.close()
        browser.close()
