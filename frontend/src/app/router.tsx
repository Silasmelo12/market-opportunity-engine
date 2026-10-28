import {
  ALLOWED_CONTEXTUAL_RETURN_SOURCES,
  LEGACY_ROUTE_MAP,
  ROUTE_CATALOG,
  type CanonicalRoute,
} from "@/types/navigation";
import { sanitizeTickerQueryParam } from "@/lib/formatters";

export const ACTIVE_ROUTE_STORAGE_KEY = "mo_active_route";
export const ACTIVE_TAB_STORAGE_KEY = "mo_active_tab";

export interface ParsedHashRoute {
  canonicalRoute: CanonicalRoute;
  isUnknownExplicitHash: boolean;
  hasExplicitHash: boolean;
  queryParams: URLSearchParams;
  contextualTicker: string | null;
  contextualFromRoute: CanonicalRoute | null;
  contextualFromLabel: string | null;
}

export function resolveRouteString(rawRoute: string | null | undefined): CanonicalRoute | null {
  if (!rawRoute || typeof rawRoute !== "string") return null;
  const cleaned = rawRoute.replace(/^#\/?/, "").split("?")[0].trim().toLowerCase();
  if (!cleaned) return null;
  if (cleaned in ROUTE_CATALOG) {
    return cleaned as CanonicalRoute;
  }
  if (cleaned in LEGACY_ROUTE_MAP) {
    return LEGACY_ROUTE_MAP[cleaned];
  }
  return null;
}

export function parseLocationHash(hashStr: string): ParsedHashRoute {
  const raw = (hashStr || "").replace(/^#\/?/, "").trim();
  if (!raw) {
    const storedRoute =
      typeof window !== "undefined"
        ? resolveRouteString(localStorage.getItem(ACTIVE_ROUTE_STORAGE_KEY)) ||
          resolveRouteString(localStorage.getItem(ACTIVE_TAB_STORAGE_KEY))
        : null;
    return {
      canonicalRoute: storedRoute || "carteira/visao-geral",
      isUnknownExplicitHash: false,
      hasExplicitHash: false,
      queryParams: new URLSearchParams(),
      contextualTicker: null,
      contextualFromRoute: null,
      contextualFromLabel: null,
    };
  }

  const [pathPart, queryPart = ""] = raw.split("?");
  const resolved = resolveRouteString(pathPart);
  const queryParams = new URLSearchParams(queryPart);

  if (!resolved) {
    return {
      canonicalRoute: "carteira/visao-geral",
      isUnknownExplicitHash: true,
      hasExplicitHash: true,
      queryParams: new URLSearchParams(),
      contextualTicker: null,
      contextualFromRoute: null,
      contextualFromLabel: null,
    };
  }

  let contextualTicker: string | null = null;
  let contextualFromRoute: CanonicalRoute | null = null;
  let contextualFromLabel: string | null = null;

  if (resolved === "quant/grafico") {
    contextualTicker = sanitizeTickerQueryParam(queryParams.get("ticker"));
    const rawFrom = (queryParams.get("from") || "").trim();
    if (rawFrom && rawFrom in ALLOWED_CONTEXTUAL_RETURN_SOURCES) {
      const allowed = ALLOWED_CONTEXTUAL_RETURN_SOURCES[rawFrom];
      contextualFromRoute = allowed.route;
      contextualFromLabel = allowed.label;
    }
  }

  return {
    canonicalRoute: resolved,
    isUnknownExplicitHash: false,
    hasExplicitHash: true,
    queryParams,
    contextualTicker,
    contextualFromRoute,
    contextualFromLabel,
  };
}

export function persistRouteToStorage(route: CanonicalRoute): void {
  try {
    const def = ROUTE_CATALOG[route];
    localStorage.setItem(ACTIVE_ROUTE_STORAGE_KEY, route);
    localStorage.setItem(ACTIVE_TAB_STORAGE_KEY, def.tabId);
  } catch {
    // Ignore storage errors
  }
}
