import * as React from "react";
import { tv, type VariantProps } from "tailwind-variants";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export const emptyStateVariants = tv({
  base: "state-empty flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border bg-surface-subtle p-6 text-center text-muted-foreground",
  variants: {
    compact: {
      true: "p-4 text-xs",
      false: "p-8 text-sm",
    },
  },
  defaultVariants: {
    compact: false,
  },
});

export interface EmptyStateProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof emptyStateVariants> {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({
  className,
  compact,
  title,
  description,
  action,
  ...props
}: EmptyStateProps) {
  return (
    <div className={cn(emptyStateVariants({ compact }), className)} {...props}>
      <p className="font-sans font-semibold text-foreground">{title}</p>
      {description && <p className="text-xs text-muted-foreground max-w-md">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}

export function ErrorState({
  title,
  message,
  onRetry,
}: {
  title: string;
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="state-error flex flex-col items-center justify-center gap-2 rounded-lg border border-danger-border bg-danger-soft p-6 text-center text-danger">
      <p className="font-sans text-sm font-bold">{title}</p>
      <p className="text-xs">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="btn-secondary mt-2 text-xs"
        >
          Tentar novamente
        </button>
      )}
    </div>
  );
}

export const statusPillVariants = tv({
  base: "filter-chip inline-flex items-center gap-1.5 rounded-full border px-3 py-1 font-sans text-xs font-semibold transition-all cursor-pointer",
  variants: {
    active: {
      true: "active active-cat bg-primary text-primary-foreground border-primary shadow-sm",
      false: "bg-surface text-muted-foreground border-border hover:bg-surface-subtle hover:text-foreground",
    },
  },
  defaultVariants: {
    active: false,
  },
});

export interface StatusPillProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof statusPillVariants> {}

export function StatusPill({ className, active, ...props }: StatusPillProps) {
  return (
    <button
      type="button"
      aria-pressed={Boolean(active)}
      className={cn(statusPillVariants({ active }), className)}
      {...props}
    />
  );
}

export interface MetricCardProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string;
  value: React.ReactNode;
  badgeText?: string;
  badgeIntent?: "neutral" | "primary" | "success" | "danger" | "warning";
  subtext?: React.ReactNode;
  valueId?: string;
  badgeId?: string;
  subtextId?: string;
}

export function MetricCard({
  id,
  className,
  label,
  value,
  badgeText,
  badgeIntent = "neutral",
  subtext,
  valueId,
  badgeId,
  subtextId,
  children,
  ...props
}: MetricCardProps) {
  return (
    <Card id={id} kind="kpi" className={cn("kpi-card card-surface", className)} {...props}>
      <div className="flex items-center justify-between gap-2">
        <span className="kpi-label section-title text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
          {label}
        </span>
        {badgeText && (
          <Badge id={badgeId} intent={badgeIntent}>
            {badgeText}
          </Badge>
        )}
      </div>
      <div
        id={valueId}
        className="kpi-value financial-value mt-2 font-mono text-2xl font-extrabold text-foreground tabular-nums"
      >
        {value}
      </div>
      {subtext && (
        <div
          id={subtextId}
          className="kpi-sub mt-1.5 flex items-center justify-between text-xs text-muted-foreground"
        >
          {subtext}
        </div>
      )}
      {children}
    </Card>
  );
}
