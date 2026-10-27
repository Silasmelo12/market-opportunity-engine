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


def test_navigation_accessibility_markup(index_html: str):
    assert 'role="tablist"' in index_html
    assert 'role="tab"' in index_html
    assert index_html.count("aria-selected=") >= 10
    assert 'aria-label="Ambientes da Plataforma"' in index_html
    assert 'aria-label="Subnavegação Minha Carteira"' in index_html
    assert 'aria-label="Subnavegação Análise Quantitativa"' in index_html


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


def test_icon_sprite_replaces_functional_emoji(index_html: str):
    sprite_ids = re.findall(r'<g id="(icon-[^"]+)"', index_html)
    assert len(sprite_ids) >= 20, f"Sprite SVG insuficiente: {sprite_ids}"
    for required in ("icon-sun", "icon-moon", "icon-chart", "icon-wallet", "icon-coins", "icon-target"):
        assert required in sprite_ids, f"Ícone ausente no sprite: {required}"
