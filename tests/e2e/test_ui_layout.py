"""Invariantes E2E do layout unificado (Feature 023).

Cobre: tema claro padrão e persistência, um único painel visível, ausência de
IDs duplicados, sincronização ARIA, tabelas com rolagem contida, navegação por
teclado e preferência por movimento reduzido.
"""

from __future__ import annotations

import json

import pytest

playwright_sync = pytest.importorskip(
    "playwright.sync_api",
    reason="Playwright não instalado; rode 'pip install -r requirements-dev.txt'.",
)

AREAS = {
    "resumo": ("carteira/visao-geral", "tab-overview", "carteira"),
    "posicoes": ("carteira/posicoes", "tab-portfolio", "carteira"),
    "proventos": ("carteira/proventos", "tab-pane-proventos", "carteira"),
    "patrimonio": ("carteira/patrimonio", "tab-pane-patrimonio", "carteira"),
    "radar": ("quant/radar", "tab-pane-radar", "quant"),
    "grafico": ("quant/grafico", "tab-terminal", "quant"),
    "simulador": ("quant/simulador", "tab-simulator", "quant"),
    "playbook": ("quant/playbook", "tab-playbook", "quant"),
}

DATA_TAB = {
    "resumo": "resumo",
    "posicoes": "posicoes",
    "proventos": "proventos",
    "patrimonio": "patrimonio",
    "radar": "radar",
    "grafico": "tradingview",
    "simulador": "simulador",
    "playbook": "playbook",
}

PAYLOAD = {
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


def _mock_routes(page) -> None:
    def quotes(route):
        body = json.loads(route.request.post_data or "{}")
        data = {
            ticker: {"ticker": ticker, "price": 40.0, "change_pct": 0.0, "time": "2026-10-23"}
            for ticker in body.get("tickers", [])
        }
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"quotes": data}))

    def radar(route):
        route.fulfill(status=200, content_type="application/json", body=json.dumps({
            "items": [{
                "ticker": "PETR4.SA", "asset_name": "Petrobras PN", "category": "Ações Brasil",
                "direction": "BUY", "strategy_sub_id": "t1_open",
                "strategy_label": "Negação Anterior (Abertura)", "status_signal": "Sinal Ativo",
                "timing_category": "IDEAL", "timing_label": "Timing Ideal", "distance_pct": 1.5,
                "historical_n": 12, "historical_win_rate": 75.0, "win_rate": 75.0,
            }],
            "page": 1, "page_size": 20, "total_assets": 1, "total_pages": 1, "direction": "BOTH",
        }))

    def analyze(route):
        route.fulfill(status=200, content_type="application/json", body=json.dumps({
            "ticker": "PETR4.SA",
            "candles": [{"time": "2026-10-20", "open": 30, "high": 32, "low": 29, "close": 31, "volume": 1000}],
            "signals": [], "reference_lines": [],
        }))

    page.route("**/api/portfolio/quotes", quotes)
    page.route("**/api/radar*", radar)
    page.route("**/api/analyze*", analyze)


@pytest.fixture()
def layout_page(server_url):
    with playwright_sync.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as exc:  # noqa: BLE001 - ambiente sem navegador
            pytest.skip(f"Chromium indisponível: {exc}")
        context = browser.new_context(viewport={"width": 1366, "height": 900})
        page = context.new_page()
        _mock_routes(page)
        page.goto(server_url + "/?e2e=1", wait_until="load")
        page.evaluate(
            "(payload) => { localStorage.clear(); localStorage.setItem('market_engine_portfolio_v1', JSON.stringify(payload)); }",
            PAYLOAD,
        )
        yield page, server_url
        context.close()
        browser.close()


def _visible_panels(page):
    return page.evaluate(
        "() => [...document.querySelectorAll('.tab-view')]"
        ".filter(v => getComputedStyle(v).display !== 'none').map(v => v.id)"
    )


def test_theme_defaults_to_light_and_persists(server_url):
    with playwright_sync.sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 900})
        page = context.new_page()
        _mock_routes(page)

        page.goto(server_url + "/?e2e=1", wait_until="load")
        page.wait_for_timeout(300)
        assert page.evaluate("document.documentElement.dataset.theme") == "light"

        page.click("#btn-theme-toggle")
        page.wait_for_timeout(200)
        assert page.evaluate("document.documentElement.dataset.theme") == "dark"
        assert page.evaluate("localStorage.getItem('terminal_theme')") == "dark"

        page.reload(wait_until="load")
        page.wait_for_timeout(300)
        assert page.evaluate("document.documentElement.dataset.theme") == "dark"

        page.evaluate("localStorage.setItem('terminal_theme', 'valor-invalido')")
        page.reload(wait_until="load")
        page.wait_for_timeout(300)
        assert page.evaluate("document.documentElement.dataset.theme") == "light"

        context.close()
        browser.close()


