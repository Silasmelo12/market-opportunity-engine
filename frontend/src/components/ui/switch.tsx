import * as React from "react";
import * as SwitchPrimitives from "@radix-ui/react-switch";
import { tv } from "tailwind-variants";
import { cn } from "@/lib/utils";

export const switchVariants = tv({
  slots: {
    root: [
      "peer inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent shadow-sm transition-colors",
      "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-border-focus",
      "disabled:cursor-not-allowed disabled:opacity-50",
      "data-[state=checked]:bg-primary data-[state=unchecked]:bg-surface-subtle",
    ],
    thumb: [
      "pointer-events-none block h-4 w-4 rounded-full bg-surface shadow-sm ring-0 transition-transform",
      "data-[state=checked]:translate-x-4 data-[state=unchecked]:translate-x-0",
    ],
  },
});

export const Switch = React.forwardRef<
  React.ElementRef<typeof SwitchPrimitives.Root>,
  React.ComponentPropsWithoutRef<typeof SwitchPrimitives.Root>
>(({ className, ...props }, ref) => {
  const { root, thumb } = switchVariants();
  return (
    <SwitchPrimitives.Root
      className={cn(root(), className)}
      {...props}
      ref={ref}
    >
      <SwitchPrimitives.Thumb className={thumb()} />
    </SwitchPrimitives.Root>
  );
});
Switch.displayName = SwitchPrimitives.Root.displayName;
