import { useMemo } from "react";
import type {
  HoldingItem,
  PortfolioStoragePayload,
  QuoteItem,
} from "@/types/portfolio";
import {
  classifyAssetCategory,
  formatCurrencyBRL,
  formatPercentPtBr,
  formatSignedCurrencyBRL,
  type AssetCategoryKey,
} from "@/lib/formatters";

export interface EnrichedHolding extends HoldingItem {
  categoryKey: AssetCategoryKey;
  categoryLabel: string;
  shortBadge: string;
  hasValidQuote: boolean;
  currentPrice: number;
  dayChangePct: number;
  costBasis: number;
  marketValue: number;
  unrealizedPnl: number;
  unrealizedPct: number | null;
  weightPct: number;
  isAboveAveragePrice: boolean;
}

export interface CategoryGroupSummary {
  key: AssetCategoryKey;
  label: string;
  holdings: EnrichedHolding[];
  totalCost: number;
  totalMarketValue: number;
  unrealizedPnl: number;
  unrealizedPct: number | null;
  weightPct: number;
}

export interface PortfolioMetricsSummary {
  availableCash: number;
  totalCostBasis: number;
  totalMarketValue: number;
  totalEquity: number;
  unrealizedPnl: number;
  unrealizedPct: number | null;
  card1VarLabel: string;
  kpiLucroValLabel: string;
  kpiLucroBadgeLabel: string;
  kpiLucroSubLabel: string;
  kpiPosicoesCountLabel: string;
  kpiPosicoesPercentLabel: string;
  kpiPosicoesSubLabel: string;
  dividendsTotalLabel: string;
  dividendsTitleLabel: string;
  dividendsPeriodLabel: string;
  dividendsMonthlyLabel: string;
  enrichedHoldings: EnrichedHolding[];
  categoryGroups: CategoryGroupSummary[];
  hasImportedData: boolean;
}

