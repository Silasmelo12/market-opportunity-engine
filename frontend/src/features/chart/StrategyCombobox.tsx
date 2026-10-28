import * as React from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

export interface StrategyItemDef {
  id: string;
  label: string;
  direction: "BUY" | "SELL";
}

export interface StrategyCategoryDef {
  id: string;
  name: string;
  direction: "BUY" | "SELL" | "BOTH";
  strategies: StrategyItemDef[];
}

export const ALL_STRATEGY_CATEGORIES: StrategyCategoryDef[] = [
  {
    id: "proprietary_buy",
    name: "Estratégia Proprietária - Compra (2x2)",
    direction: "BUY",
    strategies: [
      { id: "t1_open", label: "Negação Barra Anterior (Entrada Abertura)", direction: "BUY" },
      { id: "t1_retest", label: "Negação Barra Anterior (Entrada Reteste)", direction: "BUY" },
      { id: "t2_open", label: "Negação de Fundo N Barras (Entrada Abertura)", direction: "BUY" },
      { id: "t2_retest", label: "Negação de Fundo N Barras (Entrada Reteste)", direction: "BUY" },
    ],
  },
  {
    id: "proprietary_sell",
    name: "Estratégia Proprietária - Venda (2x2)",
    direction: "SELL",
    strategies: [
      { id: "sell_t1_open", label: "Negação Máxima Anterior (Venda Abertura)", direction: "SELL" },
      { id: "sell_t1_retest", label: "Negação Máxima Anterior (Venda Reteste)", direction: "SELL" },
      { id: "sell_t2_open", label: "Negação de Topo N Barras (Venda Abertura)", direction: "SELL" },
      { id: "sell_t2_retest", label: "Negação de Topo N Barras (Venda Reteste)", direction: "SELL" },
    ],
  },
  {
    id: "price_action_buy",
    name: "Price Action Institucional - Compra",
    direction: "BUY",
    strategies: [
      { id: "price_action_double_bottom_bos", label: "Fundo Duplo + BOS (Refinado)", direction: "BUY" },
      { id: "buy_double_top_inverted", label: "Topo Duplo Invertido (Compra)", direction: "BUY" },
      { id: "price_action_wyckoff_spring", label: "Varredura de Liquidez (Wyckoff Spring)", direction: "BUY" },
    ],
  },
  {
    id: "price_action_sell",
    name: "Price Action Institucional - Venda",
    direction: "SELL",
    strategies: [
      { id: "sell_double_top_bos", label: "Topo Duplo + BOS (Refinado)", direction: "SELL" },
      { id: "sell_double_bottom_inverted", label: "Fundo Duplo Invertido (Venda)", direction: "SELL" },
      { id: "sell_wyckoff_upthrust", label: "Varredura de Topo (Wyckoff Upthrust / UTAD)", direction: "SELL" },
    ],
  },
  {
    id: "allocation_buy",
    name: "Alocação Quantitativa & DCA - Compra",
    direction: "BUY",
    strategies: [
      { id: "dca_dynamic", label: "DCA Dinâmico (Desconto Estatístico)", direction: "BUY" },
      { id: "value_proxy", label: "Desconto Fundamentalista (Value Proxy)", direction: "BUY" },
      { id: "rebal_rf_rv", label: "Rebalanceamento Renda Fixa x Variável", direction: "BUY" },
      { id: "rebal_relative_strength", label: "Rebalanceamento Força Relativa (Z-Score)", direction: "BUY" },
    ],
  },
  {
    id: "allocation_sell",
    name: "Alocação & Realização - Venda",
    direction: "SELL",
    strategies: [
      { id: "sell_overbought_stat", label: "Excesso Estatístico / Realização Parcial", direction: "SELL" },
      { id: "sell_rebal_rv_rf", label: "Rebalanceamento Variável -> Renda Fixa", direction: "SELL" },
      { id: "sell_rebal_relative_strength", label: "Exaustão de Força Relativa", direction: "SELL" },
      { id: "sell_value_proxy", label: "Prêmio Excessivo / Valuation", direction: "SELL" },
    ],
  },
  {
    id: "mql5_bull",
    name: "Padrões de Velas de Fundo (14 MQL5 - Compra)",
    direction: "BUY",
    strategies: [
      { id: "hammer", label: "Vela: Martelo", direction: "BUY" },
      { id: "inverted_hammer", label: "Vela: Martelo Invertido", direction: "BUY" },
      { id: "bullish_engulfing", label: "Vela: Engolfo de Alta", direction: "BUY" },
      { id: "piercing_line", label: "Vela: Linha Perfurante", direction: "BUY" },
      { id: "morning_star", label: "Vela: Estrela da Manhã", direction: "BUY" },
      { id: "bullish_harami", label: "Vela: Harami de Alta", direction: "BUY" },
      { id: "three_inside_up", label: "Vela: Três Por Dentro de Alta", direction: "BUY" },
      { id: "three_outside_up", label: "Vela: Três Por Fora de Alta", direction: "BUY" },
      { id: "three_white_soldiers", label: "Vela: Três Soldados Brancos", direction: "BUY" },
      { id: "tweezer_bottom", label: "Vela: Pinça de Fundo (Tweezer Bottom)", direction: "BUY" },
      { id: "dragonfly_doji", label: "Vela: Doji Libélula", direction: "BUY" },
      { id: "abandoned_baby_bullish", label: "Vela: Bebê Abandonado de Alta", direction: "BUY" },
      { id: "bullish_kicker", label: "Vela: Chute de Alta (Bullish Kicker)", direction: "BUY" },
      { id: "climactic_pinbar", label: "Vela: Pinbar Clímax de Fundo com Volume", direction: "BUY" },
    ],
  },
  {
    id: "mql5_bear",
    name: "Padrões de Velas de Topo (14 MQL5 - Venda)",
    direction: "SELL",
    strategies: [
      { id: "shooting_star", label: "Vela Topo: Estrela Cadente (Shooting Star)", direction: "SELL" },
      { id: "hanging_man", label: "Vela Topo: Enforcado (Hanging Man)", direction: "SELL" },
      { id: "bearish_engulfing", label: "Vela Topo: Engolfo de Baixa", direction: "SELL" },
      { id: "dark_cloud_cover", label: "Vela Topo: Nuvem Negra (Dark Cloud Cover)", direction: "SELL" },
      { id: "evening_star", label: "Vela Topo: Estrela da Tarde (Evening Star)", direction: "SELL" },
      { id: "bearish_harami", label: "Vela Topo: Harami de Baixa", direction: "SELL" },
      { id: "three_inside_down", label: "Vela Topo: Três Por Dentro de Baixa", direction: "SELL" },
      { id: "three_outside_down", label: "Vela Topo: Três Por Fora de Baixa", direction: "SELL" },
      { id: "three_black_crows", label: "Vela Topo: Três Corvos Negros", direction: "SELL" },
      { id: "tweezer_top", label: "Vela Topo: Pinça de Topo (Tweezer Top)", direction: "SELL" },
      { id: "gravestone_doji", label: "Vela Topo: Doji Lápide (Gravestone)", direction: "SELL" },
      { id: "abandoned_baby_bearish", label: "Vela Topo: Bebê Abandonado de Baixa", direction: "SELL" },
      { id: "bearish_kicker", label: "Vela Topo: Chute de Baixa (Bearish Kicker)", direction: "SELL" },
      { id: "climactic_bearish_pinbar", label: "Vela Topo: Pinbar Clímax de Topo com Volume", direction: "SELL" },
    ],
  },
  {
    id: "quant_indicators",
    name: "Indicadores Técnicos & Quant",
    direction: "BOTH",
    strategies: [
      { id: "bollinger_close_in", label: "Bandas de Bollinger (Fechou Fora/Dentro)", direction: "BUY" },
      { id: "keltner_squeeze", label: "Keltner Squeeze (Compressão/Expansão)", direction: "BUY" },
      { id: "zscore_extreme", label: "Z-Score de Preço em Extremos", direction: "BUY" },
      { id: "rsi_divergence", label: "Divergência de IFR/RSI", direction: "BUY" },
      { id: "stochastic_extreme", label: "Estocástico Lento em Extremos", direction: "BUY" },
      { id: "macd_momentum", label: "MACD Histogram Momentum", direction: "BUY" },
      { id: "vwap_bands", label: "Bandas de VWAP", direction: "BUY" },
      { id: "mfi_extreme", label: "Money Flow Index (MFI) Extremo", direction: "BUY" },
      { id: "volume_climax_vsa", label: "Volume Clímax / VSA Absorção", direction: "BUY" },
      { id: "supertrend_trailing", label: "SuperTrend / ATR Trailing", direction: "BUY" },
    ],
  },
];

