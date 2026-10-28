import * as React from "react";
import * as ScrollAreaPrimitive from "@radix-ui/react-scroll-area";
import { tv } from "tailwind-variants";
import { cn } from "@/lib/utils";

export const scrollAreaVariants = tv({
  slots: {
    root: "relative overflow-hidden",
    viewport: "h-full w-full rounded-[inherit]",
    scrollbar: "flex touch-none select-none transition-colors p-0.5",
    thumb: "relative flex-1 rounded-full bg-border-strong",
  },
});

export const ScrollArea = React.forwardRef<
  React.ElementRef<typeof ScrollAreaPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof ScrollAreaPrimitive.Root>
>(({ className, children, ...props }, ref) => {
  const { root, viewport } = scrollAreaVariants();
  return (
    <ScrollAreaPrimitive.Root
      ref={ref}
      className={cn(root(), className)}
      {...props}
    >
      <ScrollAreaPrimitive.Viewport className={viewport()}>
        {children}
      </ScrollAreaPrimitive.Viewport>
      <ScrollBar />
      <ScrollAreaPrimitive.Corner />
    </ScrollAreaPrimitive.Root>
  );
});
ScrollArea.displayName = ScrollAreaPrimitive.Root.displayName;

export const ScrollBar = React.forwardRef<
  React.ElementRef<typeof ScrollAreaPrimitive.ScrollAreaScrollbar>,
  React.ComponentPropsWithoutRef<typeof ScrollAreaPrimitive.ScrollAreaScrollbar>
>(({ className, orientation = "vertical", ...props }, ref) => {
  const { scrollbar, thumb } = scrollAreaVariants();
  return (
    <ScrollAreaPrimitive.ScrollAreaScrollbar
      ref={ref}
      orientation={orientation}
      className={cn(
        scrollbar(),
        orientation === "vertical" && "h-full w-2 border-l border-l-transparent",
        orientation === "horizontal" && "h-2 flex-col border-t border-t-transparent",
        className
      )}
      {...props}
    >
      <ScrollAreaPrimitive.ScrollAreaThumb className={thumb()} />
    </ScrollAreaPrimitive.ScrollAreaScrollbar>
  );
});
ScrollBar.displayName = ScrollAreaPrimitive.ScrollAreaScrollbar.displayName;
