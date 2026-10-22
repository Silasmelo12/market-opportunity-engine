# Research: Correção de Exibição dos Novos Indicadores na Aba Gráfico, Filtragem Inicial por Direção e Persistência de Aba Ativa ao Atualizar Página

## 1. Contexto e Objetivos

Esta pesquisa investiga os pontos exatos de intervenção no frontend web (`src/web/index.html` e `src/web/app.js`) para sanar 3 lacunas de experiência do usuário:
1. Inclusão dos 10 novos indicadores quantitativos na barra lateral esquerda da aba Gráfico (`#tab-terminal`).
2. Garantia de que a filtragem por direção (`BUY` / `SELL` / `BOTH`) seja aplicada imediatamente na inicialização da página e ao alternar para a aba Gráfico.
3. Persistência da aba ativa ao atualizar a página com F5 / recarregar o navegador.

---

## 2. Decisões Técnicas

### 2.1 Adição dos Indicadores Quantitativos na Barra Lateral do Gráfico
- **Decisão**: Criar dois novos acordeões `.strategy-group-wrapper` em `src/web/index.html` dentro do container `#strategy-accordion-container`:
  - `data-direction="BUY"` com id de acordeão `acc-quant-buy` ("Indicadores Quantitativos de Fundo (10)")
  - `data-direction="SELL"` com id de acordeão `acc-quant-sell` ("Indicadores Quantitativos de Topo (10)")
- **Mapeamento de Checkboxes**:
  - Cada checkbox `.strategy-cb` terá `data-id` idêntico ao identificador de estratégia ou sub-estratégia correspondente (`bollinger_close_in`, `keltner_squeeze`, `zscore_extreme`, `rsi_divergence`, `stochastic_extreme`, `macd_momentum`, `vwap_bands`, `mfi_extreme`, `volume_climax_vsa`, `supertrend_trailing`).
- **Aliases em `app.js`**:
  - No `STRATEGY_ALIASES`, mapear cada ID pai para suas variantes técnicas (`bb_reversal_buy`, `squeeze_breakout_buy`, etc.) permitindo que marcar o checkbox ative instantaneamente os sinais gerados na análise.

### 2.2 Filtragem Inicial por Direção na Sidebar
- **Decisão**: Extrair a lógica de filtragem dos wrappers para uma função reutilizável:
  ```javascript
  function updateSidebarDirectionFilter() {
    const dir = state.activeDirection;
    document.querySelectorAll('.strategy-group-wrapper').forEach(wrapper => {
      const wrapDir = wrapper.getAttribute('data-direction');
      if (dir === 'BOTH' || wrapDir === dir) {
        wrapper.classList.remove('hidden');
      } else {
        wrapper.classList.add('hidden');
      }
    });
  }
  ```
- **Pontos de Invocação**:
  1. Durante o `DOMContentLoaded` após configurar o seletor de direção.
  2. Em `switchTab(tabId)` sempre que o usuário alternar para `tab-terminal`.
  3. No clique dos botões do `#global-direction-selector`.

### 2.3 Persistência da Aba Ativa (F5 / Reload)
- **Decisão**: Utilizar uma estratégia híbrida robusta com `window.location.hash` e fallback para `localStorage`:
  - Mapeamento bidirecional:
    - `#radar` $\leftrightarrow$ `tab-radar`
    - `#terminal` / `#grafico` $\leftrightarrow$ `tab-terminal`
    - `#simulator` $\leftrightarrow$ `tab-simulator`
    - `#playbook` $\leftrightarrow$ `tab-playbook`
  - Em `switchTab(tabId)`:
    - Atualizar `window.location.hash = hashName;`
    - Salvar `localStorage.setItem('market_engine_active_tab', tabId);`
  - Na inicialização (`DOMContentLoaded`):
    - Obter a hash atual (`window.location.hash`). Se mapear para uma aba válida, chavear para ela.
    - Caso contrário, ler `localStorage.getItem('market_engine_active_tab')`.
    - Se nenhum for válido, fallback para `tab-radar`.
- **Garantia de Renderização Gráfica**:
  - Se a aba restaurada for `tab-terminal`, garantir que `loadAnalysisData()` e `resizeChartResponsive()` sejam disparados com pequeno atraso via `requestAnimationFrame` ou `setTimeout` de 50ms para que o canvas do TradingView receba as dimensões reais do container visível.
