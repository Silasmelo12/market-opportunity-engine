import * as React from "react";
import { useAppContext } from "@/state/app-context";
import { fetchAssetAnalysis } from "@/services/market-service";
import type { AnalyzeResponse } from "@/types/market";
import { renderPlotlySafely } from "@/hooks/use-plotly-chart";
import { getChartThemeTokens } from "@/lib/theme";
import { formatCurrencyBRL, formatPercentPtBr } from "@/lib/formatters";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";

const KNOWN_ASSET_NAMES: Record<string, string> = {
  "PETR4.SA": "Petrobras PN",
  "VALE3.SA": "Vale ON",
  "WEGE3.SA": "WEG ON",
  "ITUB4.SA": "Itaú Unibanco PN",
  "BBAS3.SA": "Banco do Brasil ON",
  "TGAR11.SA": "TG Ativo Real FII",
  "HGLG11.SA": "CSHG Logística FII",
  "CL=F": "Crude Oil WTI (Petróleo)",
  "GC=F": "Gold Futures (Ouro)",
  "BTC-USD": "Bitcoin USD",
};

const STRATEGY_GROUPS = [
  {
    id: "group_reversal",
    title: "Reversão & Negação 2x2",
    strategies: [
      { id: "t1_open", label: "Negação Anterior (Abertura)" },
      { id: "t1_close", label: "Negação Anterior (Fechamento)" },
      { id: "spring_wyckoff", label: "Spring Institucional Wyckoff" },
    ],
  },
  {
    id: "group_patterns",
    title: "Padrões Duplos & Estruturais",
    strategies: [
      { id: "double_bottom", label: "Fundo Duplo Confirmado" },
      { id: "double_top", label: "Topo Duplo de Exaustão" },
      { id: "bearish_engulfing", label: "Engolfo de Baixa" },
      { id: "shooting_star", label: "Estrela Cadente" },
    ],
  },
] as const;

declare global {
  interface Window {
    LightweightCharts?: {
      createChart: (
        container: HTMLElement,
        options: Record<string, unknown>
      ) => {
        addCandlestickSeries: (
          opts: Record<string, unknown>
        ) => {
          setData: (data: unknown[]) => void;
          setMarkers?: (markers: unknown[]) => void;
        };
        timeScale: () => { fitContent: () => void };
        remove: () => void;
      };
    };
  }
}

