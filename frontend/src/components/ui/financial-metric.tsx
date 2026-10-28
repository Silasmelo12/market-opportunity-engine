import * as React from "react";
import { tv, type VariantProps } from "tailwind-variants";
import { cn } from "@/lib/utils";

export const financialMetricVariants = tv({
  base: "financial-value font-mono tabular-nums tracking-tight",
  variants: {
    trend: {
      positive: "text-success",
      negative: "text-danger",
      neutral: "text-foreground",
      muted: "text-muted-foreground",
    },
    size: {
      sm: "text-xs font-semibold",
      md: "text-sm font-bold",
      lg: "text-lg font-extrabold",
      hero: "kpi-value text-2xl font-extrabold",
    },
  },
  defaultVariants: {
    trend: "neutral",
    size: "md",
  },
});

export interface FinancialMetricProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof financialMetricVariants> {
  showGlyph?: boolean;
}

export function FinancialMetric({
  className,
  trend,
  size,
  showGlyph = false,
  children,
  ...props
}: FinancialMetricProps) {
  const glyph =
    showGlyph && trend === "positive"
      ? "▲ "
      : showGlyph && trend === "negative"
        ? "▼ "
        : "";
  return (
    <span
      data-financial="true"
      className={cn(financialMetricVariants({ trend, size }), className)}
      {...props}
    >
      {glyph}
      {children}
    </span>
  );
}
