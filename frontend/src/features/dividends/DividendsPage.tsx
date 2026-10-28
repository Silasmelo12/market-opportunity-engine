import * as React from "react";
import { useAppContext } from "@/state/app-context";
import { usePortfolioMetrics } from "@/hooks/use-portfolio-metrics";
import {
  aggregateAnnualIncomeSeries,
  normalizeMonthlyIncomeSeries,
} from "@/services/dividends-service";
import { renderPlotlySafely } from "@/hooks/use-plotly-chart";
import { getChartThemeTokens } from "@/lib/theme";
import { formatCurrencyBRL, formatPercentPtBr } from "@/lib/formatters";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";

export function DividendsPage() {
  const { activeRoute, theme, portfolio, quotes } = useAppContext();
  const metrics = usePortfolioMetrics(portfolio, quotes);
  const [viewMode, setViewMode] = React.useState<"mensal" | "anual">("mensal");
  const chartRef = React.useRef<HTMLDivElement | null>(null);

  const normalizedSeries = React.useMemo(
    () => normalizeMonthlyIncomeSeries(portfolio.b3MonthlyIncome || []),
    [portfolio.b3MonthlyIncome]
  );

  const annualSeries = React.useMemo(
    () => aggregateAnnualIncomeSeries(normalizedSeries),
    [normalizedSeries]
  );

  const totalDividends = React.useMemo(() => {
    const fromSeries = normalizedSeries.reduce((acc, i) => acc + i.total, 0);
    return fromSeries > 0 ? fromSeries : Number(portfolio.b3TotalIncome) || 0;
  }, [normalizedSeries, portfolio.b3TotalIncome]);

  const monthlyAvg =
    normalizedSeries.length > 0 ? totalDividends / normalizedSeries.length : 0;
  const yieldOnCost =
    metrics.totalCostBasis > 0
      ? (totalDividends / metrics.totalCostBasis) * 100
      : 0;

  const breakdown = React.useMemo(() => {
    const div = normalizedSeries.reduce((acc, i) => acc + i.dividendos, 0);
    const jcp = normalizedSeries.reduce((acc, i) => acc + i.jcp, 0);
    const rend = normalizedSeries.reduce((acc, i) => acc + i.rendimentos, 0);
    const sum = div + jcp + rend || 1;
    return [
      {
        label: "Dividendos Isentos",
        value: div,
        pct: (div / sum) * 100,
      },
      {
        label: "Juros sobre Capital Próprio (JCP)",
        value: jcp,
        pct: (jcp / sum) * 100,
      },
      {
        label: "Rendimentos de FIIs & Outros",
        value: rend,
        pct: (rend / sum) * 100,
      },
    ];
  }, [normalizedSeries]);

  React.useEffect(() => {
    const tokens = getChartThemeTokens();
    const xValues =
      viewMode === "mensal"
        ? normalizedSeries.map((i) => i.shortLabel)
        : annualSeries.map((i) => i.year);
    const yValues =
      viewMode === "mensal"
        ? normalizedSeries.map((i) => i.total)
        : annualSeries.map((i) => i.total);

    const traces = [
      {
        name: "Proventos (R$)",
        x: xValues,
        y: yValues,
        type: "bar",
        marker: {
          color: tokens.proventos,
          cornerradius: 4,
        },
      },
    ];

    renderPlotlySafely(chartRef.current, traces, {
      margin: { t: 16, r: 16, b: 36, l: 54 },
      paper_bgcolor: tokens.bg,
      plot_bgcolor: tokens.bg,
      font: {
        family: "Plus Jakarta Sans, sans-serif",
        size: 11,
        color: tokens.text,
      },
      xaxis: {
        type: "category",
        gridcolor: "rgba(0,0,0,0)",
      },
      yaxis: {
        gridcolor: tokens.grid,
        tickprefix: "R$ ",
      },
      showlegend: false,
    });
  }, [theme, activeRoute, viewMode, normalizedSeries, annualSeries]);

  const isVisible = activeRoute === "carteira/proventos";

  return (
    <section
      id="tab-pane-proventos"
      role="tabpanel"
      aria-labelledby="subnav-tab-proventos"
      className={`tab-view area-proventos mx-auto max-w-[1600px] space-y-5 px-4 py-5 pb-20 ${
        isVisible ? "" : "hidden"
      }`}
    >
      {/* 4 KPIs de Proventos (Penpot Screen 03) */}
      <div
        id="proventos-kpis-grid"
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <Card kind="kpi" className="kpi-card card-surface">
          <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            Total Acumulado
          </span>
          <div
            id="prov-kpi-total"
            className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-foreground tabular-nums"
          >
            {formatCurrencyBRL(totalDividends)}
          </div>
          <div className="kpi-sub mt-1.5 text-xs text-muted-foreground">
            Histórico conciliado B3
          </div>
        </Card>

        <Card kind="kpi" className="kpi-card card-surface">
          <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            Média Mensal
          </span>
          <div
            id="prov-kpi-avg"
            className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-foreground tabular-nums"
          >
            {formatCurrencyBRL(monthlyAvg)}
          </div>
          <div className="kpi-sub mt-1.5 text-xs text-muted-foreground">
            Por mês com distribuição
          </div>
        </Card>

        <Card kind="kpi" className="kpi-card card-surface">
          <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            Yield on Cost (YoC)
          </span>
          <div
            id="prov-kpi-yoc"
            className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-success tabular-nums"
          >
            {formatPercentPtBr(yieldOnCost, 2)}
          </div>
          <div className="kpi-sub mt-1.5 text-xs text-muted-foreground">
            Sobre custo de aquisição
          </div>
        </Card>

        <Card kind="kpi" className="kpi-card card-surface">
          <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            Meses com Registros
          </span>
          <div
            id="prov-kpi-months"
            className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-foreground tabular-nums"
          >
            {normalizedSeries.length} meses
          </div>
          <div className="kpi-sub mt-1.5 text-xs text-muted-foreground">
            Fluxo de caixa passivo
          </div>
        </Card>
      </div>

      {/* Gráfico de Evolução de Proventos + Composição da Renda */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <Card
          kind="chart"
          className="card-surface chart-card bg-white lg:col-span-8 overflow-hidden"
        >
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border pb-3">
            <div>
              <h3 className="section-title font-sans text-sm font-bold text-foreground">
                Evolução de Proventos
              </h3>
              <p className="section-subtitle text-xs text-muted-foreground">
                Distribuição histórica de dividendos, JCP e rendimentos creditados
              </p>
            </div>
            <div className="segmented inline-flex rounded-md border border-border bg-surface-subtle p-0.5">
              <button
                type="button"
                id="btn-proventos-view-mensal"
                aria-pressed={viewMode === "mensal"}
                onClick={() => setViewMode("mensal")}
                className={`rounded-sm px-3 py-1 text-xs font-semibold ${
                  viewMode === "mensal"
                    ? "bg-surface text-foreground shadow-sm"
                    : "text-muted-foreground"
                }`}
              >
                Mensal
              </button>
              <button
                type="button"
                id="btn-proventos-view-anual"
                aria-pressed={viewMode === "anual"}
                onClick={() => setViewMode("anual")}
                className={`rounded-sm px-3 py-1 text-xs font-semibold ${
                  viewMode === "anual"
                    ? "bg-surface text-foreground shadow-sm"
                    : "text-muted-foreground"
                }`}
              >
                Anual
              </button>
            </div>
          </div>
          <div
            id="chart-proventos-detailed"
            ref={chartRef}
            className="mt-3 h-[300px] w-full block"
          />
        </Card>

        <Card className="card-surface lg:col-span-4 flex flex-col justify-between">
          <div>
            <div className="border-b border-border pb-3">
              <h3 className="section-title font-sans text-sm font-bold text-foreground">
                Composição da Renda
              </h3>
              <p className="section-subtitle text-xs text-muted-foreground">
                Participação por natureza fiscal do provento
              </p>
            </div>
            <div id="prov-composition-list" className="mt-4 space-y-4">
              {breakdown.map((item) => (
                <div key={item.label} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-foreground">{item.label}</span>
                    <span className="font-mono font-bold text-foreground">
                      {formatCurrencyBRL(item.value)} ({formatPercentPtBr(item.pct, 1)})
                    </span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-surface-subtle">
                    <div
                      className="h-full rounded-full bg-primary transition-all"
                      style={{ width: `${Math.min(100, Math.max(4, item.pct))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 rounded-md border border-border bg-surface-subtle p-3 text-xs text-muted-foreground">
            Dados consolidados diretamente dos extratos de movimentação da B3, sem projeções artificiais.
          </div>
        </Card>
      </div>

      {/* Tabela de Histórico de Proventos Creditados */}
      <Card className="card-surface">
        <div className="mb-3 border-b border-border pb-3">
          <h3 className="section-title font-sans text-sm font-bold text-foreground">
            Últimos proventos creditados
          </h3>
          <p className="section-subtitle text-xs text-muted-foreground">
            Detalhamento cronológico mensal por categoria de provento
          </p>
        </div>
        <Table showMobileHint>
          <TableHeader>
            <TableRow>
              <TableHead>Competência</TableHead>
              <TableHead>Tipo Principal</TableHead>
              <TableHead className="text-right">Dividendos</TableHead>
              <TableHead className="text-right">JCP</TableHead>
              <TableHead className="text-right">Rendimentos</TableHead>
              <TableHead className="text-right">Total Recebido</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody id="prov-history-tbody">
            {normalizedSeries.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="py-6 text-center text-muted-foreground">
                  Nenhum provento registrado. Importe seu extrato B3 para visualizar o histórico.
                </TableCell>
              </TableRow>
            ) : (
              [...normalizedSeries].reverse().map((row) => (
                <TableRow key={row.rawMonthYear}>
                  <TableCell className="font-mono font-bold">{row.shortLabel}</TableCell>
                  <TableCell>
                    <Badge intent="success">PROVENTO CREDITADO</Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCurrencyBRL(row.dividendos)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCurrencyBRL(row.jcp)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCurrencyBRL(row.rendimentos)}
                  </TableCell>
                  <TableCell className="text-right font-mono font-bold text-success">
                    {formatCurrencyBRL(row.total)}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>
    </section>
  );
}