export const ALL_STRATEGY_IDS = ALL_STRATEGY_CATEGORIES.flatMap((c) =>
  c.strategies.map((s) => s.id)
);

interface StrategyComboboxProps {
  enabledStrategies: Record<string, boolean>;
  onChange: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
  activeDirection: string;
}

export function StrategyCombobox({
  enabledStrategies,
  onChange,
  activeDirection,
}: StrategyComboboxProps) {
  const [isOpen, setIsOpen] = React.useState<boolean>(false);
  const [search, setSearch] = React.useState<string>("");
  const popoverRef = React.useRef<HTMLDivElement | null>(null);

  // Close when clicking outside
  React.useEffect(() => {
    if (!isOpen) return;
    const handleClickOutside = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  const totalCount = ALL_STRATEGY_IDS.length;
  const selectedCount = ALL_STRATEGY_IDS.filter(
    (id) => enabledStrategies[id] !== false
  ).length;

  const toggleAll = (enable: boolean) => {
    const next: Record<string, boolean> = {};
    ALL_STRATEGY_IDS.forEach((id) => {
      next[id] = enable;
    });
    onChange(next);
  };

  const toggleByDirection = (dir: "BUY" | "SELL") => {
    const next: Record<string, boolean> = {};
    ALL_STRATEGY_CATEGORIES.forEach((cat) => {
      cat.strategies.forEach((st) => {
        next[st.id] = st.direction === dir;
      });
    });
    onChange(next);
  };

  const toggleCategory = (cat: StrategyCategoryDef, enable: boolean) => {
    onChange((prev) => {
      const next = { ...prev };
      cat.strategies.forEach((st) => {
        next[st.id] = enable;
      });
      return next;
    });
  };

  // Filter categories by search term
  const filteredCategories = ALL_STRATEGY_CATEGORIES.map((cat) => {
    const matched = cat.strategies.filter((st) => {
      if (!search.trim()) return true;
      const q = search.toLowerCase();
      return (
        st.label.toLowerCase().includes(q) ||
        st.id.toLowerCase().includes(q) ||
        cat.name.toLowerCase().includes(q)
      );
    });
    return {
      ...cat,
      strategies: matched,
    };
  }).filter((cat) => cat.strategies.length > 0);

  return (
    <div className="strategy-group segmented relative w-full" ref={popoverRef}>
      <button
        type="button"
        id="btn-strategy-combobox"
        aria-haspopup="true"
        aria-expanded={isOpen}
        onClick={() => setIsOpen((prev) => !prev)}
        className="flex w-full items-center justify-between rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-surface-subtle transition-colors shadow-sm"
      >
        <span className="truncate">
          Filtro de Estratégias ({selectedCount}/{totalCount})
        </span>
        <span className="ml-2 text-muted-foreground text-[11px]">▼</span>
      </button>

      {isOpen && (
        <div className="absolute left-0 top-full z-50 mt-1 max-h-[440px] w-full min-w-[320px] rounded-lg border border-border bg-surface p-3 shadow-xl flex flex-col gap-2">
          {/* Campo de Busca Rápida */}
          <div>
            <Input
              type="text"
              placeholder="Buscar estratégia por nome..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              inputSize="sm"
              autoFocus
            />
          </div>

          {/* Botões de Ação Rápida */}
          <div className="flex flex-wrap items-center gap-1.5 border-b border-border pb-2 text-[11px]">
            <button
              type="button"
              onClick={() => toggleAll(true)}
              className="rounded bg-surface-subtle px-2 py-0.5 font-bold text-foreground hover:bg-primary-soft hover:text-primary transition-colors"
            >
              Todas
            </button>
            <button
              type="button"
              onClick={() => toggleAll(false)}
              className="rounded bg-surface-subtle px-2 py-0.5 font-bold text-foreground hover:bg-danger-soft hover:text-danger transition-colors"
            >
              Nenhuma
            </button>
            <button
              type="button"
              onClick={() => toggleByDirection("BUY")}
              className="rounded bg-success-soft px-2 py-0.5 font-bold text-success border border-success-border"
            >
              ▲ Compra
            </button>
            <button
              type="button"
              onClick={() => toggleByDirection("SELL")}
              className="rounded bg-danger-soft px-2 py-0.5 font-bold text-danger border border-danger-border"
            >
              ▼ Venda
            </button>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="ml-auto rounded px-2 py-0.5 text-muted-foreground hover:text-foreground"
            >
              Fechar
            </button>
          </div>

          {/* Lista de Categorias com Checkboxes */}
          <div className="flex-1 overflow-y-auto space-y-3 pr-1 max-h-[300px]">
            {filteredCategories.map((cat) => {
              const allChecked = cat.strategies.every(
                (st) => enabledStrategies[st.id] !== false
              );
              const someChecked = cat.strategies.some(
                (st) => enabledStrategies[st.id] !== false
              );

              return (
                <div
                  key={cat.id}
                  className="strategy-group rounded-md border border-border bg-surface-subtle/50 p-2 space-y-1.5"
                >
                  <div className="flex items-center justify-between gap-2 border-b border-border/60 pb-1">
                    <label className="flex items-center gap-2 cursor-pointer text-xs font-bold text-foreground">
                      <Checkbox
                        checked={allChecked ? true : someChecked ? "indeterminate" : false}
                        onCheckedChange={(checked) =>
                          toggleCategory(cat, checked === true)
                        }
                      />
                      <span>{cat.name}</span>
                    </label>
                    <Badge
                      size="sm"
                      intent={
                        cat.direction === "BUY"
                          ? "success"
                          : cat.direction === "SELL"
                            ? "danger"
                            : "primary"
                      }
                    >
                      {cat.direction === "BUY"
                        ? "▲ COMPRA"
                        : cat.direction === "SELL"
                          ? "▼ VENDA"
                          : "AMBOS"}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-1 gap-1 pl-1 pt-1">
                    {cat.strategies.map((st) => {
                      const isChecked = enabledStrategies[st.id] !== false;
                      return (
                        <label
                          key={st.id}
                          className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground cursor-pointer py-0.5"
                        >
                          <Checkbox
                            checked={isChecked}
                            onCheckedChange={(checked) =>
                              onChange((prev) => ({
                                ...prev,
                                [st.id]: Boolean(checked),
                              }))
                            }
                          />
                          <span className="truncate flex-1">{st.label}</span>
                          <span
                            className={`font-mono text-[11px] uppercase font-bold ${
                              st.direction === "BUY"
                                ? "text-success"
                                : "text-danger"
                            }`}
                          >
                            {st.direction === "BUY" ? "▲" : "▼"}
                          </span>
                        </label>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
