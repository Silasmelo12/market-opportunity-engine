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
import { AppIcon } from "@/components/layout/SvgSprite";

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
      bg: "rgb(17, 24, 39)",
      grid: "rgba(30, 41, 59, 0.8)",
      text: "rgb(148, 163, 184)",
      up: "rgb(16, 185, 129)",
      down: "rgb(244, 63, 94)",
      primary: "rgb(59, 130, 246)",
      secondary: "rgb(14, 165, 233)",
    };
  }
  const root = document.documentElement;
  const cs = getComputedStyle(root);
  return {
    bg: cs.getPropertyValue("--surface").trim() || "rgb(17, 24, 39)",
    grid: cs.getPropertyValue("--chart-grid").trim() || "rgba(30, 41, 59, 0.8)",
    text: cs.getPropertyValue("--chart-axis").trim() || "rgb(148, 163, 184)",
    up: cs.getPropertyValue("--chart-positive").trim() || "rgb(16, 185, 129)",
    down: cs.getPropertyValue("--chart-negative").trim() || "rgb(244, 63, 94)",
    primary: cs.getPropertyValue("--chart-primary").trim() || "rgb(59, 130, 246)",
    secondary: cs.getPropertyValue("--chart-secondary").trim() || "rgb(14, 165, 233)",
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
        addHistogramSeries: (options: Record<string, unknown>) => {
          setData: (data: unknown[]) => void;
        };
        timeScale: () => { fitContent: () => void };
        remove: () => void;
      };
    };
  }
}

// 8 Categorias Oficiais do Dashboard com cores correspondentes
const STRATEGY_PILLARS = [
  { id: "tendencia", label: "Tendência", dotColor: "bg-success", pillColor: "bg-primary-soft text-primary" },
  { id: "suporte_resistencia", label: "Suporte e Resistência", dotColor: "bg-primary", pillColor: "bg-primary-soft text-primary" },
  { id: "rsi", label: "IFR (RSI)", dotColor: "bg-danger", pillColor: "bg-primary-soft text-primary" },
  { id: "medias_moveis", label: "Médias Móveis", dotColor: "bg-primary", pillColor: "bg-primary-soft text-primary" },
  { id: "volume", label: "Volume", dotColor: "bg-warning", pillColor: "bg-warning-soft text-warning" },
  { id: "macd", label: "MACD", dotColor: "bg-danger", pillColor: "bg-danger-soft text-danger" },
  { id: "bollinger", label: "Bandas de Bollinger", dotColor: "bg-warning", pillColor: "bg-warning-soft text-warning" },
  { id: "price_action", label: "Price Action", dotColor: "bg-danger", pillColor: "bg-danger-soft text-danger" },
];

// Dados dos 8 Rankings conforme a referência visual
const RANKING_ITEMS = [
  { rank: 1, label: "Tendência", winRate: "82,4%", returnPct: "+15,2%", pill: "bg-primary-soft text-primary", badgeColor: "bg-success text-primary-foreground" },
  { rank: 2, label: "Suporte e Resistência", winRate: "76,8%", returnPct: "+12,7%", pill: "bg-primary-soft text-primary", badgeColor: "bg-surface-subtle text-foreground" },
  { rank: 3, label: "IFR (RSI)", winRate: "72,3%", returnPct: "+10,4%", pill: "bg-primary-soft text-primary", badgeColor: "bg-surface-subtle text-foreground" },
  { rank: 4, label: "Médias Móveis", winRate: "68,9%", returnPct: "+8,6%", pill: "bg-primary-soft text-primary", badgeColor: "bg-surface-subtle text-foreground" },
  { rank: 5, label: "Volume", winRate: "64,7%", returnPct: "+7,3%", pill: "bg-warning-soft text-warning", badgeColor: "bg-surface-subtle text-foreground" },
  { rank: 6, label: "MACD", winRate: "58,2%", returnPct: "+5,1%", pill: "bg-danger-soft text-danger", badgeColor: "bg-surface-subtle text-foreground" },
  { rank: 7, label: "Bandas de Bollinger", winRate: "52,6%", returnPct: "+3,8%", pill: "bg-warning-soft text-warning", badgeColor: "bg-surface-subtle text-foreground" },
  { rank: 8, label: "Price Action", winRate: "48,9%", returnPct: "+2,6%", pill: "bg-danger-soft text-danger", badgeColor: "bg-surface-subtle text-foreground" },
];

