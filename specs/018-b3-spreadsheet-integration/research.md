# Research: B3 Spreadsheet Integration & Portfolio Tracking

## 1. Contexto e Estrutura dos Arquivos da B3

A planilha oficial exportada da Área do Investidor da B3 (`B3/movimentacao-2026-10-22-13-32-52.xlsx`) possui a planilha de nome `Movimentação` com as seguintes características apuradas:
- **Colunas**:
  - `Entrada/Saída`: 'Credito' ou 'Debito'
  - `Data`: data da operação no formato `DD/MM/YYYY`
  - `Movimentação`: Tipo de evento contábil: `Compra`, `Venda`, `Transferência - Liquidação`, `Rendimento`, `Dividendo`, `Juros Sobre Capital Próprio`, `Desdobro`, `Grupamento`, `Direitos de Subscrição`, etc.
  - `Produto`: Ex: `MXRF11 - MAXI RENDA FDO INV IMOB - FII`, `PETR4 - PETROLEO BRASILEIRO S/A PETROBRAS`
  - `Instituição`: Nome da corretora
  - `Quantidade`: Quantidade de cotas ou ações operadas
  - `Preço unitário`: Preço por cota da transação
  - `Valor da Operação`: Valor financeiro total

## 2. Decisões Arquiteturais e Algoritmo de Preço Médio

### Extração do Ticker
O ticker primário é extraído da coluna `Produto` pegando a parte antes do primeiro hífen (`str.split('-')[0].strip()`).
Exemplos:
- `MXRF11 - ...` -> `MXRF11` -> `MXRF11.SA`
- `PETR4 - ...` -> `PETR4` -> `PETR4.SA`
- `M1TA34 - ...` -> `M1TA34` -> `M1TA34.SA`
- Tickers com termo `Futuro` ou sem quantidade não são ações de custódia e são ignorados na carteira à vista.

### Regra Contábil de Preço Médio (Receita Federal)
Para cada ticker, em ordem cronológica ascendente (`Data`):
1. **Compra / Transferência de Entrada**:
   - `Custo_Total_Anterior = Quantidade_Anterior * Preço_Médio_Anterior`
   - `Custo_Novo = Valor_da_Operação` (ou `Quantidade * Preço_Unitário`)
   - `Nova_Quantidade = Quantidade_Anterior + Quantidade`
   - `Novo_Preço_Médio = (Custo_Total_Anterior + Custo_Novo) / Nova_Quantidade`
2. **Venda / Transferência de Saída**:
   - `Nova_Quantidade = max(0, Quantidade_Anterior - Quantidade)`
   - Se `Nova_Quantidade == 0`: `Preço_Médio = 0.0`
   - O preço médio unitário permanece inalterado em vendas parciais.

### Consolidação de Proventos
As movimentações com tipos `Dividendo`, `Juros Sobre Capital Próprio` e `Rendimento` são somadas para compor o Total de Renda Passiva recebida e organizadas em agregações mensais (Ano/Mês) para plotagem de evolução temporal.

## 3. Endpoints e Integração Web SPA
- Criar endpoint `POST /api/b3/parse` e `GET /api/b3/sync-local` para processar a planilha da B3 em disco ou via upload multipart.
- O resultado alimenta o estado da aplicação web `state.portfolioState.holdings` e as métricas da aba **Visão Geral**.
