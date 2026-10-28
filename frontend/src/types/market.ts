export type DirectionMode = "BUY" | "SELL" | "BOTH";

export interface RadarItem {
  ticker: string;
  asset_name: string;
  category: string;
  direction: "BUY" | "SELL";
  strategy_sub_id: string;
  strategy_label: string;
  status_signal: string;
  timing_category: "IDEAL" | "EXTENDED" | "WAIT" | string;
  timing_label: string;
  distance_pct: number;
  historical_n: number;
  historical_win_rate: number;
  win_rate: number;
  last_price?: number;
}

export interface RadarResponse {
  items: RadarItem[];
  page: number;
  page_size: number;
  total_assets: number;
  total_pages: number;
  direction: string;
}

export interface CandlePoint {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

export interface SignalPoint {
  time?: string;
  signal_date?: string;
  execution_date?: string;
  signal_bar_index?: number | null;
  execution_bar_index?: number | null;
  price?: number;
  execution_price?: number;
  direction: "BUY" | "SELL";
  strategy_sub_id: string;
  strategy_label: string;
  forward_return?: number | null;
  forward_return_pct?: number | null;
  mae?: number | null;
  mae_pct?: number | null;
  win?: boolean;
}

export interface StrategySummary {
  strategy_sub_id: string;
  strategy_label: string;
  direction: "BUY" | "SELL";
  win_rate: number;
  mean_forward_return: number;
  mean_mae: number;
  total_signals: number;
  executed_buys?: number;
}

export interface AnalyzeResponse {
  ticker: string;
  asset_name?: string;
  interval?: string;
  period?: string;
  candles: CandlePoint[];
  signals: SignalPoint[];
  summaries?: StrategySummary[];
  timing_status?:
    | string
    | {
        category?: string;
        label?: string;
        distance_pct?: number;
      }
    | null;
  reference_lines?: Array<{
    price?: number;
    price_level?: number;
    label?: string;
    color?: string;
  }>;
}

export interface SimulationTrade {
  entry_date: string;
  exit_date?: string;
  entry_price: number;
  exit_price?: number;
  shares: number;
  pnl_brl: number;
  pnl_pct: number;
  buy_strategy?: string;
  sell_strategy?: string;
  sub_entries?: Array<{
    date: string;
    price: number;
    shares: number;
    strategy: string;
  }>;
}

export interface SimulationResponse {
  ticker: string;
  final_equity: number;
  total_return_pct: number;
  buy_and_hold_return_pct: number;
  alpha_pct: number;
  win_rate_pct: number;
  profit_factor: number;
  max_drawdown_pct: number;
  total_trades: number;
  equity_curve: Array<{
    time: string;
    equity: number;
    benchmark?: number;
    invested?: number;
  }>;
  trades: SimulationTrade[];
}

export interface OptimizerCombination {
  rank: number;
  buy_strategy_id: string;
  buy_strategy_label: string;
  sell_strategy_id: string;
  sell_strategy_label: string;
  total_return_pct: number;
  win_rate_pct: number;
  max_drawdown_pct: number;
  profit_factor: number;
  total_trades: number;
}

export interface OptimizerResponse {
  ticker: string;
  champion: OptimizerCombination | null;
  combinations: OptimizerCombination[];
}

export interface PlaybookStrategyDef {
  id: string;
  title: string;
  group: string;
  direction: "BUY" | "SELL" | "RISK";
  badgeLabel: string;
  formula: string;
  description: string;
  idealRegime: string;
}
