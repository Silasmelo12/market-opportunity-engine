import * as React from "react";
import { useAppContext } from "@/state/app-context";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import { formatCurrencyBRL, formatPercentPtBr } from "@/lib/formatters";
import { KNOWN_ASSET_NAMES } from "@/lib/constants";
import { fetchAssetAnalysis } from "@/services/market-service";
import type { AnalyzeResponse } from "@/types/market";
import { renderPlotlySafely } from "@/hooks/use-plotly-chart";
import {
  StrategyCombobox,
  ALL_STRATEGY_IDS,
} from "./StrategyCombobox";

interface ChartThemeTokens {
  bg: string;
  grid: string;
  text: string;
  up: string;
  down: string;
  primary: string;
  secondary: string;
}

function getChartThemeTokens(): ChartThemeTokens {
  if (typeof document === "undefined") {
    return {
      bg: "rgb(255, 255, 255)",
      grid: "rgba(226, 232, 240, 0.6)",
      text: "rgb(71, 85, 105)",
      up: "rgb(4, 120, 87)",
      down: "rgb(190, 18, 60)",
      primary: "rgb(3, 105, 161)",
      secondary: "rgb(13, 148, 136)",
    };
  }
  const root = document.documentElement;
  const cs = getComputedStyle(root);
  return {
    bg: cs.getPropertyValue("--surface").trim() || "rgb(255, 255, 255)",
    grid: cs.getPropertyValue("--chart-grid").trim() || "rgba(226, 232, 240, 0.6)",
    text: cs.getPropertyValue("--chart-axis").trim() || "rgb(71, 85, 105)",
    up: cs.getPropertyValue("--chart-positive").trim() || "rgb(4, 120, 87)",
    down: cs.getPropertyValue("--chart-negative").trim() || "rgb(190, 18, 60)",
    primary: cs.getPropertyValue("--chart-primary").trim() || "rgb(3, 105, 161)",
    secondary: cs.getPropertyValue("--chart-secondary").trim() || "rgb(13, 148, 136)",
  };
}

