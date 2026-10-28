import * as React from "react";
import { useAppContext } from "@/state/app-context";
import { usePortfolioMetrics } from "@/hooks/use-portfolio-metrics";
import { requestPortfolioAdvice } from "@/services/portfolio-service";
import type { RebalanceOrderItem } from "@/types/portfolio";
import {
  formatCurrencyBRL,
  formatPercentPtBr,
  formatQuantityPtBr,
  formatSignedCurrencyBRL,
} from "@/lib/formatters";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import { StatusPill } from "@/components/shared";
import { AppIcon } from "@/components/layout/SvgSprite";

const CUSTODY_CLASSES = [
  { id: "ALL", label: "Todos" },
  { id: "acao_br", label: "Ações Brasil" },
  { id: "fii", label: "FIIs" },
  { id: "bdr", label: "BDRs" },
  { id: "cripto", label: "Cripto" },
] as const;

export function PortfolioPage() {
  const {
    activeRoute,
    portfolio,
    quotes,
    updatePortfolio,
    addOrUpdateManualHolding,
    removeHolding,
    openChartForHolding,
    triggerSharedCsvImport,
    setIsB3ModalOpen,
    setIsNewTradeModalOpen,
    showToast,
  } = useAppContext();

  const metrics = usePortfolioMetrics(portfolio, quotes);
  const [selectedClass, setSelectedClass] = React.useState<string>("ALL");
  const [newTicker, setNewTicker] = React.useState<string>("");
  const [newShares, setNewShares] = React.useState<string>("");
  const [newAvgPrice, setNewAvgPrice] = React.useState<string>("");
  const [adviceOrders, setAdviceOrders] = React.useState<RebalanceOrderItem[]>([]);
  const [adviceLoading, setAdviceLoading] = React.useState<boolean>(false);

  const filteredGroups = React.useMemo(() => {
    if (selectedClass === "ALL") return metrics.categoryGroups;
    return metrics.categoryGroups.filter((g) => g.key === selectedClass);
  }, [metrics.categoryGroups, selectedClass]);

  const filteredHoldings = React.useMemo(() => {
    if (selectedClass === "ALL") return metrics.enrichedHoldings;
    return metrics.enrichedHoldings.filter(
      (h) => h.categoryKey === selectedClass
    );
  }, [metrics.enrichedHoldings, selectedClass]);

  const handleExportCsv = () => {
    const header = "Ticker,Quantidade,Preço Médio,Cotação Atual,Saldo Bruto\n";
    const rows = metrics.enrichedHoldings
      .map(
        (h) =>
          `${h.ticker},${h.shares},${h.average_buy_price.toFixed(2)},${h.currentPrice.toFixed(2)},${h.marketValue.toFixed(2)}`
      )
      .join("\n");
    const blob = new Blob([header + rows], {
      type: "text/csv;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "custodia_market_opportunity.csv";
    link.click();
    URL.revokeObjectURL(url);
    showToast("CSV de custódia exportado.", "success");
  };

  const handleQuickAddHolding = (e: React.FormEvent) => {
    e.preventDefault();
    const sharesNum = Number(newShares.replace(",", "."));
    const priceNum = Number(newAvgPrice.replace(",", "."));
    if (!newTicker.trim() || !Number.isFinite(sharesNum) || sharesNum <= 0) {
      showToast("Informe ticker e quantidade válidos.", "warning");
      return;
    }
    addOrUpdateManualHolding({
      ticker: newTicker.trim(),
      shares: sharesNum,
      average_buy_price: Number.isFinite(priceNum) ? priceNum : 0,
      operation: "BUY",
    });
    setNewTicker("");
    setNewShares("");
    setNewAvgPrice("");
    showToast(`Posição ${newTicker.toUpperCase()} atualizada.`, "success");
  };

  const handleRunRebalanceAdvisor = async () => {
    setAdviceLoading(true);
    try {
      const resp = await requestPortfolioAdvice({
        available_cash: metrics.availableCash,
        holdings: portfolio.holdings,
        universe_category: portfolio.universeCategory || "featured",
        interval: portfolio.interval || "1d",
        period: portfolio.period || "2y",
        max_weight_pct: portfolio.maxWeightPct || 25.0,
      });
      setAdviceOrders(resp.orders || []);
      showToast("Plano de alocação calculado com sucesso.", "success");
    } catch (err) {
      showToast(
        err instanceof Error ? err.message : "Erro ao gerar recomendações",
        "error"
      );
    } finally {
      setAdviceLoading(false);
    }
  };

  const isVisible = activeRoute === "carteira/posicoes";

  return (
    <section
      id="tab-portfolio"
      role="tabpanel"
      aria-labelledby="subnav-tab-posicoes"
      className={`tab-view area-posicoes mx-auto max-w-[1600px] space-y-5 px-4 py-5 pb-20 ${
        isVisible ? "" : "hidden"
      }`}
    >
      {/* 4 KPIs de Custódia (Penpot Screen 02) */}
      <div
        id="custody-kpis-grid"
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <Card kind="kpi" className="kpi-card card-surface">
          <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            Valor em Custódia
          </span>
          <div
            id="custody-kpi-equity"
            className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-foreground tabular-nums"
          >
            {formatCurrencyBRL(metrics.totalMarketValue)}
          </div>
          <div className="kpi-sub mt-1.5 text-xs text-muted-foreground">
            Caixa livre: {formatCurrencyBRL(metrics.availableCash)}
          </div>
        </Card>

        <Card kind="kpi" className="kpi-card card-surface">
          <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            Custo Total de Aquisição
          </span>
          <div
            id="custody-kpi-cost"
            className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-foreground tabular-nums"
          >
            {formatCurrencyBRL(metrics.totalCostBasis)}
          </div>
          <div className="kpi-sub mt-1.5 text-xs text-muted-foreground">
            Base de preço médio ponderado
          </div>
        </Card>

        <Card kind="kpi" className="kpi-card card-surface">
          <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            Resultado Aberto
          </span>
          <div
            id="custody-kpi-pnl"
            className={`kpi-value financial-value mt-2 font-mono text-2xl font-extrabold tabular-nums ${
              metrics.unrealizedPnl >= 0 ? "text-success" : "text-danger"
            }`}
          >
            {formatSignedCurrencyBRL(metrics.unrealizedPnl)}
          </div>
          <div className="kpi-sub mt-1.5 text-xs text-muted-foreground">
            Rentabilidade: {metrics.card1VarLabel}
          </div>
        </Card>

        <Card kind="kpi" className="kpi-card card-surface">
          <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            Diversificação da Custódia
          </span>
          <div
            id="custody-kpi-count"
            className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-foreground tabular-nums"
          >
            {metrics.enrichedHoldings.length} ativos
          </div>
          <div className="kpi-sub mt-1.5 text-xs text-muted-foreground">
            Distribuídos em {metrics.categoryGroups.length} classes
          </div>
        </Card>
      </div>

      {/* Barra de Filtros por Classe e Ações de Custódia */}
      <Card className="card-surface flex flex-wrap items-center justify-between gap-3 p-3.5">
        <div
          id="custody-category-pills"
          role="group"
          aria-label="Filtrar custódia por classe de ativo"
          className="flex flex-wrap items-center gap-1.5"
        >
          {CUSTODY_CLASSES.map((cls) => (
            <StatusPill
              key={cls.id}
              active={selectedClass === cls.id}
              onClick={() => setSelectedClass(cls.id)}
            >
              {cls.label}
            </StatusPill>
          ))}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            type="button"
            id="btn-portfolio-import-csv"
            variant="secondary"
            size="xs"
            onClick={triggerSharedCsvImport}
          >
            <AppIcon name="icon-import" className="h-3.5 w-3.5" />
            <span>Importar CSV</span>
          </Button>
          <Button
            type="button"
            id="btn-open-b3-modal"
            variant="secondary"
            size="xs"
            onClick={() => setIsB3ModalOpen(true)}
          >
            <span>Conciliar Extratos B3</span>
          </Button>
          <Button
            type="button"
            id="btn-custody-export-csv"
            variant="secondary"
            size="xs"
            onClick={handleExportCsv}
          >
            <span>Exportar CSV</span>
          </Button>
          <Button
            type="button"
            variant="primary"
            size="xs"
            onClick={() => setIsNewTradeModalOpen(true)}
          >
            <AppIcon name="icon-plus" className="h-3.5 w-3.5" />
            <span>Adicionar Posição</span>
          </Button>
        </div>
      </Card>

      {/* Acordeões de Custódia por Classe (#investidor10-positions-categories) */}
      <div id="investidor10-positions-categories" className="space-y-3">
        {filteredGroups.length === 0 ? (
          <Card className="category-card card-surface p-6 text-center text-xs text-muted-foreground">
            Nenhuma posição encontrada para a classe selecionada.
          </Card>
        ) : (
          filteredGroups.map((group) => (
            <div
              key={group.key}
              className="category-card card-surface overflow-hidden rounded-lg border border-border bg-surface shadow-sm"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border bg-surface-subtle px-4 py-3">
                <div className="flex items-center gap-2">
                  <h3 className="section-title font-sans text-sm font-bold text-foreground">
                    {group.label}
                  </h3>
                  <Badge intent="neutral">{group.holdings.length} ativos</Badge>
                </div>
                <div className="flex items-center gap-4 font-mono text-xs">
                  <span>
                    Custo: <strong>{formatCurrencyBRL(group.totalCost)}</strong>
                  </span>
                  <span>
                    Saldo: <strong>{formatCurrencyBRL(group.totalMarketValue)}</strong>
                  </span>
                  <span
                    className={
                      group.unrealizedPnl >= 0 ? "text-success font-bold" : "text-danger font-bold"
                    }
                  >
                    {formatSignedCurrencyBRL(group.unrealizedPnl)}
                  </span>
                </div>
              </div>
              <div className="p-3">
                <Table density="compact" showMobileHint>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Ativo</TableHead>
                      <TableHead className="text-right">Quantidade</TableHead>
                      <TableHead className="text-right">Preço Médio</TableHead>
                      <TableHead className="text-right">Cotação Atual</TableHead>
                      <TableHead className="text-right">Custo Total</TableHead>
                      <TableHead className="text-right">Valor de Mercado</TableHead>
                      <TableHead className="text-right">Resultado</TableHead>
                      <TableHead className="text-right">% Classe</TableHead>
                      <TableHead className="text-right">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {group.holdings.map((h) => (
                      <TableRow key={h.ticker}>
                        <TableCell className="font-mono font-bold">{h.ticker}</TableCell>
                        <TableCell className="text-right font-mono">{formatQuantityPtBr(h.shares)}</TableCell>
                        <TableCell className="text-right font-mono">{formatCurrencyBRL(h.average_buy_price)}</TableCell>
                        <TableCell className="text-right font-mono">{formatCurrencyBRL(h.currentPrice)}</TableCell>
                        <TableCell className="text-right font-mono">{formatCurrencyBRL(h.costBasis)}</TableCell>
                        <TableCell className="text-right font-mono font-bold">{formatCurrencyBRL(h.marketValue)}</TableCell>
                        <TableCell
                          className={`text-right font-mono font-semibold ${
                            h.unrealizedPnl >= 0 ? "text-success" : "text-danger"
                          }`}
                        >
                          {formatSignedCurrencyBRL(h.unrealizedPnl)}
                        </TableCell>
                        <TableCell className="text-right font-mono">
                          {formatPercentPtBr(h.weightPct, 1)}
                        </TableCell>
                        <TableCell className="text-right">
                          <button
                            type="button"
                            data-ticker={h.ticker}
                            onClick={() => openChartForHolding(h.ticker)}
                            className="btn-contextual btn-holding-open-chart rounded-md px-2.5 py-1 text-[11px] font-bold"
                          >
                            Abrir gráfico
                          </button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Tabela Consolidada e Editor Rápido de Custódia */}
      <Card className="card-surface space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border pb-3">
          <div>
            <h3 className="section-title font-sans text-sm font-bold text-foreground">
              Gestão Direta de Posições & Caixa Livre
            </h3>
            <p className="section-subtitle text-xs text-muted-foreground">
              Edite posições, ajuste o saldo em caixa ou navegue diretamente para a análise gráfica do ativo
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Label htmlFor="portfolio-cash-input" className="text-xs">
              Caixa Livre (R$):
            </Label>
            <Input
              id="portfolio-cash-input"
              type="number"
              step="0.01"
              mono
              inputSize="sm"
              className="w-36"
              value={portfolio.availableCash}
              onChange={(e) => {
                const val = Number(e.target.value);
                updatePortfolio((prev) => ({
                  ...prev,
                  availableCash: Number.isFinite(val) ? val : 0,
                }));
              }}
            />
          </div>
        </div>

        <form
          onSubmit={handleQuickAddHolding}
          className="grid grid-cols-1 sm:grid-cols-4 gap-3 items-end"
        >
          <div>
            <Label htmlFor="quick-holding-ticker">Ticker do Ativo</Label>
            <Input
              id="quick-holding-ticker"
              placeholder="Ex: PETR4.SA"
              mono
              inputSize="sm"
              value={newTicker}
              onChange={(e) => setNewTicker(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="quick-holding-shares">Quantidade</Label>
            <Input
              id="quick-holding-shares"
              type="number"
              step="any"
              placeholder="100"
              mono
              inputSize="sm"
              value={newShares}
              onChange={(e) => setNewShares(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="quick-holding-price">Preço Médio (R$)</Label>
            <Input
              id="quick-holding-price"
              type="number"
              step="0.01"
              placeholder="35.50"
              mono
              inputSize="sm"
              value={newAvgPrice}
              onChange={(e) => setNewAvgPrice(e.target.value)}
            />
          </div>
          <Button type="submit" variant="primary" size="sm">
            Salvar na Custódia
          </Button>
        </form>

        <Table showMobileHint className="min-w-[1380px]">
          <TableHeader>
            <TableRow>
              <TableHead>Ticker</TableHead>
              <TableHead>Classe</TableHead>
              <TableHead className="text-right">Qtd.</TableHead>
              <TableHead className="text-right">Preço Médio</TableHead>
              <TableHead className="text-right">Cotação</TableHead>
              <TableHead className="text-right">Valor de Mercado</TableHead>
              <TableHead className="text-right">Resultado</TableHead>
              <TableHead className="text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody id="portfolio-holdings-list">
            {filteredHoldings.map((item) => (
              <TableRow key={item.ticker}>
                <TableCell className="font-mono font-bold">{item.ticker}</TableCell>
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
                  {formatSignedCurrencyBRL(item.unrealizedPnl)}
                </TableCell>
                <TableCell className="text-right">
                  <div className="inline-flex items-center gap-1.5">
                    <button
                      type="button"
                      data-ticker={item.ticker}
                      onClick={() => openChartForHolding(item.ticker)}
                      className="btn-contextual btn-holding-open-chart rounded-md px-2.5 py-1 text-[11px] font-bold"
                    >
                      Abrir gráfico
                    </button>
                    <button
                      type="button"
                      aria-label={`Remover ${item.ticker}`}
                      onClick={() => removeHolding(item.ticker)}
                      className="btn-remove-holding btn-danger rounded-md px-2 py-1 text-[11px]"
                    >
                      Remover
                    </button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {/* Consultor Quantitativo de Rebalanceamento & Backtest Multi-Ativo */}
      <Card className="card-surface space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border pb-3">
          <div>
            <h3 className="section-title font-sans text-sm font-bold text-foreground">
              Plano de Ação Quantitativo (Rebalanceamento)
            </h3>
            <p className="section-subtitle text-xs text-muted-foreground">
              Patrimônio Consolidado:{" "}
              <span id="advise-total-equity" className="font-mono font-bold text-foreground">
                {formatCurrencyBRL(metrics.totalEquity)}
              </span>{" "}
              • Caixa Disponível:{" "}
              <span id="advise-cash-transition" className="font-mono font-bold text-foreground">
                {formatCurrencyBRL(metrics.availableCash)}
              </span>
            </p>
          </div>
          <Button
            type="button"
            variant="primary"
            size="sm"
            disabled={adviceLoading}
            onClick={handleRunRebalanceAdvisor}
          >
            {adviceLoading ? "Calculando..." : "Gerar Plano de Ação"}
          </Button>
        </div>

        <Table density="compact">
          <TableHeader>
            <TableRow>
              <TableHead>Ativo</TableHead>
              <TableHead>Ordem</TableHead>
              <TableHead className="text-right">Quantidade</TableHead>
              <TableHead className="text-right">Preço Ref.</TableHead>
              <TableHead className="text-right">Volume Financeiro</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody id="portfolio-recommendations-tbody">
            {adviceOrders.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="py-4 text-center text-muted-foreground">
                  Clique em &ldquo;Gerar Plano de Ação&rdquo; para calcular ordens de rebalanceamento.
                </TableCell>
              </TableRow>
            ) : (
              adviceOrders.map((ord, idx) => (
                <TableRow key={`${ord.ticker}-${idx}`}>
                  <TableCell className="font-mono font-bold">{ord.ticker}</TableCell>
                  <TableCell>
                    <Badge
                      intent={
                        ord.action === "BUY"
                          ? "success"
                          : ord.action === "SELL"
                            ? "danger"
                            : "neutral"
                      }
                    >
                      {ord.action === "BUY" ? "▲ COMPRA" : ord.action === "SELL" ? "▼ VENDA" : "MANTER"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono">{ord.shares}</TableCell>
                  <TableCell className="text-right font-mono">{formatCurrencyBRL(ord.price)}</TableCell>
                  <TableCell className="text-right font-mono font-bold">
                    {formatCurrencyBRL(ord.financial_volume)}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>

        {/* KPIs e Gráficos de Simulação Multi-Ativo da Carteira */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 pt-2">
          <div className="rounded-md bg-surface-subtle p-2.5">
            <span className="text-[11px] text-muted-foreground">Capital Inicial</span>
            <div id="port-kpi-initial" className="font-mono text-xs font-bold">
              {formatCurrencyBRL(metrics.availableCash)}
            </div>
            <span id="port-kpi-cash-sub" className="text-[11px] text-muted-foreground">
              Caixa informado
            </span>
          </div>
          <div className="rounded-md bg-surface-subtle p-2.5">
            <span className="text-[11px] text-muted-foreground">Patrimônio Final</span>
            <div id="port-kpi-final" className="font-mono text-xs font-bold">
              {formatCurrencyBRL(metrics.totalEquity)}
            </div>
            <span id="port-kpi-profit-sub" className="text-[11px] text-muted-foreground">
              Resultado consolidado
            </span>
          </div>
          <div className="rounded-md bg-surface-subtle p-2.5">
            <span className="text-[11px] text-muted-foreground">Retorno Total</span>
            <div id="port-kpi-return" className="font-mono text-xs font-bold">
              {metrics.card1VarLabel}
            </div>
            <span id="port-kpi-bench-sub" className="text-[11px] text-muted-foreground">
              vs. Custo
            </span>
          </div>
          <div className="rounded-md bg-surface-subtle p-2.5">
            <span className="text-[11px] text-muted-foreground">Win Rate</span>
            <div id="port-kpi-winrate" className="font-mono text-xs font-bold">
              {metrics.kpiPosicoesPercentLabel}
            </div>
            <span id="port-kpi-exits-sub" className="text-[11px] text-muted-foreground">
              Acima do PM
            </span>
          </div>
          <div className="rounded-md bg-surface-subtle p-2.5">
            <span className="text-[11px] text-muted-foreground">Profit Factor</span>
            <div id="port-kpi-pf" className="font-mono text-xs font-bold">
              —
            </div>
            <span id="port-kpi-rotations-sub" className="text-[11px] text-muted-foreground">
              0 rotações
            </span>
          </div>
          <div className="rounded-md bg-surface-subtle p-2.5">
            <span className="text-[11px] text-muted-foreground">Drawdown Máx.</span>
            <div id="port-kpi-dd" className="font-mono text-xs font-bold">
              0,00%
            </div>
            <span id="port-kpi-events-sub" className="text-[11px] text-muted-foreground">
              0 eventos
            </span>
          </div>
        </div>

        <div id="portfolio-equity-chart" className="hidden" />
        <div id="portfolio-allocation-chart" className="hidden" />
        <Table density="compact" wrapperClassName="hidden">
          <TableBody id="portfolio-ledger-tbody" />
        </Table>
        <Table density="compact" wrapperClassName="hidden">
          <TableBody id="portfolio-ranking-tbody" />
        </Table>
      </Card>
    </section>
  );
}
