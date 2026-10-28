import * as React from "react";
import { useAppContext } from "@/state/app-context";
import { fetchRadarOpportunities } from "@/services/market-service";
import type { RadarItem } from "@/types/market";
import { formatPercentPtBr } from "@/lib/formatters";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import { AppIcon } from "@/components/layout/SvgSprite";

const RADAR_CATEGORIES = [
  { id: "featured", label: "Destaques" },
  { id: "Ações Brasil", label: "Ações Brasil" },
  { id: "FIIs", label: "FIIs" },
  { id: "ETFs", label: "ETFs" },
  { id: "BDRs", label: "BDRs" },
  { id: "EUA", label: "EUA" },
  { id: "Cripto", label: "Cripto" },
  { id: "Commodities", label: "Commodities" },
  { id: "Moedas", label: "Moedas / FX" },
] as const;

const RADAR_TIMEFRAMES = [
  { id: "1d", label: "1D (Diário)" },
  { id: "1wk", label: "1S (Semanal)" },
  { id: "4h", label: "4h (Intraday)" },
  { id: "1h", label: "1h" },
] as const;

export function RadarPage() {
  const {
    activeRoute,
    activeDirection,
    radarActiveCategory,
    setRadarActiveCategory,
    radarTimeframe,
    setRadarTimeframe,
    radarPage,
    setRadarPage,
    openChartFromRadar,
  } = useAppContext();

  const [items, setItems] = React.useState<RadarItem[]>([]);
  const [totalPages, setTotalPages] = React.useState<number>(1);
  const [totalAssets, setTotalAssets] = React.useState<number>(0);
  const [loading, setLoading] = React.useState<boolean>(false);
  const [selectedStrategy, setSelectedStrategy] = React.useState<string>("ALL");

  const loadRadar = React.useCallback(
    async (forceRefresh = false) => {
      setLoading(true);
      try {
        const resp = await fetchRadarOpportunities({
          category: radarActiveCategory,
          direction: activeDirection,
          interval: radarTimeframe,
          page: radarPage,
          pageSize: 20,
          strategies:
            selectedStrategy !== "ALL" ? [selectedStrategy] : undefined,
          forceRefresh,
        });
        setItems(Array.isArray(resp.items) ? resp.items : []);
        setTotalPages(Math.max(1, Number(resp.total_pages) || 1));
        setTotalAssets(Number(resp.total_assets) || 0);
      } catch {
        setItems([]);
      } finally {
        setLoading(false);
      }
    },
    [
      radarActiveCategory,
      activeDirection,
      radarTimeframe,
      radarPage,
      selectedStrategy,
    ]
  );

  React.useEffect(() => {
    void loadRadar(false);
  }, [loadRadar]);

  const idealCount = items.filter((i) => i.timing_category === "IDEAL").length;
  const buySignalsCount = items.filter((i) => i.direction === "BUY").length;
  const sellSignalsCount = items.filter((i) => i.direction === "SELL").length;
  const avgWinRate =
    items.length > 0
      ? items.reduce(
          (acc, i) => acc + (Number(i.historical_win_rate ?? i.win_rate) || 0),
          0
        ) / items.length
      : 0;

  const isVisible = activeRoute === "quant/radar";

  return (
    <section
      id="tab-pane-radar"
      role="tabpanel"
      aria-labelledby="subnav-tab-radar"
      className={`tab-view quant-area mx-auto max-w-[1600px] space-y-5 px-4 py-5 pb-20 ${
        isVisible ? "" : "hidden"
      }`}
    >
      {/* 4 KPIs Executivos do Radar (#radar-executive-deck) */}
      <div
        id="radar-executive-deck"
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <Card kind="kpi" className="kpi-card card-surface">
          <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            Oportunidades Mapeadas
          </span>
          <div className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-foreground tabular-nums">
            {totalAssets || items.length}
          </div>
          <div className="kpi-sub mt-1.5 text-xs text-muted-foreground">
            {buySignalsCount} Compra • {sellSignalsCount} Venda
          </div>
        </Card>

        <Card kind="kpi" className="kpi-card card-surface">
          <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            Zona de Timing Ideal
          </span>
          <div className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-success tabular-nums">
            {idealCount} ativos
          </div>
          <div className="kpi-sub mt-1.5 text-xs text-muted-foreground">
            Distância de entrada estatisticamente favorável
          </div>
        </Card>

        <Card kind="kpi" className="kpi-card card-surface">
          <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            Taxa de Acerto Média
          </span>
          <div className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-primary tabular-nums">
            {formatPercentPtBr(avgWinRate, 1)}
          </div>
          <div className="kpi-sub mt-1.5 text-xs text-muted-foreground">
            Backtest histórico da página atual
          </div>
        </Card>

        <Card kind="kpi" className="kpi-card card-surface">
          <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            Timeframe & Direção
          </span>
          <div className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-foreground tabular-nums">
            {radarTimeframe.toUpperCase()} • {activeDirection}
          </div>
          <div className="kpi-sub mt-1.5 text-xs text-muted-foreground">
            Categoria: {radarActiveCategory}
          </div>
        </Card>
      </div>

      {/* Controles de Timeframe, Filtro de Estratégias e Categorias */}
      <Card className="card-surface space-y-3 p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div
            id="radar-timeframe-buttons"
            role="group"
            aria-label="Timeframe do Radar"
            className="segmented inline-flex items-center rounded-md border border-border bg-surface-subtle p-1"
          >
            {RADAR_TIMEFRAMES.map((tf) => {
              const active = radarTimeframe === tf.id;
              return (
                <button
                  key={tf.id}
                  type="button"
                  data-tf={tf.id}
                  aria-pressed={active}
                  onClick={() => setRadarTimeframe(tf.id)}
                  className={`radar-tf-btn rounded-sm px-3 py-1 font-mono text-xs font-bold transition-all ${
                    active
                      ? "active bg-surface text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {tf.label}
                </button>
              );
            })}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div id="radar-strategy-dropdown-wrapper" className="flex items-center gap-2">
              <label
                htmlFor="radar-strategy-select"
                className="text-xs font-semibold text-muted-foreground"
              >
                Estratégia:
              </label>
              <select
                id="radar-strategy-select"
                value={selectedStrategy}
                onChange={(e) => setSelectedStrategy(e.target.value)}
                className="select rounded-md border border-border-strong bg-surface px-3 py-1.5 text-xs font-semibold text-foreground"
              >
                <option value="ALL">Todas as Estratégias (48)</option>
                <option value="t1_open">Negação Anterior (Abertura)</option>
                <option value="double_bottom">Fundo Duplo Institucional</option>
                <option value="spring_wyckoff">Spring Wyckoff</option>
                <option value="shooting_star">Estrela Cadente (Topo)</option>
                <option value="bearish_engulfing">Engolfo de Baixa</option>
              </select>
            </div>

            <Button
              type="button"
              id="btn-radar-rescan"
              variant="primary"
              size="sm"
              disabled={loading}
              onClick={() => void loadRadar(true)}
            >
              <AppIcon name="icon-refresh" className="h-3.5 w-3.5" />
              <span>{loading ? "Escaneando..." : "Atualizar Radar"}</span>
            </Button>
          </div>
        </div>

        {/* Pílulas de Categoria de Universo (#radar-category-pills) */}
        <div
          id="radar-category-pills"
          role="group"
          aria-label="Categorias de Universo do Radar"
          className="flex flex-wrap items-center gap-1.5 border-t border-border pt-3"
        >
          {RADAR_CATEGORIES.map((cat) => {
            const active = radarActiveCategory === cat.id;
            return (
              <button
                key={cat.id}
                type="button"
                data-cat={cat.id}
                aria-pressed={active}
                onClick={() => setRadarActiveCategory(cat.id)}
                className={`filter-chip rounded-full border px-3 py-1 font-sans text-xs font-semibold transition-all ${
                  active
                    ? "active active-cat bg-primary text-primary-foreground border-primary shadow-sm"
                    : "bg-surface text-muted-foreground border-border hover:bg-surface-subtle hover:text-foreground"
                }`}
              >
                {cat.label}
              </button>
            );
          })}
        </div>
      </Card>

      {/* Tabela de Oportunidades do Radar */}
      <Card className="card-surface space-y-3">
        <Table showMobileHint>
          <TableHeader>
            <TableRow>
              <TableHead>Ativo</TableHead>
              <TableHead>Direção</TableHead>
              <TableHead>Estratégia Detectada</TableHead>
              <TableHead>Status de Timing</TableHead>
              <TableHead className="text-right">Distância</TableHead>
              <TableHead className="text-right">Amostra (N)</TableHead>
              <TableHead className="text-right">Win Rate Hist.</TableHead>
              <TableHead className="text-right">Ação</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody id="radar-table-body">
            {items.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="py-8 text-center text-muted-foreground">
                  {loading
                    ? "Escaneando oportunidades estatísticas no universo selecionado..."
                    : "Nenhum sinal ativo encontrado para os filtros selecionados."}
                </TableCell>
              </TableRow>
            ) : (
              items.map((item, idx) => {
                const winRate = Number(
                  item.historical_win_rate ?? item.win_rate ?? 0
                );
                const isBuy = item.direction === "BUY";
                return (
                  <TableRow key={`${item.ticker}-${item.strategy_sub_id}-${idx}`}>
                    <TableCell>
                      <div className="flex flex-col">
                        <span className="font-mono font-bold text-foreground">
                          {item.ticker}
                        </span>
                        <span className="text-[11px] text-muted-foreground">
                          {item.asset_name || item.category}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge intent={isBuy ? "success" : "danger"}>
                        {isBuy ? "▲ COMPRA" : "▼ VENDA"}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-semibold text-foreground">
                      {item.strategy_label || item.strategy_sub_id}
                    </TableCell>
                    <TableCell>
                      <Badge
                        intent={
                          item.timing_category === "IDEAL"
                            ? "success"
                            : item.timing_category === "EXTENDED"
                              ? "warning"
                              : "neutral"
                        }
                      >
                        {item.timing_label || item.timing_category}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatPercentPtBr(item.distance_pct, 2, true)}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {item.historical_n ?? 0}
                    </TableCell>
                    <TableCell className="text-right font-mono font-bold text-primary">
                      {formatPercentPtBr(winRate, 1)}
                    </TableCell>
                    <TableCell className="text-right">
                      <button
                        type="button"
                        data-ticker={item.ticker}
                        onClick={() =>
                          openChartFromRadar(item.ticker, item.asset_name)
                        }
                        className="btn-contextual btn-radar-open-chart rounded-md px-2.5 py-1 text-[11px] font-bold"
                      >
                        Abrir gráfico
                      </button>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>

        {/* Paginação do Radar */}
        <div
          id="radar-pagination-container"
          className="flex flex-wrap items-center justify-between gap-2 border-t border-border pt-3 text-xs"
        >
          <span id="radar-pagination-info" className="text-muted-foreground">
            Página <strong className="text-foreground">{radarPage}</strong> de{" "}
            <strong className="text-foreground">{totalPages}</strong> (
            {totalAssets || items.length} ativos avaliados)
          </span>
          <div className="flex items-center gap-2">
            <Button
              type="button"
              id="btn-radar-prev"
              variant="secondary"
              size="xs"
              disabled={radarPage <= 1 || loading}
              onClick={() => setRadarPage(Math.max(1, radarPage - 1))}
            >
              ← Anterior
            </Button>
            <Button
              type="button"
              id="btn-radar-next"
              variant="secondary"
              size="xs"
              disabled={radarPage >= totalPages || loading}
              onClick={() => setRadarPage(radarPage + 1)}
            >
              Próxima →
            </Button>
          </div>
        </div>
      </Card>
    </section>
  );
}
