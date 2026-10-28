import * as React from "react";
import { tv, type VariantProps } from "tailwind-variants";
import { cn } from "@/lib/utils";

export const badgeVariants = tv({
  base: "badge badge-pill inline-flex items-center gap-1 rounded-sm border px-2 py-0.5 font-mono text-[11px] font-bold leading-tight transition-colors",
  variants: {
    intent: {
      neutral: "bg-surface-subtle text-muted-foreground border-border",
      primary: "badge-info bg-primary-soft text-primary border-primary",
      success: "badge-success bg-success-soft text-success border-success-border",
      danger: "badge-danger bg-danger-soft text-danger border-danger-border",
      warning: "badge-warning bg-warning-soft text-warning border-warning-border",
      purple: "bg-purple-soft text-purple border-border",
      teal: "bg-accent-teal-soft text-accent-teal border-border",
    },
    size: {
      sm: "min-h-[20px] px-1.5 text-[11px]",
      md: "min-h-[22px] px-2 text-[11px]",
      lg: "min-h-[26px] px-2.5 text-xs",
    },
  },
  defaultVariants: {
    intent: "neutral",
    size: "md",
  },
});

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, intent, size, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ intent, size }), className)} {...props} />
  );
}