def test_single_panel_unique_ids_and_aria_for_all_areas(layout_page):
    page, base = layout_page
    for name, (route, panel, pillar) in AREAS.items():
        page.goto(f"{base}/?e2e=1#{route}", wait_until="load")
        page.wait_for_selector(f"#{panel}", state="visible", timeout=15000)
        assert _visible_panels(page) == [panel], f"{name}: painéis visíveis incorretos"

        duplicates = page.evaluate(
            """() => { const c = {};
                document.querySelectorAll('[id]').forEach(e => c[e.id] = (c[e.id] || 0) + 1);
                return Object.fromEntries(Object.entries(c).filter(([, v]) => v > 1)); }"""
        )
        assert duplicates == {}, f"{name}: IDs duplicados {duplicates}"

        selected = page.evaluate(
            """() => [...document.querySelectorAll('#main-subnav-pills .nav-tab[aria-selected="true"]')].length"""
        )
        assert selected == 1, f"{name}: esperado 1 item de subnav ativo, obtido {selected}"
        assert page.get_attribute(f"#pillar-btn-{pillar}", "aria-selected") == "true"


def test_tables_scroll_inside_their_container(layout_page):
    page, base = layout_page
    for name, (route, panel, _) in AREAS.items():
        page.goto(f"{base}/?e2e=1#{route}", wait_until="load")
        page.wait_for_selector(f"#{panel}", state="visible", timeout=15000)
        report = page.evaluate(
            """() => [...document.querySelectorAll('table')].map(table => {
                let node = table.parentElement;
                let scroller = null;
                while (node) {
                    const overflowX = getComputedStyle(node).overflowX;
                    if (overflowX === 'auto' || overflowX === 'scroll') { scroller = node; break; }
                    node = node.parentElement;
                }
                return {id: table.id || table.className, scrollable: !!scroller};
            })"""
        )
        assert all(item["scrollable"] for item in report), f"{name}: tabela sem contêiner rolável: {report}"

    for width in (375, 768, 1366, 1920):
        page.set_viewport_size({"width": width, "height": 900})
        page.wait_for_timeout(200)
        overflow = page.evaluate(
            "() => ({ doc: document.documentElement.scrollWidth, win: window.innerWidth })"
        )
        assert overflow["doc"] <= overflow["win"] + 1, f"Overflow horizontal global em {width}px: {overflow}"


def test_keyboard_navigation_reaches_every_area(layout_page):
    page, base = layout_page
    page.goto(f"{base}/?e2e=1#carteira/visao-geral", wait_until="load")
    page.wait_for_selector("#tab-overview", state="visible")

    page.focus("#pillar-btn-quant")
    page.keyboard.press("Enter")
    page.wait_for_selector("#subnav-group-quant", state="visible")

    for key, (_, panel, _) in AREAS.items():
        if key not in {"radar", "grafico", "simulador", "playbook"}:
            continue
        tab = DATA_TAB[key]
        page.focus(f'#subnav-group-quant [data-tab="{tab}"]')
        page.keyboard.press("Enter")
        page.wait_for_selector(f"#{panel}", state="visible", timeout=15000)
        assert page.get_attribute(f'#subnav-group-quant [data-tab="{tab}"]', "aria-selected") == "true"

    page.focus("#pillar-btn-carteira")
    page.keyboard.press("Enter")
    page.wait_for_selector("#subnav-group-carteira", state="visible")
    for key, (_, panel, _) in AREAS.items():
        if key not in {"resumo", "posicoes", "proventos", "patrimonio"}:
            continue
        tab = DATA_TAB[key]
        page.focus(f'#subnav-group-carteira [data-tab="{tab}"]')
        page.keyboard.press("Enter")
        page.wait_for_selector(f"#{panel}", state="visible", timeout=15000)
        assert page.get_attribute(f'#subnav-group-carteira [data-tab="{tab}"]', "aria-selected") == "true"


