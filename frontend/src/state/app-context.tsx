import * as React from "react";
import {
  ROUTE_CATALOG,
  type CanonicalRoute,
  type PillarId,
  type TabId,
} from "@/types/navigation";
import type {
  HoldingItem,
  PortfolioStoragePayload,
  QuoteItem,
} from "@/types/portfolio";
import type { DirectionMode } from "@/types/market";
import {
  applyTheme as applyDomTheme,
  getSavedTheme,
  type ThemeMode,
} from "@/lib/theme";
import {
  fetchPortfolioQuotes,
  loadPortfolioFromStorage,
  savePortfolioToStorage,
} from "@/services/portfolio-service";
import {
  parseLocationHash,
  persistRouteToStorage,
  resolveRouteString,
} from "@/app/router";

export interface ToastNotice {
  id: number;
  message: string;
  type: "info" | "success" | "error" | "warning";
}

export interface AppContextValue {
  theme: ThemeMode;
  setTheme: (theme: ThemeMode, persist?: boolean) => void;
  toggleTheme: () => void;

  activeRoute: CanonicalRoute;
  activePillar: PillarId;
  activeTabId: TabId;
  navigateToRoute: (
    routeOrTab: string,
    options?: { replace?: boolean; query?: string }
  ) => void;
  switchPillar: (pillar: PillarId) => void;

  contextualTicker: string | null;
  contextualFromRoute: CanonicalRoute | null;
  contextualFromLabel: string | null;
  openChartForHolding: (ticker: string) => void;
  openChartFromRadar: (ticker: string, assetName?: string) => void;
  returnFromChartToSource: () => void;

  chartTicker: string;
  setChartTicker: React.Dispatch<React.SetStateAction<string>>;
  chartAssetName: string;
  setChartAssetName: React.Dispatch<React.SetStateAction<string>>;

  simTicker: string;
  setSimTicker: React.Dispatch<React.SetStateAction<string>>;

  activeDirection: DirectionMode;
  setActiveDirection: (dir: DirectionMode) => void;

  radarActiveCategory: string;
  setRadarActiveCategory: (cat: string) => void;
  radarTimeframe: string;
  setRadarTimeframe: (tf: string) => void;
  radarPage: number;
  setRadarPage: (page: number) => void;

  portfolio: PortfolioStoragePayload;
  updatePortfolio: (
    updater:
      | PortfolioStoragePayload
      | ((prev: PortfolioStoragePayload) => PortfolioStoragePayload)
  ) => void;
  addOrUpdateManualHolding: (item: HoldingItem & { operation?: "BUY" | "SELL" }) => void;
  removeHolding: (ticker: string) => void;

  quotes: Record<string, QuoteItem>;
  quotesLoading: boolean;
  refreshQuotes: () => Promise<void>;

  isB3ModalOpen: boolean;
  setIsB3ModalOpen: (open: boolean) => void;
  isNewTradeModalOpen: boolean;
  setIsNewTradeModalOpen: (open: boolean) => void;
  isMetasModalOpen: boolean;
  setIsMetasModalOpen: (open: boolean) => void;

  toast: ToastNotice | null;
  showToast: (
    message: string,
    type?: "info" | "success" | "error" | "warning"
  ) => void;
  loadingText: string | null;
  setLoadingText: (text: string | null) => void;

  triggerSharedCsvImport: () => void;
  sharedCsvInputRef: React.RefObject<HTMLInputElement>;
}

const AppContext = React.createContext<AppContextValue | null>(null);

