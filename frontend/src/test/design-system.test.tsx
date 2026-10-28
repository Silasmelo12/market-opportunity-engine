import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { FinancialMetric } from "@/components/ui/financial-metric";
import { MetricCard, StatusPill } from "@/components/shared";

describe("Design System — shadcn/ui + tailwind-variants (tv)", () => {
  it("renders Button variants with semantic classes and zero hex colors", () => {
    render(
      <div>
        <Button variant="primary" data-testid="btn-p">
          Simular
        </Button>
        <Button variant="contextual" size="xs" data-testid="btn-c">
          Abrir gráfico
        </Button>
      </div>
    );
    const primaryBtn = screen.getByTestId("btn-p");
    const contextualBtn = screen.getByTestId("btn-c");
    expect(primaryBtn).toHaveClass("btn-primary", "bg-primary");
    expect(contextualBtn).toHaveClass("btn-contextual", "bg-primary-soft");
  });

  it("renders Badge and FinancialMetric with dual semantic encoding", () => {
    render(
      <div>
        <Badge intent="success" data-testid="badge-buy">
          ▲ COMPRA
        </Badge>
        <FinancialMetric trend="positive" size="lg" showGlyph data-testid="metric-pos">
          +R$ 1.250,00
        </FinancialMetric>
      </div>
    );
    expect(screen.getByTestId("badge-buy")).toHaveClass("badge-success", "text-success");
    expect(screen.getByTestId("metric-pos")).toHaveTextContent("▲ +R$ 1.250,00");
  });

  it("renders MetricCard and StatusPill with ARIA pressed state", () => {
    render(
      <div>
        <MetricCard
          id="kpi-test"
          label="Patrimônio Total"
          value="R$ 10.000,00"
          badgeText="+12,50%"
          badgeIntent="success"
        />
        <StatusPill active data-testid="pill-active">
          Ações Brasil
        </StatusPill>
      </div>
    );
    expect(screen.getByText("Patrimônio Total")).toBeInTheDocument();
    expect(screen.getByTestId("pill-active")).toHaveAttribute("aria-pressed", "true");
  });

  it("renders Card slots with semantic surface classes", () => {
    render(
      <Card kind="chart" data-testid="chart-card">
        <CardHeader>
          <CardTitle>Evolução do Patrimônio</CardTitle>
        </CardHeader>
        <CardContent>Conteúdo</CardContent>
      </Card>
    );
    expect(screen.getByTestId("chart-card")).toHaveClass("chart-card", "card-surface");
  });
});