def test_both_themes_apply_to_every_area(layout_page):
    page, base = layout_page
    for name, (route, panel, _) in AREAS.items():
        page.goto(f"{base}/?e2e=1#{route}", wait_until="load")
        page.wait_for_selector(f"#{panel}", state="visible", timeout=15000)
        for theme in ("light", "dark"):
            page.evaluate("(t) => window.applyTheme(t, false)", theme)
            page.wait_for_timeout(120)
            assert page.evaluate("document.documentElement.dataset.theme") == theme
            colors = page.evaluate(
                """() => {
                    const el = document.getElementById('tab-overview') || document.body;
                    const cs = getComputedStyle(document.body);
                    return {bg: cs.backgroundColor, color: cs.color};
                }"""
            )
            assert colors["bg"] != colors["color"], f"{name}/{theme}: texto e fundo idênticos"


def test_portfolio_areas_share_cards_and_banner_state(layout_page):
    page, base = layout_page
    page.goto(f"{base}/?e2e=1#carteira/visao-geral", wait_until="load")
    page.wait_for_selector("#tab-overview", state="visible")

    assert page.locator("#investidor10-welcome-banner").is_hidden()
    assert page.locator("#tab-overview .kpi-card").count() == 4
    assert page.locator("#tab-overview .chart-card").count() == 2

    page.goto(f"{base}/?e2e=1#carteira/posicoes", wait_until="load")
    page.wait_for_selector("#tab-portfolio", state="visible")
    assert page.locator("#tab-portfolio .category-card.card-surface").count() >= 1
    page.goto(f"{base}/?e2e=1#carteira/visao-geral", wait_until="load")
    page.wait_for_selector("#tab-overview", state="visible")
    assert page.locator("#tab-overview table.table-standard").count() >= 1

    page.goto(f"{base}/?e2e=1#carteira/proventos", wait_until="load")
    page.wait_for_selector("#tab-pane-proventos", state="visible")
    assert page.locator("#tab-pane-proventos .chart-card").count() == 1
    assert page.get_attribute("#btn-proventos-view-mensal", "aria-pressed") == "true"
    page.click("#btn-proventos-view-anual")
    page.wait_for_timeout(150)
    assert page.get_attribute("#btn-proventos-view-anual", "aria-pressed") == "true"
    assert page.get_attribute("#btn-proventos-view-mensal", "aria-pressed") == "false"

    page.goto(f"{base}/?e2e=1#carteira/patrimonio", wait_until="load")
    page.wait_for_selector("#tab-pane-patrimonio", state="visible")
    assert page.locator("#tab-pane-patrimonio .chart-card").count() == 1


def test_portfolio_cards_adapt_to_theme_tokens(layout_page):
    page, base = layout_page
    page.goto(f"{base}/?e2e=1#carteira/visao-geral", wait_until="load")
    page.wait_for_selector("#tab-overview", state="visible")

    def card_colors():
        return page.evaluate(
            """() => {
                const card = document.querySelector('#tab-overview .kpi-card');
                const cs = getComputedStyle(card);
                return {bg: cs.backgroundColor, border: cs.borderColor, color: getComputedStyle(card.querySelector('.section-title, .kpi-label')).color};
            }"""
        )

    light = card_colors()
    page.evaluate("() => window.applyTheme('dark', false)")
    page.wait_for_timeout(150)
    dark = card_colors()
    assert light["bg"] != dark["bg"]
    assert light["border"] != dark["border"]


QUANT_AREAS = {
    "radar": (
        "quant/radar",
        "tab-pane-radar",
        [".kpi-card", ".segmented", ".filter-chip", ".table-standard", ".btn-primary"],
    ),
    "grafico": (
        "quant/grafico",
        "tab-terminal",
        [".chart-sidebar", ".chart-shell", ".strategy-group", ".segmented", ".input"],
    ),
    "simulador": (
        "quant/simulador",
        "tab-simulator",
        [".card-surface", ".input", ".btn-primary", ".kpi-card", ".chart-card", ".table-standard"],
    ),
    "playbook": (
        "quant/playbook",
        "tab-playbook",
        [".playbook-group-title", ".playbook-block"],
    ),
}


