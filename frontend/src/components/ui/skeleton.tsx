import * as React from "react";
import { tv, type VariantProps } from "tailwind-variants";
import { cn } from "@/lib/utils";

export const skeletonVariants = tv({
  base: "state-loading animate-pulse rounded-md bg-surface-subtle",
  variants: {
    shape: {
      rect: "rounded-md",
      pill: "rounded-full",
    },
  },
  defaultVariants: {
    shape: "rect",
  },
});

export interface SkeletonProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof skeletonVariants> {}

export function Skeleton({ className, shape, ...props }: SkeletonProps) {
  return (
    <div className={cn(skeletonVariants({ shape }), className)} {...props} />
  );
}
