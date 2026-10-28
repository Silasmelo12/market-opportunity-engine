import * as React from "react";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { tv } from "tailwind-variants";
import { cn } from "@/lib/utils";

export const dialogVariants = tv({
  slots: {
    overlay: "fixed inset-0 z-50 bg-canvas/80 backdrop-blur-sm transition-opacity",
    content: [
      "fixed left-1/2 top-1/2 z-50 w-full max-w-2xl -translate-x-1/2 -translate-y-1/2",
      "rounded-xl border border-border bg-surface p-6 text-foreground shadow-lg",
      "focus-visible:outline-none",
    ],
    header: "flex items-center justify-between border-b border-border pb-3",
    title: "font-sans text-base font-bold text-foreground",
    description: "text-xs text-muted-foreground",
    footer: "mt-4 flex items-center justify-end gap-2 border-t border-border pt-3",
  },
});

export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;
export const DialogPortal = DialogPrimitive.Portal;
export const DialogClose = DialogPrimitive.Close;

export const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => {
  const { overlay } = dialogVariants();
  return (
    <DialogPrimitive.Overlay
      ref={ref}
      className={cn(overlay(), className)}
      {...props}
    />
  );
});
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName;

export const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => {
  const { content } = dialogVariants();
  return (
    <DialogPortal>
      <DialogOverlay />
      <DialogPrimitive.Content
        ref={ref}
        className={cn(content(), className)}
        {...props}
      >
        {children}
      </DialogPrimitive.Content>
    </DialogPortal>
  );
});
DialogContent.displayName = DialogPrimitive.Content.displayName;

export function DialogHeader({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  const { header } = dialogVariants();
  return <div className={cn(header(), className)} {...props} />;
}

export const DialogTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => {
  const { title } = dialogVariants();
  return (
    <DialogPrimitive.Title
      ref={ref}
      className={cn(title(), className)}
      {...props}
    />
  );
});
DialogTitle.displayName = DialogPrimitive.Title.displayName;

export const DialogDescription = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => {
  const { description } = dialogVariants();
  return (
    <DialogPrimitive.Description
      ref={ref}
      className={cn(description(), className)}
      {...props}
    />
  );
});
DialogDescription.displayName = DialogPrimitive.Description.displayName;

export function DialogFooter({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  const { footer } = dialogVariants();
  return <div className={cn(footer(), className)} {...props} />;
}