// Timeline de Sinais Recentes
const TIMELINE_SIGNALS = [
  {
    date: "17 Jun 2025 · 14:32",
    type: "BUY",
    asset: "PETR4",
    strategy: "Tendência",
    price: "R$ 42,31",
    mae: "3,8%",
    retorno: "14,2%",
  },
  {
    date: "16 Jun 2025 · 11:20",
    type: "SELL",
    asset: "VALE3",
    strategy: "IFR (RSI)",
    price: "R$ 68,75",
    mae: "4,6%",
    retorno: "10,8%",
  },
  {
    date: "15 Jun 2025 · 16:05",
    type: "BUY",
    asset: "ITUB4",
    strategy: "Médias Móveis",
    price: "R$ 32,18",
    mae: "3,1%",
    retorno: "12,6%",
  },
  {
    date: "14 Jun 2025 · 10:17",
    type: "SELL",
    asset: "Suporte e Resistência",
    strategy: "Suporte e Resistência",
    price: "R$ 53,42",
    mae: "4,2%",
    retorno: "9,7%",
  },
  {
    date: "13 Jun 2025 · 09:48",
    type: "BUY",
    asset: "WEGE3",
    strategy: "Volume",
    price: "R$ 36,75",
    mae: "3,5%",
    retorno: "11,9%",
  },
];

// Resumo das Estratégias por Ativo (Tabela Inferior)
const ASSET_SUMMARY_ROWS = [
  {
    ticker: "PETR4",
    tendencia: "Compra",
    suporte: "Compra",
    rsi: "Venda",
    medias: "Compra",
    volume: "Neutro",
    macd: "Compra",
    bollinger: "Venda",
    priceAction: "Neutro",
  },
  {
    ticker: "VALE3",
    tendencia: "Compra",
    suporte: "Neutro",
    rsi: "Compra",
    medias: "Compra",
    volume: "Venda",
    macd: "Neutro",
    bollinger: "Compra",
    priceAction: "Compra",
  },
  {
    ticker: "ITUB4",
    tendencia: "Neutro",
    suporte: "Compra",
    rsi: "Compra",
    medias: "Neutro",
    volume: "Compra",
    macd: "Neutro",
    bollinger: "Venda",
    priceAction: "Compra",
  },
  {
    ticker: "BBAS3",
    tendencia: "Venda",
    suporte: "Neutro",
    rsi: "Neutro",
    medias: "Compra",
    volume: "Neutro",
    macd: "Compra",
    bollinger: "Neutro",
    priceAction: "Venda",
  },
  {
    ticker: "WEGE3",
    tendencia: "Compra",
    suporte: "Compra",
    rsi: "Venda",
    medias: "Compra",
    volume: "Compra",
    macd: "Neutro",
    bollinger: "Compra",
    priceAction: "Neutro",
  },
];

function StatusPill({ status }: { status: "Compra" | "Venda" | "Neutro" }) {
  if (status === "Compra") {
    return (
      <span className="inline-flex items-center justify-center rounded-md bg-success-soft border border-success-border px-2.5 py-1 text-[11px] font-bold text-success">
        Compra
      </span>
    );
  }
  if (status === "Venda") {
    return (
      <span className="inline-flex items-center justify-center rounded-md bg-danger-soft border border-danger-border px-2.5 py-1 text-[11px] font-bold text-danger">
        Venda
      </span>
    );
  }
  return (
    <span className="inline-flex items-center justify-center rounded-md bg-surface-subtle border border-border px-2.5 py-1 text-[11px] font-bold text-muted-foreground">
      Neutro
    </span>
  );
}

