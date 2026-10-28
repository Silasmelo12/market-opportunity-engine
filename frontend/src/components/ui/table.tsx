import * as React from "react";
import { tv, type VariantProps } from "tailwind-variants";
import { cn } from "@/lib/utils";

export const tableVariants = tv({
  slots: {
    wrapper: "table-scroll w-full overflow-x-auto rounded-md border border-border",
    table: "table-standard w-full border-collapse text-left text-xs",
    thead: "bg-surface-subtle text-[11px] font-semibold uppercase tracking-wider text-muted-foreground border-b border-border",
    tbody: "divide-y divide-border bg-surface",
    tr: "transition-colors hover:bg-surface-hover",
    th: "px-3.5 py-2.5 font-semibold text-muted-foreground whitespace-nowrap",
    td: "px-3.5 py-2 align-middle text-foreground",
  },
  variants: {
    density: {
      compact: {
        th: "px-2.5 py-2 text-[11px]",
        td: "px-2.5 py-1.5 text-xs",
      },
      default: {
        th: "px-3.5 py-2.5 text-[11px]",
        td: "px-3.5 py-2 text-xs",
      },
    },
  },
  defaultVariants: {
    density: "default",
  },
});

export interface ScrollableTableProps
  extends React.TableHTMLAttributes<HTMLTableElement>,
    VariantProps<typeof tableVariants> {
  wrapperClassName?: string;
  showMobileHint?: boolean;
  hintText?: string;
}

export const Table = React.forwardRef<HTMLTableElement, ScrollableTableProps>(
  (
    {
      className,
      wrapperClassName,
      density,
      showMobileHint = false,
      hintText = "Arraste horizontalmente para ver todas as colunas",
      children,
      ...props
    },
    ref
  ) => {
    const { wrapper, table } = tableVariants({ density });
    const handleScrollKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
      if (e.key === "ArrowRight") {
        e.currentTarget.scrollLeft += 48;
      } else if (e.key === "ArrowLeft") {
        e.currentTarget.scrollLeft = Math.max(0, e.currentTarget.scrollLeft - 48);
      }
    };
    return (
      <>
        {showMobileHint && (
          <p className="table-scroll-hint mb-1 text-[11px] text-muted-foreground md:hidden">
            {hintText}
          </p>
        )}
        <div
          className={cn(wrapper(), wrapperClassName)}
          tabIndex={0}
          onKeyDown={handleScrollKeyDown}
        >
          <table ref={ref} className={cn(table(), className)} {...props}>
            {children}
          </table>
        </div>
      </>
    );
  }
);
Table.displayName = "Table";

export const TableHeader = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => {
  const { thead } = tableVariants();
  return <thead ref={ref} className={cn(thead(), className)} {...props} />;
});
TableHeader.displayName = "TableHeader";

export const TableBody = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => {
  const { tbody } = tableVariants();
  return <tbody ref={ref} className={cn(tbody(), className)} {...props} />;
});
TableBody.displayName = "TableBody";

export const TableRow = React.forwardRef<
  HTMLTableRowElement,
  React.HTMLAttributes<HTMLTableRowElement>
>(({ className, ...props }, ref) => {
  const { tr } = tableVariants();
  return <tr ref={ref} className={cn(tr(), className)} {...props} />;
});
TableRow.displayName = "TableRow";

export const TableHead = React.forwardRef<
  HTMLTableCellElement,
  React.ThHTMLAttributes<HTMLTableCellElement>
>(({ className, ...props }, ref) => {
  const { th } = tableVariants();
  return <th ref={ref} className={cn(th(), className)} {...props} />;
});
TableHead.displayName = "TableHead";

export const TableCell = React.forwardRef<
  HTMLTableCellElement,
  React.TdHTMLAttributes<HTMLTableCellElement>
>(({ className, ...props }, ref) => {
  const { td } = tableVariants();
  return <td ref={ref} className={cn(td(), className)} {...props} />;
});
TableCell.displayName = "TableCell";
