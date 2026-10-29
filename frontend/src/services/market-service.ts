import { fetchJson } from "./api-client";
import type { AnalyzeResponse, RadarResponse } from "@/types/market";

export interface FetchRadarParams {
  category?: string;
  direction?: string;
  interval?: string;
  page?: number;
  pageSize?: number;
  strategies?: string[];
  forceRefresh?: boolean;
}

export async function fetchRadarOpportunities(
  params: FetchRadarParams,
  signal?: AbortSignal
): Promise<RadarResponse> {
  const search = new URLSearchParams();
  if (params.category) search.set("category", params.category);
  if (params.direction) search.set("direction", params.direction);
  if (params.interval) search.set("interval", params.interval);
  search.set("page", String(params.page || 1));
  search.set("page_size", String(params.pageSize || 20));
  if (params.strategies && params.strategies.length > 0) {
    search.set("strategies", params.strategies.join(","));
  }
  if (params.forceRefresh) {
    search.set("force_refresh", "true");
  }
  return fetchJson<RadarResponse>(`/api/radar?${search.toString()}`, {
    signal,
  });
}

export interface AnalyzeAssetParams {
  ticker: string;
  period?: string;
  interval?: string;
  nBars?: number;
  mBars?: number;
  minReturnPct?: number;
  direction?: string;
  horizonX?: number;
  forceRefresh?: boolean;
}

export async function fetchAssetAnalysis(
  params: AnalyzeAssetParams,
  signal?: AbortSignal
): Promise<AnalyzeResponse> {
  const search = new URLSearchParams();
  search.set("ticker", params.ticker);
  search.set("period", params.period || "2y");
  search.set("interval", params.interval || "1d");
  search.set("n_bars", String(params.nBars ?? 15));
  search.set("m_bars", String(params.mBars ?? 5));
  search.set("min_return_pct", String(params.minReturnPct ?? 3.0));
  if (params.direction) search.set("direction", params.direction);
  if (typeof params.horizonX === "number") search.set("horizon_x", String(params.horizonX));
  if (params.forceRefresh) search.set("force_refresh", "true");

  return fetchJson<AnalyzeResponse>(`/api/analyze?${search.toString()}`, {
    signal,
  });
}
