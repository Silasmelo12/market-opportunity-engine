# Data Model & UI State: Redesign Estilo Investidor10

## 1. Estado da Interface no Frontend (Client State)

```typescript
interface DashboardState {
  activeTab: 'resumo' | 'posicoes' | 'proventos' | 'patrimonio' | 'radar' | 'tradingview';
  portfolioSummary: {
    totalPatrimonio: number;
    totalInvestido: number;
    lucroTotal: number;
    lucroPercent: number;
    proventos12M: number;
    proventosMediaMensal: number;
    posicoesNoLucro: number;
    totalPosicoes: number;
  };
  assetGroups: {
    [category: string]: { // 'Ações', 'FIIs', 'BDRs', 'Cripto'
      categoryName: string;
      totalValue: number;
      variationPercent: number;
      actualPercent: number;
      idealPercent: number;
      collapsed: boolean;
      items: AssetItem[];
    };
  };
  filterPeriod: '1M' | '6M' | '12M' | 'ALL';
  proventosView: 'mensal' | 'anual';
}

interface AssetItem {
  ticker: string;
  name: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  totalValue: number;
  profitPercent: number;
  timingStatus: string; // 'Fundo 2x2 Detectado', 'Neutro', etc.
  score: number;        // Nota (ex: 10)
  recommendation: 'Comprar' | 'Aguardar' | 'Vender';
}
```

## 2. Contratos de Armazenamento Local (`localStorage`)

| Chave | Tipo | Descrição |
| :--- | :--- | :--- |
| `mo_active_tab` | `string` | Aba ativa atual do usuário (padrão: `'resumo'`) |
| `mo_collapsed_categories` | `string[]` | Array com identificadores das categorias recolhidas |
| `mo_proventos_view` | `'mensal' \| 'anual'` | Modo de visualização do gráfico de dividendos |
