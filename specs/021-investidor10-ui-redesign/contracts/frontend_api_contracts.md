# Contratos de API Consumidos pelo Frontend Redesenhado

## 1. `GET /api/portfolio`
- Retorna posições ativas, preço médio, cotação atual e valor acumulado.
- Contrato mantido 100% idêntico. O frontend agrupa por classe (`asset_type` ou heurística de ticker: 11 = FII, 34 = BDR, 3/4 = Ação).

## 2. `GET /api/evolution`
- Retorna série temporal de patrimônio (investido vs ganho de capital).
- Utilizado pelo card "Evolução do Patrimônio" com visual de barras verdes arredondadas.

## 3. `GET /api/b3/dividends` (ou endpoint de proventos consolidado)
- Retorna histórico de proventos recebidos agrupados por mês/ano.
- Utilizado pelo card KPI de proventos e pela aba dedicada de Proventos.
