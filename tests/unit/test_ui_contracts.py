import re
import pytest
import os
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)

def test_api_health_contract():
    """Valida endpoint de health check"""
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_api_strategies_contract():
    """Valida contrato do catálogo de estratégias consumido pela UI"""
    res = client.get("/api/strategies")
    assert res.status_code == 200
    data = res.json()
    assert "proprietary" in data
    assert "mql5" in data

def test_api_portfolio_quotes_contract():
    """Valida contrato consumido pelo frontend: POST /api/portfolio/quotes"""
    payload = {"tickers": ["PETR4.SA", "VALE3.SA"]}
    res = client.post("/api/portfolio/quotes", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)

def test_spa_index_html_exists():
    """Valida que o index.html principal existe e tem tamanho adequado"""
    index_path = os.path.join("src", "web", "index.html")
    assert os.path.exists(index_path)
    assert os.path.getsize(index_path) > 1000


def test_spa_has_investidor10_subnav_and_tab_panes():
    """T006: Valida que index.html possui a barra de navegação por abas e containers .tab-pane"""
    index_path = os.path.join("src", "web", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Valida presença da subnav bar
    assert "subnav-bar" in html
    assert "subnav-container" in html

    # Valida abas requeridas
    assert 'data-tab="resumo"' in html
    assert 'data-tab="posicoes"' in html
    assert 'data-tab="proventos"' in html
    assert 'data-tab="patrimonio"' in html
    assert 'data-tab="radar"' in html
    assert 'data-tab="tradingview"' in html

    # Valida contêineres de abas
    assert ('id="tab-pane-resumo"' in html or 'id="tab-overview"' in html)
    assert ('id="tab-pane-posicoes"' in html or 'id="tab-portfolio"' in html)
    assert 'id="tab-pane-proventos"' in html
    assert 'id="tab-pane-patrimonio"' in html
    assert 'id="tab-pane-radar"' in html
    assert ('id="tab-pane-tradingview"' in html or 'id="tab-terminal"' in html)


def test_spa_has_investidor10_hero_kpis_and_charts():
    """T007: Valida que a aba Resumo possui os 4 cards de KPI e os containers dos gráficos de Evolução e Alocação"""
    index_path = os.path.join("src", "web", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Valida KPIs de Resumo
    assert 'id="kpi-patrimonio-total"' in html
    assert 'id="kpi-lucro-total"' in html
    assert 'id="kpi-proventos-12m"' in html
    assert 'id="kpi-posicoes-lucro"' in html

    # Valida Gráficos principais da aba Resumo
    assert 'id="overview-stacked-bar-chart"' in html
    assert 'id="overview-donut-chart"' in html


def test_spa_has_investidor10_category_accordions():
    """T012: Valida que a aba Posições possui a estrutura de acordeões por categoria de ativos"""
    index_path = os.path.join("src", "web", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Valida container de grupos de ativos
    assert 'id="investidor10-positions-categories"' in html
    assert 'class="category-card"' in html or 'category-card' in html


def test_spa_has_investidor10_proventos_tab():
    """T017: Valida que a aba Proventos possui alternador mensal/anual e container de grafico"""
    index_path = os.path.join("src", "web", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    assert 'id="tab-pane-proventos"' in html
    assert 'id="btn-proventos-view-mensal"' in html
    assert 'id="btn-proventos-view-anual"' in html
    assert 'id="chart-proventos-detailed"' in html


def test_regression_chart_container_no_flex_and_no_duplicate_overview():
    """
    Teste de Regressão Obrigatório:
    1. Garante que os containers de gráfico (#overview-stacked-bar-chart e #overview-donut-chart)
       são únicos no DOM (sem IDs duplicados causando colisão e sobreposição de layout).
    2. Garante que os containers usam display block/relative com overflow-hidden para
       enquadramento correto do Plotly.js, e NÃO usam 'flex items-center justify-center'.
    3. Garante que o bloco legado de layout escuro (Destaques da Carteira / overview-sub-nav)
       não está presente na aba de Resumo.
    """
    index_path = os.path.join("src", "web", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Unicidade de IDs dos gráficos
    assert html.count('id="overview-stacked-bar-chart"') == 1, "ID overview-stacked-bar-chart duplicado no DOM!"
    assert html.count('id="overview-donut-chart"') == 1, "ID overview-donut-chart duplicado no DOM!"

    # 2. Enquadramento e ausência de flex nos containers de gráfico
    import re
    bar_chart_match = re.search(r'<div[^>]*id="overview-stacked-bar-chart"[^>]*class="([^"]*)"', html)
    assert bar_chart_match is not None, "overview-stacked-bar-chart não encontrado!"
    bar_classes = bar_chart_match.group(1).split()
    assert "flex" not in bar_classes, "overview-stacked-bar-chart não pode ter classe 'flex' (deve ser block/relative)"
    assert "overflow-hidden" in bar_classes, "overview-stacked-bar-chart deve conter 'overflow-hidden' para enquadramento"

    donut_chart_match = re.search(r'<div[^>]*id="overview-donut-chart"[^>]*class="([^"]*)"', html)
    assert donut_chart_match is not None, "overview-donut-chart não encontrado!"
    donut_classes = donut_chart_match.group(1).split()
    assert "flex" not in donut_classes, "overview-donut-chart não pode ter classe 'flex'"
    assert "overflow-hidden" in donut_classes, "overview-donut-chart deve conter 'overflow-hidden'"

    # 3. Ausência de layout escuro duplicado na Visão Geral
    assert "overview-sub-nav" not in html, "overview-sub-nav legado ainda presente no DOM!"
    assert "Destaques da Carteira" not in html, "Card legado Destaques da Carteira ainda presente no DOM!"


def test_regression_b3_import_does_not_keep_fake_cash():
    """US1/T005: caixa padrão zero e reset do caixa ao aplicar um resultado B3."""
    app_path = os.path.join("src", "web", "app.js")
    with open(app_path, "r", encoding="utf-8") as f:
        app_js = f.read()

    default_state = re.search(
        r"state\.portfolioState\s*=\s*\{(?P<body>.*?)\n\};",
        app_js,
        re.DOTALL,
    )
    assert default_state is not None, "Bloco inicial de state.portfolioState não encontrado em app.js"
    assert re.search(
        r"availableCash\s*:\s*0\.0\b",
        default_state.group("body"),
    ), "availableCash deve iniciar em 0.0; caixa fictício de R$ 10.000 não é permitido"

    apply_result = re.search(
        r"function applyB3ParsedResult\s*\(data\)\s*\{(?P<body>.*?)\n\}",
        app_js,
        re.DOTALL,
    )
    assert apply_result is not None, "applyB3ParsedResult não encontrado em app.js"
    assert re.search(
        r"state\.portfolioState\.availableCash\s*=\s*0\.0\s*;",
        apply_result.group("body"),
    ), "applyB3ParsedResult deve resetar state.portfolioState.availableCash para 0.0"


def _read_web_asset(filename: str) -> str:
    """Lê um asset estático de src/web sem depender do servidor."""
    path = os.path.join("src", "web", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _extract_js_function_body(source: str, function_name: str) -> str:
    """Extrai o corpo de uma função JS balanceando as chaves da assinatura."""
    signature = re.search(
        rf"(?:async\s+)?function\s+{re.escape(function_name)}\s*\([^)]*\)\s*\{{",
        source,
    )
    assert signature is not None, f"Função {function_name} não encontrada em app.js"

    body_start = signature.end()
    depth = 1
    for index in range(body_start, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[body_start:index]

    raise AssertionError(f"Chaves desbalanceadas ao extrair {function_name}")


def test_regression_portfolio_simulation_requires_informed_cash():
    """
    US1/T005 (spec 024): a simulação histórica da carteira não pode inventar
    capital quando o caixa é zero/ausente. A função deve curto-circuitar antes
    de chamar a API e renderizar o estado indisponível.
    """
    app_js = _read_web_asset("app.js")
    body = _extract_js_function_body(app_js, "runPortfolioHistoricalSimulation")

    # Nenhum fallback silencioso de capital (R$ 10.000 ou piso de R$ 100).
    assert not re.search(r"\|\|\s*10_?000", body), (
        "runPortfolioHistoricalSimulation não pode usar fallback || 10000 para o capital"
    )
    assert not re.search(r"Math\.max\(\s*100", body), (
        "runPortfolioHistoricalSimulation não pode inflar o capital com Math.max(100, ...)"
    )

    # O capital enviado à API é exatamente o caixa informado pelo usuário.
    assert re.search(r"initial_capital\s*:\s*cash\s*,", body), (
        "simPayload deve enviar initial_capital: cash, sem valor fictício"
    )

    assert re.search(r"function\s+renderPortfolioSimulationUnavailable\s*\(", app_js), (
        "renderPortfolioSimulationUnavailable deve estar definida em app.js"
    )

    guard = re.search(
        r"if\s*\(\s*cash\s*<=\s*0\s*\)\s*\{(?P<guard>.*?)\n\s*\}",
        body,
        re.DOTALL,
    )
    assert guard is not None, (
        "Guarda 'if (cash <= 0)' ausente em runPortfolioHistoricalSimulation"
    )
    guard_body = guard.group("guard")
    assert re.search(r"renderPortfolioSimulationUnavailable\s*\(", guard_body), (
        "A guarda de caixa deve renderizar o estado indisponível"
    )
    assert re.search(r"\breturn\s*;", guard_body), (
        "A guarda de caixa deve retornar antes de chamar a simulação"
    )

    simulate_fetch = re.search(r"fetch\(\s*['\"]/api/portfolio/simulate['\"]", body)
    assert simulate_fetch is not None, "Chamada a /api/portfolio/simulate não encontrada"
    assert guard.start() < simulate_fetch.start(), (
        "A guarda de caixa deve ocorrer antes da chamada a /api/portfolio/simulate"
    )


def test_regression_portfolio_ui_has_no_fake_cash_default():
    """
    US1 (spec 024): KPIs e resumo da carteira não exibem R$ 10.000,00 fictício
    e o input de caixa inicia em zero.
    """
    html = _read_web_asset("index.html")

    cash_input = re.search(r'<input[^>]*id="portfolio-cash-input"[^>]*>', html)
    assert cash_input is not None, "Input #portfolio-cash-input não encontrado em index.html"
    assert re.search(r'\bvalue\s*=\s*["\']0["\']', cash_input.group(0)), (
        '#portfolio-cash-input deve iniciar com value="0", sem caixa fictício'
    )

    fake_money = re.compile(r"R\$\s*10[.\s]?000(?:[.,]00)?")

    kpi_elements = {
        match.group("element_id"): match.group("content").strip()
        for match in re.finditer(
            r'<[^>]*id="(?P<element_id>port-kpi-[^"]+)"[^>]*>(?P<content>.*?)</',
            html,
            re.DOTALL,
        )
    }
    expected_kpis = {
        "port-kpi-initial",
        "port-kpi-cash-sub",
        "port-kpi-final",
        "port-kpi-profit-sub",
        "port-kpi-return",
        "port-kpi-bench-sub",
        "port-kpi-winrate",
        "port-kpi-exits-sub",
        "port-kpi-pf",
        "port-kpi-rotations-sub",
        "port-kpi-dd",
        "port-kpi-events-sub",
    }
    missing_kpis = expected_kpis - set(kpi_elements)
    assert not missing_kpis, f"KPIs da carteira ausentes em index.html: {sorted(missing_kpis)}"
    for element_id, content in kpi_elements.items():
        assert not fake_money.search(content), (
            f"#{element_id} não pode exibir R$ 10.000,00 fictício (conteúdo: {content!r})"
        )

    for element_id in ("advise-total-equity", "advise-cash-transition"):
        element = re.search(
            rf'<[^>]*id="{element_id}"[^>]*>(?P<content>.*?)</',
            html,
            re.DOTALL,
        )
        assert element is not None, f"#{element_id} não encontrado em index.html"
        assert not fake_money.search(element.group("content")), (
            f"#{element_id} não pode exibir R$ 10.000,00 fictício"
        )
