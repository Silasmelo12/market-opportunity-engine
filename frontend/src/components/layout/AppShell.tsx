import * as React from "react";
import { SvgSprite } from "./SvgSprite";
import { Topbar } from "./Topbar";
import { SubnavBar } from "./SubnavBar";
import {
  LoadingOverlay,
  MobileNavigation,
  ToastBanner,
} from "./MobileNavigation";
import { B3ImportDialog } from "@/features/b3-import/B3ImportDialog";
import { NewTransactionDialog } from "@/features/portfolio/NewTransactionDialog";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-canvas text-foreground font-sans antialiased">
      <SvgSprite />
      <Topbar />
      <SubnavBar />
      <main id="app-main-content" className="min-w-0">
        {children}
      </main>
      <B3ImportDialog />
      <NewTransactionDialog />
      <MobileNavigation />
      <ToastBanner />
      <LoadingOverlay />
    </div>
  );
}
