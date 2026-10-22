# Data Model: Estrutura da Tabela do Radar e Ordenação

## 1. Entities & UI State

### 1.1 RadarSortState
Representa a configuração ativa de ordenação das colunas da tabela:

| Atributo | Tipo | Valores Permitidos | Padrão | Descrição |
|---|---|---|---|---|
| `radarSortField` | `string \| null` | `'historical_n'`, `'historical_win_rate'`, `null` | `null` | Coluna pela qual a tabela está ordenada |
| `radarSortOrder` | `string` | `'desc'`, `'asc'` | `'desc'` | Direção da ordenação (decrescente ou crescente) |

### 1.2 RadarRowSchema (Frontend)
Mapeamento de colunas por linha da tabela:

| Coluna | Campo do Objeto | Formatação / Render | Alinhamento |
|---|---|---|---|
| Ativo | `ticker`, `asset_name` | Botão com Nome Amigável + Ticker mono | Esquerda |
| Dir | `direction` | Pílula circular com `C` ou `V` + title | Centro |
| Estratégia | `strategy_label` | Texto colorido (esmeralda/rosa) | Esquerda |
| Setup | `status_signal` | Texto mono | Esquerda |
| Timing | `timing_category`, `timing_label` | Círculo 12px com brilho e tooltip | Centro |
| Distância | `distance_pct` | Porcentagem colorida (+/-) | Esquerda |
| Qtd Sinais | `historical_n` | Número inteiro mono | Direita / Centro |
| Win Rate | `historical_win_rate` | Percentual formatado (ex: `74.5%`) | Direita / Centro |
