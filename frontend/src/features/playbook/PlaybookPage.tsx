import * as React from "react";
import { useAppContext } from "@/state/app-context";
import type { PlaybookStrategyDef } from "@/types/market";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

const PLAYBOOK_STRATEGIES: PlaybookStrategyDef[] = [
  {
    id: "t1_open",
    title: "Negação da Barra Anterior (Abertura 2x2)",
    group: "Reversão de Fundo 2x2",
    direction: "BUY",
    badgeLabel: "▲ COMPRA (FUNDO)",
    formula: "Low[0] < Low[-1] && Close[0] > Open[-1]",
    description:
      "Captura varreduras de liquidez abaixo da mínima anterior seguidas de absorção compradora imediata.",
    idealRegime: "Correção aguda em tendência primária de alta",
  },
  {
    id: "t1_close",
    title: "Negação da Barra Anterior (Fechamento)",
    group: "Reversão de Fundo 2x2",
    direction: "BUY",
    badgeLabel: "▲ COMPRA (FUNDO)",
    formula: "Low[0] < Low[-1] && Close[0] > Close[-1]",
    description:
      "Confirmação de fechamento acima do fechamento prévio após violação da mínima.",
    idealRegime: "Suporte institucional com volume climático",
  },
  {
    id: "double_bottom",
    title: "Fundo Duplo Institucional (W-Pattern)",
    group: "Padrões Estruturais",
    direction: "BUY",
    badgeLabel: "▲ COMPRA (FUNDO)",
    formula: "|Low[t] - Low[t-k]| <= ATR * 0.5 && RSI_Div > 0",
    description:
      "Re-teste simétrico de zona de demanda com divergência positiva de momentum.",
    idealRegime: "Consolidação de fundo após ciclo de distribuição",
  },
  {
    id: "spring_wyckoff",
    title: "Spring Institucional Wyckoff",
    group: "Liquidez & Microestrutura",
    direction: "BUY",
    badgeLabel: "▲ COMPRA (FUNDO)",
    formula: "Low[0] < Min(Low, 20) && Close[0] > Min(Low, 20)",
    description:
      "Falso rompimento do suporte de 20 períodos com rejeição imediata (armadilha de ursos).",
    idealRegime: "Fase C de acumulação de Wyckoff",
  },
  {
    id: "zscore_oversold",
    title: "Exaustão Estatística Z-Score (-2.5σ)",
    group: "Reversão à Média",
    direction: "BUY",
    badgeLabel: "▲ COMPRA (FUNDO)",
    formula: "(Close - SMA20) / StdDev20 <= -2.5",
    description:
      "Desvio extremo abaixo da média móvel de 20 períodos indicando capitulação vendedora.",
    idealRegime: "Mercados laterais ou choque de liquidez temporário",
  },
  {
    id: "bullish_engulfing",
    title: "Engolfo de Alta Institucional",
    group: "Ação de Preço",
    direction: "BUY",
    badgeLabel: "▲ COMPRA (FUNDO)",
    formula: "Close[0] > Open[0] && Body[0] > Body[-1] * 1.25",
    description:
      "Corpo real comprador envolve integralmente a barra vendedora anterior em região descontada.",
    idealRegime: "Final de pullback em ativos de alta qualidade",
  },
  {
    id: "shooting_star",
    title: "Estrela Cadente de Exaustão (Topo)",
    group: "Reversão de Topo",
    direction: "SELL",
    badgeLabel: "▼ VENDA (TOPO)",
    formula: "UpperWick >= 2.0 * Body && Close < MidPoint",
    description:
      "Rejeição severa de preços superiores após rali estendido, sinalizando distribuição institucional.",
    idealRegime: "Sobrecompra estatística (Z-Score > +2.0σ)",
  },
  {
    id: "double_top",
    title: "Topo Duplo Confirmado (M-Pattern)",
    group: "Padrões Estruturais",
    direction: "SELL",
    badgeLabel: "▼ VENDA (TOPO)",
    formula: "|High[t] - High[t-k]| <= ATR * 0.5 && Close < Neckline",
    description:
      "Falha dupla em superar máxima histórica ou resistência intermediária com perda de força relativa.",
    idealRegime: "Exaustão de tendência e rotação setorial",
  },
  {
    id: "bearish_engulfing",
    title: "Engolfo de Baixa em Zona Estendida",
    group: "Reversão de Topo",
    direction: "SELL",
    badgeLabel: "▼ VENDA (TOPO)",
    formula: "Close[0] < Open[0] && Close[0] < Low[-1]",
    description:
      "Barra de distribuição ampla anulando o ganho anterior no topo do canal de volatilidade.",
    idealRegime: "Realização de lucros parcial ou total da posição",
  },
  {
    id: "mae_risk_guard",
    title: "Controle de Excursão Máxima Adversa (MAE)",
    group: "Gestão de Risco",
    direction: "RISK",
    badgeLabel: "◆ GESTÃO DE RISCO",
    formula: "StopLoss = EntryPrice * (1 - P75_MAE)",
    description:
      "Dimensionamento dinâmico de proteção baseado no percentil 75 da excursão adversa histórica do ativo.",
    idealRegime: "Proteção de capital em todas as janelas operacionais",
  },
];