declare global {
  interface Window {
    LightweightCharts?: {
      createChart: (
        container: HTMLElement,
        options: Record<string, unknown>
      ) => {
        addCandlestickSeries: (options: Record<string, unknown>) => {
          setData: (candles: unknown[]) => void;
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

  // Initialize all 50 strategies as enabled by default
  const [enabledStrategies, setEnabledStrategies] = React.useState<
    Record<string, boolean>
  >(() => {
    const initial: Record<string, boolean> = {};
    ALL_STRATEGY_IDS.forEach((id) => {
      initial[id] = true;
    });
    return initial;
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

  // Filter signals strictly by activeDirection and enabledStrategies
  const displayedSignals = React.useMemo(() => {
    const all = analysis?.signals || [];
    return all.filter((sig) => {
      if (activeDirection === "BUY" && sig.direction !== "BUY") return false;
      if (activeDirection === "SELL" && sig.direction !== "SELL") return false;
      const stratId = sig.strategy_sub_id;
      if (stratId && enabledStrategies[stratId] === false) return false;
      return true;
    });
  }, [analysis, activeDirection, enabledStrategies]);

  // Filter summaries strictly by activeDirection and enabledStrategies
  const displayedSummaries = React.useMemo(() => {
    const all = analysis?.summaries || [];
    return all.filter((s) => {
      if (activeDirection === "BUY" && s.direction !== "BUY") return false;
      if (activeDirection === "SELL" && s.direction !== "SELL") return false;
      const stratId = s.strategy_sub_id;
      if (stratId && enabledStrategies[stratId] === false) return false;
      return true;
    });
  }, [analysis, activeDirection, enabledStrategies]);

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

        if (series.setMarkers && displayedSignals.length > 0) {
          const markers = displayedSignals
            .map((sig) => {
              const isBuy = sig.direction === "BUY";
              const timeVal = sig.time || sig.signal_date || sig.execution_date;
              if (!timeVal) return null;
              return {
                time: timeVal,
                position: isBuy ? "belowBar" : "aboveBar",
                color: isBuy ? tokens.up : tokens.down,
                shape: isBuy ? "arrowUp" : "arrowDown",
                text: `${isBuy ? "▲" : "▼"} ${sig.strategy_label || sig.strategy_sub_id}`,
              };
            })
            .filter(Boolean);
          series.setMarkers(markers);
        }

        chart.timeScale().fitContent();
      } catch {
        // Fallback safely if canvas unavailable in headless unit test
      }
    }

    renderPlotlySafely(
      rankingPlotRef.current,
      [
        {
          type: "bar",
          orientation: "h",
          x: displayedSummaries.map((s) => s.win_rate),
          y: displayedSummaries.map((s) => s.strategy_label || s.strategy_sub_id),
          marker: { color: tokens.primary, cornerradius: 4 },
        },
      ],
      {
        margin: { t: 12, r: 16, b: 28, l: 140 },
        paper_bgcolor: tokens.bg,
        plot_bgcolor: tokens.bg,
        font: { family: "Plus Jakarta Sans, sans-serif", size: 11, color: tokens.text },
        xaxis: { gridcolor: tokens.grid, ticksuffix: "%" },
        yaxis: { gridcolor: "rgba(0,0,0,0)", automargin: true },
      }
    );

    renderPlotlySafely(
      scatterPlotRef.current,
      [
        {
          type: "scatter",
          mode: "markers",
          x: displayedSummaries.map((s) => Math.abs(s.mean_mae || 1)),
          y: displayedSummaries.map((s) => s.mean_forward_return || 0),
          text: displayedSummaries.map((s) => s.strategy_label || s.strategy_sub_id),
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
  }, [theme, analysis, displayedSignals, displayedSummaries]);

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

      {/* Layout Principal: Sidebar compacta de Controles + Shell do Gráfico */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Barra Lateral do Gráfico: Mais curta na vertical */}
        <aside className="chart-sidebar card-surface lg:col-span-3 h-fit self-start space-y-3 rounded-lg border border-border bg-surface p-4 shadow-sm">
          <div className="border-b border-border pb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
              Configurações do Ativo
            </span>
          </div>

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

            <div>
              <Label>Filtro de Estratégias</Label>
              <StrategyCombobox
                enabledStrategies={enabledStrategies}
                onChange={setEnabledStrategies}
                activeDirection={activeDirection}
              />
            </div>

            <div className="flex items-center gap-2 pt-1">
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
        </aside>

        {/* Área Principal: Candlesticks TradingView */}
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

          {/* Gráfico 1: Ranking de Eficiência por Estratégia - Ocupa 100% da largura */}
          <Card kind="chart" className="card-surface chart-card bg-white w-full">
            <div className="flex items-center justify-between border-b border-border pb-2 mb-1">
              <h3 className="section-title font-sans text-sm font-bold text-foreground">
                Ranking de Eficiência por Estratégia
              </h3>
              <span className="text-xs text-muted-foreground font-mono">
                {displayedSummaries.length} estratégias avaliadas ({activeDirection})
              </span>
            </div>
            <div
              id="plot-ranking"
              ref={rankingPlotRef}
              className="mt-2 h-[260px] w-full block"
            />
          </Card>

          {/* Gráfico 2: Matriz Risco (MAE) x Retorno Esperado - Ocupa 100% da largura */}
          <Card kind="chart" className="card-surface chart-card bg-white w-full">
            <div className="flex items-center justify-between border-b border-border pb-2 mb-1">
              <h3 className="section-title font-sans text-sm font-bold text-foreground">
                Matriz Risco (MAE) x Retorno Esperado
              </h3>
              <span className="text-xs text-muted-foreground font-mono">
                Retorno Médio vs Drawdown Máximo Adverso ({activeDirection})
              </span>
            </div>
            <div
              id="plot-scatter"
              ref={scatterPlotRef}
              className="mt-2 h-[260px] w-full block"
            />
          </Card>

          {/* Tabela de Sinais Filtrados */}
          <Card className="card-surface">
            <div className="mb-3 flex items-center justify-between border-b border-border pb-2.5">
              <h3 className="section-title font-sans text-sm font-bold text-foreground">
                Histórico Cronológico de Sinais Detectados
              </h3>
              <Badge intent="neutral">
                {displayedSignals.length} sinais filtrados
              </Badge>
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
                {displayedSignals.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="py-6 text-center text-muted-foreground">
                      Nenhum sinal filtrado para os critérios selecionados ({activeDirection}).
                    </TableCell>
                  </TableRow>
                ) : (
                  displayedSignals.slice(0, 40).map((sig, idx) => (
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
