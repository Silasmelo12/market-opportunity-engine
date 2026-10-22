# Contract: Radar Table Layout & Sorting Contract

## 1. Contrato da Tabela do Radar

A tabela `#radar-table` deve manter rigorosamente o alinhamento de 8 colunas entre `<thead>` e `<tbody>`:

### 1.1 Colunas do Cabeçalho (`<thead>`)
1. `Ativo`
2. `Dir` (Centralizado)
3. `Estratégia Confirmada`
4. `Status do Setup`
5. `Timing` (Centralizado)
6. `Distância (%)`
7. `Qtd Sinais` (Interativo / Ordenável: `#th-sort-n`)
8. `Win Rate (%)` (Interativo / Ordenável: `#th-sort-winrate`)

### 1.2 Mensagens de Estado Vazio
Linhas com `colspan="8"` quando não houver registros.

### 1.3 Comportamento de Ordenação Clicável
- Ao clicar em `#th-sort-n`:
  - Ordena por `historical_n`.
  - Exibe indicador $\blacktriangledown$ (maior para menor) ou $\blacktriangle$ (menor para maior).
- Ao clicar em `#th-sort-winrate`:
  - Ordena por `historical_win_rate`.
  - Exibe indicador $\blacktriangledown$ ou $\blacktriangle$.
