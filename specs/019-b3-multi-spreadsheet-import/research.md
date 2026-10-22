# Research: B3 Multi-Spreadsheet & Negociação Support

## 1. Identificação dos Tipos de Planilha da B3

A B3 exporta relatórios com cabeçalhos e estruturas bem definidas:

1. **Planilha de Movimentação**:
   - Nome da aba: normalmente `Movimentação` ou similar.
   - Colunas essenciais: `Entrada/Saída`, `Data`, `Movimentação`, `Produto`, `Quantidade`, `Preço unitário`, `Valor da Operação`.
   - Propósito: Histórico cronológico de lançamentos e fonte primária de proventos (Dividendos, JCP, Rendimentos).

2. **Planilha de Negociação - Resumo**:
   - Nome da aba: `Negociação - Resumo`.
   - Colunas essenciais: `Código de Negociação`, `Quantidade (Compra)`, `Quantidade (Venda)`, `Quantidade (Líquida)`, `Preço Médio (Compra)`, `Preço Médio (Venda)`.
   - Propósito: Resumo consolidado de ordens de pregão no período. `Quantidade (Líquida) > 0` representa posição comprada com seu respectivo `Preço Médio (Compra)`.

3. **CSV Legado de Carteira**:
   - Formato simples: `Ticker, Quantidade, Preço Médio`.

## 2. Estratégia de Mesclagem de Múltiplos Arquivos

Quando o usuário seleciona 2 ou mais planilhas:
- Se houver múltiplas planilhas de **Movimentação** (ex: extratos de períodos complementares), concatenar e reordenar cronologicamente por `Data`, apurando o Preço Médio contínuo e somando todos os proventos.
- Se houver planilhas de **Negociação** e **Movimentação** enviadas juntas:
  - Os proventos são extraídos das movimentações.
  - Para posições: se o usuário enviar uma planilha de Movimentação completa, ela dita o histórico contábil. Se a movimentação for de período recente/parcial sem as compras originais, as posições líquidas da planilha de Negociação preenchem ou ajustam a custódia com o Preço Médio oficial da B3.
  - Tickers com sufixo fracionário (ex: `AZTE3F`) têm a letra `F` removida na normalização para agrupar com o ticker padrão (`AZTE3.SA`).
  - Tickers de mercado futuro sem posição física (ex: `WINQ26`, `Futuro`) são desconsiderados na carteira à vista.

## 3. Arquitetura da Interface Web (Pronta para Produção)
- O input `#portfolio-csv-file-input` terá o atributo `multiple="multiple"`.
- O botão "Sincronizar B3" (`#btn-portfolio-sync-b3`) é removido, deixando a interface limpa e dependente apenas dos uploads enviados pelo usuário.
- O endpoint `/api/b3/parse` passará a aceitar `List[UploadFile]` e processará todos os arquivos em um único lote.
