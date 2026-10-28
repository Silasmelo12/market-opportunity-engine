import * as React from "react";
import { tv, type VariantProps } from "tailwind-variants";
import { cn } from "@/lib/utils";

export const cardVariants = tv({
  slots: {
    root: "card card-surface rounded-lg border border-border bg-surface text-card-foreground shadow-sm transition-colors",
    header: "card-header flex flex-col gap-1 border-b border-border pb-3",
    title: "card-title section-title font-sans text-[15px] font-bold tracking-tight text-foreground",
    description: "card-subtitle section-subtitle text-xs text-muted-foreground",
    content: "card-body pt-3",
    footer: "flex items-center justify-between border-t border-border pt-3",
  },
  variants: {
    kind: {
      default: {
        root: "p-4",
      },
      kpi: {
        root: "kpi-card metric-card p-4 flex flex-col justify-between",
      },
      chart: {
        root: "chart-card bg-white p-5",
      },
      category: {
        root: "category-card overflow-hidden p-0",
      },
      subtle: {
        root: "bg-surface-subtle p-3.5 shadow-none",
      },
    },
    interactive: {
      true: {
        root: "cursor-pointer hover:border-border-strong hover:bg-surface-hover",
      },
      false: {},
    },
  },
  defaultVariants: {
    kind: "default",
    interactive: false,
  },
});

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, kind, interactive, ...props }, ref) => {
    const { root } = cardVariants({ kind, interactive });
    return <div ref={ref} className={cn(root(), className)} {...props} />;
  }
);
Card.displayName = "Card";

export const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => {
  const { header } = cardVariants();
  return <div ref={ref} className={cn(header(), className)} {...props} />;
});
CardHeader.displayName = "CardHeader";

export const CardTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => {
  const { title } = cardVariants();
  return <h3 ref={ref} className={cn(title(), className)} {...props} />;
});
CardTitle.displayName = "CardTitle";

export const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => {
  const { description } = cardVariants();
  return <p ref={ref} className={cn(description(), className)} {...props} />;
});
CardDescription.displayName = "CardDescription";

export const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => {
  const { content } = cardVariants();
  return <div ref={ref} className={cn(content(), className)} {...props} />;
});
CardContent.displayName = "CardContent";

export const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => {
  const { footer } = cardVariants();
  return <div ref={ref} className={cn(footer(), className)} {...props} />;
});
CardFooter.displayName = "CardFooter";
