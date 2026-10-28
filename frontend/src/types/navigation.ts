export type PillarId = "carteira" | "quant";

export type TabId =
  | "resumo"
  | "posicoes"
  | "proventos"
  | "patrimonio"
  | "radar"
  | "tradingview"
  | "simulador"
  | "playbook";

export type CanonicalRoute =
  | "carteira/visao-geral"
  | "carteira/posicoes"
  | "carteira/proventos"
  | "carteira/patrimonio"
  | "quant/radar"
  | "quant/grafico"
  | "quant/simulador"
  | "quant/playbook";

export interface RouteDefinition {
  route: CanonicalRoute;
  pillar: PillarId;
  tabId: TabId;
  paneId: string;
  subnavBtnId: string;
  label: string;
  icon: string;
}

export const ROUTE_CATALOG: Record<CanonicalRoute, RouteDefinition> = {
  "carteira/visao-geral": {
    route: "carteira/visao-geral",
    pillar: "carteira",
    tabId: "resumo",
    paneId: "tab-overview",
    subnavBtnId: "subnav-tab-resumo",
    label: "Visão Geral",
    icon: "icon-chart",
  },
  "carteira/posicoes": {
    route: "carteira/posicoes",
    pillar: "carteira",
    tabId: "posicoes",
    paneId: "tab-portfolio",
    subnavBtnId: "subnav-tab-posicoes",
    label: "Posições & Custódia",
    icon: "icon-wallet",
  },
  "carteira/proventos": {
    route: "carteira/proventos",
    pillar: "carteira",
    tabId: "proventos",
    paneId: "tab-pane-proventos",
    subnavBtnId: "subnav-tab-proventos",
    label: "Proventos",
    icon: "icon-coins",
  },
  "carteira/patrimonio": {
    route: "carteira/patrimonio",
    pillar: "carteira",
    tabId: "patrimonio",
    paneId: "tab-pane-patrimonio",
    subnavBtnId: "subnav-tab-patrimonio",
    label: "Evolução Patrimonial",
    icon: "icon-trending-up",
  },
  "quant/radar": {
    route: "quant/radar",
    pillar: "quant",
    tabId: "radar",
    paneId: "tab-pane-radar",
    subnavBtnId: "subnav-tab-radar",
    label: "Radar de Oportunidades",
    icon: "icon-target",
  },
  "quant/grafico": {
    route: "quant/grafico",
    pillar: "quant",
    tabId: "tradingview",
    paneId: "tab-terminal",
    subnavBtnId: "subnav-tab-tradingview",
    label: "Gráfico Interativo",
    icon: "icon-candlestick",
  },
  "quant/simulador": {
    route: "quant/simulador",
    pillar: "quant",
    tabId: "simulador",
    paneId: "tab-simulator",
    subnavBtnId: "subnav-tab-simulador",
    label: "Simulador & Backtest",
    icon: "icon-bolt",
  },
  "quant/playbook": {
    route: "quant/playbook",
    pillar: "quant",
    tabId: "playbook",
    paneId: "tab-playbook",
    subnavBtnId: "subnav-tab-playbook",
    label: "Playbook de Estratégias",
    icon: "icon-book",
  },
};

export const LEGACY_ROUTE_MAP: Record<string, CanonicalRoute> = {
  resumo: "carteira/visao-geral",
  overview: "carteira/visao-geral",
  "visao-geral": "carteira/visao-geral",
  posicoes: "carteira/posicoes",
  portfolio: "carteira/posicoes",
  custodia: "carteira/posicoes",
  proventos: "carteira/proventos",
  dividendos: "carteira/proventos",
  patrimonio: "carteira/patrimonio",
  evolucao: "carteira/patrimonio",
  radar: "quant/radar",
  terminal: "quant/grafico",
  tradingview: "quant/grafico",
  grafico: "quant/grafico",
  simulador: "quant/simulador",
  simulator: "quant/simulador",
  playbook: "quant/playbook",
};

export const ALLOWED_CONTEXTUAL_RETURN_SOURCES: Record<
  string,
  { route: CanonicalRoute; label: string }
> = {
  "carteira/posicoes": {
    route: "carteira/posicoes",
    label: "← Voltar para Posições",
  },
  "quant/radar": {
    route: "quant/radar",
    label: "← Voltar para Radar",
  },
};
