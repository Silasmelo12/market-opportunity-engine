import * as React from "react";
import { useAppContext } from "@/state/app-context";
import { AppIcon } from "./SvgSprite";
import { parseCsvHoldingsText, uploadB3Files } from "@/services/portfolio-service";
import type { PillarId } from "@/types/navigation";

export function Topbar() {
  const {
    isSidebarOpen,
    toggleSidebar,
    theme,
    toggleTheme,
    activePillar,
    activeRoute,
    switchPillar,
    activeDirection,
    setActiveDirection,
    portfolio,
    updatePortfolio,
    setIsNewTradeModalOpen,
    triggerSharedCsvImport,
    sharedCsvInputRef,
    showToast,
    setLoadingText,
  } = useAppContext();

  const headerRef = React.useRef<HTMLElement | null>(null);
  const b3MultiInputRef = React.useRef<HTMLInputElement | null>(null);

  React.useEffect(() => {
    const el = headerRef.current;
    if (!el || typeof window === "undefined") return;
    const syncHeight = () => {
      const h = Math.round(el.getBoundingClientRect().height);
      if (h > 0) {
        document.documentElement.style.setProperty(
          "--shell-header-height",
          `${h}px`
        );
      }
    };
    syncHeight();
    window.addEventListener("resize", syncHeight);
    let ro: ResizeObserver | null = null;
    if (typeof ResizeObserver !== "undefined") {
      ro = new ResizeObserver(syncHeight);
      ro.observe(el);
    }
    return () => {
      window.removeEventListener("resize", syncHeight);
      if (ro) ro.disconnect();
    };
  }, [activeRoute, activePillar]);

  const handlePillarKeyDown = (
    e: React.KeyboardEvent<HTMLButtonElement>,
    current: PillarId
  ) => {
    if (
      e.key === "ArrowRight" ||
      e.key === "ArrowLeft" ||
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

  const handleCsvInputChange = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;
    try {
      const first = files[0];
      if (first.name.toLowerCase().endsWith(".csv") && files.length === 1) {
        const text = await first.text();
        const parsedHoldings = parseCsvHoldingsText(text);
        if (parsedHoldings.length > 0) {
          updatePortfolio((prev) => ({
            ...prev,
            holdings: parsedHoldings,
          }));
          showToast(
            `${parsedHoldings.length} ativos importados com sucesso.`,
            "success"
          );
          e.target.value = "";
          return;
        }
      }
      setLoadingText("Processando arquivos B3...");
      const resp = await uploadB3Files(files);
      updatePortfolio((prev) => ({
        ...prev,
        holdings: resp.holdings || prev.holdings,
        b3TotalIncome: resp.total_income ?? prev.b3TotalIncome,
        b3MonthlyIncome: resp.monthly_income || prev.b3MonthlyIncome,
        b3Timeline: resp.timeline || prev.b3Timeline,
      }));
      showToast("Extratos B3 conciliados com sucesso.", "success");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Erro ao importar arquivo";
      showToast(msg, "error");
    } finally {
      setLoadingText(null);
      e.target.value = "";
    }
  };

  const holdingsCount = (portfolio.holdings || []).length;
  const b3Label =
    holdingsCount > 0 ? `${holdingsCount} ativos importados` : "Importar B3";

  // Mantém verificação compatível para ocultar em posicoes/carteira
  const showDirectionSelector =
    (activeRoute === "quant/radar" || activeRoute === "quant/grafico") &&
    activeRoute !== "quant/grafico";

  return (
    <header
      ref={headerRef}
      className="app-header sticky top-0 z-40 border-b border-border bg-surface px-4 py-2.5"
    >
      <div className="mx-auto flex max-w-[1600px] flex-wrap items-center justify-between gap-3">
        <div className="brand-group flex min-w-0 items-center gap-2.5">
          <button
            type="button"
            id="btn-sidebar-toggle"
            aria-label={isSidebarOpen ? "Ocultar barra lateral" : "Exibir barra lateral"}
            title={isSidebarOpen ? "Ocultar barra lateral" : "Exibir barra lateral"}
            onClick={toggleSidebar}
            className="btn-icon flex h-8 w-8 items-center justify-center rounded-md border border-border bg-surface text-muted-foreground hover:bg-surface-subtle hover:text-foreground transition-colors shadow-sm"
          >
            <AppIcon name="icon-layers" className="h-4 w-4" />
          </button>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="brand-title truncate font-sans text-sm font-extrabold tracking-tight text-foreground">
                Market Opportunity
              </span>
              <span className="brand-tag hidden xl:inline-flex items-center rounded-sm border border-border bg-surface-subtle px-2 py-0.5 font-mono text-[11px] font-bold text-muted-foreground">
                Quantitative Pro
              </span>
            </div>
          </div>
        </div>

        {/* Ações Globais & Direção */}
        <div className="header-actions flex flex-wrap items-center gap-2">
          <div
            id="global-direction-selector"
            role="group"
            aria-label="Direção de Operação"
            className={`segmented inline-flex items-center rounded-md border border-border bg-surface-subtle p-0.5 ${
              showDirectionSelector ? "" : "hidden"
            }`}
          >
            <button
              type="button"
              data-dir="BUY"
              aria-pressed={activeDirection === "BUY"}
              onClick={() => setActiveDirection("BUY")}
              className={`dir-seg-btn rounded-sm px-2.5 py-1 font-mono text-[11px] font-bold transition-all ${
                activeDirection === "BUY"
                  ? "active active-buy bg-success-soft text-success border border-success-border"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              ▲ Compra (Fundo)
            </button>
            <button
              type="button"
              data-dir="SELL"
              aria-pressed={activeDirection === "SELL"}
              onClick={() => setActiveDirection("SELL")}
              className={`dir-seg-btn rounded-sm px-2.5 py-1 font-mono text-[11px] font-bold transition-all ${
                activeDirection === "SELL"
                  ? "active active-sell bg-danger-soft text-danger border border-danger-border"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              ▼ Venda (Topo)
            </button>
            <button
              type="button"
              data-dir="BOTH"
              aria-pressed={activeDirection === "BOTH"}
              onClick={() => setActiveDirection("BOTH")}
              className={`dir-seg-btn rounded-sm px-2.5 py-1 font-mono text-[11px] font-bold transition-all ${
                activeDirection === "BOTH"
                  ? "active bg-surface text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Ambos
            </button>
          </div>

          {/* Inputs de Arquivo Compartilhados */}
          <input
            ref={sharedCsvInputRef}
            id="portfolio-csv-file-input"
            type="file"
            accept=".csv,.xlsx,.xls"
            multiple
            className="hidden"
            aria-label="Selecionar arquivo CSV ou extrato da carteira"
            onChange={handleCsvInputChange}
          />
          <input
            ref={b3MultiInputRef}
            id="b3-multi-file-input"
            type="file"
            accept=".xlsx,.xls,.csv"
            multiple
            className="hidden"
            aria-label="Selecionar múltiplos arquivos B3"
            onChange={handleCsvInputChange}
          />

          <button
            type="button"
            id="btn-header-b3-status"
            aria-label="Importar dados da B3 ou CSV"
            onClick={triggerSharedCsvImport}
            className="btn-b3 btn-secondary inline-flex items-center gap-1.5 px-3 py-1.5 text-xs"
          >
            <AppIcon name="icon-import" className="h-3.5 w-3.5" />
            <span id="b3-import-label">{b3Label}</span>
          </button>

          <button
            type="button"
            id="btn-header-add-trade"
            aria-label="Novo Lançamento Manual"
            onClick={() => setIsNewTradeModalOpen(true)}
            className="btn-primary inline-flex items-center gap-1.5 px-3 py-1.5 text-xs"
          >
            <AppIcon name="icon-plus" className="h-3.5 w-3.5" />
            <span>Novo Lançamento</span>
          </button>

          <button
            type="button"
            id="btn-theme-toggle"
            aria-label="Alternar tema claro ou escuro"
            aria-pressed={theme === "dark"}
            onClick={toggleTheme}
            className="btn-icon inline-flex h-8 w-8 items-center justify-center rounded-md border border-border bg-surface-subtle text-foreground"
          >
            <svg
              id="theme-toggle-icon"
              className="icon h-4 w-4"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <use href={theme === "dark" ? "#icon-sun" : "#icon-moon"} />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}
