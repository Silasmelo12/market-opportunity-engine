import * as React from "react";
import { SvgSprite } from "./SvgSprite";
import { Topbar } from "./Topbar";
import { AppSidebar } from "./AppSidebar";
import {
  LoadingOverlay,
  MobileNavigation,
  ToastBanner,
} from "./MobileNavigation";
import { B3ImportDialog } from "@/features/b3-import/B3ImportDialog";
import { NewTransactionDialog } from "@/features/portfolio/NewTransactionDialog";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-canvas text-foreground font-sans antialiased flex flex-col">
      <SvgSprite />
      <Topbar />
      <div className="flex-1 flex min-w-0">
        <AppSidebar />
        <main id="app-main-content" className="flex-1 min-w-0">
          {children}
        </main>
      </div>
      <B3ImportDialog />
      <NewTransactionDialog />
      <MobileNavigation />
      <ToastBanner />
      <LoadingOverlay />
    </div>
  );
}