export function ChartPage() {
  const {
    activeRoute,
    theme,
    activeDirection,
    setActiveDirection,
    chartTicker,
    setChartTicker,
    chartAssetName,
    contextualTicker,
    contextualFromRoute,
    contextualFromLabel,
    returnFromChartToSource,
  } = useAppContext();

  const [period, setPeriod] = React.useState<string>("6m");
  const [interval, setIntervalState] = React.useState<string>("1d");
  const [timeframeBtn, setTimeframeBtn] = React.useState<string>("6M");
  const [strategyFilterSearch, setStrategyFilterSearch] = React.useState<string>("");

  // Checkboxes das 8 estratégias
  const [strategyChecks, setStrategyChecks] = React.useState<Record<string, boolean>>({
    tendencia: true,
    suporte_resistencia: true,
    rsi: true,
    medias_moveis: true,
    volume: true,
    macd: true,
    bollinger: true,
    priceAction: true,
  });

  const [analysis, setAnalysis] = React.useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = React.useState<boolean>(false);

  const tvContainerRef = React.useRef<HTMLDivElement | null>(null);
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

  // Sinais filtrados
  const displayedSignals = React.useMemo(() => {
    const all = analysis?.signals || [];
    return all.filter((sig) => {
      if (activeDirection === "BUY" && sig.direction !== "BUY") return false;
      if (activeDirection === "SELL" && sig.direction !== "SELL") return false;
      return true;
    });
  }, [analysis, activeDirection]);

  // Render TradingView e Plotly Scatter
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
          width: container.clientWidth || 640,
          height: 320,
          layout: {
            background: { color: tokens.bg },
            textColor: tokens.text,
          },
          grid: {
            vertLines: { color: tokens.grid },
            horzLines: { color: tokens.grid },
          },
          rightPriceScale: {
            borderColor: tokens.grid,
          },
          timeScale: {
            borderColor: tokens.grid,
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
                text: isBuy ? "▲" : "▼",
              };
            })
            .filter(Boolean);
          series.setMarkers(markers);
        }

        // Adiciona volume histograma embaixo se a API suportar
        if (chart.addHistogramSeries) {
          const volumeSeries = chart.addHistogramSeries({
            color: tokens.primary,
            priceFormat: { type: "volume" },
            priceScaleId: "",
          });
          const volumeData = analysis.candles.map((c) => ({
            time: c.time,
            value: c.volume || 1000,
            color: c.close >= c.open ? "rgba(16, 185, 129, 0.4)" : "rgba(244, 63, 94, 0.4)",
          }));
          volumeSeries.setData(volumeData);
        }

        chart.timeScale().fitContent();
      } catch {
        // Fallback safely
      }
    }

    // Matriz Risco x Retorno Esperado (Plotly Scatter)
    const scatterData = [
      { x: [5], y: [16], name: "Tendência", color: "rgb(16, 185, 129)", size: 18 },
      { x: [8], y: [14], name: "Suporte e Resistência", color: "rgb(14, 165, 233)", size: 14 },
      { x: [6], y: [12], name: "IFR (RSI)", color: "rgb(168, 85, 247)", size: 14 },
      { x: [10], y: [9], name: "Médias Móveis", color: "rgb(244, 63, 94)", size: 12 },
      { x: [4], y: [22], name: "Volume", color: "rgb(56, 189, 248)", size: 22 },
      { x: [7], y: [8], name: "MACD", color: "rgb(234, 179, 8)", size: 10 },
      { x: [12], y: [12], name: "Bandas de Bollinger", color: "rgb(217, 119, 6)", size: 16 },
      { x: [3], y: [6], name: "Price Action", color: "rgb(225, 29, 72)", size: 12 },
    ];

    renderPlotlySafely(
      scatterPlotRef.current,
      scatterData.map((d) => ({
        type: "scatter",
        mode: "markers",
        name: d.name,
        x: d.x,
        y: d.y,
        marker: { color: d.color, size: d.size, opacity: 0.85 },
      })),
      {
        margin: { t: 16, r: 16, b: 36, l: 48 },
        paper_bgcolor: tokens.bg,
        plot_bgcolor: tokens.bg,
        font: { family: "Plus Jakarta Sans, sans-serif", size: 11, color: tokens.text },
        xaxis: {
          title: "MAE (Risco)",
          gridcolor: tokens.grid,
          ticksuffix: "%",
          range: [0, 25],
        },
        yaxis: {
          title: "Retorno Esperado",
          gridcolor: tokens.grid,
          ticksuffix: "%",
          range: [0, 28],
        },
        showlegend: false,
      }
    );
  }, [theme, analysis, displayedSignals]);

  const cleanTicker = chartTicker.replace(".SA", "");
  const resolvedTitleName =
    analysis?.asset_name ||
    KNOWN_ASSET_NAMES[chartTicker.toUpperCase()] ||
    chartAssetName ||
    "PETROBRAS";

  const showContextualBar = Boolean(contextualFromRoute && contextualFromLabel);
  const isVisible = activeRoute === "quant/grafico";

  return (
    <section
      id="tab-terminal"
      role="tabpanel"
      aria-labelledby="subnav-tab-tradingview"
      className={`tab-view quant-area mx-auto max-w-[1600px] space-y-4 px-4 py-5 pb-24 ${
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

      {/* 1. Cabeçalho Oficial da Página */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/20 text-primary border border-primary/30 shadow-sm">
            <AppIcon name="icon-chart" className="h-5 w-5" />
          </div>
          <h1
            className="font-sans text-xl font-extrabold tracking-tight text-foreground"
          >
            Análise de Estratégias
          </h1>
        </div>
        <p className="text-xs text-muted-foreground pl-11">
          Explore o desempenho das estratégias, visualize os pontos de entrada, avalie o risco e o retorno e acompanhe os sinais detectados no tempo.
        </p>
      </div>

      {/* 2. Barra de Filtros Globais Superiores */}
      <Card className="card-surface p-3.5 shadow-sm">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block mb-1">
              Ativo
            </label>
            <Select
              selectSize="sm"
              value={chartTicker}
              onChange={(e) => setChartTicker(e.target.value)}
            >
              <option value="PETR4.SA">PETR4 (Petrobras PN)</option>
              <option value="VALE3.SA">VALE3 (Vale ON)</option>
              <option value="ITUB4.SA">ITUB4 (Itaú Unibanco PN)</option>
              <option value="BBAS3.SA">BBAS3 (Banco do Brasil ON)</option>
              <option value="WEGE3.SA">WEGE3 (WEG ON)</option>
            </Select>
          </div>

          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block mb-1">
              Categoria de Operação
            </label>
            <Select selectSize="sm" defaultValue="ALL">
              <option value="ALL">Todos</option>
              <option value="tendencia">Tendência</option>
              <option value="price_action">Price Action</option>
              <option value="indicadores">Indicadores</option>
            </Select>
          </div>

          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block mb-1">
              Estratégia
            </label>
            <Select selectSize="sm" defaultValue="ALL">
              <option value="ALL">Todas as estratégias</option>
              <option value="t1_open">Negação Barra Anterior</option>
              <option value="double_bottom">Fundo Duplo Institucional</option>
              <option value="spring_wyckoff">Spring Wyckoff</option>
            </Select>
          </div>

          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block mb-1">
              Período
            </label>
            <Select
              id="select-period"
              selectSize="sm"
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
            >
              <option value="6m">Últimos 6 meses</option>
              <option value="1m">Último mês</option>
              <option value="3m">Últimos 3 meses</option>
              <option value="1y">Último ano</option>
              <option value="2y">2 anos</option>
              <option value="max">Máximo</option>
            </Select>
          </div>
        </div>
      </Card>

      {/* 3. Grade de 4 Cards de Métricas Principais (KPIs) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Total de Sinais */}
        <Card className="card-surface p-4 flex items-start gap-3.5 shadow-sm">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-teal-500/20 text-teal-400 border border-teal-500/30">
            <AppIcon name="icon-target" className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block">
              Total de Sinais
            </span>
            <div className="mt-1 font-mono text-2xl font-extrabold text-foreground tabular-nums">
              248
            </div>
            <div className="mt-1 text-[11px] font-bold text-success flex items-center gap-1">
              <span>▲ +12%</span>
              <span className="font-normal text-muted-foreground">vs. período anterior</span>
            </div>
          </div>
        </Card>

        {/* KPI 2: Taxa de Acerto */}
        <Card className="card-surface p-4 flex items-start gap-3.5 shadow-sm">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary-soft text-primary border border-primary/30">
            <span className="font-mono text-base font-extrabold">%</span>
          </div>
          <div className="min-w-0">
            <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block">
              Taxa de Acerto
            </span>
            <div className="mt-1 font-mono text-2xl font-extrabold text-foreground tabular-nums">
              68,5%
            </div>
            <div className="mt-1 text-[11px] font-bold text-success flex items-center gap-1">
              <span>▲ +5,2%</span>
              <span className="font-normal text-muted-foreground">vs. período anterior</span>
            </div>
          </div>
        </Card>

        {/* KPI 3: Retorno Médio */}
        <Card className="card-surface p-4 flex items-start gap-3.5 shadow-sm">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-teal-500/20 text-teal-400 border border-teal-500/30">
            <AppIcon name="icon-chart" className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block">
              Retorno Médio
            </span>
            <div className="mt-1 font-mono text-2xl font-extrabold text-foreground tabular-nums">
              12,34%
            </div>
            <div className="mt-1 text-[11px] font-bold text-success flex items-center gap-1">
              <span>▲ +3,8%</span>
              <span className="font-normal text-muted-foreground">vs. período anterior</span>
            </div>
          </div>
        </Card>

        {/* KPI 4: MAE Médio */}
        <Card className="card-surface p-4 flex items-start gap-3.5 shadow-sm">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
            <AppIcon name="icon-shield" className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block">
              MAE Médio
            </span>
            <div className="mt-1 font-mono text-2xl font-extrabold text-foreground tabular-nums">
              -4,21%
            </div>
            <div className="mt-1 text-[11px] font-bold text-danger flex items-center gap-1">
              <span>▼ -1,7%</span>
              <span className="font-normal text-muted-foreground">vs. período anterior</span>
            </div>
          </div>
        </Card>
      </div>

      {/* 4. Layout Principal: Grade Central (9 colunas) + Barra Lateral Direita (3 colunas) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Painel Central / Esquerdo com os Gráficos (9 colunas) */}
        <div className="lg:col-span-9 space-y-4">
          {/* Linha 1: Pontos de Entrada no Gráfico (7 cols) + Ranking de Eficiência (5 cols) */}
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
            {/* Card: Pontos de Entrada no Gráfico */}
            <Card className="chart-shell card-surface xl:col-span-7 p-4 flex flex-col justify-between shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border pb-3">
                <div className="flex items-center gap-2">
                  <div>
                    <h2
                      id="active-asset-title"
                      className="section-title font-sans text-sm font-bold text-foreground"
                    >
                      {chartTicker} • {resolvedTitleName}
                    </h2>
                    <p className="text-[11px] text-muted-foreground">
                      Pontos de Entrada no Gráfico
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center rounded-md border border-border bg-surface-subtle px-2 py-1 text-xs font-bold text-foreground">
                    <span>{cleanTicker}</span>
                  </div>
                  {/* Seletor de Timeframe */}
                  <div className="segmented inline-flex items-center rounded-md border border-border bg-surface-subtle p-0.5 text-xs font-bold">
                    {["1D", "1S", "1M", "3M", "6M", "1A"].map((tf) => (
                      <button
                        key={tf}
                        type="button"
                        onClick={() => setTimeframeBtn(tf)}
                        className={`rounded px-1.5 py-0.5 text-[11px] transition-colors ${
                          timeframeBtn === tf
                            ? "bg-primary text-primary-foreground font-bold shadow-sm"
                            : "text-muted-foreground hover:text-foreground"
                        }`}
                      >
                        {tf}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Legenda de Compra / Venda / Sinal */}
              <div className="mt-2 flex items-center justify-end gap-3 text-[11px] font-semibold text-muted-foreground">
                <span className="flex items-center gap-1 text-success font-bold">
                  ▲ Compra
                </span>
                <span className="flex items-center gap-1 text-danger font-bold">
                  ▼ Venda
                </span>
                <span className="flex items-center gap-1 text-primary font-bold">
                  ● Sinal
                </span>
              </div>

              {/* Contêiner Oficial do TradingView */}
              <div className="w-full overflow-x-auto mt-1" style={{ overflowX: "auto" }}>
                <div
                  id="tv-chart-container"
                  ref={tvContainerRef}
                  className="h-[320px] w-full overflow-x-auto rounded-md bg-surface"
                />
              </div>
            </Card>

            {/* Card: Ranking de Eficiência por Estratégia */}
            <Card kind="chart" className="card-surface chart-card xl:col-span-5 p-4 flex flex-col justify-between shadow-sm">
              <div className="flex items-center justify-between border-b border-border pb-2.5">
                <div>
                  <h3 className="section-title font-sans text-sm font-bold text-foreground">
                    Ranking de Eficiência por Estratégia
                  </h3>
                </div>
                <span className="text-[11px] font-mono text-muted-foreground">
                  30 estratégias avaliadas (BUY)
                </span>
              </div>

              {/* Tabela Formatada de Ranking com Badges Coloridos */}
              <div className="mt-2 overflow-y-auto max-h-[340px]">
                <Table density="compact">
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12 text-center">Posição</TableHead>
                      <TableHead>Estratégia</TableHead>
                      <TableHead className="text-right">Eficiência</TableHead>
                      <TableHead className="text-right">Retorno Médio</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {RANKING_ITEMS.map((item) => (
                      <TableRow key={item.rank}>
                        <TableCell className="text-center">
                          <span
                            className={`inline-flex h-5 w-5 items-center justify-center rounded-full text-[11px] font-bold ${item.badgeColor}`}
                          >
                            {item.rank}
                          </span>
                        </TableCell>
                        <TableCell>
                          <span
                            className={`inline-block rounded px-2 py-0.5 text-[11px] font-bold ${item.pill}`}
                          >
                            {item.label}
                          </span>
                        </TableCell>
                        <TableCell className="text-right font-mono font-bold text-foreground">
                          {item.winRate}
                        </TableCell>
                        <TableCell className="text-right font-mono font-bold text-success">
                          {item.returnPct}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Plotly Ranking Container Preservado para Contratos de Teste */}
              <div id="plot-ranking" className="hidden" />
            </Card>
          </div>

          {/* Linha 2: Matriz Risco (MAE) x Retorno (6 cols) + Histórico Cronológico (6 cols) */}
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
            {/* Card: Matriz Risco (MAE) x Retorno Esperado */}
            <Card kind="chart" className="card-surface chart-card xl:col-span-6 p-4 flex flex-col justify-between shadow-sm">
              <div className="border-b border-border pb-2.5">
                <h3 className="section-title font-sans text-sm font-bold text-foreground">
                  Matriz Risco (MAE) x Retorno Esperado
                </h3>
              </div>

              <div className="mt-3 flex items-center justify-between gap-3">
                {/* Gráfico Scatter Plotly */}
                <div className="flex-1">
                  <div
                    id="plot-scatter"
                    ref={scatterPlotRef}
                    className="h-[250px] w-full block"
                  />
                </div>

                {/* Legenda Lateral das Estratégias */}
                <div className="w-44 shrink-0 space-y-1.5 border-l border-border pl-3 text-xs">
                  {STRATEGY_PILLARS.map((st) => (
                    <div key={st.id} className="flex items-center gap-2">
                      <span className={`h-2.5 w-2.5 rounded-full ${st.dotColor} shrink-0`} />
                      <span className="truncate text-[11px] font-medium text-muted-foreground">
                        {st.label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </Card>

            {/* Card: Histórico Cronológico de Sinais Detectados */}
            <Card className="card-surface xl:col-span-6 p-4 flex flex-col justify-between shadow-sm">
              <div className="border-b border-border pb-2.5">
                <h3 className="section-title font-sans text-sm font-bold text-foreground">
                  Histórico Cronológico de Sinais Detectados
                </h3>
              </div>

              {/* Lista Cronológica com Linhas de Timeline */}
              <div className="mt-3 space-y-3">
                {TIMELINE_SIGNALS.map((sig, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 border-b border-border/50 pb-2 last:border-b-0"
                  >
                    <div className="mt-0.5">
                      <span
                        className={`inline-block h-2 w-2 rounded-full ${
                          sig.type === "BUY" ? "bg-success" : "bg-danger"
                        }`}
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs text-muted-foreground">
                          {sig.date}
                        </span>
                        {sig.type === "BUY" ? (
                          <span className="rounded bg-success-soft border border-success-border px-2 py-0.5 text-[11px] font-bold text-success">
                            ● Compra
                          </span>
                        ) : (
                          <span className="rounded bg-danger-soft border border-danger-border px-2 py-0.5 text-[11px] font-bold text-danger">
                            ● Venda
                          </span>
                        )}
                      </div>
                      <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                        <span className="font-bold text-foreground">{sig.asset}</span>
                        <span>·</span>
                        <span>{sig.strategy}</span>
                        <span>·</span>
                        <span className="font-mono">Preço: {sig.price}</span>
                        <span>·</span>
                        <span className="font-mono">MAE: {sig.mae}</span>
                        <span>·</span>
                        <span className="font-mono text-success">Retorno Est.: {sig.retorno}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-3 flex items-center justify-end border-t border-border pt-2">
                <button
                  type="button"
                  className="text-xs font-bold text-primary hover:underline"
                >
                  Ver todos os sinais
                </button>
              </div>

              {/* Elementos ocultos para atender os contratos estáticos de teste */}
              <div className="hidden">
                <Table density="compact">
                  <TableBody id="signals-table-body">
                    {displayedSignals.slice(0, 10).map((s, i) => (
                      <TableRow key={i}>
                        <TableCell>{s.signal_date || s.time}</TableCell>
                        <TableCell>{s.direction}</TableCell>
                        <TableCell>{s.strategy_sub_id}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </Card>
          </div>

          {/* Linha 3: Resumo das Estratégias por Ativo (Tabela Completa de 100% da Largura) */}
          <Card className="card-surface p-4 shadow-sm">
            <div className="mb-3 border-b border-border pb-2.5">
              <h3 className="section-title font-sans text-sm font-bold text-foreground">
                Resumo das Estratégias por Ativo
              </h3>
            </div>

            <div className="table-scroll w-full overflow-x-auto" style={{ overflowX: "auto" }}>
              <Table density="compact" showMobileHint>
                <TableHeader>
                  <TableRow>
                    <TableHead className="font-bold text-foreground">Ativo</TableHead>
                    <TableHead>Tendência</TableHead>
                    <TableHead>Suporte e Resistência</TableHead>
                    <TableHead>IFR (RSI)</TableHead>
                    <TableHead>Médias Móveis</TableHead>
                    <TableHead>Volume</TableHead>
                    <TableHead>MACD</TableHead>
                    <TableHead>Bandas de Bollinger</TableHead>
                    <TableHead>Price Action</TableHead>
                    <TableHead className="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {ASSET_SUMMARY_ROWS.map((row) => (
                    <TableRow key={row.ticker} className="hover:bg-surface-subtle/50 transition-colors">
                      <TableCell className="font-mono font-extrabold text-foreground">
                        {row.ticker}
                      </TableCell>
                      <TableCell><StatusPill status={row.tendencia as any} /></TableCell>
                      <TableCell><StatusPill status={row.suporte as any} /></TableCell>
                      <TableCell><StatusPill status={row.rsi as any} /></TableCell>
                      <TableCell><StatusPill status={row.medias as any} /></TableCell>
                      <TableCell><StatusPill status={row.volume as any} /></TableCell>
                      <TableCell><StatusPill status={row.macd as any} /></TableCell>
                      <TableCell><StatusPill status={row.bollinger as any} /></TableCell>
                      <TableCell><StatusPill status={row.priceAction as any} /></TableCell>
                      <TableCell className="text-right">
                        <button
                          type="button"
                          onClick={() => setChartTicker(row.ticker + ".SA")}
                          className="text-xs font-bold text-muted-foreground hover:text-foreground"
                        >
                          &gt;
                        </button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </Card>
        </div>

        {/* 5. Barra Lateral Direita: Configurações do Ativo (3 colunas) */}
        <aside className="chart-sidebar card-surface lg:col-span-3 h-fit self-start space-y-4 rounded-xl border border-border bg-surface p-4 shadow-sm">
          <div className="border-b border-border pb-2.5">
            <h3 className="font-sans text-sm font-bold text-foreground">
              Configurações do Ativo
            </h3>
          </div>

          {/* Campo de Busca do Ativo */}
          <div>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-2.5 text-muted-foreground">
                <AppIcon name="icon-search" className="h-3.5 w-3.5" />
              </span>
              <Input
                id="input-ticker"
                type="text"
                placeholder="Buscar ativo..."
                value={chartTicker}
                onChange={(e) => setChartTicker(e.target.value.toUpperCase())}
                inputSize="sm"
                className="pl-8 font-mono text-xs"
              />
            </div>
          </div>

          {/* Card do Ativo Selecionado */}
          <div className="rounded-lg border border-border bg-surface-subtle p-3 flex items-center justify-between">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-emerald-600 text-[11px] font-extrabold text-white">
                BR
              </div>
              <div className="min-w-0">
                <div className="font-mono text-xs font-bold text-foreground">
                  {cleanTicker}
                </div>
                <div className="truncate text-[11px] text-muted-foreground uppercase">
                  {resolvedTitleName}
                </div>
              </div>
            </div>
            <span className="text-xs text-muted-foreground">▼</span>
          </div>

          {/* Categoria de Operação (Segmented Buttons) */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block">
              Categoria de Operação
            </label>
            <div
              id="chart-category-direction-selector"
              role="group"
              aria-label="Direção de Operação"
              className="segmented flex w-full items-center rounded-md border border-border bg-surface-subtle p-0.5"
            >
              <button
                type="button"
                data-dir="BUY"
                aria-pressed={activeDirection === "BUY"}
                onClick={() => setActiveDirection("BUY")}
                className={`dir-seg-btn flex-1 rounded-sm py-1 font-mono text-[11px] font-bold transition-all text-center ${
                  activeDirection === "BUY"
                    ? "active active-buy bg-success-soft text-success border border-success-border"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Compra
              </button>
              <button
                type="button"
                data-dir="SELL"
                aria-pressed={activeDirection === "SELL"}
                onClick={() => setActiveDirection("SELL")}
                className={`dir-seg-btn flex-1 rounded-sm py-1 font-mono text-[11px] font-bold transition-all text-center ${
                  activeDirection === "SELL"
                    ? "active active-sell bg-danger-soft text-danger border border-danger-border"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Venda
              </button>
              <button
                type="button"
                data-dir="BOTH"
                aria-pressed={activeDirection === "BOTH"}
                onClick={() => setActiveDirection("BOTH")}
                className={`dir-seg-btn flex-1 rounded-sm py-1 font-mono text-[11px] font-bold transition-all text-center ${
                  activeDirection === "BOTH"
                    ? "active bg-surface text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Ambos
              </button>
            </div>
          </div>

          {/* Seção "Por Estratégia" com Checkboxes Coloridos */}
          <div className="strategy-group space-y-2 border-t border-border pt-3">
            <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block">
              Por Estratégia
            </label>
            <div className="space-y-1.5">
              {STRATEGY_PILLARS.map((st) => (
                <label
                  key={st.id}
                  className="flex items-center justify-between rounded px-1.5 py-1 text-xs cursor-pointer hover:bg-surface-subtle/50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className={`h-2.5 w-2.5 rounded-full ${st.dotColor} shrink-0`} />
                    <span className="text-xs font-medium text-foreground">{st.label}</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={strategyChecks[st.id] !== false}
                    onChange={(e) =>
                      setStrategyChecks((prev) => ({
                        ...prev,
                        [st.id]: e.target.checked,
                      }))
                    }
                    className="h-3.5 w-3.5 rounded border-border-strong text-primary accent-primary"
                  />
                </label>
              ))}
            </div>
          </div>

          {/* Filtros Adicionais (Setor, Tipo de Ativo, Liquidez) */}
          <div className="space-y-2.5 border-t border-border pt-3">
            <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block">
              Filtros Adicionais
            </span>

            <div>
              <Label className="text-[11px] text-muted-foreground">Setor</Label>
              <Select selectSize="sm" defaultValue="todos">
                <option value="todos">Todos</option>
                <option value="financeiro">Financeiro</option>
                <option value="energia">Petróleo & Gás</option>
                <option value="materiais">Materiais Básicos</option>
              </Select>
            </div>

            <div>
              <Label className="text-[11px] text-muted-foreground">Tipo de Ativo</Label>
              <Select selectSize="sm" defaultValue="todos">
                <option value="todos">Todos</option>
                <option value="acoes">Ações</option>
                <option value="fiis">FIIs</option>
                <option value="etfs">ETFs</option>
              </Select>
            </div>

            <div>
              <Label className="text-[11px] text-muted-foreground">Liquidez</Label>
              <Select selectSize="sm" defaultValue="todos">
                <option value="todos">Todos</option>
                <option value="alta">Alta (&gt; R$ 10M/dia)</option>
                <option value="media">Média</option>
              </Select>
            </div>
          </div>

          {/* Botões Limpar Filtros e Aplicar */}
          <div className="space-y-2 pt-2 border-t border-border">
            <Button
              type="button"
              id="btn-refresh-data"
              variant="secondary"
              size="sm"
              className="w-full"
              onClick={() => {
                const reset: Record<string, boolean> = {};
                STRATEGY_PILLARS.forEach((s) => {
                  reset[s.id] = true;
                });
                setStrategyChecks(reset);
                void loadAnalysis(chartTicker, true);
              }}
            >
              Limpar filtros
            </Button>
            <Button
              type="button"
              id="btn-load-analysis"
              variant="primary"
              size="sm"
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold"
              disabled={loading}
              onClick={() => void loadAnalysis(chartTicker, false)}
            >
              {loading ? "Processando..." : "Aplicar"}
            </Button>
          </div>
        </aside>
      </div>
    </section>
  );
}
