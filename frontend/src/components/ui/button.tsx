import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { tv, type VariantProps } from "tailwind-variants";
import { cn } from "@/lib/utils";

export const buttonVariants = tv({
  base: [
    "inline-flex items-center justify-center gap-1.5 whitespace-nowrap rounded-md font-sans font-semibold transition-all",
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-border-focus",
    "disabled:pointer-events-none disabled:opacity-45",
  ],
  variants: {
    variant: {
      primary: "btn-primary bg-primary text-primary-foreground shadow-sm hover:bg-primary-hover",
      secondary: "btn-secondary bg-surface text-foreground border border-border-strong shadow-sm hover:bg-surface-subtle",
      contextual: "btn-contextual bg-primary-soft text-primary border border-primary hover:bg-primary hover:text-primary-foreground",
      danger: "btn-danger bg-danger-soft text-danger border border-danger-border hover:bg-danger hover:text-primary-foreground",
      ghost: "btn-ghost bg-transparent text-muted-foreground hover:bg-surface-subtle hover:text-foreground",
      icon: "btn-icon bg-surface-subtle text-foreground border border-border hover:bg-surface-hover",
    },
    size: {
      xs: "min-h-[28px] px-2.5 py-1 text-[11px]",
      sm: "min-h-[32px] px-3 py-1.5 text-xs",
      md: "min-h-[36px] px-4 py-2 text-[13px]",
      lg: "min-h-[42px] px-5 py-2.5 text-sm",
      icon: "h-8 w-8 p-0",
    },
    activeState: {
      true: "ring-2 ring-border-focus",
      false: "",
    },
  },
  compoundVariants: [
    {
      variant: "contextual",
      size: "xs",
      class: "font-mono font-bold tracking-tight",
    },
  ],
  defaultVariants: {
    variant: "primary",
    size: "sm",
    activeState: false,
  },
});

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, activeState, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, activeState }), className)}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";