def test_quant_areas_use_shared_semantic_system(layout_page):
    page, base = layout_page
    legacy_pattern = (
        r"(^|\s)("
        r"(bg|border|divide)-(fintech|gray)-|"
        r"text-(fintech|gray|white|cyan|emerald|rose|amber|sky|blue|slate)-|"
        r"bg-black"
        r")"
    )
    for name, (route, panel, selectors) in QUANT_AREAS.items():
        page.goto(f"{base}/?e2e=1#{route}", wait_until="load")
        page.wait_for_selector(f"#{panel}", state="visible", timeout=15000)
        if name == "radar":
            page.wait_for_selector("#radar-table-body tr", timeout=15000)
        page.wait_for_timeout(250)

        assert page.locator(f"#{panel}.quant-area").count() == 1, f"{name}: sem .quant-area"
        for selector in selectors:
            assert page.locator(f"#{panel} {selector}").count() >= 1, f"{name}: falta {selector}"

        legacy = page.evaluate(
            """([id, pattern]) => {
                const root = document.getElementById(id);
                const re = new RegExp(pattern);
                return [...root.querySelectorAll('*')]
                    .filter(el => re.test(el.className || ''))
                    .map(el => el.className)
                    .slice(0, 5);
            }""",
            [panel, legacy_pattern],
        )
        assert legacy == [], f"{name}: classes legadas remanescentes {legacy}"


def test_quant_areas_adapt_to_theme_tokens(layout_page):
    page, base = layout_page
    page.goto(f"{base}/?e2e=1#quant/radar", wait_until="load")
    page.wait_for_selector("#tab-pane-radar", state="visible", timeout=15000)
    page.wait_for_timeout(250)

    def colors():
        return page.evaluate(
            """() => {
                const root = document.getElementById('tab-pane-radar');
                const card = root.querySelector('.kpi-card');
                const cs = getComputedStyle(root);
                const cc = getComputedStyle(card);
                return {rootBg: cs.backgroundColor, cardBg: cc.backgroundColor, cardColor: cc.color};
            }"""
        )

    light = colors()
    page.evaluate("() => window.applyTheme('dark', false)")
    page.wait_for_timeout(200)
    dark = colors()

    assert light["rootBg"] != dark["rootBg"]
    assert light["cardBg"] != dark["cardBg"]
    assert dark["cardColor"] != dark["rootBg"]


def test_reduced_motion_suppresses_non_essential_animation(server_url):
    with playwright_sync.sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 900}, reduced_motion="reduce")
        page = context.new_page()
        _mock_routes(page)
        page.goto(server_url + "/?e2e=1", wait_until="load")
        page.wait_for_selector("#tab-overview", state="visible")
        duration = page.evaluate(
            "() => getComputedStyle(document.querySelector('#btn-theme-toggle')).transitionDuration"
        )
        values = [float(v.replace('s', '')) for v in duration.split(',')]
        assert max(values) <= 0.001, f"Movimento reduzido não suprimiu transições: {duration}"
        context.close()
        browser.close()


def _has_visible_focus_indicator(info: dict) -> bool:
    if info.get("outlineStyle") not in (None, "none"):
        try:
            if float(str(info.get("outlineWidth", "0")).replace("px", "")) > 0:
                return True
        except ValueError:
            pass
    return info.get("boxShadow") not in (None, "none")


def test_keyboard_focus_indicator_is_visible(layout_page):
    page, base = layout_page
    page.goto(f"{base}/?e2e=1#quant/radar", wait_until="load")
    page.wait_for_selector("#tab-pane-radar", state="visible")

    focused = []
    for _ in range(14):
        page.keyboard.press("Tab")
        info = page.evaluate(
            """() => {
                const el = document.activeElement;
                if (!el || el === document.body) return null;
                const cs = getComputedStyle(el);
                return {
                    tag: el.tagName,
                    id: el.id || '',
                    text: (el.textContent || '').trim().slice(0, 30),
                    outlineStyle: cs.outlineStyle,
                    outlineWidth: cs.outlineWidth,
                    boxShadow: cs.boxShadow,
                };
            }"""
        )
        if info:
            focused.append(info)

    assert len(focused) >= 8, f"Poucos controles alcançados por Tab: {focused}"
    missing = [item for item in focused if not _has_visible_focus_indicator(item)]
    assert missing == [], f"Controles sem indicador de foco visível: {missing}"


