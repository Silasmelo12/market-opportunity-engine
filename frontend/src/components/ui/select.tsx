import * as React from "react";
import { tv, type VariantProps } from "tailwind-variants";
import { cn } from "@/lib/utils";

export const selectVariants = tv({
  base: [
    "select flex w-full items-center justify-between rounded-md border border-border-strong bg-surface px-3 py-1.5 text-[13px] font-medium text-foreground shadow-sm transition-colors",
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-border-focus",
    "disabled:cursor-not-allowed disabled:opacity-50",
  ],
  variants: {
    selectSize: {
      sm: "min-h-[32px] px-2.5 py-1 text-xs",
      md: "min-h-[36px] px-3 py-1.5 text-[13px]",
    },
  },
  defaultVariants: {
    selectSize: "md",
  },
});

export interface SelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement>,
    VariantProps<typeof selectVariants> {}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, selectSize, children, ...props }, ref) => (
    <select
      ref={ref}
      className={cn(selectVariants({ selectSize }), className)}
      {...props}
    >
      {children}
    </select>
  )
);
Select.displayName = "Select";
