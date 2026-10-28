import { postJson } from "./api-client";
import type { OptimizerResponse, SimulationResponse } from "@/types/market";

export interface RunSimulationPayload {
  ticker: string;
  interval: string;
  mode: string;
  cycle_mode: string;
  buy_strategy: string;
  sell_strategy: string;
  initial_capital: number;
  monthly_contribution: number;
  start_date?: string;
  end_date?: string;
  stop_loss_pct?: number;
  take_profit_pct?: number;
}

export async function runStrategySimulation(
  payload: RunSimulationPayload,
  signal?: AbortSignal
): Promise<SimulationResponse> {
  return postJson<SimulationResponse>("/api/simulate", payload, signal);
}

export async function runStrategyOptimization(
  payload: Omit<RunSimulationPayload, "buy_strategy" | "sell_strategy">,
  signal?: AbortSignal
): Promise<OptimizerResponse> {
  return postJson<OptimizerResponse>("/api/simulate/optimize", payload, signal);
}