export function computePortfolioMetrics(
  portfolio: PortfolioStoragePayload,
  quotes: Record<string, QuoteItem>
): PortfolioMetricsSummary {
  const availableCash = Number.isFinite(Number(portfolio.availableCash))
    ? Number(portfolio.availableCash)
    : 0;
  const holdings = Array.isArray(portfolio.holdings) ? portfolio.holdings : [];

  let totalCostBasis = 0;
  let totalMarketValue = 0;
  let eligibleForAvgCheck = 0;
  let aboveAvgCount = 0;
  let missingQuotesCount = 0;

  const rawEnriched: Omit<EnrichedHolding, "weightPct">[] = holdings.map((h) => {
    const ticker = String(h.ticker || "").toUpperCase().trim();
    const shares = Math.max(0, Number(h.shares) || 0);
    const avgPrice = Math.max(0, Number(h.average_buy_price) || 0);
    const costBasis = shares * avgPrice;

    const quoteObj = quotes[ticker];
    const quotedPrice =
      quoteObj &&
      quoteObj.price !== null &&
      quoteObj.price !== undefined &&
      Number.isFinite(Number(quoteObj.price)) &&
      Number(quoteObj.price) > 0 &&
      !quoteObj.fallback
        ? Number(quoteObj.price)
        : null;

    const hasValidQuote = quotedPrice !== null;
    if (!hasValidQuote && shares > 0) {
      missingQuotesCount += 1;
    }

    const currentPrice = hasValidQuote ? quotedPrice : avgPrice;
    const marketValue = shares * currentPrice;
    const unrealizedPnl = marketValue - costBasis;
    const unrealizedPct =
      costBasis > 0 ? (unrealizedPnl / costBasis) * 100 : null;

    const isEligible = hasValidQuote && avgPrice > 0 && shares > 0;
    const isAboveAveragePrice = isEligible && currentPrice > avgPrice;
    if (isEligible) {
      eligibleForAvgCheck += 1;
      if (isAboveAveragePrice) {
        aboveAvgCount += 1;
      }
    }

    totalCostBasis += costBasis;
    totalMarketValue += marketValue;

    const cat = classifyAssetCategory(ticker);
    return {
      ticker,
      shares,
      average_buy_price: avgPrice,
      asset_class: h.asset_class,
      categoryKey: cat.key,
      categoryLabel: cat.label,
      shortBadge: cat.shortBadge,
      hasValidQuote,
      currentPrice,
      dayChangePct: Number(quoteObj?.change_pct) || 0,
      costBasis,
      marketValue,
      unrealizedPnl,
      unrealizedPct,
      isAboveAveragePrice,
    };
  });

  const totalEquity = availableCash + totalMarketValue;
  const unrealizedPnl = totalMarketValue - totalCostBasis;
  const unrealizedPct =
    totalCostBasis > 0 ? (unrealizedPnl / totalCostBasis) * 100 : null;

  const enrichedHoldings: EnrichedHolding[] = rawEnriched.map((item) => ({
    ...item,
    weightPct:
      totalMarketValue > 0 ? (item.marketValue / totalMarketValue) * 100 : 0,
  }));

  const groupMap = new Map<AssetCategoryKey, EnrichedHolding[]>();
  for (const h of enrichedHoldings) {
    const list = groupMap.get(h.categoryKey) || [];
    list.push(h);
    groupMap.set(h.categoryKey, list);
  }

  const categoryGroups: CategoryGroupSummary[] = Array.from(
    groupMap.entries()
  ).map(([key, items]) => {
    const totalCost = items.reduce((acc, i) => acc + i.costBasis, 0);
    const groupMarket = items.reduce((acc, i) => acc + i.marketValue, 0);
    const groupPnl = groupMarket - totalCost;
    const groupPct = totalCost > 0 ? (groupPnl / totalCost) * 100 : null;
    const weightPct =
      totalMarketValue > 0 ? (groupMarket / totalMarketValue) * 100 : 0;
    return {
      key,
      label: items[0].categoryLabel,
      holdings: items,
      totalCost,
      totalMarketValue: groupMarket,
      unrealizedPnl: groupPnl,
      unrealizedPct: groupPct,
      weightPct,
    };
  });

  const card1VarLabel =
    unrealizedPct !== null ? formatPercentPtBr(unrealizedPct, 2, true) : "N/A";
  const kpiLucroValLabel = formatSignedCurrencyBRL(unrealizedPnl);
  const kpiLucroBadgeLabel =
    unrealizedPct !== null ? formatPercentPtBr(unrealizedPct, 2, true) : "N/A";
  const kpiLucroSubLabel =
    totalCostBasis > 0
      ? `Sobre custo: ${formatCurrencyBRL(totalCostBasis)}`
      : "Sem custo em custódia";

  let kpiPosicoesCountLabel = "0 de 0";
  let kpiPosicoesPercentLabel = "0%";
  let kpiPosicoesSubLabel = "Carteira ativa";

  if (holdings.length === 0) {
    kpiPosicoesCountLabel = "0 de 0";
    kpiPosicoesPercentLabel = "0%";
    kpiPosicoesSubLabel = "Nenhum ativo em custódia";
  } else if (eligibleForAvgCheck === 0) {
    kpiPosicoesCountLabel = "Sem cotações válidas";
    kpiPosicoesPercentLabel = "N/A";
    kpiPosicoesSubLabel =
      missingQuotesCount > 0
        ? `${missingQuotesCount} sem cotação válida`
        : "Sem base de preço médio";
  } else {
    kpiPosicoesCountLabel = `${aboveAvgCount} de ${eligibleForAvgCheck}`;
    const pct = Math.round((aboveAvgCount / eligibleForAvgCheck) * 100);
    kpiPosicoesPercentLabel = `${pct}%`;
    kpiPosicoesSubLabel =
      missingQuotesCount > 0
        ? `${missingQuotesCount} sem cotação válida`
        : "Com cotação de mercado válida";
  }

  const monthlyIncomeList = Array.isArray(portfolio.b3MonthlyIncome)
    ? portfolio.b3MonthlyIncome
    : [];
  const totalDividends =
    Number(portfolio.b3TotalIncome) ||
    monthlyIncomeList.reduce((acc, m) => acc + (Number(m.total) || 0), 0);
  const dividendsTotalLabel = formatCurrencyBRL(totalDividends);
  const dividendsTitleLabel =
    monthlyIncomeList.length > 0 || totalDividends > 0
      ? "Proventos registrados no histórico importado"
      : "Nenhum provento importado";
  const dividendsPeriodLabel =
    monthlyIncomeList.length > 0 || totalDividends > 0
      ? "Histórico total"
      : "Sem registros";
  const dividendsMonthlyLabel =
    monthlyIncomeList.length > 0
      ? `${monthlyIncomeList.length} meses com registros`
      : "Importe extratos B3";

  const hasImportedData =
    holdings.length > 0 ||
    monthlyIncomeList.length > 0 ||
    totalDividends > 0 ||
    (Array.isArray(portfolio.b3Timeline) && portfolio.b3Timeline.length > 0);

  return {
    availableCash,
    totalCostBasis,
    totalMarketValue,
    totalEquity,
    unrealizedPnl,
    unrealizedPct,
    card1VarLabel,
    kpiLucroValLabel,
    kpiLucroBadgeLabel,
    kpiLucroSubLabel,
    kpiPosicoesCountLabel,
    kpiPosicoesPercentLabel,
    kpiPosicoesSubLabel,
    dividendsTotalLabel,
    dividendsTitleLabel,
    dividendsPeriodLabel,
    dividendsMonthlyLabel,
    enrichedHoldings,
    categoryGroups,
    hasImportedData,
  };
}

export function usePortfolioMetrics(
  portfolio: PortfolioStoragePayload,
  quotes: Record<string, QuoteItem>
): PortfolioMetricsSummary {
  return useMemo(
    () => computePortfolioMetrics(portfolio, quotes),
    [portfolio, quotes]
  );
}
