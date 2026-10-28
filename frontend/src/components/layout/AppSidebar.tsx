import * as React from "react";
import { useAppContext } from "@/state/app-context";
import { ROUTE_CATALOG, type CanonicalRoute, type PillarId } from "@/types/navigation";
import { AppIcon } from "./SvgSprite";

const CARTEIRA_ITEMS: CanonicalRoute[] = [
  "carteira/visao-geral",
  "carteira/posicoes",
  "carteira/proventos",
  "carteira/patrimonio",
];

const QUANT_ITEMS: CanonicalRoute[] = [
  "quant/radar",
  "quant/grafico",
  "quant/simulador",
  "quant/playbook",
];

export function AppSidebar() {
  const {
    isSidebarOpen,
    toggleSidebar,
    activePillar,
    activeRoute,
    switchPillar,
    navigateToRoute,
    portfolio,
  } = useAppContext();

  const handlePillarKeyDown = (
    e: React.KeyboardEvent<HTMLButtonElement>,
    current: PillarId
  ) => {
    if (
      e.key === "ArrowRight" ||
      e.key === "ArrowLeft" ||
      e.key === "ArrowUp" ||
      e.key === "ArrowDown" ||
      e.key === "Home" ||
      e.key === "End"
    ) {
      e.preventDefault();
      const next: PillarId =
        e.key === "Home"
          ? "carteira"
          : e.key === "End"
            ? "quant"
            : current === "carteira"
              ? "quant"
              : "carteira";
      switchPillar(next);
      const targetId =
        next === "carteira" ? "pillar-btn-carteira" : "pillar-btn-quant";
      document.getElementById(targetId)?.focus();
    } else if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      switchPillar(current);
    }
  };

  const handleTabKeyDown = (
    e: React.KeyboardEvent<HTMLDivElement>,
    group: CanonicalRoute[],
    idx: number
  ) => {
    const currentDef = ROUTE_CATALOG[group[idx]];
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      navigateToRoute(currentDef.route);
      return;
    }
    if (
      e.key === "ArrowRight" ||
      e.key === "ArrowDown" ||
      e.key === "ArrowLeft" ||
      e.key === "ArrowUp" ||
      e.key === "Home" ||
      e.key === "End"
    ) {
      e.preventDefault();
      let nextIdx = idx;
      if (e.key === "ArrowRight" || e.key === "ArrowDown")
        nextIdx = (idx + 1) % group.length;
      if (e.key === "ArrowLeft" || e.key === "ArrowUp")
        nextIdx = (idx - 1 + group.length) % group.length;
      if (e.key === "Home") nextIdx = 0;
      if (e.key === "End") nextIdx = group.length - 1;
      const targetDef = ROUTE_CATALOG[group[nextIdx]];
      navigateToRoute(targetDef.route);
      document.getElementById(targetDef.subnavBtnId)?.focus();
    }
  };

  if (!isSidebarOpen) {
    return null;
  }

  const holdingsCount = (portfolio.holdings || []).length;

  return (
    <aside
      id="app-sidebar-nav"
      aria-label="Barra Lateral de Navegação"
      className="app-sidebar flex flex-col w-64 shrink-0 border-r border-border bg-surface z-30 sticky top-[var(--shell-header-height,56px)] h-[calc(100vh-var(--shell-header-height,56px))] overflow-hidden transition-all duration-200"
    >
      {/* Cabeçalho da Barra Lateral */}
      <div className="flex items-center justify-between border-b border-border px-3 py-2.5">
        <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
          Navegação Principal
        </span>
        <button
          type="button"
          id="btn-sidebar-collapse"
          aria-label="Ocultar barra lateral"
          title="Ocultar barra lateral"
          onClick={toggleSidebar}
          className="btn-icon flex h-6 w-6 items-center justify-center rounded-md border border-border bg-surface text-muted-foreground hover:bg-surface-subtle hover:text-foreground transition-colors"
        >
          <AppIcon name="icon-arrow-left" className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Seletor de Pilares */}
      <div className="p-3 pb-2 border-b border-border bg-surface-subtle/50">
        <div
          id="global-pillar-selector"
          role="tablist"
          aria-label="Ambientes da Plataforma"
          aria-orientation="horizontal"
          className="segmented flex w-full items-center rounded-lg border border-border bg-surface-subtle p-1"
        >
          <button
            type="button"
            id="pillar-btn-carteira"
            role="tab"
            data-pillar="carteira"
            aria-selected={activePillar === "carteira"}
            aria-controls="subnav-group-carteira"
            tabIndex={activePillar === "carteira" ? 0 : -1}
            onClick={() => switchPillar("carteira")}
            onKeyDown={(e) => handlePillarKeyDown(e, "carteira")}
            className={`pillar-tab flex-1 inline-flex items-center justify-center gap-1.5 rounded-md px-2.5 py-1.5 font-sans text-xs font-bold transition-all ${
              activePillar === "carteira"
                ? "active bg-surface text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <AppIcon name="icon-wallet" className="h-3.5 w-3.5" />
            <span>Carteira</span>
          </button>

          <button
            type="button"
            id="pillar-btn-quant"
            role="tab"
            data-pillar="quant"
            aria-selected={activePillar === "quant"}
            aria-controls="subnav-group-quant"
            tabIndex={activePillar === "quant" ? 0 : -1}
            onClick={() => switchPillar("quant")}
            onKeyDown={(e) => handlePillarKeyDown(e, "quant")}
            className={`pillar-tab flex-1 inline-flex items-center justify-center gap-1.5 rounded-md px-2.5 py-1.5 font-sans text-xs font-bold transition-all ${
              activePillar === "quant"
                ? "active bg-surface text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <AppIcon name="icon-target" className="h-3.5 w-3.5" />
            <span>Quant</span>
          </button>
        </div>
      </div>

      {/* Subnavegação de Itens */}
      <nav
        aria-label="Subnavegação Contextual"
        style={{ top: "var(--shell-header-height, 56px)" }}
        className="subnav-bar flex-1 overflow-y-auto p-3"
      >
        <div id="main-subnav-pills" className="subnav-container flex flex-col gap-1">
          {/* Subnavegação Minha Carteira */}
          <div
            id="subnav-group-carteira"
            role="tablist"
            aria-label="Subnavegação Minha Carteira"
            aria-orientation="vertical"
            className={`flex flex-col gap-1 ${
              activePillar === "carteira" ? "" : "hidden"
            }`}
          >
            <span className="px-2 py-1 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
              Módulos da Carteira
            </span>
            {CARTEIRA_ITEMS.map((routeKey, idx) => {
              const def = ROUTE_CATALOG[routeKey];
              const isSelected = activeRoute === def.route;
              return (
                <div
                  key={def.route}
                  id={def.subnavBtnId}
                  data-tab={def.tabId}
                  role="tab"
                  aria-selected={isSelected}
                  aria-controls={def.paneId}
                  tabIndex={isSelected ? 0 : -1}
                  onClick={() => navigateToRoute(def.route)}
                  onKeyDown={(e) => handleTabKeyDown(e, CARTEIRA_ITEMS, idx)}
                  className={`nav-tab flex cursor-pointer items-center gap-2.5 rounded-md px-3 py-2 font-sans text-xs font-semibold transition-all ${
                    isSelected
                      ? "active bg-primary-soft text-primary font-bold shadow-sm"
                      : "text-muted-foreground hover:bg-surface-subtle hover:text-foreground"
                  }`}
                >
                  <AppIcon name={def.icon} className="h-4 w-4 shrink-0" />
                  <span className="truncate">{def.label}</span>
                </div>
              );
            })}
          </div>

          {/* Subnavegação Análise Quantitativa */}
          <div
            id="subnav-group-quant"
            role="tablist"
            aria-label="Subnavegação Análise Quantitativa"
            aria-orientation="vertical"
            className={`flex flex-col gap-1 ${
              activePillar === "quant" ? "" : "hidden"
            }`}
          >
            <span className="px-2 py-1 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
              Módulos Quantitativos
            </span>
            {QUANT_ITEMS.map((routeKey, idx) => {
              const def = ROUTE_CATALOG[routeKey];
              const isSelected = activeRoute === def.route;
              return (
                <div
                  key={def.route}
                  id={def.subnavBtnId}
                  data-tab={def.tabId}
                  role="tab"
                  aria-selected={isSelected}
                  aria-controls={def.paneId}
                  tabIndex={isSelected ? 0 : -1}
                  onClick={() => navigateToRoute(def.route)}
                  onKeyDown={(e) => handleTabKeyDown(e, QUANT_ITEMS, idx)}
                  className={`nav-tab flex cursor-pointer items-center gap-2.5 rounded-md px-3 py-2 font-sans text-xs font-semibold transition-all ${
                    isSelected
                      ? "active bg-primary-soft text-primary font-bold shadow-sm"
                      : "text-muted-foreground hover:bg-surface-subtle hover:text-foreground"
                  }`}
                >
                  <AppIcon name={def.icon} className="h-4 w-4 shrink-0" />
                  <span className="truncate">{def.label}</span>
                </div>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Rodapé da Barra Lateral */}
      <div className="border-t border-border bg-surface-subtle/40 p-3 text-xs text-muted-foreground">
        <div className="flex items-center justify-between">
          <span>Ativos monitorados:</span>
          <span className="font-mono font-bold text-foreground">
            {holdingsCount}
          </span>
        </div>
      </div>
    </aside>
  );
}
