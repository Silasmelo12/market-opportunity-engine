import * as React from "react";
import { tv, type VariantProps } from "tailwind-variants";
import { cn } from "@/lib/utils";

export const inputVariants = tv({
  base: [
    "input flex w-full rounded-md border border-border-strong bg-surface px-3 py-1.5 text-[13px] text-foreground shadow-sm transition-colors",
    "placeholder:text-muted-foreground",
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-border-focus",
    "disabled:cursor-not-allowed disabled:opacity-50",
  ],
  variants: {
    inputSize: {
      sm: "min-h-[32px] px-2.5 py-1 text-xs",
      md: "min-h-[36px] px-3 py-1.5 text-[13px]",
      lg: "min-h-[40px] px-3.5 py-2 text-sm",
    },
    mono: {
      true: "font-mono tabular-nums",
      false: "font-sans",
    },
  },
  defaultVariants: {
    inputSize: "md",
    mono: false,
  },
});

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement>,
    VariantProps<typeof inputVariants> {}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = "text", inputSize, mono, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(inputVariants({ inputSize, mono }), className)}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";
