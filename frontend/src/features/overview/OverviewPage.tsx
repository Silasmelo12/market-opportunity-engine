import * as React from "react";
import { useAppContext } from "@/state/app-context";
import { usePortfolioMetrics } from "@/hooks/use-portfolio-metrics";
import { renderPlotlySafely } from "@/hooks/use-plotly-chart";
import { getChartThemeTokens } from "@/lib/theme";
import {
  formatCurrencyBRL,
  formatPercentPtBr,
  formatQuantityPtBr,
  formatSignedCurrencyBRL,
} from "@/lib/formatters";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { AppIcon } from "@/components/layout/SvgSprite";

export function OverviewPage() {
  const {
    activeRoute,
    theme,
    portfolio,
    quotes,
    navigateToRoute,
    openChartForHolding,
    triggerSharedCsvImport,
    setIsB3ModalOpen,
    setIsMetasModalOpen,
  } = useAppContext();

  const metrics = usePortfolioMetrics(portfolio, quotes);
  const [chartWindow, setChartWindow] = React.useState<"12m" | "all">("12m");
  const [expandedGroups, setExpandedGroups] = React.useState<Record<string, boolean>>({});

  const stackedChartRef = React.useRef<HTMLDivElement | null>(null);
  const donutChartRef = React.useRef<HTMLDivElement | null>(null);

  const toggleGroup = (key: string) => {
    setExpandedGroups((prev) => ({
      ...prev,
      [key]: prev[key] === undefined ? false : !prev[key],
    }));
  };

  React.useEffect(() => {
    const tokens = getChartThemeTokens();
    const timeline = Array.isArray(portfolio.b3Timeline) ? portfolio.b3Timeline : [];
    const sliced = chartWindow === "12m" ? timeline.slice(-12) : timeline;

    let xLabels: string[] = [];
    let investedSeries: number[] = [];
    let gainSeries: number[] = [];

    if (sliced.length > 0) {
      xLabels = sliced.map((pt, i) => String(pt.month_year || pt.date || `M${i + 1}`));
      investedSeries = sliced.map((pt) => Number(pt.invested ?? pt.total_value ?? metrics.totalCostBasis));
      gainSeries = sliced.map((pt, idx) => {
        const eq = Number(pt.total_equity ?? metrics.totalMarketValue);
        return Math.max(0, eq - investedSeries[idx]);
      });
    } else if (metrics.totalCostBasis > 0 || metrics.totalMarketValue > 0) {
      xLabels = ["Atual"];
      investedSeries = [metrics.totalCostBasis];
      gainSeries = [Math.max(0, metrics.unrealizedPnl)];
    }

    const barTraces = [
      {
        name: "Valor Aplicado",
        x: xLabels,
        y: investedSeries,
        type: "bar",
        marker: { color: tokens.invested, cornerradius: 4 },
      },
      {
        name: "Ganho de Capital",
        x: xLabels,
        y: gainSeries,
        type: "bar",
        marker: { color: tokens.gain, cornerradius: 4 },
      },
    ];

    renderPlotlySafely(stackedChartRef.current, barTraces, {
      barmode: "stack",
      margin: { t: 12, r: 12, b: 32, l: 48 },
      paper_bgcolor: tokens.bg,
      plot_bgcolor: tokens.bg,
      font: { family: "Plus Jakarta Sans, sans-serif", size: 11, color: tokens.text },
      showlegend: true,
      legend: { orientation: "h", y: 1.12, x: 0 },
      xaxis: { gridcolor: "rgba(0,0,0,0)" },
      yaxis: { gridcolor: tokens.grid, tickprefix: "R$ " },
    });

    const donutLabels =
      metrics.categoryGroups.length > 0
        ? metrics.categoryGroups.map((g) => g.label)
        : ["Caixa Livre"];
    const donutValues =
      metrics.categoryGroups.length > 0
        ? metrics.categoryGroups.map((g) => g.totalMarketValue)
        : [Math.max(1, metrics.availableCash)];

    const donutTraces = [
      {
        labels: donutLabels,
        values: donutValues,
        type: "pie",
        hole: 0.64,
        textinfo: "percent",
        marker: { colors: tokens.slices },
      },
    ];

    renderPlotlySafely(donutChartRef.current, donutTraces, {
      margin: { t: 8, r: 8, b: 8, l: 8 },
      paper_bgcolor: tokens.bg,
      plot_bgcolor: tokens.bg,
      font: { family: "Plus Jakarta Sans, sans-serif", size: 11, color: tokens.text },
      showlegend: false,
    });
  }, [
    theme,
    activeRoute,
    chartWindow,
    portfolio.b3Timeline,
    metrics.totalCostBasis,
    metrics.totalMarketValue,
    metrics.unrealizedPnl,
    metrics.categoryGroups,
    metrics.availableCash,
  ]);

  const isVisible = activeRoute === "carteira/visao-geral";

  return (
    <section
      id="tab-overview"
      role="tabpanel"
      aria-labelledby="subnav-tab-resumo"
      className={`tab-view area-resumo mx-auto max-w-[1600px] space-y-5 px-4 py-5 pb-20 ${
        isVisible ? "" : "hidden"
      }`}
    >
      {/* Banner Condicional de Boas-Vindas / Importação B3 */}
      <div
        id="investidor10-welcome-banner"
        className={`card-surface flex flex-wrap items-center justify-between gap-4 rounded-lg border border-border bg-surface p-4 shadow-sm ${
          metrics.hasImportedData ? "hidden" : ""
        }`}
      >
        <div className="space-y-1">
          <h2 className="section-title font-sans text-sm font-bold text-foreground">
            Sincronize sua Custódia Oficial da B3
          </h2>
          <p className="section-subtitle text-xs text-muted-foreground">
            Importe seus extratos de negociação, movimentação ou carteira CSV para consolidar patrimônio, preço médio e proventos reais.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            type="button"
            id="btn-banner-import-b3"
            variant="primary"
            size="sm"
            onClick={triggerSharedCsvImport}
          >
            <AppIcon name="icon-import" className="h-3.5 w-3.5" />
            <span>Importar CSV / Extrato</span>
          </Button>
          <Button
            type="button"
            id="btn-open-b3-modal-banner"
            variant="secondary"
            size="sm"
            onClick={() => setIsB3ModalOpen(true)}
          >
            <span>Conciliação Múltipla B3</span>
          </Button>
        </div>
      </div>

      {/* 4 Hero KPIs Executivos */}
      <div
        id="investidor10-hero-kpis"
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {/* KPI 1: Patrimônio Total */}
        <div id="kpi-patrimonio-total" className="kpi-card card-surface flex flex-col justify-between rounded-lg border border-border bg-surface p-4 shadow-sm">
          <div className="flex items-center justify-between gap-2">
            <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
              Patrimônio Total
            </span>
            <Badge
              id="overview-card1-var"
              intent={
                metrics.unrealizedPct === null
                  ? "neutral"
                  : metrics.unrealizedPct >= 0
                    ? "success"
                    : "danger"
              }
            >
              {metrics.card1VarLabel}
            </Badge>
          </div>
          <div
            id="overview-total-equity"
            className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-foreground tabular-nums"
          >
            {formatCurrencyBRL(metrics.totalEquity)}
          </div>
          <div className="kpi-sub mt-1.5 flex items-center justify-between text-xs text-muted-foreground">
            <span>Valor investido:</span>
            <span id="overview-invested-val" className="font-mono font-semibold text-foreground">
              {formatCurrencyBRL(metrics.totalCostBasis)}
            </span>
          </div>
        </div>

        {/* KPI 2: Lucro / Resultado Não Realizado */}
        <div id="kpi-lucro-total" className="kpi-card card-surface flex flex-col justify-between rounded-lg border border-border bg-surface p-4 shadow-sm">
          <div className="flex items-center justify-between gap-2">
            <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
              Resultado Não Realizado
            </span>
            <Badge
              id="kpi-lucro-badge"
              intent={
                metrics.unrealizedPct === null
                  ? "neutral"
                  : metrics.unrealizedPnl >= 0
                    ? "success"
                    : "danger"
              }
            >
              {metrics.kpiLucroBadgeLabel}
            </Badge>
          </div>
          <div
            id="kpi-lucro-val"
            className={`kpi-value financial-value mt-2 font-mono text-2xl font-extrabold tabular-nums ${
              metrics.unrealizedPnl >= 0 ? "text-success" : "text-danger"
            }`}
          >
            {metrics.kpiLucroValLabel}
          </div>
          <div className="kpi-sub mt-1.5 flex items-center justify-between text-xs text-muted-foreground">
            <span id="kpi-lucro-sub">{metrics.kpiLucroSubLabel}</span>
          </div>
        </div>

        {/* KPI 3: Proventos Recebidos */}
        <div id="kpi-proventos-12m" className="kpi-card card-surface flex flex-col justify-between rounded-lg border border-border bg-surface p-4 shadow-sm">
          <div className="flex items-center justify-between gap-2">
            <span
              id="overview-dividends-title"
              className="kpi-label section-title text-[11px] font-bold tracking-wider text-muted-foreground"
              style={{ textTransform: "none" }}
            >
              {metrics.dividendsTitleLabel}
            </span>
            <Badge id="overview-dividends-period-label" intent="primary">
              {metrics.dividendsPeriodLabel}
            </Badge>
          </div>
          <div
            id="overview-dividends-total"
            className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-foreground tabular-nums"
          >
            {metrics.dividendsTotalLabel}
          </div>
          <div className="kpi-sub mt-1.5 flex items-center justify-between text-xs text-muted-foreground">
            <span id="overview-dividends-monthly">{metrics.dividendsMonthlyLabel}</span>
          </div>
        </div>

        {/* KPI 4: Ativos acima do preço médio */}
        <div id="kpi-posicoes-lucro" className="kpi-card card-surface flex flex-col justify-between rounded-lg border border-border bg-surface p-4 shadow-sm">
          <div className="flex items-center justify-between gap-2">
            <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
              Ativos Acima do Preço Médio
            </span>
            <Badge id="kpi-posicoes-percent" intent="teal">
              {metrics.kpiPosicoesPercentLabel}
            </Badge>
          </div>
          <div
            id="kpi-posicoes-count"
            className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-foreground tabular-nums"
          >
            {metrics.kpiPosicoesCountLabel}
          </div>
          <div className="kpi-sub mt-1.5 flex items-center justify-between text-xs text-muted-foreground">
            <span id="kpi-posicoes-sub">{metrics.kpiPosicoesSubLabel}</span>
          </div>
        </div>
      </div>

      {/* Gráficos Principais: Evolução do Patrimônio & Alocação por Classe */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <Card kind="chart" className="card-surface chart-card bg-white lg:col-span-8">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border pb-3">
            <div>
              <h3 className="section-title font-sans text-sm font-bold text-foreground">
                Evolução do Patrimônio
              </h3>
              <p className="section-subtitle text-xs text-muted-foreground">
                Comparativo entre capital aportado e valor de mercado consolidado
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className="segmented inline-flex rounded-md border border-border bg-surface-subtle p-0.5">
                <button
                  type="button"
                  aria-pressed={chartWindow === "12m"}
                  onClick={() => setChartWindow("12m")}
                  className={`rounded-sm px-2.5 py-1 text-[11px] font-semibold ${
                    chartWindow === "12m"
                      ? "bg-surface text-foreground shadow-sm"
                      : "text-muted-foreground"
                  }`}
                >
                  12M
                </button>
                <button
                  type="button"
                  aria-pressed={chartWindow === "all"}
                  onClick={() => setChartWindow("all")}
                  className={`rounded-sm px-2.5 py-1 text-[11px] font-semibold ${
                    chartWindow === "all"
                      ? "bg-surface text-foreground shadow-sm"
                      : "text-muted-foreground"
                  }`}
                >
                  Tudo
                </button>
              </div>
              <button
                type="button"
                id="link-overview-ver-patrimonio"
                onClick={() => navigateToRoute("carteira/patrimonio")}
                className="btn-contextual rounded-md px-2.5 py-1 text-xs font-semibold"
              >
                Ver detalhes →
              </button>
            </div>
          </div>
          <div
            id="overview-stacked-bar-chart"
            ref={stackedChartRef}
            className="mt-3 h-[280px] w-full block overflow-hidden"
          />
        </Card>

        <Card kind="chart" className="card-surface chart-card bg-white lg:col-span-4">
          <div className="flex items-center justify-between gap-2 border-b border-border pb-3">
            <div>
              <h3 className="section-title font-sans text-sm font-bold text-foreground">
                Alocação por Classe
              </h3>
              <p className="section-subtitle text-xs text-muted-foreground">
                Distribuição percentual da carteira
              </p>
            </div>
            <Button
              type="button"
              id="btn-overview-metas"
              variant="secondary"
              size="xs"
              onClick={() => setIsMetasModalOpen(true)}
            >
              Metas %
            </Button>
          </div>
          <div
            id="overview-donut-chart"
            ref={donutChartRef}
            className="mt-3 h-[210px] w-full block overflow-hidden"
          />
          <div id="overview-donut-legend" className="mt-3 space-y-1.5 border-t border-border pt-2.5 text-xs">
            {metrics.categoryGroups.map((grp) => (
              <div key={grp.key} className="flex items-center justify-between">
                <span className="font-medium text-foreground">{grp.label}</span>
                <span className="font-mono font-semibold text-muted-foreground">
                  {formatPercentPtBr(grp.weightPct, 1)} ({formatCurrencyBRL(grp.totalMarketValue)})
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Tabela Penpot 01: Ativos em Destaque na Carteira */}
      <Card id="overview-highlights-card" className="card-surface">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-border pb-3">
          <div>
            <h3 className="section-title font-sans text-sm font-bold text-foreground">
              Ativos em destaque na carteira
            </h3>
            <p className="section-subtitle text-xs text-muted-foreground">
              Principais posições ordenadas por participação patrimonial e rentabilidade
            </p>
          </div>
          <Button
            type="button"
            variant="secondary"
            size="xs"
            onClick={() => navigateToRoute("carteira/posicoes")}
          >
            Ver todas as posições
          </Button>
        </div>

        <Table showMobileHint>
          <TableHeader>
            <TableRow>
              <TableHead>Ativo</TableHead>
              <TableHead>Classe</TableHead>
              <TableHead className="text-right">Qtd.</TableHead>
              <TableHead className="text-right">Preço Médio</TableHead>
              <TableHead className="text-right">Cotação Atual</TableHead>
              <TableHead className="text-right">Saldo Bruto</TableHead>
              <TableHead className="text-right">Resultado</TableHead>
              <TableHead className="text-right">% Carteira</TableHead>
              <TableHead className="text-right">Ação</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody id="overview-highlights-tbody">
            {metrics.enrichedHoldings.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} className="py-6 text-center text-muted-foreground">
                  Nenhum ativo cadastrado na carteira. Importe um extrato B3 ou adicione um lançamento manual.
                </TableCell>
              </TableRow>
            ) : (
              metrics.enrichedHoldings.map((item) => (
                <TableRow key={item.ticker}>
                  <TableCell className="font-mono font-bold text-foreground">
                    {item.ticker}
                  </TableCell>
                  <TableCell>
                    <Badge intent="neutral">{item.shortBadge}</Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatQuantityPtBr(item.shares)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCurrencyBRL(item.average_buy_price)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCurrencyBRL(item.currentPrice)}
                  </TableCell>
                  <TableCell className="text-right font-mono font-bold">
                    {formatCurrencyBRL(item.marketValue)}
                  </TableCell>
                  <TableCell
                    className={`text-right font-mono font-semibold ${
                      item.unrealizedPnl >= 0 ? "text-success" : "text-danger"
                    }`}
                  >
                    {formatSignedCurrencyBRL(item.unrealizedPnl)}{" "}
                    {item.unrealizedPct !== null && (
                      <span className="text-[11px]">
                        ({formatPercentPtBr(item.unrealizedPct, 2, true)})
                      </span>
                    )}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatPercentPtBr(item.weightPct, 1)}
                  </TableCell>
                  <TableCell className="text-right">
                    <button
                      type="button"
                      data-ticker={item.ticker}
                      onClick={() => openChartForHolding(item.ticker)}
                      className="btn-contextual rounded-md px-2.5 py-1 text-[11px] font-bold"
                    >
                      Abrir gráfico
                    </button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Acordeões de Categorias na Visão Geral */}
      <div id="overview-categories-accordions" className="space-y-3">
        {metrics.categoryGroups.map((group) => {
          const isOpen = expandedGroups[group.key] !== false;
          return (
            <div
              key={group.key}
              className="category-card card-surface accordion overflow-hidden rounded-lg border border-border bg-surface shadow-sm"
            >
              <button
                type="button"
                aria-expanded={isOpen}
                onClick={() => toggleGroup(group.key)}
                className="accordion-header flex w-full items-center justify-between gap-3 bg-surface-subtle px-4 py-3 text-left transition-colors hover:bg-surface-hover"
              >
                <div className="flex items-center gap-2.5">
                  <span className="font-sans text-sm font-bold text-foreground">
                    {group.label}
                  </span>
                  <Badge intent="neutral">{group.holdings.length} ativos</Badge>
                </div>
                <div className="flex items-center gap-4 font-mono text-xs">
                  <span className="text-muted-foreground">
                    Peso: <strong className="text-foreground">{formatPercentPtBr(group.weightPct, 1)}</strong>
                  </span>
                  <span className="font-bold text-foreground">
                    {formatCurrencyBRL(group.totalMarketValue)}
                  </span>
                </div>
              </button>
              {isOpen && (
                <div className="accordion-body p-3">
                  <Table density="compact">
                    <TableHeader>
                      <TableRow>
                        <TableHead>Ticker</TableHead>
                        <TableHead className="text-right">Quantidade</TableHead>
                        <TableHead className="text-right">Preço Médio</TableHead>
                        <TableHead className="text-right">Preço Atual</TableHead>
                        <TableHead className="text-right">Saldo</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {group.holdings.map((h) => (
                        <TableRow key={h.ticker}>
                          <TableCell className="font-mono font-bold">{h.ticker}</TableCell>
                          <TableCell className="text-right font-mono">{formatQuantityPtBr(h.shares)}</TableCell>
                          <TableCell className="text-right font-mono">{formatCurrencyBRL(h.average_buy_price)}</TableCell>
                          <TableCell className="text-right font-mono">{formatCurrencyBRL(h.currentPrice)}</TableCell>
                          <TableCell className="text-right font-mono font-bold">{formatCurrencyBRL(h.marketValue)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
