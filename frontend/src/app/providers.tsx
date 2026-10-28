import * as React from "react";
import { AppProvider } from "@/state/app-context";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return <AppProvider>{children}</AppProvider>;
}
