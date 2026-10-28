import { describe, expect, it, beforeEach, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import fs from "node:fs";
import path from "node:path";
import { App } from "@/app/App";
import { computePortfolioMetrics } from "@/hooks/use-portfolio-metrics";
import { DEFAULT_PORTFOLIO_STATE } from "@/services/portfolio-service";

describe("Market Opportunity React Application — Features & Architecture", () => {
  beforeEach(() => {
    localStorage.clear();
    window.location.hash = "";
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({ quotes: {}, items: [], total_pages: 1, total_assets: 0 }),
    } as Response);
  });

  it("renders all 8 canonical panels with exactly 1 visible by default and zero duplicate IDs", () => {
    const { container } = render(<App />);
    const panels = container.querySelectorAll("section.tab-view");
    expect(panels.length).toBe(8);

    const visiblePanels = Array.from(panels).filter(
      (p) => !p.classList.contains("hidden")
    );
    expect(visiblePanels.length).toBe(1);
    expect(visiblePanels[0].id).toBe("tab-overview");

    const idCounts = new Map<string, number>();
    container.querySelectorAll("[id]").forEach((el) => {
      idCounts.set(el.id, (idCounts.get(el.id) || 0) + 1);
    });
    const duplicates = Array.from(idCounts.entries()).filter(([, c]) => c > 1);
    expect(duplicates).toEqual([]);
  });

  it("navigates across pillars and subnav tabs and toggles theme", () => {
    render(<App />);
    const quantPillarBtn = document.getElementById("pillar-btn-quant")!;
    fireEvent.click(quantPillarBtn);

    expect(quantPillarBtn).toHaveAttribute("aria-selected", "true");
    expect(document.getElementById("tab-pane-radar")).not.toHaveClass("hidden");
    expect(document.getElementById("tab-overview")).toHaveClass("hidden");

    const playbookTab = document.getElementById("subnav-tab-playbook")!;
    fireEvent.click(playbookTab);
    expect(document.getElementById("tab-playbook")).not.toHaveClass("hidden");

    const themeBtn = document.getElementById("btn-theme-toggle")!;
    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
    fireEvent.click(themeBtn);
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });

  it("computes financial metrics accurately (zero-cost N/A and missing quote exclusion)", () => {
    const zeroCostSummary = computePortfolioMetrics(
      {
        ...DEFAULT_PORTFOLIO_STATE,
        availableCash: 2500,
        holdings: [{ ticker: "PETR4.SA", shares: 10, average_buy_price: 0 }],
      },
      {
        "PETR4.SA": { ticker: "PETR4.SA", price: 40, change_pct: 0 },
      }
    );
    expect(zeroCostSummary.totalEquity).toBe(2900);
    expect(zeroCostSummary.unrealizedPnl).toBe(400);
    expect(zeroCostSummary.kpiLucroBadgeLabel).toBe("N/A");
    expect(zeroCostSummary.kpiLucroSubLabel).toBe("Sem custo em custódia");
    expect(zeroCostSummary.kpiPosicoesCountLabel).toBe("Sem cotações válidas");
    expect(zeroCostSummary.kpiPosicoesPercentLabel).toBe("N/A");

    const partialQuoteSummary = computePortfolioMetrics(
      {
        ...DEFAULT_PORTFOLIO_STATE,
        availableCash: 500,
        holdings: [
          { ticker: "PETR4.SA", shares: 10, average_buy_price: 30 },
          { ticker: "VALE3.SA", shares: 10, average_buy_price: 60 },
        ],
      },
      {
        "PETR4.SA": { ticker: "PETR4.SA", price: 40, change_pct: 0 },
      }
    );
    expect(partialQuoteSummary.kpiPosicoesCountLabel).toBe("1 de 1");
    expect(partialQuoteSummary.kpiPosicoesPercentLabel).toBe("100%");
    expect(partialQuoteSummary.kpiPosicoesSubLabel).toBe("1 sem cotação válida");
  });

  it("adds a manual transaction via Modal 10 and updates holdings table", () => {
    render(<App />);
    const openBtn = document.getElementById("btn-header-add-trade")!;
    fireEvent.click(openBtn);

    fireEvent.change(document.getElementById("modal-trade-ticker")!, {
      target: { value: "ITUB4.SA" },
    });
    fireEvent.change(document.getElementById("modal-trade-shares")!, {
      target: { value: "50" },
    });
    fireEvent.change(document.getElementById("modal-trade-price")!, {
      target: { value: "40.00" },
    });
    fireEvent.click(document.getElementById("btn-modal-trade-save")!);

    expect(
      document.getElementById("overview-highlights-tbody")?.textContent
    ).toContain("ITUB4.SA");
  });

  it("enforces zero hexadecimal color codes across all React/TS/CSS files", () => {
    const srcDir = path.resolve(__dirname, "..");
    const hexRegex = /#[0-9a-fA-F]{3,8}\b/g;
    const offenders: string[] = [];

    function walk(dir: string) {
      for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          walk(full);
        } else if (/\.(ts|tsx|css)$/.test(entry.name)) {
          const content = fs.readFileSync(full, "utf-8");
          // Ignore SVG <use href="#icon-..." /> and URL hash "#..."
          const cleaned = content
            .replace(/href="#icon-[^"]+"/g, "")
            .replace(/#[a-zA-Z][\w/-]*/g, "");
          const matches = cleaned.match(hexRegex);
          if (matches) {
            offenders.push(`${path.relative(srcDir, full)}: ${matches.join(", ")}`);
          }
        }
      }
    }

    walk(srcDir);
    expect(offenders).toEqual([]);
  });
});
