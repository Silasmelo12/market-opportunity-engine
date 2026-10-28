import * as React from "react";
import { useAppContext } from "@/state/app-context";
import { ROUTE_CATALOG, type CanonicalRoute } from "@/types/navigation";
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

export function SubnavBar() {
  const { activePillar, activeRoute, navigateToRoute } = useAppContext();

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
      e.key === "ArrowLeft" ||
      e.key === "Home" ||
      e.key === "End"
    ) {
      e.preventDefault();
      let nextIdx = idx;
      if (e.key === "ArrowRight") nextIdx = (idx + 1) % group.length;
      if (e.key === "ArrowLeft")
        nextIdx = (idx - 1 + group.length) % group.length;
      if (e.key === "Home") nextIdx = 0;
      if (e.key === "End") nextIdx = group.length - 1;
      const targetDef = ROUTE_CATALOG[group[nextIdx]];
      navigateToRoute(targetDef.route);
      document.getElementById(targetDef.subnavBtnId)?.focus();
    }
  };

  return (
    <nav
      aria-label="Subnavegação Contextual"
      style={{ top: "var(--shell-header-height, 56px)" }}
      className="subnav-bar sticky z-30 border-b border-border bg-surface px-4 py-1.5"
    >
      <div
        id="main-subnav-pills"
        className="mx-auto flex max-w-[1600px] items-center justify-between gap-2 overflow-x-auto"
      >
        {/* Subnavegação Minha Carteira */}
        <div
          id="subnav-group-carteira"
          role="tablist"
          aria-label="Subnavegação Minha Carteira"
          aria-orientation="horizontal"
          className={`flex items-center gap-1.5 ${
            activePillar === "carteira" ? "" : "hidden"
          }`}
        >
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
                className={`nav-tab inline-flex cursor-pointer items-center gap-1.5 rounded-md px-3 py-1.5 font-sans text-xs font-semibold transition-all ${
                  isSelected
                    ? "active bg-primary-soft text-primary font-bold"
                    : "text-muted-foreground hover:bg-surface-subtle hover:text-foreground"
                }`}
              >
                <AppIcon name={def.icon} className="h-3.5 w-3.5" />
                <span>{def.label}</span>
              </div>
            );
          })}
        </div>

        {/* Subnavegação Análise Quantitativa */}
        <div
          id="subnav-group-quant"
          role="tablist"
          aria-label="Subnavegação Análise Quantitativa"
          aria-orientation="horizontal"
          className={`flex items-center gap-1.5 ${
            activePillar === "quant" ? "" : "hidden"
          }`}
        >
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
                className={`nav-tab inline-flex cursor-pointer items-center gap-1.5 rounded-md px-3 py-1.5 font-sans text-xs font-semibold transition-all ${
                  isSelected
                    ? "active bg-primary-soft text-primary font-bold"
                    : "text-muted-foreground hover:bg-surface-subtle hover:text-foreground"
                }`}
              >
                <AppIcon name={def.icon} className="h-3.5 w-3.5" />
                <span>{def.label}</span>
              </div>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
