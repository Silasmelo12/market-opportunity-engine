import * as React from "react";
import * as SeparatorPrimitive from "@radix-ui/react-separator";
import { tv, type VariantProps } from "tailwind-variants";
import { cn } from "@/lib/utils";

export const separatorVariants = tv({
  base: "shrink-0 bg-border",
  variants: {
    orientation: {
      horizontal: "h-[1px] w-full",
      vertical: "h-full w-[1px]",
    },
  },
  defaultVariants: {
    orientation: "horizontal",
  },
});

export const Separator = React.forwardRef<
  React.ElementRef<typeof SeparatorPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SeparatorPrimitive.Root> &
    VariantProps<typeof separatorVariants>
>(
  (
    { className, orientation = "horizontal", decorative = true, ...props },
    ref
  ) => (
    <SeparatorPrimitive.Root
      ref={ref}
      decorative={decorative}
      orientation={orientation}
      className={cn(separatorVariants({ orientation }), className)}
      {...props}
    />
  )
);
Separator.displayName = SeparatorPrimitive.Root.displayName;
