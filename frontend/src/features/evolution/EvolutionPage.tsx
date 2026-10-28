import * as React from "react";
import { useAppContext } from "@/state/app-context";
import { usePortfolioMetrics } from "@/hooks/use-portfolio-metrics";
import { renderPlotlySafely } from "@/hooks/use-plotly-chart";
import { getChartThemeTokens } from "@/lib/theme";
import {
  formatCurrencyBRL,
  formatPercentPtBr,
  formatSignedCurrencyBRL,
} from "@/lib/formatters";
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

export function EvolutionPage() {
  const { activeRoute, theme, portfolio, quotes } = useAppContext();
  const metrics = usePortfolioMetrics(portfolio, quotes);
  const [periodMode, setPeriodMode] = React.useState<"12m" | "all">("12m");
  const chartRef = React.useRef<HTMLDivElement | null>(null);

  const timelineEvents = React.useMemo(() => {
    const raw = Array.isArray(portfolio.b3Timeline) ? portfolio.b3Timeline : [];
    return periodMode === "12m" ? raw.slice(-12) : raw;
  }, [portfolio.b3Timeline, periodMode]);

  React.useEffect(() => {
    const tokens = getChartThemeTokens();
    let xAxis: string[] = [];
    let equityY: number[] = [];
    let investedY: number[] = [];

    if (timelineEvents.length > 0) {
      xAxis = timelineEvents.map(
        (ev, idx) => String(ev.month_year || ev.date || `P${idx + 1}`)
      );
      investedY = timelineEvents.map((ev) =>
        Number(ev.invested ?? ev.total_value ?? metrics.totalCostBasis)
      );
      equityY = timelineEvents.map((ev, idx) =>
        Number(ev.total_equity ?? Math.max(investedY[idx], metrics.totalEquity))
      );
    } else if (metrics.totalEquity > 0 || metrics.totalCostBasis > 0) {
      xAxis = ["Posição Atual"];
      investedY = [metrics.totalCostBasis];
      equityY = [metrics.totalEquity];
    }

    const traces = [
      {
        name: "Patrimônio Consolidado",
        x: xAxis,
        y: equityY,
        type: "scatter",
        mode: "lines+markers",
        line: { color: tokens.primary, width: 3 },
      },
      {
        name: "Capital Aportado",
        x: xAxis,
        y: investedY,
        type: "bar",
        marker: { color: tokens.invested, opacity: 0.55, cornerradius: 4 },
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
      legend: { orientation: "h", y: 1.12, x: 0 },
      xaxis: { gridcolor: "rgba(0,0,0,0)" },
      yaxis: { gridcolor: tokens.grid, tickprefix: "R$ " },
    });
  }, [
    theme,
    activeRoute,
    timelineEvents,
    metrics.totalCostBasis,
    metrics.totalEquity,
  ]);

  const isVisible = activeRoute === "carteira/patrimonio";

  return (
    <section
      id="tab-pane-patrimonio"
      role="tabpanel"
      aria-labelledby="subnav-tab-patrimonio"
      className={`tab-view area-patrimonio mx-auto max-w-[1600px] space-y-5 px-4 py-5 pb-20 ${
        isVisible ? "" : "hidden"
      }`}
    >
      {/* Gráfico Patrimônio x Aportes + Resumo do Período (Penpot Screen 04) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <Card
          kind="chart"
          className="card-surface chart-card bg-white lg:col-span-8"
        >
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border pb-3">
            <div>
              <h3 className="section-title font-sans text-sm font-bold text-foreground">
                Patrimônio x aportes
              </h3>
              <p className="section-subtitle text-xs text-muted-foreground">
                Curva de crescimento patrimonial confrontada com o desembolso acumulado
              </p>
            </div>
            <div className="segmented inline-flex rounded-md border border-border bg-surface-subtle p-0.5">
              <button
                type="button"
                id="btn-patrimonio-12m"
                aria-pressed={periodMode === "12m"}
                onClick={() => setPeriodMode("12m")}
                className={`rounded-sm px-3 py-1 text-xs font-semibold ${
                  periodMode === "12m"
                    ? "bg-surface text-foreground shadow-sm"
                    : "text-muted-foreground"
                }`}
              >
                12 meses
              </button>
              <button
                type="button"
                id="btn-patrimonio-all"
                aria-pressed={periodMode === "all"}
                onClick={() => setPeriodMode("all")}
                className={`rounded-sm px-3 py-1 text-xs font-semibold ${
                  periodMode === "all"
                    ? "bg-surface text-foreground shadow-sm"
                    : "text-muted-foreground"
                }`}
              >
                Tudo
              </button>
            </div>
          </div>
          <div
            id="chart-patrimonio-detailed"
            ref={chartRef}
            className="mt-3 h-[300px] w-full block"
          />
        </Card>

        <Card className="card-surface lg:col-span-4 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="border-b border-border pb-3">
              <h3 className="section-title font-sans text-sm font-bold text-foreground">
                Resumo do período
              </h3>
              <p className="section-subtitle text-xs text-muted-foreground">
                Consolidação contábil sem projeções sintéticas
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between rounded-md bg-surface-subtle p-3">
                <span className="text-xs font-semibold text-muted-foreground">
                  Patrimônio Final
                </span>
                <span
                  id="pat-summary-final"
                  className="font-mono text-base font-extrabold text-foreground"
                >
                  {formatCurrencyBRL(metrics.totalEquity)}
                </span>
              </div>

              <div className="flex items-center justify-between rounded-md bg-surface-subtle p-3">
                <span className="text-xs font-semibold text-muted-foreground">
                  Capital Investido
                </span>
                <span
                  id="pat-summary-invested"
                  className="font-mono text-sm font-bold text-foreground"
                >
                  {formatCurrencyBRL(metrics.totalCostBasis)}
                </span>
              </div>

              <div className="flex items-center justify-between rounded-md bg-surface-subtle p-3">
                <span className="text-xs font-semibold text-muted-foreground">
                  Ganho de Capital
                </span>
                <span
                  id="pat-summary-gain"
                  className={`font-mono text-sm font-bold ${
                    metrics.unrealizedPnl >= 0 ? "text-success" : "text-danger"
                  }`}
                >
                  {formatSignedCurrencyBRL(metrics.unrealizedPnl)} (
                  {metrics.unrealizedPct !== null
                    ? formatPercentPtBr(metrics.unrealizedPct, 2, true)
                    : "N/A"}
                  )
                </span>
              </div>
            </div>
          </div>

          <div className="mt-4 rounded-md border border-border bg-surface-subtle p-3 text-xs text-muted-foreground">
            Caixa livre contabilizado: {formatCurrencyBRL(metrics.availableCash)}
          </div>
        </Card>
      </div>

      {/* Histórico de Aportes e Eventos */}
      <Card className="card-surface">
        <div className="mb-3 border-b border-border pb-3">
          <h3 className="section-title font-sans text-sm font-bold text-foreground">
            Histórico de aportes e eventos patrimoniais
          </h3>
          <p className="section-subtitle text-xs text-muted-foreground">
            Lançamentos reais extraídos da custódia e notas de corretagem
          </p>
        </div>

        <Table showMobileHint>
          <TableHeader>
            <TableRow>
              <TableHead>Data / Mês</TableHead>
              <TableHead>Natureza</TableHead>
              <TableHead>Ativo</TableHead>
              <TableHead className="text-right">Capital Aportado</TableHead>
              <TableHead className="text-right">Patrimônio Consolidado</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody id="pat-history-tbody">
            {timelineEvents.length > 0 ? (
              [...timelineEvents].reverse().map((ev, idx) => (
                <TableRow key={`${ev.month_year || ev.date || idx}`}>
                  <TableCell className="font-mono font-bold">
                    {ev.month_year || ev.date || "Atual"}
                  </TableCell>
                  <TableCell>
                    <Badge intent="primary">
                      {ev.type || ev.event_type || "CONSOLIDAÇÃO MENSAL"}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-mono">
                    {ev.ticker || ev.product || "Carteira"}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCurrencyBRL(
                      Number(ev.invested ?? ev.total_value ?? metrics.totalCostBasis)
                    )}
                  </TableCell>
                  <TableCell className="text-right font-mono font-bold">
                    {formatCurrencyBRL(
                      Number(ev.total_equity ?? metrics.totalEquity)
                    )}
                  </TableCell>
                </TableRow>
              ))
            ) : metrics.enrichedHoldings.length > 0 ? (
              metrics.enrichedHoldings.map((h) => (
                <TableRow key={h.ticker}>
                  <TableCell className="font-mono font-bold">Posição Ativa</TableCell>
                  <TableCell>
                    <Badge intent="success">CUSTÓDIA ATIVA</Badge>
                  </TableCell>
                  <TableCell className="font-mono font-bold">{h.ticker}</TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCurrencyBRL(h.costBasis)}
                  </TableCell>
                  <TableCell className="text-right font-mono font-bold">
                    {formatCurrencyBRL(h.marketValue)}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} className="py-6 text-center text-muted-foreground">
                  Nenhum evento patrimonial registrado.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
    </section>
  );
}
