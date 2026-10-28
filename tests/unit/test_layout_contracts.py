"""Contratos estruturais do layout unificado (Feature 023).

Estes testes são estáticos e não exigem navegador. Eles protegem os
invariantes do contrato de UI: IDs estáveis, rotas, tema padrão, um único
painel ativo, tipografia, acessibilidade e responsividade estrutural.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WEB = REPO_ROOT / "src" / "web"
INDEX = WEB / "index.html"
APP = WEB / "app.js"
STYLES = WEB / "styles.css"
CONSTANTS = WEB / "modules" / "constants.js"

STABLE_IDS = [
    # Shell e navegação
    "global-pillar-selector",
    "pillar-btn-carteira",
    "pillar-btn-quant",
    "main-subnav-pills",
    "subnav-group-carteira",
    "subnav-group-quant",
    "btn-theme-toggle",
    "theme-toggle-icon",
    "btn-header-b3-status",
    "b3-import-label",
    "btn-header-add-trade",
    "b3-multi-file-input",
    "loading-spinner",
    "loading-text",
    "global-direction-selector",
    # Carteira
    "tab-overview",
    "tab-portfolio",
    "tab-pane-proventos",
    "tab-pane-patrimonio",
    "kpi-patrimonio-total",
    "kpi-lucro-total",
    "kpi-proventos-12m",
    "kpi-posicoes-lucro",
    "overview-stacked-bar-chart",
    "overview-donut-chart",
    "chart-proventos-detailed",
    "chart-patrimonio-detailed",
    "investidor10-positions-categories",
    "btn-proventos-view-mensal",
    "btn-proventos-view-anual",
    "investidor10-welcome-banner",
    "link-overview-ver-patrimonio",
    # Quantitativo
    "tab-pane-radar",
    "tab-terminal",
    "tab-simulator",
    "tab-playbook",
    "radar-table-body",
    "radar-pagination-container",
    "radar-pagination-info",
    "btn-radar-rescan",
    "btn-radar-prev",
    "btn-radar-next",
    "radar-timeframe-buttons",
    "radar-category-pills",
    "radar-strategy-dropdown-wrapper",
    "input-ticker",
    "select-period",
    "btn-load-analysis",
    "btn-refresh-data",
    "sim-ticker",
    "sim-interval",
    "sim-mode",
    "sim-cycle-mode",
    "sim-buy-strategy",
    "sim-sell-strategy",
    "btn-run-simulation",
    "btn-optimize-combinations",
    "sim-optimizer-container",
]

CANONICAL_AREAS = {
    "carteira/visao-geral": "tab-overview",
    "carteira/posicoes": "tab-portfolio",
    "carteira/proventos": "tab-pane-proventos",
    "carteira/patrimonio": "tab-pane-patrimonio",
    "quant/radar": "tab-pane-radar",
    "quant/grafico": "tab-terminal",
    "quant/simulador": "tab-simulator",
    "quant/playbook": "tab-playbook",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def index_html() -> str:
    return read(INDEX)


@pytest.fixture(scope="module")
def app_js() -> str:
    return read(APP)


@pytest.fixture(scope="module")
def styles_css() -> str:
    return read(STYLES)


@pytest.fixture(scope="module")
def constants_js() -> str:
    return read(CONSTANTS)


def test_all_stable_contract_ids_exist(index_html: str):
    missing = [element_id for element_id in STABLE_IDS if f'id="{element_id}"' not in index_html]
    assert missing == [], f"IDs estáveis ausentes: {missing}"


def test_no_duplicate_element_ids(index_html: str):
    ids = re.findall(r'(?<![\w-])id="([^"]+)"', index_html)
    duplicates = sorted({element_id for element_id in ids if ids.count(element_id) > 1})
    assert duplicates == [], f"IDs duplicados no DOM: {duplicates}"


def test_exactly_one_default_visible_panel(index_html: str):
    sections = re.findall(r"<section\b[^>]*>", index_html)
    tab_views = [tag for tag in sections if "tab-view" in tag]
    assert len(tab_views) == 8, f"Esperados 8 painéis, encontrados {len(tab_views)}"
    visible = [tag for tag in tab_views if not re.search(r"\bhidden\b", tag)]
    assert len(visible) == 1, f"Esperado exatamente 1 painel visível no markup: {visible}"


def test_canonical_routes_and_panels_are_declared(constants_js: str, index_html: str):
    for route, panel in CANONICAL_AREAS.items():
        assert f"'{route}'" in constants_js, f"Rota canônica ausente: {route}"
        assert f"paneId: '{panel}'" in constants_js, f"paneId ausente para {route}: {panel}"
        assert f'id="{panel}"' in index_html, f"Painel ausente no DOM: {panel}"


def test_legacy_routes_remain_supported(constants_js: str):
    for legacy in ("resumo", "posicoes", "proventos", "patrimonio", "radar", "terminal", "simulador", "playbook"):
        assert legacy in constants_js, f"Rota legada ausente: {legacy}"


def test_light_theme_is_the_default(app_js: str, index_html: str):
    assert "stored === 'light' || stored === 'dark'" in app_js
    assert "? stored : 'light'" in app_js
    assert "stored === 'dark' ? 'dark' : 'light'" in index_html
    assert "getAttribute('data-theme') || 'dark'" not in app_js


def test_theme_tokens_and_persistence_contract(styles_css: str, app_js: str):
    assert ':root {' in styles_css
    assert '[data-theme="dark"] {' in styles_css
    assert "--surface:" in styles_css
    assert "--border:" in styles_css
    assert "--text-main:" in styles_css
    assert "--success:" in styles_css
    assert "--danger:" in styles_css
    assert "terminal_theme" in app_js
    assert "window.appState" in app_js
    assert "function applyTheme" in app_js


def test_typography_floor_and_tabular_figures(styles_css: str):
    assert "--font-size-floor: 11px" in styles_css
    assert ".text-\\[10px\\]" in styles_css
    assert "font-variant-numeric: tabular-nums" in styles_css
    assert "--font-mono:" in styles_css


def test_shared_component_contracts(styles_css: str):
    for selector in (
        ".btn-primary",
        ".btn-secondary",
        ".btn-contextual",
        ".btn-danger",
        ".btn-ghost",
        ".card {",
        ".table-standard",
        ".table-scroll",
        ".accordion",
        ".state-empty",
        ".state-error",
        ".state-loading",
        ".badge {",
        ".input,",
        ".select {",
    ):
        assert selector in styles_css, f"Componente ausente: {selector}"


def test_portfolio_areas_share_executive_components(index_html: str, styles_css: str, app_js: str):
    assert 'area-posicoes' in index_html
    assert 'area-proventos' in index_html
    assert 'area-patrimonio' in index_html
    assert index_html.count('kpi-card card-surface') == 4
    assert index_html.count('card-surface chart-card') >= 3
    assert 'section-title' in index_html and '.section-title {' in styles_css
    assert 'section-subtitle' in index_html and '.section-subtitle {' in styles_css
    assert "category-card card-surface" in app_js
    assert "investidor10-welcome-banner" in app_js
    assert "classList.toggle('hidden', hasImportedData)" in app_js
    assert "chart-proventos-detailed" in index_html
    assert "chart-patrimonio-detailed" in index_html


def test_navigation_accessibility_markup(index_html: str):
    assert 'role="tablist"' in index_html
    assert 'role="tab"' in index_html
    assert index_html.count("aria-selected=") >= 10
    assert 'aria-label="Ambientes da Plataforma"' in index_html
    assert 'aria-label="Subnavegação Minha Carteira"' in index_html
    assert 'aria-label="Subnavegação Análise Quantitativa"' in index_html
    assert 'aria-orientation="horizontal"' in index_html
    assert 'aria-pressed="false"' in index_html
    nav_tabs = re.findall(r'<div class="nav-tab[^>]*>', index_html)
    assert len(nav_tabs) == 8, f"Esperadas 8 abas contextuais: {len(nav_tabs)}"
    assert all('aria-controls="' in tab for tab in nav_tabs)
    # T054: além das abas, cada região de tabela rolável é focável por teclado.
    scroll_regions = re.findall(
        r'<div class="table-scroll(?!-hint)[^"]*" tabindex="0">', index_html
    )
    assert len(scroll_regions) >= 8, f"Regiões roláveis focáveis: {len(scroll_regions)}"
    assert index_html.count('tabindex="0"') == 2 + len(scroll_regions)
    assert index_html.count('role="tab" tabindex="-1"') == 7


def test_reduced_motion_and_focus_contract(styles_css: str):
    assert "@media (prefers-reduced-motion: reduce)" in styles_css
    assert ":focus-visible" in styles_css
    assert "--border-focus:" in styles_css


MOJIBAKE_PATTERN = re.compile(
    r"Ã[\x80-\xff]|Â[\x80-\xff]|â€|â†|âœ|â–|â‰|âˆ|â•|ï¿½"
)


def test_index_html_has_no_encoding_artifacts(index_html: str):
    artifacts = MOJIBAKE_PATTERN.findall(index_html)
    assert artifacts == [], (
        f"Artefatos de encoding encontrados em index.html: {artifacts[:10]}"
    )
    assert '<meta charset="UTF-8">' in index_html


def test_javascript_sources_have_no_encoding_artifacts(app_js: str):
    sources = {"app.js": app_js}
    for module in sorted((WEB / "modules").glob("*.js")):
        sources[module.name] = read(module)
    for name, source in sources.items():
        artifacts = MOJIBAKE_PATTERN.findall(source)
        assert artifacts == [], (
            f"Artefatos de encoding encontrados em {name}: {artifacts[:10]}"
        )


FUNCTIONAL_EMOJI_PATTERN = re.compile(
    r"[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]"
)


def test_index_html_has_no_functional_emoji(index_html: str):
    emojis = FUNCTIONAL_EMOJI_PATTERN.findall(index_html)
    assert emojis == [], f"Emojis funcionais encontrados em index.html: {emojis[:10]}"


def test_javascript_sources_have_no_functional_emoji(app_js: str):
    sources = {"app.js": app_js}
    for module in sorted((WEB / "modules").glob("*.js")):
        sources[module.name] = read(module)
    for name, source in sources.items():
        emojis = FUNCTIONAL_EMOJI_PATTERN.findall(source)
        assert emojis == [], f"Emojis funcionais encontrados em {name}: {emojis[:10]}"


SUBFLOOR_SIZE_PATTERN = re.compile(r"text-\[(?:[0-9]|10)px\]|font-size:\s*(?:[0-9]|10)px")


def test_sources_do_not_declare_text_below_the_floor():
    sources = {"index.html": INDEX, "app.js": APP}
    for module in sorted((WEB / "modules").glob("*.js")):
        sources[module.name] = module
    for name, path in sources.items():
        source = read(path)
        offenders = SUBFLOOR_SIZE_PATTERN.findall(source)
        assert offenders == [], f"Tamanhos abaixo de 11px em {name}: {offenders[:10]}"


def test_typography_floor_contract_is_active(styles_css: str):
    assert "--font-size-floor: 11px" in styles_css
    assert ".text-\\[10px\\]" in styles_css
    assert "font-variant-numeric: tabular-nums" in styles_css


def test_icon_sprite_replaces_functional_emoji(index_html: str):
    sprite_ids = re.findall(r'<g id="(icon-[^"]+)"', index_html)
    assert len(sprite_ids) >= 20, f"Sprite SVG insuficiente: {sprite_ids}"
    for required in ("icon-sun", "icon-moon", "icon-chart", "icon-wallet", "icon-coins", "icon-target"):
        assert required in sprite_ids, f"Ícone ausente no sprite: {required}"


# =========================================================================
# T057 / US5 — responsividade estrutural, overflow e contraste
# =========================================================================
from html.parser import HTMLParser  # noqa: E402

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class _ScrollableTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[dict] = []
        self.tables: list[dict] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        is_scroll = "table-scroll" in classes
        node = {
            "tag": tag,
            "scroll": is_scroll,
            "tabindex": attributes.get("tabindex"),
        }
        self.stack.append(node)
        if tag == "table":
            scrollers = [item for item in self.stack if item["scroll"]]
            self.tables.append({
                "scroll": bool(scrollers),
                "focusable": bool(scrollers and scrollers[-1]["tabindex"] == "0"),
            })
        if tag in VOID_TAGS:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                break


def test_wide_tables_have_focusable_scroll_wrappers(index_html: str):
    parser = _ScrollableTableParser()
    parser.feed(index_html)
    assert len(parser.tables) >= 9, f"Tabelas encontradas: {len(parser.tables)}"
    without_scroller = [table for table in parser.tables if not table["scroll"]]
    assert without_scroller == [], "Tabelas sem contêiner .table-scroll"
    without_focus = [table for table in parser.tables if not table["focusable"]]
    assert without_focus == [], "Contêineres de tabela sem tabindex=\"0\""
    assert index_html.count("table-scroll-hint") >= 5


def test_responsive_breakpoints_and_overflow_contract(styles_css: str):
    assert "overflow-x: auto" in styles_css
    assert "overscroll-behavior-x: contain" in styles_css
    assert "min-width: 0" in styles_css
    assert ".table-scroll > table" in styles_css
    assert "min-width: 100%" in styles_css
    assert "@media (max-width: 767px)" in styles_css
    assert "@media (min-width: 768px)" in styles_css
    assert "@media (min-width: 1024px)" in styles_css
    assert ".touch-target" in styles_css
    assert ".btn-remove-holding" in styles_css
    assert ".dir-seg-btn" in styles_css

    # Nenhuma largura fixa maior que o maior viewport de referência.
    fixed = [int(value) for value in re.findall(r"(?:^|\s)(?:min-)?width:\s*(\d{4,})px", styles_css)]
    assert all(value <= 1920 for value in fixed), f"Larguras fixas excessivas: {fixed}"

    reduced = re.search(r"@media \(prefers-reduced-motion: reduce\)\s*\{(.*?)\n\}", styles_css, re.S)
    assert reduced is not None, "Bloco prefers-reduced-motion ausente"
    block = reduced.group(1)
    assert "animation-duration: 0.01ms !important" in block
    assert "transition-duration: 0.01ms !important" in block
    assert "scroll-behavior: auto !important" in block


def test_kpi_grids_follow_one_two_four_columns(index_html: str):
    for element_id in ("investidor10-hero-kpis", "radar-executive-deck"):
        tag = re.search(rf'<div[^>]*id="{element_id}"[^>]*>', index_html)
        assert tag is not None, f"Grid de KPIs ausente: {element_id}"
        class_match = re.search(r'class="([^"]+)"', tag.group(0))
        assert class_match is not None, f"Grid sem classe: {element_id}"
        classes = class_match.group(1)
        assert "grid-cols-1" in classes, f"{element_id}: mobile deve ter 1 coluna"
        assert "sm:grid-cols-2" in classes, f"{element_id}: tablet deve ter 2 colunas"
        assert "lg:grid-cols-4" in classes, f"{element_id}: desktop deve ter 4 colunas"
    assert "grid-cols-2 md:grid-cols-4" not in index_html


def _theme_tokens(css: str, selector: str) -> dict[str, str]:
    match = re.search(re.escape(selector) + r"\s*\{(.*?)\n\}", css, re.S)
    assert match is not None, f"Bloco de tokens ausente: {selector}"
    return dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{6})", match.group(1)))


def _relative_luminance(color: str) -> float:
    color = color.lstrip("#")
    channels = [int(color[index:index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def test_theme_tokens_meet_wcag_aa_contrast(styles_css: str):
    pairs = [
        ("--text-main", "--surface"),
        ("--text-main", "--canvas"),
        ("--text-muted", "--surface"),
        ("--text-muted", "--surface-subtle"),
        ("--text-subtle", "--surface"),
        ("--text-subtle", "--canvas"),
        ("--text-subtle", "--surface-subtle"),
        ("--primary", "--surface"),
        ("--primary", "--canvas"),
        ("--success", "--surface"),
        ("--danger", "--surface"),
        ("--warning", "--surface"),
        ("--warning", "--surface-subtle"),
    ]
    failures = []
    for selector in (":root", '[data-theme="dark"]'):
        tokens = _theme_tokens(styles_css, selector)
        for foreground, background in pairs:
            assert foreground in tokens, f"{selector}: token ausente {foreground}"
            assert background in tokens, f"{selector}: token ausente {background}"
            ratio = _contrast_ratio(tokens[foreground], tokens[background])
            if ratio < 4.5:
                failures.append((selector, foreground, background, round(ratio, 2)))
    assert failures == [], f"Pares abaixo de WCAG AA (4.5:1): {failures}"


def test_penpot_screens_modals_and_modular_scripts_contract(index_html: str):
    """Verifica que todos os elementos estruturais das 13 telas Penpot e módulos JS estão declarados."""
    required_ids = (
        "overview-highlights-card",
        "overview-highlights-tbody",
        "proventos-kpis-grid",
        "prov-kpi-total",
        "prov-composition-list",
        "prov-history-tbody",
        "btn-patrimonio-12m",
        "btn-patrimonio-all",
        "pat-summary-final",
        "pat-history-tbody",
        "custody-kpis-grid",
        "custody-category-pills",
        "btn-custody-export-csv",
        "playbook-search-input",
        "playbook-filter-pills",
        "playbook-cards-grid",
        "modal-b3-import",
        "modal-new-trade",
        "mobile-bottom-nav",
    )
    for el_id in required_ids:
        assert f'id="{el_id}"' in index_html, f"Elemento Penpot obrigatório ausente: {el_id}"

    assert index_html.count('role="tabpanel"') == 8
    assert index_html.count('role="dialog" aria-modal="true"') == 4

    for mod_script in (
        "modules/constants.js",
        "modules/formatters.js",
        "modules/api-client.js",
        "modules/toast.js",
        "modules/proventos.js",
        "modules/evolution.js",
        "modules/playbook.js",
        "modules/modals.js",
    ):
        assert f'<script src="{mod_script}"></script>' in index_html, f"Script modular ausente: {mod_script}"
