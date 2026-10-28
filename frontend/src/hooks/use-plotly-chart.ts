import * as React from "react";

declare global {
  interface Window {
    Plotly?: {
      react: (
        el: HTMLElement,
        data: unknown[],
        layout?: Record<string, unknown>,
        config?: Record<string, unknown>
      ) => Promise<void>;
      purge: (el: HTMLElement) => void;
      Plots?: {
        resize: (el: HTMLElement) => void;
      };
    };
  }
}

export function renderPlotlySafely(
  el: HTMLElement | null,
  data: unknown[],
  layout: Record<string, unknown>,
  config: Record<string, unknown> = {
    responsive: true,
    displayModeBar: false,
  }
): void {
  if (!el) return;
  (el as unknown as { data: unknown[] }).data = data;
  if (typeof window !== "undefined" && window.Plotly?.react) {
    try {
      void window.Plotly.react(el, data, layout, config);
    } catch {
      // Fallback safely if WebGL/SVG unavailable in jsdom
    }
  }
}
