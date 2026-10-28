export type ThemeMode = "light" | "dark";

export const THEME_STORAGE_KEY = "terminal_theme";

export function getSavedTheme(): ThemeMode {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    return stored === "light" || stored === "dark" ? stored : "light";
  } catch {
    return "light";
  }
}

export function applyTheme(theme: string, persist = true): ThemeMode {
  const normalized: ThemeMode = theme === "dark" ? "dark" : "light";
  if (typeof document !== "undefined") {
    document.documentElement.setAttribute("data-theme", normalized);
    document.documentElement.dataset.theme = normalized;
  }
  if (persist) {
    try {
      localStorage.setItem(THEME_STORAGE_KEY, normalized);
    } catch {
      // Ignore storage quota errors in private browsing
    }
  }
  return normalized;
}

export function getThemeToken(tokenName: string, fallback = "rgb(15, 23, 42)"): string {
  if (typeof window === "undefined" || typeof document === "undefined") {
    return fallback;
  }
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(tokenName)
    .trim();
  return value || fallback;
}

export function getChartThemeTokens() {
  return {
    bg: getThemeToken("--chart-bg", "rgba(0, 0, 0, 0)"),
    surface: getThemeToken("--surface", "rgb(255, 255, 255)"),
    text: getThemeToken("--chart-text", "rgb(71, 85, 105)"),
    textMain: getThemeToken("--text-main", "rgb(15, 23, 42)"),
    grid: getThemeToken("--chart-grid", "rgba(203, 213, 225, 0.55)"),
    border: getThemeToken("--chart-border", "rgb(226, 232, 240)"),
    up: getThemeToken("--chart-up", "rgb(16, 185, 129)"),
    down: getThemeToken("--chart-down", "rgb(244, 63, 94)"),
    primary: getThemeToken("--chart-primary", "rgb(3, 105, 161)"),
    secondary: getThemeToken("--chart-secondary", "rgb(15, 118, 110)"),
    invested: getThemeToken("--chart-invested", "rgb(59, 130, 246)"),
    gain: getThemeToken("--chart-gain", "rgb(16, 185, 129)"),
    loss: getThemeToken("--chart-loss", "rgb(244, 63, 94)"),
    proventos: getThemeToken("--chart-proventos", "rgb(245, 158, 11)"),
    avgLine: getThemeToken("--chart-avg-line", "rgb(245, 158, 11)"),
    slices: [
      getThemeToken("--chart-slice-1", "rgb(59, 130, 246)"),
      getThemeToken("--chart-slice-2", "rgb(16, 185, 129)"),
      getThemeToken("--chart-slice-3", "rgb(245, 158, 11)"),
      getThemeToken("--chart-slice-4", "rgb(139, 92, 246)"),
      getThemeToken("--chart-slice-5", "rgb(6, 182, 212)"),
      getThemeToken("--chart-slice-6", "rgb(236, 72, 153)"),
    ],
  };
}
