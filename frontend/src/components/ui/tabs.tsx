import * as React from "react";
import * as TabsPrimitive from "@radix-ui/react-tabs";
import { tv, type VariantProps } from "tailwind-variants";
import { cn } from "@/lib/utils";

export const tabsVariants = tv({
  slots: {
    list: "segmented inline-flex items-center justify-center rounded-md bg-surface-subtle p-1 text-muted-foreground border border-border",
    trigger: [
      "inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-xs font-semibold transition-all",
      "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-border-focus",
      "disabled:pointer-events-none disabled:opacity-50",
      "data-[state=active]:bg-surface data-[state=active]:text-foreground data-[state=active]:shadow-sm",
    ],
    content: "mt-2 focus-visible:outline-none",
  },
  variants: {
    density: {
      compact: {
        list: "p-0.5",
        trigger: "px-2.5 py-1 text-[11px]",
      },
      default: {
        list: "p-1",
        trigger: "px-3 py-1.5 text-xs",
      },
    },
  },
  defaultVariants: {
    density: "default",
  },
});

export const Tabs = TabsPrimitive.Root;

export const TabsList = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.List>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.List> &
    VariantProps<typeof tabsVariants>
>(({ className, density, ...props }, ref) => {
  const { list } = tabsVariants({ density });
  return (
    <TabsPrimitive.List
      ref={ref}
      className={cn(list(), className)}
      {...props}
    />
  );
});
TabsList.displayName = TabsPrimitive.List.displayName;

export const TabsTrigger = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger> &
    VariantProps<typeof tabsVariants>
>(({ className, density, ...props }, ref) => {
  const { trigger } = tabsVariants({ density });
  return (
    <TabsPrimitive.Trigger
      ref={ref}
      className={cn(trigger(), className)}
      {...props}
    />
  );
});
TabsTrigger.displayName = TabsPrimitive.Trigger.displayName;

export const TabsContent = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content>
>(({ className, ...props }, ref) => {
  const { content } = tabsVariants();
  return (
    <TabsPrimitive.Content
      ref={ref}
      className={cn(content(), className)}
      {...props}
    />
  );
});
TabsContent.displayName = TabsPrimitive.Content.displayName;
