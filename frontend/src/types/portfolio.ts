export interface HoldingItem {
  ticker: string;
  shares: number;
  average_buy_price: number;
  asset_class?: string;
}

export interface QuoteItem {
  ticker: string;
  price: number | null;
  change_pct: number;
  time?: string;
  fallback?: boolean;
}

export interface QuotesResponse {
  quotes: Record<string, QuoteItem>;
}

export interface B3TimelineEvent {
  date?: string;
  month_year?: string;
  type?: string;
  event_type?: string;
  ticker?: string;
  product?: string;
  quantity?: number;
  unit_price?: number;
  total_value?: number;
  net_value?: number;
  invested?: number;
  total_equity?: number;
}

export interface B3MonthlyIncomeItem {
  month_year: string;
  dividendos: number;
  jcp: number;
  rendimentos: number;
  total: number;
  events?: Array<{
    date: string;
    ticker: string;
    type: string;
    value: number;
  }>;
}

export interface PortfolioStoragePayload {
  availableCash: number;
  holdings: HoldingItem[];
  universeCategory: string;
  interval: string;
  period: string;
  maxWeightPct: number;
  b3TotalIncome: number;
  b3Timeline: B3TimelineEvent[];
  b3MonthlyIncome: B3MonthlyIncomeItem[];
  assetGoals?: Record<string, number>;
}

export interface RebalanceOrderItem {
  ticker: string;
  action: "BUY" | "SELL" | "HOLD";
  shares: number;
  price: number;
  financial_volume: number;
  current_weight_pct?: number;
  target_weight_pct?: number;
  reason?: string;
}

export interface RebalanceAdviceResponse {
  total_equity: number;
  available_cash: number;
  orders: RebalanceOrderItem[];
  summary?: string;
}

export interface B3ParseResponse {
  status: string;
  holdings: HoldingItem[];
  total_income: number;
  monthly_income: B3MonthlyIncomeItem[];
  timeline: B3TimelineEvent[];
  files_processed?: number;
}