export function ChartPage() {
  const {
    activeRoute,
    theme,
    activeDirection,
    chartTicker,
    setChartTicker,
    chartAssetName,
    contextualTicker,
    contextualFromRoute,
    contextualFromLabel,
    returnFromChartToSource,
  } = useAppContext();

  const [period, setPeriod] = React.useState<string>("2y");
  const [interval, setIntervalState] = React.useState<string>("1d");
  const [preset, setPreset] = React.useState<"essencial" | "all">("essencial");
  const [enabledStrategies, setEnabledStrategies] = React.useState<
    Record<string, boolean>
  >({
    t1_open: true,
    t1_close: true,
    spring_wyckoff: true,
    double_bottom: true,
    double_top: true,
    bearish_engulfing: true,
    shooting_star: true,
  });

  const [analysis, setAnalysis] = React.useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = React.useState<boolean>(false);

  const tvContainerRef = React.useRef<HTMLDivElement | null>(null);
  const rankingPlotRef = React.useRef<HTMLDivElement | null>(null);
  const scatterPlotRef = React.useRef<HTMLDivElement | null>(null);

  const loadAnalysis = React.useCallback(
    async (targetTicker: string, forceRefresh = false) => {
      const clean = String(targetTicker || "PETR4.SA").toUpperCase().trim();
      setLoading(true);
      try {
        const resp = await fetchAssetAnalysis({
          ticker: clean,
          period,
          interval,
          direction: activeDirection,
          forceRefresh,
        });
        setAnalysis(resp);
      } catch {
        setAnalysis({
          ticker: clean,
          candles: [],
          signals: [],
          summaries: [],
        });
      } finally {
        setLoading(false);
      }
    },
    [period, interval, activeDirection]
  );

  React.useEffect(() => {
    if (activeRoute === "quant/grafico") {
      void loadAnalysis(chartTicker, false);
    }
  }, [activeRoute, chartTicker, loadAnalysis]);

  React.useEffect(() => {
    const tokens = getChartThemeTokens();
    const container = tvContainerRef.current;
    if (
      container &&
      typeof window !== "undefined" &&
      window.LightweightCharts?.createChart &&
      analysis?.candles?.length
    ) {
      container.innerHTML = "";
      try {
        const chart = window.LightweightCharts.createChart(container, {
          width: container.clientWidth || 800,
          height: 380,
          layout: {
            background: { color: tokens.bg },
            textColor: tokens.text,
          },
          grid: {
            vertLines: { color: tokens.grid },
            horzLines: { color: tokens.grid },
          },
        });
        const series = chart.addCandlestickSeries({
          upColor: tokens.up,
          downColor: tokens.down,
          borderUpColor: tokens.up,
          borderDownColor: tokens.down,
          wickUpColor: tokens.up,
          wickDownColor: tokens.down,
        });
        series.setData(analysis.candles);
        chart.timeScale().fitContent();
      } catch {
        // Fallback safely if canvas unavailable in headless unit test
      }
    }

    const summaries = analysis?.summaries || [];
    renderPlotlySafely(
      rankingPlotRef.current,
      [
        {
          type: "bar",
          orientation: "h",
          x: summaries.map((s) => s.win_rate),
          y: summaries.map((s) => s.strategy_label || s.strategy_sub_id),
          marker: { color: tokens.primary, cornerradius: 4 },
        },
      ],
      {
        margin: { t: 12, r: 16, b: 28, l: 120 },
        paper_bgcolor: tokens.bg,
        plot_bgcolor: tokens.bg,
        font: { family: "Plus Jakarta Sans, sans-serif", size: 11, color: tokens.text },
        xaxis: { gridcolor: tokens.grid, ticksuffix: "%" },
        yaxis: { gridcolor: "rgba(0,0,0,0)" },
      }
    );

    renderPlotlySafely(
      scatterPlotRef.current,
      [
        {
          type: "scatter",
          mode: "markers",
          x: summaries.map((s) => Math.abs(s.mean_mae || 1)),
          y: summaries.map((s) => s.mean_forward_return || 0),
          text: summaries.map((s) => s.strategy_label),
          marker: { color: tokens.secondary, size: 10 },
        },
      ],
      {
        margin: { t: 12, r: 16, b: 32, l: 48 },
        paper_bgcolor: tokens.bg,
        plot_bgcolor: tokens.bg,
        font: { family: "Plus Jakarta Sans, sans-serif", size: 11, color: tokens.text },
        xaxis: { title: "Risco Médio (MAE %)", gridcolor: tokens.grid },
        yaxis: { title: "Retorno Médio (%)", gridcolor: tokens.grid },
      }
    );
  }, [theme, analysis]);

  const resolvedTitleName =
    analysis?.asset_name ||
    KNOWN_ASSET_NAMES[chartTicker.toUpperCase()] ||
    chartAssetName ||
    "Análise Estatística";

  const resolvedTimingStatus =
    typeof analysis?.timing_status === "string"
      ? analysis.timing_status
      : analysis?.timing_status?.label ||
        analysis?.timing_status?.category ||
        "ANÁLISE QUANTITATIVA";

  const showContextualBar = Boolean(contextualFromRoute && contextualFromLabel);
  const isVisible = activeRoute === "quant/grafico";

  return (
    <section
      id="tab-terminal"
      role="tabpanel"
      aria-labelledby="subnav-tab-tradingview"
      className={`tab-view quant-area mx-auto max-w-[1600px] space-y-4 px-4 py-5 pb-20 ${
        isVisible ? "" : "hidden"
      }`}
    >
      {/* Barra de Retorno Contextual (Posições / Radar -> Gráfico) */}
      <div
        id="chart-contextual-return-bar"
        className={`card-surface flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border bg-surface px-4 py-2.5 shadow-sm ${
          showContextualBar ? "" : "hidden"
        }`}
      >
        <div className="flex items-center gap-2.5">
          <button
            type="button"
            id="btn-chart-return-to-source"
            onClick={returnFromChartToSource}
            className="btn-secondary rounded-md px-3 py-1 text-xs font-bold"
          >
            <span id="chart-return-label">
              {contextualFromLabel || "← Voltar"}
            </span>
          </button>
          <span className="text-xs text-muted-foreground">
            Visualizando ativo selecionado:
          </span>
          <Badge id="chart-contextual-ticker-badge" intent="primary">
            {contextualTicker || chartTicker}
          </Badge>
        </div>
      </div>

      {/* Layout Principal: Sidebar de Estratégias + Shell do Gráfico */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <aside className="chart-sidebar card-surface lg:col-span-3 space-y-4 rounded-lg border border-border bg-surface p-4 shadow-sm">
          <div className="space-y-3">
            <div>
              <Label htmlFor="input-ticker">Ticker do Ativo</Label>
              <Input
                id="input-ticker"
                mono
                inputSize="sm"
                value={chartTicker}
                onChange={(e) => setChartTicker(e.target.value.toUpperCase())}
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label htmlFor="select-period">Período</Label>
                <Select
                  id="select-period"
                  selectSize="sm"
                  value={period}
                  onChange={(e) => setPeriod(e.target.value)}
                >
                  <option value="1y">1 Ano</option>
                  <option value="2y">2 Anos</option>
                  <option value="5y">5 Anos</option>
                  <option value="max">Máximo</option>
                </Select>
              </div>
              <div>
                <Label htmlFor="select-interval-chart">Timeframe</Label>
                <Select
                  id="select-interval-chart"
                  selectSize="sm"
                  value={interval}
                  onChange={(e) => setIntervalState(e.target.value)}
                >
                  <option value="1d">1D (Diário)</option>
                  <option value="1wk">1S (Semanal)</option>
                  <option value="4h">4h</option>
                </Select>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                type="button"
                id="btn-load-analysis"
                variant="primary"
                size="sm"
                className="flex-1"
                disabled={loading}
                onClick={() => void loadAnalysis(chartTicker, false)}
              >
                {loading ? "Carregando..." : "Analisar Ativo"}
              </Button>
              <Button
                type="button"
                id="btn-refresh-data"
                variant="secondary"
                size="sm"
                onClick={() => void loadAnalysis(chartTicker, true)}
              >
                Atualizar
              </Button>
            </div>
          </div>

          {/* Presets de Estratégias */}
          <div className="space-y-2 border-t border-border pt-3">
            <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
              Filtro Rápido de Sinais
            </span>
            <div className="segmented flex rounded-md border border-border bg-surface-subtle p-0.5">
              <button
                type="button"
                aria-pressed={preset === "essencial"}
                onClick={() => setPreset("essencial")}
                className={`flex-1 rounded-sm py-1 text-[11px] font-semibold ${
                  preset === "essencial"
                    ? "bg-surface text-foreground shadow-sm"
                    : "text-muted-foreground"
                }`}
              >
                Essencial
              </button>
              <button
                type="button"
                aria-pressed={preset === "all"}
                onClick={() => setPreset("all")}
                className={`flex-1 rounded-sm py-1 text-[11px] font-semibold ${
                  preset === "all"
                    ? "bg-surface text-foreground shadow-sm"
                    : "text-muted-foreground"
                }`}
              >
                Todas (48)
              </button>
            </div>
          </div>

          {/* Grupos de Estratégias */}
          <div className="space-y-3 border-t border-border pt-3">
            {STRATEGY_GROUPS.map((grp) => (
              <div
                key={grp.id}
                className="strategy-group rounded-md border border-border bg-surface-subtle p-2.5 space-y-2"
              >
                <div className="font-sans text-xs font-bold text-foreground">
                  {grp.title}
                </div>
                <div className="space-y-1.5">
                  {grp.strategies.map((st) => (
                    <label
                      key={st.id}
                      className="flex items-center gap-2 text-xs text-muted-foreground cursor-pointer hover:text-foreground"
                    >
                      <Checkbox
                        checked={Boolean(enabledStrategies[st.id])}
                        onCheckedChange={(checked) =>
                          setEnabledStrategies((prev) => ({
                            ...prev,
                            [st.id]: Boolean(checked),
                          }))
                        }
                      />
                      <span>{st.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </aside>

        {/* Área Principal do Gráfico e Métricas */}
        <div className="chart-shell lg:col-span-9 space-y-4">
          <Card className="card-surface p-4">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border pb-3">
              <div>
                <h2
                  id="active-asset-title"
                  className="section-title font-sans text-base font-extrabold text-foreground"
                >
                  {chartTicker} • {resolvedTitleName}
                </h2>
                <p className="section-subtitle text-xs text-muted-foreground">
                  Série histórica OHLCV com marcações de fundo/topo estatístico e preço médio B3
                </p>
              </div>
              <Badge intent="primary">
                {resolvedTimingStatus}
              </Badge>
            </div>

            <div className="w-full overflow-x-auto" style={{ overflowX: "auto" }}>
              <div
                id="tv-chart-container"
                ref={tvContainerRef}
                className="mt-3 h-[380px] w-full overflow-x-auto rounded-md bg-surface"
              />
            </div>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card kind="chart" className="card-surface chart-card bg-white">
              <h3 className="section-title font-sans text-sm font-bold text-foreground">
                Ranking de Eficiência por Estratégia
              </h3>
              <div
                id="plot-ranking"
                ref={rankingPlotRef}
                className="mt-2 h-[220px] w-full block"
              />
            </Card>

            <Card kind="chart" className="card-surface chart-card bg-white">
              <h3 className="section-title font-sans text-sm font-bold text-foreground">
                Matriz Risco (MAE) x Retorno Esperado
              </h3>
              <div
                id="plot-scatter"
                ref={scatterPlotRef}
                className="mt-2 h-[220px] w-full block"
              />
            </Card>
          </div>

          <Card className="card-surface">
            <div className="mb-3 border-b border-border pb-2.5">
              <h3 className="section-title font-sans text-sm font-bold text-foreground">
                Histórico Cronológico de Sinais Detectados
              </h3>
            </div>
            <Table density="compact" showMobileHint>
              <TableHeader>
                <TableRow>
                  <TableHead>Data</TableHead>
                  <TableHead>Direção</TableHead>
                  <TableHead>Estratégia</TableHead>
                  <TableHead className="text-right">Preço no Sinal</TableHead>
                  <TableHead className="text-right">Retorno Forward</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody id="signals-table-body">
                {(analysis?.signals || []).length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="py-6 text-center text-muted-foreground">
                      Nenhum sinal filtrado no período selecionado.
                    </TableCell>
                  </TableRow>
                ) : (
                  (analysis?.signals || []).slice(0, 30).map((sig, idx) => (
                    <TableRow key={`${sig.time || sig.signal_date || idx}-${idx}`}>
                      <TableCell className="font-mono">
                        {sig.time || sig.signal_date || sig.execution_date || "—"}
                      </TableCell>
                      <TableCell>
                        <Badge intent={sig.direction === "BUY" ? "success" : "danger"}>
                          {sig.direction === "BUY" ? "▲ COMPRA" : "▼ VENDA"}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-semibold">
                        {sig.strategy_label || sig.strategy_sub_id}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {formatCurrencyBRL(sig.price ?? sig.execution_price ?? 0)}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {formatPercentPtBr(
                          sig.forward_return ?? sig.forward_return_pct ?? 0,
                          2,
                          true
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </div>
      </div>
    </section>
  );
}