def test_scrollable_tables_support_keyboard_scrolling(layout_page):
    page, base = layout_page
    page.goto(f"{base}/?e2e=1#carteira/posicoes", wait_until="load")
    page.wait_for_selector("#tab-portfolio", state="visible")
    page.wait_for_timeout(300)

    focusable = page.evaluate(
        """() => [...document.querySelectorAll('#tab-portfolio .table-scroll')]
            .filter(el => el.getAttribute('tabindex') === '0').length"""
    )
    total = page.locator("#tab-portfolio .table-scroll").count()
    assert focusable == total and total >= 1, f"Regiões roláveis focáveis: {focusable}/{total}"

    handle = page.evaluate_handle(
        """() => [...document.querySelectorAll('#tab-portfolio .table-scroll[tabindex="0"]')]
            .find(el => el.scrollWidth > el.clientWidth + 1) || null"""
    )
    element = handle.as_element()
    assert element is not None, "Nenhuma tabela larga encontrada em Posições"
    element.focus()
    for _ in range(4):
        page.keyboard.press("ArrowRight")
    page.wait_for_timeout(150)
    scroll_left = page.evaluate("(el) => el.scrollLeft", element)
    assert scroll_left > 0, "A tabela focável não respondeu às setas do teclado"


def test_live_regions_and_accessible_names(layout_page):
    page, base = layout_page
    page.goto(f"{base}/?e2e=1#quant/radar", wait_until="load")
    page.wait_for_selector("#tab-pane-radar", state="visible")

    assert page.get_attribute("#toast-notification", "role") == "status"
    assert page.get_attribute("#toast-notification", "aria-live") == "polite"
    assert page.get_attribute("#loading-spinner", "role") == "status"
    assert page.get_attribute("#loading-spinner", "aria-live") == "polite"

    unnamed = page.evaluate(
        """() => [...document.querySelectorAll('button, [role="button"], a')]
            .filter(el => {
                const r = el.getBoundingClientRect();
                if (r.width === 0 || r.height === 0) return false;
                const name = (el.getAttribute('aria-label') || el.getAttribute('title') || el.textContent || '').trim();
                return name === '';
            })
            .map(el => el.outerHTML.slice(0, 120))"""
    )
    assert unnamed == [], f"Controles sem nome acessível: {unnamed}"

    assert page.get_attribute("#btn-theme-toggle", "aria-pressed") == "false"
    page.click("#btn-theme-toggle")
    page.wait_for_timeout(150)
    assert page.get_attribute("#btn-theme-toggle", "aria-pressed") == "true"

    pressed = page.evaluate(
        """() => [...document.querySelectorAll('#global-direction-selector .dir-seg-btn')]
            .map(b => [b.dataset.dir, b.getAttribute('aria-pressed')])"""
    )
    assert sum(1 for _, value in pressed if value == "true") == 1, pressed
    page.click('#global-direction-selector .dir-seg-btn[data-dir="SELL"]')
    page.wait_for_timeout(100)
    assert page.get_attribute('#global-direction-selector .dir-seg-btn[data-dir="SELL"]', "aria-pressed") == "true"
    assert page.get_attribute('#global-direction-selector .dir-seg-btn[data-dir="BUY"]', "aria-pressed") == "false"

    timeframe = page.evaluate(
        """() => [...document.querySelectorAll('#radar-timeframe-buttons .radar-tf-btn')]
            .map(b => [b.dataset.tf, b.getAttribute('aria-pressed')])"""
    )
    assert sum(1 for _, value in timeframe if value == "true") == 1, timeframe
    page.click('#radar-timeframe-buttons .radar-tf-btn[data-tf="1wk"]')
    page.wait_for_timeout(200)
    assert page.get_attribute('#radar-timeframe-buttons .radar-tf-btn[data-tf="1wk"]', "aria-pressed") == "true"


def test_all_areas_respect_reference_widths(layout_page):
    page, base = layout_page
    for name, (route, panel, _) in AREAS.items():
        page.goto(f"{base}/?e2e=1#{route}", wait_until="load")
        page.wait_for_selector(f"#{panel}", state="visible", timeout=15000)
        for width in (375, 768, 1366, 1920):
            page.set_viewport_size({"width": width, "height": 900})
            page.wait_for_timeout(180)
            report = page.evaluate(
                """() => {
                    const tiny = [...document.querySelectorAll('body *')].filter(el => {
                        const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
                        if (!hasText) return false;
                        const r = el.getBoundingClientRect();
                        if (r.width === 0 || r.height === 0) return false;
                        return parseFloat(getComputedStyle(el).fontSize) < 10.99;
                    }).map(el => el.tagName + '.' + el.className).slice(0, 5);
                    return {
                        doc: document.documentElement.scrollWidth,
                        win: document.documentElement.clientWidth,
                        tiny,
                    };
                }"""
            )
            assert report["doc"] <= report["win"] + 1, f"{name}/{width}: overflow global {report}"
            assert report["tiny"] == [], f"{name}/{width}: texto abaixo de 11px {report['tiny']}"
        page.set_viewport_size({"width": 1366, "height": 900})
