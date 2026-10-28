import * as React from "react";
import * as LabelPrimitive from "@radix-ui/react-label";
import { tv, type VariantProps } from "tailwind-variants";
import { cn } from "@/lib/utils";

export const labelVariants = tv({
  base: "field-label font-sans text-xs font-semibold leading-none text-muted-foreground peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
  variants: {
    uppercase: {
      true: " uppercase tracking-wider text-[11px]",
      false: "",
    },
  },
  defaultVariants: {
    uppercase: false,
  },
});

export interface LabelProps
  extends React.ComponentPropsWithoutRef<typeof LabelPrimitive.Root>,
    VariantProps<typeof labelVariants> {}

export const Label = React.forwardRef<
  React.ElementRef<typeof LabelPrimitive.Root>,
  LabelProps
>(({ className, uppercase, ...props }, ref) => (
  <LabelPrimitive.Root
    ref={ref}
    className={cn(labelVariants({ uppercase }), className)}
    {...props}
  />
));
Label.displayName = LabelPrimitive.Root.displayName;
