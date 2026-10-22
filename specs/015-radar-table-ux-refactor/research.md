# Research: Refatoração da Tabela do Radar

## 1. Contexto e Objetivos

Esta pesquisa investiga o layout e o comportamento da tabela do **Radar de Oportunidades** em `src/web/index.html` e `src/web/app.js` para entregar uma experiência moderna, limpa e com ordenação interativa de métricas estatísticas:
1. Remoção das colunas Categoria, Preço Atual e Ação.
2. Semáforo em formato de bolinha colorida com tooltip no hover.
3. Indicador de direção compacto ("C" e "V").
4. Separação da métrica histórica em duas colunas ordenáveis (Qtd Sinais e Win Rate).

---

## 2. Decisões de Design e Implementação

### 2.1 Novo Layout de Colunas (8 colunas)
- **Cabeçalho (`index.html`)**:
  ```html
  <table class="w-full text-left text-xs text-gray-300">
    <thead class="bg-fintech-bg/60 text-gray-400 font-semibold uppercase text-[11px] border-b border-fintech-border whitespace-nowrap">
      <tr>
        <th class="px-4 py-3">Ativo</th>
        <th class="px-3 py-3 text-center">Dir</th>
        <th class="px-4 py-3">Estratégia Confirmada</th>
        <th class="px-4 py-3">Status do Setup</th>
        <th class="px-3 py-3 text-center">Timing</th>
        <th class="px-4 py-3">Distância (%)</th>
        <th class="px-4 py-3 cursor-pointer hover:text-white select-none" id="th-sort-n">
          <div class="flex items-center gap-1">
            <span>Qtd Sinais</span>
            <span id="sort-icon-n" class="text-[10px] text-gray-500">↕</span>
          </div>
        </th>
        <th class="px-4 py-3 cursor-pointer hover:text-white select-none" id="th-sort-winrate">
          <div class="flex items-center gap-1">
            <span>Win Rate (%)</span>
            <span id="sort-icon-winrate" class="text-[10px] text-gray-500">↕</span>
          </div>
        </th>
      </tr>
    </thead>
  ```
- **Fallback Row**: `colspan="8"` quando não houver itens encontrados.

### 2.2 Badge de Direção Compacto
- **Implementação**:
  - Compra:
    ```html
    <span class="inline-flex items-center justify-center w-6 h-6 rounded-full font-bold text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/40" title="Compra (Fundo)">C</span>
    ```
  - Venda:
    ```html
    <span class="inline-flex items-center justify-center w-6 h-6 rounded-full font-bold text-xs bg-rose-500/20 text-rose-400 border border-rose-500/40" title="Venda (Topo)">V</span>
    ```

### 2.3 Semáforo Minimalista com Bolinha e Tooltip
- **Cores & Efeitos Visuais**:
  - `IDEAL`: `<span class="inline-block w-3 h-3 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)] cursor-help" title="${item.timing_label}"></span>`
  - `EXTENDED`: `<span class="inline-block w-3 h-3 rounded-full bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)] cursor-help" title="${item.timing_label}"></span>`
  - `LATE`: `<span class="inline-block w-3 h-3 rounded-full bg-rose-400 shadow-[0_0_8px_rgba(251,113,133,0.6)] cursor-help" title="${item.timing_label}"></span>`

### 2.4 Ordenação Interativa no Cliente (0ms Latência)
- **Estado no `appState`**:
  - `radarSortField`: `null` | `'historical_n'` | `'historical_win_rate'`
  - `radarSortOrder`: `'desc'` | `'asc'`
- **Comportamento**:
  - Ao clicar no cabeçalho: se já estiver ordenando pelo mesmo campo, inverte a direção (`desc` $\leftrightarrow$ `asc`); se for novo campo, inicia em `desc`.
  - Reordena o array `filtered` antes de renderizar as linhas.
  - Atualiza os ícones `sort-icon-n` e `sort-icon-winrate` com $\blacktriangledown$ (descendente) ou $\blacktriangle$ (ascendente).