export function PlaybookPage() {
  const { activeRoute } = useAppContext();
  const [searchQuery, setSearchQuery] = React.useState<string>("");
  const [activeFilter, setActiveFilter] = React.useState<
    "ALL" | "BUY" | "SELL" | "RISK"
  >("ALL");

  const filteredStrategies = React.useMemo(() => {
    const q = searchQuery.toLowerCase().trim();
    return PLAYBOOK_STRATEGIES.filter((st) => {
      if (activeFilter !== "ALL" && st.direction !== activeFilter) {
        return false;
      }
      if (!q) return true;
      return (
        st.title.toLowerCase().includes(q) ||
        st.description.toLowerCase().includes(q) ||
        st.group.toLowerCase().includes(q) ||
        st.formula.toLowerCase().includes(q)
      );
    });
  }, [searchQuery, activeFilter]);

  const isVisible = activeRoute === "quant/playbook";

  return (
    <section
      id="tab-playbook"
      role="tabpanel"
      aria-labelledby="subnav-tab-playbook"
      className={`tab-view quant-area mx-auto max-w-[1600px] space-y-5 px-4 py-5 pb-20 ${
        isVisible ? "" : "hidden"
      }`}
    >
      {/* Barra de Busca e Filtros do Playbook (Penpot Screen 08) */}
      <Card className="card-surface flex flex-wrap items-center justify-between gap-3 p-4">
        <div className="space-y-0.5">
          <h2 className="section-title font-sans text-base font-bold text-foreground">
            Playbook Quantitativo & Catálogo de Estratégias
          </h2>
          <p className="section-subtitle text-xs text-muted-foreground">
            Documentação matemática, regras de gatilho e regimes ideais das estratégias do motor estatístico
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Input
            id="playbook-search-input"
            placeholder="Buscar estratégia, fórmula ou grupo..."
            inputSize="sm"
            className="w-64"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />

          <div
            id="playbook-filter-pills"
            role="group"
            aria-label="Filtrar estratégias por direção"
            className="segmented inline-flex rounded-md border border-border bg-surface-subtle p-0.5"
          >
            {(
              [
                { id: "ALL", label: "Todas" },
                { id: "BUY", label: "Compra (Fundo)" },
                { id: "SELL", label: "Venda (Topo)" },
                { id: "RISK", label: "Gestão de Risco" },
              ] as const
            ).map((f) => {
              const active = activeFilter === f.id;
              return (
                <button
                  key={f.id}
                  type="button"
                  data-filter={f.id}
                  aria-pressed={active}
                  onClick={() => setActiveFilter(f.id)}
                  className={`playbook-filter-btn rounded-sm px-3 py-1 text-xs font-semibold transition-all ${
                    active
                      ? "active bg-surface text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {f.label}
                </button>
              );
            })}
          </div>
        </div>
      </Card>

      {/* Grid de Cards de Estratégias (#playbook-cards-grid) */}
      <div
        id="playbook-cards-grid"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        {filteredStrategies.map((st) => (
          <Card
            key={st.id}
            className="playbook-strategy-card card-surface flex flex-col justify-between space-y-3"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between gap-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
                  {st.group}
                </span>
                <Badge
                  intent={
                    st.direction === "BUY"
                      ? "success"
                      : st.direction === "SELL"
                        ? "danger"
                        : "warning"
                  }
                >
                  {st.badgeLabel}
                </Badge>
              </div>
              <h3 className="font-sans text-sm font-bold text-foreground">
                {st.title}
              </h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                {st.description}
              </p>
            </div>

            <div className="space-y-2 border-t border-border pt-2.5">
              <div className="rounded-sm bg-surface-subtle px-2.5 py-1.5 font-mono text-[11px] text-foreground">
                {st.formula}
              </div>
              <div className="text-[11px] text-muted-foreground">
                <strong className="text-foreground">Regime ideal:</strong>{" "}
                {st.idealRegime}
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Blocos Metodológicos Institucionais */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="playbook-block card-surface space-y-2">
          <h3 className="playbook-group-title font-sans text-sm font-bold text-foreground">
            1. Protocolo de Validação Estatística (N, M, X%)
          </h3>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Cada sinal é auditado avaliando se nos <strong>N períodos subsequentes</strong> o ativo atingiu pelo menos <strong>X% de retorno favorável</strong> antes de violar o limite de risco nos primeiros <strong>M períodos</strong>.
          </p>
        </Card>

        <Card className="playbook-block card-surface space-y-2">
          <h3 className="playbook-group-title font-sans text-sm font-bold text-foreground">
            2. Classificação de Zona de Timing (Ideal vs. Estendida)
          </h3>
          <p className="text-xs text-muted-foreground leading-relaxed">
            O motor compara a cotação atual com o preço de disparo do sinal. Ativos dentro da banda de tolerância estatística recebem selo de <strong>Timing Ideal</strong>.
          </p>
        </Card>
      </div>
    </section>
  );
}
