import { fetchJson, postJson, postMultipart } from "./api-client";
import type {
  B3ParseResponse,
  HoldingItem,
  PortfolioStoragePayload,
  QuotesResponse,
  RebalanceAdviceResponse,
} from "@/types/portfolio";

export const PORTFOLIO_STORAGE_KEY = "market_engine_portfolio_v1";

export const DEFAULT_PORTFOLIO_STATE: PortfolioStoragePayload = {
  availableCash: 0,
  holdings: [],
  universeCategory: "featured",
  interval: "1d",
  period: "2y",
  maxWeightPct: 25.0,
  b3TotalIncome: 0,
  b3Timeline: [],
  b3MonthlyIncome: [],
  assetGoals: {
    acao_br: 45,
    fii: 30,
    bdr: 15,
    cripto: 10,
  },
};

export function loadPortfolioFromStorage(): PortfolioStoragePayload {
  try {
    const raw = localStorage.getItem(PORTFOLIO_STORAGE_KEY);
    if (!raw) return { ...DEFAULT_PORTFOLIO_STATE };
    const parsed = JSON.parse(raw) as Partial<PortfolioStoragePayload>;
    return {
      ...DEFAULT_PORTFOLIO_STATE,
      ...parsed,
      availableCash: Number.isFinite(Number(parsed.availableCash))
        ? Number(parsed.availableCash)
        : 0,
      holdings: Array.isArray(parsed.holdings)
        ? parsed.holdings.map((h) => ({
            ticker: String(h.ticker || "").toUpperCase().trim(),
            shares: Number(h.shares) || 0,
            average_buy_price: Number(h.average_buy_price) || 0,
            asset_class: h.asset_class,
          }))
        : [],
      b3TotalIncome: Number(parsed.b3TotalIncome) || 0,
      b3Timeline: Array.isArray(parsed.b3Timeline) ? parsed.b3Timeline : [],
      b3MonthlyIncome: Array.isArray(parsed.b3MonthlyIncome)
        ? parsed.b3MonthlyIncome
        : [],
    };
  } catch {
    return { ...DEFAULT_PORTFOLIO_STATE };
  }
}

export function savePortfolioToStorage(state: PortfolioStoragePayload): void {
  try {
    localStorage.setItem(PORTFOLIO_STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Ignore quota errors
  }
}

export async function fetchPortfolioQuotes(
  tickers: string[],
  signal?: AbortSignal
): Promise<QuotesResponse> {
  if (!tickers.length) {
    return { quotes: {} };
  }
  return postJson<QuotesResponse>("/api/portfolio/quotes", { tickers }, signal);
}

export async function requestPortfolioAdvice(
  payload: {
    available_cash: number;
    holdings: HoldingItem[];
    universe_category: string;
    interval: string;
    period: string;
    max_weight_pct: number;
  },
  signal?: AbortSignal
): Promise<RebalanceAdviceResponse> {
  return postJson<RebalanceAdviceResponse>(
    "/api/portfolio/advise",
    payload,
    signal
  );
}

export async function uploadB3Files(
  files: File[],
  signal?: AbortSignal
): Promise<B3ParseResponse> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  return postMultipart<B3ParseResponse>("/api/b3/parse", formData, signal);
}

export async function syncLocalB3Folder(
  signal?: AbortSignal
): Promise<B3ParseResponse> {
  return fetchJson<B3ParseResponse>("/api/b3/sync-local", {
    method: "POST",
    signal,
  });
}

export function parseCsvHoldingsText(csvText: string): HoldingItem[] {
  const lines = csvText
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean);
  if (!lines.length) return [];

  const result: HoldingItem[] = [];
  for (let idx = 0; idx < lines.length; idx++) {
    const line = lines[idx];
    if (idx === 0 && /ticker|ativo|papel/i.test(line)) {
      continue;
    }
    const separator = line.includes(";") ? ";" : ",";
    const cols = line.split(separator).map((c) => c.trim().replace(/^"|"$/g, ""));
    if (cols.length < 2) continue;
    const rawTicker = cols[0].toUpperCase();
    if (!rawTicker) continue;
    const ticker =
      /^[A-Z]{4}\d{1,2}$/.test(rawTicker) && !rawTicker.endsWith(".SA")
        ? `${rawTicker}.SA`
        : rawTicker;
    const parseNum = (val: string | undefined) => {
      if (!val) return 0;
      const cleaned = val.replace(/[R$\s]/g, "");
      if (cleaned.includes(",") && cleaned.includes(".")) {
        return Number(cleaned.replace(/\./g, "").replace(",", ".")) || 0;
      }
      return Number(cleaned.replace(",", ".")) || 0;
    };
    const shares = parseNum(cols[1]);
    const average_buy_price = parseNum(cols[2]);
    if (shares > 0) {
      result.push({ ticker, shares, average_buy_price });
    }
  }
  return result;
}