declare global {
  interface Window {
    appState?: Record<string, unknown>;
    applyTheme?: (theme: string, persist?: boolean) => string;
    navigateToRoute?: (route: string) => void;
    openChartForHolding?: (ticker: string) => void;
    openChartFromRadar?: (ticker: string, assetName?: string) => void;
  }
}

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = React.useState<ThemeMode>(() =>
    getSavedTheme()
  );

  const initialParsed = React.useMemo(
    () =>
      typeof window !== "undefined"
        ? parseLocationHash(window.location.hash)
        : parseLocationHash(""),
    []
  );

  const [activeRoute, setActiveRoute] = React.useState<CanonicalRoute>(
    initialParsed.canonicalRoute
  );
  const [contextualTicker, setContextualTicker] = React.useState<string | null>(
    initialParsed.contextualTicker
  );
  const [contextualFromRoute, setContextualFromRoute] =
    React.useState<CanonicalRoute | null>(initialParsed.contextualFromRoute);
  const [contextualFromLabel, setContextualFromLabel] = React.useState<
    string | null
  >(initialParsed.contextualFromLabel);

  const internalContextualFlowRef = React.useRef<boolean>(false);
  const lastPillarRouteRef = React.useRef<Record<PillarId, CanonicalRoute>>({
    carteira: "carteira/visao-geral",
    quant: "quant/radar",
  });
  const radarScrollTopRef = React.useRef<number>(0);

  const [chartTicker, setChartTicker] = React.useState<string>(
    initialParsed.contextualTicker || "PETR4.SA"
  );
  const [chartAssetName, setChartAssetName] = React.useState<string>("");
  const [simTicker, setSimTicker] = React.useState<string>("PETR4.SA");

  const [activeDirection, setActiveDirectionState] =
    React.useState<DirectionMode>("BUY");
  const [radarActiveCategory, setRadarActiveCategoryState] =
    React.useState<string>("featured");
  const [radarTimeframe, setRadarTimeframeState] = React.useState<string>("1d");
  const [radarPage, setRadarPageState] = React.useState<number>(1);

  const [portfolio, setPortfolioState] =
    React.useState<PortfolioStoragePayload>(() => loadPortfolioFromStorage());
  const [quotes, setQuotes] = React.useState<Record<string, QuoteItem>>({});
  const [quotesLoading, setQuotesLoading] = React.useState<boolean>(false);

  const [isB3ModalOpen, setIsB3ModalOpen] = React.useState<boolean>(false);
  const [isNewTradeModalOpen, setIsNewTradeModalOpen] =
    React.useState<boolean>(false);
  const [isMetasModalOpen, setIsMetasModalOpen] =
    React.useState<boolean>(false);

  const [toast, setToast] = React.useState<ToastNotice | null>(null);
  const [loadingText, setLoadingText] = React.useState<string | null>(null);
  const sharedCsvInputRef = React.useRef<HTMLInputElement | null>(null);

  const showToast = React.useCallback(
    (
      message: string,
      type: "info" | "success" | "error" | "warning" = "info"
    ) => {
      setToast({ id: Date.now(), message, type });
    },
    []
  );

  React.useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(null), 4000);
    return () => window.clearTimeout(timer);
  }, [toast]);

  const setTheme = React.useCallback((next: ThemeMode, persist = true) => {
    const normalized = applyDomTheme(next, persist);
    setThemeState(normalized);
  }, []);

  const toggleTheme = React.useCallback(() => {
    setTheme(theme === "dark" ? "light" : "dark", true);
  }, [theme, setTheme]);

  React.useEffect(() => {
    applyDomTheme(theme, false);
  }, [theme]);

  // Normalize unknown initial hash immediately
  React.useEffect(() => {
    if (typeof window === "undefined") return;
    const parsed = parseLocationHash(window.location.hash);
    if (parsed.isUnknownExplicitHash) {
      window.history.replaceState(null, "", "#carteira/visao-geral");
      setActiveRoute("carteira/visao-geral");
      persistRouteToStorage("carteira/visao-geral");
    } else {
      persistRouteToStorage(parsed.canonicalRoute);
    }
  }, []);

  const applyHashLocation = React.useCallback(() => {
    if (typeof window === "undefined") return;
    setPortfolioState(loadPortfolioFromStorage());
    const savedTheme = getSavedTheme();
    applyDomTheme(savedTheme, false);
    setThemeState(savedTheme);

    const parsed = parseLocationHash(window.location.hash);
    if (parsed.isUnknownExplicitHash) {
      window.history.replaceState(null, "", "#carteira/visao-geral");
    }
    setActiveRoute(parsed.canonicalRoute);
    const def = ROUTE_CATALOG[parsed.canonicalRoute];
    lastPillarRouteRef.current[def.pillar] = parsed.canonicalRoute;
    persistRouteToStorage(parsed.canonicalRoute);

    setContextualTicker(parsed.contextualTicker);
    setContextualFromRoute(parsed.contextualFromRoute);
    setContextualFromLabel(parsed.contextualFromLabel);

    if (parsed.contextualTicker) {
      setChartTicker(parsed.contextualTicker);
    }

    if (parsed.canonicalRoute === "quant/radar") {
      const savedScroll = radarScrollTopRef.current;
      if (savedScroll > 0) {
        window.requestAnimationFrame(() => {
          const el = document.getElementById("tab-pane-radar");
          if (el) el.scrollTop = savedScroll;
        });
      }
    }
  }, []);

  React.useEffect(() => {
    if (typeof window === "undefined") return;
    const onHashOrPop = () => applyHashLocation();
    window.addEventListener("hashchange", onHashOrPop);
    window.addEventListener("popstate", onHashOrPop);
    return () => {
      window.removeEventListener("hashchange", onHashOrPop);
      window.removeEventListener("popstate", onHashOrPop);
    };
  }, [applyHashLocation]);

  const navigateToRoute = React.useCallback(
    (
      routeOrTab: string,
      options?: { replace?: boolean; query?: string }
    ) => {
      const resolved = resolveRouteString(routeOrTab) || "carteira/visao-geral";
      const def = ROUTE_CATALOG[resolved];
      lastPillarRouteRef.current[def.pillar] = resolved;
      persistRouteToStorage(resolved);
      setActiveRoute(resolved);

      if (!options?.query) {
        internalContextualFlowRef.current = false;
        setContextualTicker(null);
        setContextualFromRoute(null);
        setContextualFromLabel(null);
      }

      const targetHash = options?.query
        ? `#${resolved}?${options.query.replace(/^\?/, "")}`
        : `#${resolved}`;

      if (typeof window !== "undefined") {
        if (options?.replace) {
          window.history.replaceState(null, "", targetHash);
          applyHashLocation();
        } else if (window.location.hash !== targetHash) {
          window.location.hash = targetHash;
        } else {
          applyHashLocation();
        }
      }
    },
    [applyHashLocation]
  );

  const switchPillar = React.useCallback(
    (pillar: PillarId) => {
      const target =
        lastPillarRouteRef.current[pillar] ||
        (pillar === "carteira" ? "carteira/visao-geral" : "quant/radar");
      navigateToRoute(target);
    },
    [navigateToRoute]
  );

  const openChartForHolding = React.useCallback(
    (rawTicker: string) => {
      const clean = String(rawTicker || "").toUpperCase().trim();
      if (!clean) return;
      internalContextualFlowRef.current = true;
      setChartTicker(clean);
      setContextualTicker(clean);
      setContextualFromRoute("carteira/posicoes");
      setContextualFromLabel("← Voltar para Posições");
      navigateToRoute("quant/grafico", {
        query: `ticker=${encodeURIComponent(clean)}&from=carteira/posicoes`,
      });
    },
    [navigateToRoute]
  );

  const openChartFromRadar = React.useCallback(
    (rawTicker: string, assetName?: string) => {
      const clean = String(rawTicker || "").toUpperCase().trim();
      if (!clean) return;
      if (typeof document !== "undefined") {
        const radarPane = document.getElementById("tab-pane-radar");
        if (radarPane) {
          radarScrollTopRef.current = radarPane.scrollTop;
        }
      }
      internalContextualFlowRef.current = true;
      setChartTicker(clean);
      if (assetName) {
        setChartAssetName(assetName);
      }
      setContextualTicker(clean);
      setContextualFromRoute("quant/radar");
      setContextualFromLabel("← Voltar para Radar");
      const encodedTicker = clean.includes("=")
        ? encodeURIComponent(clean)
        : clean;
      navigateToRoute("quant/grafico", {
        query: `ticker=${encodedTicker}&from=quant/radar`,
      });
    },
    [navigateToRoute]
  );

  const returnFromChartToSource = React.useCallback(() => {
    const source = contextualFromRoute || "carteira/posicoes";
    if (internalContextualFlowRef.current && typeof window !== "undefined") {
      internalContextualFlowRef.current = false;
      window.history.back();
      return;
    }
    internalContextualFlowRef.current = false;
    navigateToRoute(source, { replace: true });
  }, [contextualFromRoute, navigateToRoute]);

  const updatePortfolio = React.useCallback(
    (
      updater:
        | PortfolioStoragePayload
        | ((prev: PortfolioStoragePayload) => PortfolioStoragePayload)
    ) => {
      setPortfolioState((prev) => {
        const next = typeof updater === "function" ? updater(prev) : updater;
        savePortfolioToStorage(next);
        return next;
      });
    },
    []
  );

  const addOrUpdateManualHolding = React.useCallback(
    (item: HoldingItem & { operation?: "BUY" | "SELL" }) => {
      const rawTicker = String(item.ticker || "").toUpperCase().trim();
      if (!rawTicker) return;
      const ticker =
        /^[A-Z]{4}\d{1,2}$/.test(rawTicker) && !rawTicker.endsWith(".SA")
          ? `${rawTicker}.SA`
          : rawTicker;
      const shares = Math.max(0, Number(item.shares) || 0);
      const price = Math.max(0, Number(item.average_buy_price) || 0);
      if (shares <= 0) return;

      updatePortfolio((prev) => {
        const existingIdx = prev.holdings.findIndex(
          (h) => h.ticker.toUpperCase() === ticker
        );
        const nextHoldings = [...prev.holdings];
        if (existingIdx >= 0) {
          const existing = nextHoldings[existingIdx];
          if (item.operation === "SELL") {
            const remaining = existing.shares - shares;
            if (remaining <= 1e-6) {
              nextHoldings.splice(existingIdx, 1);
            } else {
              nextHoldings[existingIdx] = {
                ...existing,
                shares: remaining,
              };
            }
          } else {
            const totalShares = existing.shares + shares;
            const weightedAvg =
              totalShares > 0
                ? (existing.shares * existing.average_buy_price +
                    shares * price) /
                  totalShares
                : price;
            nextHoldings[existingIdx] = {
              ...existing,
              shares: totalShares,
              average_buy_price: weightedAvg,
            };
          }
        } else if (item.operation !== "SELL") {
          nextHoldings.push({
            ticker,
            shares,
            average_buy_price: price,
            asset_class: item.asset_class,
          });
        }
        return {
          ...prev,
          holdings: nextHoldings,
        };
      });
    },
    [updatePortfolio]
  );

  const removeHolding = React.useCallback(
    (ticker: string) => {
      const upper = String(ticker || "").toUpperCase().trim();
      updatePortfolio((prev) => ({
        ...prev,
        holdings: prev.holdings.filter((h) => h.ticker.toUpperCase() !== upper),
      }));
    },
    [updatePortfolio]
  );

  const refreshQuotes = React.useCallback(async () => {
    const tickers = Array.from(
      new Set(
        (portfolio.holdings || [])
          .map((h) => String(h.ticker || "").toUpperCase().trim())
          .filter(Boolean)
      )
    );
    if (!tickers.length) {
      setQuotes({});
      return;
    }
    setQuotesLoading(true);
    try {
      const resp = await fetchPortfolioQuotes(tickers);
      setQuotes(resp.quotes || {});
    } catch {
      // Keep existing quotes or fallback cleanly
    } finally {
      setQuotesLoading(false);
    }
  }, [portfolio.holdings]);

  React.useEffect(() => {
    void refreshQuotes();
  }, [refreshQuotes]);

  const triggerSharedCsvImport = React.useCallback(() => {
    if (sharedCsvInputRef.current) {
      sharedCsvInputRef.current.click();
    }
  }, []);

  const activeDef = ROUTE_CATALOG[activeRoute];
  const activePillar = activeDef.pillar;
  const activeTabId = activeDef.tabId;

  // Expose reactive bridge on window for Playwright E2E and external tooling
  React.useEffect(() => {
    if (typeof window === "undefined") return;
    window.appState = {
      ...(window.appState || {}),
      theme,
      activeRoute,
      activePillar,
      activeTab: activeTabId,
      activeDirection,
      radarActiveCategory,
      radarTimeframe,
      radarPage,
      chartTicker,
      simTicker,
      portfolio,
      quotes,
    };
    window.applyTheme = (t: string, persist = true) => {
      const mode: ThemeMode = t === "dark" ? "dark" : "light";
      setTheme(mode, persist);
      return mode;
    };
    window.navigateToRoute = (r: string) => navigateToRoute(r);
    window.openChartForHolding = openChartForHolding;
    window.openChartFromRadar = openChartFromRadar;
  }, [
    theme,
    activeRoute,
    activePillar,
    activeTabId,
    activeDirection,
    radarActiveCategory,
    radarTimeframe,
    radarPage,
    chartTicker,
    simTicker,
    portfolio,
    quotes,
    setTheme,
    navigateToRoute,
    openChartForHolding,
    openChartFromRadar,
  ]);

  const setActiveDirection = React.useCallback((dir: DirectionMode) => {
    setActiveDirectionState(dir);
    if (typeof window !== "undefined" && window.appState) {
      window.appState.activeDirection = dir;
    }
  }, []);

  const setRadarActiveCategory = React.useCallback((cat: string) => {
    setRadarActiveCategoryState(cat);
    setRadarPageState(1);
    if (typeof window !== "undefined" && window.appState) {
      window.appState.radarActiveCategory = cat;
      window.appState.radarPage = 1;
    }
  }, []);

  const setRadarTimeframe = React.useCallback((tf: string) => {
    setRadarTimeframeState(tf);
    setRadarPageState(1);
    if (typeof window !== "undefined" && window.appState) {
      window.appState.radarTimeframe = tf;
      window.appState.radarPage = 1;
    }
  }, []);

  const setRadarPage = React.useCallback((page: number) => {
    setRadarPageState(page);
    if (typeof window !== "undefined" && window.appState) {
      window.appState.radarPage = page;
    }
  }, []);

  const value = React.useMemo<AppContextValue>(
    () => ({
      theme,
      setTheme,
      toggleTheme,
      activeRoute,
      activePillar,
      activeTabId,
      navigateToRoute,
      switchPillar,
      contextualTicker,
      contextualFromRoute,
      contextualFromLabel,
      openChartForHolding,
      openChartFromRadar,
      returnFromChartToSource,
      chartTicker,
      setChartTicker,
      chartAssetName,
      setChartAssetName,
      simTicker,
      setSimTicker,
      activeDirection,
      setActiveDirection,
      radarActiveCategory,
      setRadarActiveCategory,
      radarTimeframe,
      setRadarTimeframe,
      radarPage,
      setRadarPage,
      portfolio,
      updatePortfolio,
      addOrUpdateManualHolding,
      removeHolding,
      quotes,
      quotesLoading,
      refreshQuotes,
      isB3ModalOpen,
      setIsB3ModalOpen,
      isNewTradeModalOpen,
      setIsNewTradeModalOpen,
      isMetasModalOpen,
      setIsMetasModalOpen,
      toast,
      showToast,
      loadingText,
      setLoadingText,
      triggerSharedCsvImport,
      sharedCsvInputRef,
    }),
    [
      theme,
      setTheme,
      toggleTheme,
      activeRoute,
      activePillar,
      activeTabId,
      navigateToRoute,
      switchPillar,
      contextualTicker,
      contextualFromRoute,
      contextualFromLabel,
      openChartForHolding,
      openChartFromRadar,
      returnFromChartToSource,
      chartTicker,
      chartAssetName,
      simTicker,
      activeDirection,
      setActiveDirection,
      radarActiveCategory,
      setRadarActiveCategory,
      radarTimeframe,
      setRadarTimeframe,
      radarPage,
      setRadarPage,
      portfolio,
      updatePortfolio,
      addOrUpdateManualHolding,
      removeHolding,
      quotes,
      quotesLoading,
      refreshQuotes,
      isB3ModalOpen,
      isNewTradeModalOpen,
      isMetasModalOpen,
      toast,
      showToast,
      loadingText,
      triggerSharedCsvImport,
    ]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext(): AppContextValue {
  const ctx = React.useContext(AppContext);
  if (!ctx) {
    throw new Error("useAppContext must be used inside <AppProvider>");
  }
  return ctx;
}
