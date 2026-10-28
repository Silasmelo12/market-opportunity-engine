import * as React from "react";
import { useAppContext } from "@/state/app-context";
import { AppIcon } from "./SvgSprite";

export function MobileNavigation() {
  const { activeRoute, navigateToRoute } = useAppContext();

  const items = [
    {
      route: "carteira/visao-geral",
      label: "Resumo",
      icon: "icon-chart",
    },
    {
      route: "carteira/posicoes",
      label: "Carteira",
      icon: "icon-wallet",
    },
    {
      route: "quant/radar",
      label: "Radar",
      icon: "icon-target",
    },
    {
      route: "quant/grafico",
      label: "Gráfico",
      icon: "icon-candlestick",
    },
  ] as const;

  return (
    <nav
      id="mobile-bottom-nav"
      aria-label="Navegação Móvel Rápida"
      className="fixed bottom-0 left-0 right-0 z-40 flex items-center justify-around border-t border-border bg-surface py-1.5 shadow-md md:hidden"
    >
      {items.map((item) => {
        const active = activeRoute === item.route;
        return (
          <button
            key={item.route}
            type="button"
            aria-label={item.label}
            aria-current={active ? "page" : undefined}
            onClick={() => navigateToRoute(item.route)}
            className={`flex flex-col items-center gap-0.5 rounded-md px-3 py-1 text-[11px] font-semibold transition-colors ${
              active ? "text-primary font-bold" : "text-muted-foreground"
            }`}
          >
            <AppIcon name={item.icon} className="h-4 w-4" />
            <span>{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}

export function ToastBanner() {
  const { toast } = useAppContext();
  return (
    <div
      id="toast-notification"
      role="status"
      aria-live="polite"
      className={`fixed bottom-16 right-4 z-50 rounded-lg border px-4 py-2.5 text-xs font-semibold shadow-lg transition-all ${
        toast
          ? "bg-surface text-foreground border-border opacity-100"
          : "pointer-events-none hidden opacity-0"
      }`}
    >
      {toast?.message || ""}
    </div>
  );
}

export function LoadingOverlay() {
  const { loadingText } = useAppContext();
  return (
    <div
      id="loading-spinner"
      role="status"
      aria-live="polite"
      className={`fixed inset-0 z-50 flex items-center justify-center bg-canvas/75 backdrop-blur-sm ${
        loadingText ? "" : "hidden"
      }`}
    >
      <div className="card-surface flex items-center gap-3 rounded-lg border border-border bg-surface px-5 py-3.5 shadow-lg">
        <AppIcon name="icon-refresh" className="h-5 w-5 animate-spin text-primary" />
        <span id="loading-text" className="font-sans text-xs font-bold text-foreground">
          {loadingText || "Processando..."}
        </span>
      </div>
    </div>
  );
}
