import * as React from "react";
import { AppProviders } from "./providers";
import { AppShell } from "@/components/layout/AppShell";
import { OverviewPage } from "@/features/overview/OverviewPage";
import { PortfolioPage } from "@/features/portfolio/PortfolioPage";
import { DividendsPage } from "@/features/dividends/DividendsPage";
import { EvolutionPage } from "@/features/evolution/EvolutionPage";
import { RadarPage } from "@/features/radar/RadarPage";
import { ChartPage } from "@/features/chart/ChartPage";
import { SimulatorPage } from "@/features/simulator/SimulatorPage";
import { PlaybookPage } from "@/features/playbook/PlaybookPage";

export function App() {
  return (
    <AppProviders>
      <AppShell>
        <OverviewPage />
        <PortfolioPage />
        <DividendsPage />
        <EvolutionPage />
        <RadarPage />
        <ChartPage />
        <SimulatorPage />
        <PlaybookPage />
      </AppShell>
    </AppProviders>
  );
}

export default App;
