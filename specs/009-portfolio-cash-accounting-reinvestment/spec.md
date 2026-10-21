# Feature Specification: Fluxo de Caixa Realista e Reinvestimento de Vendas no Simulador de Ciclo

**Feature Branch**: `009-portfolio-cash-accounting-reinvestment`  
**Created**: 2026-10-21  
**Status**: Draft  

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reinvestimento de Caixa e Contabilidade de Fluxo de Caixa (Priority: P1)

Como investidor quantitativo, quero que o simulador mantenha uma conta corrente/saldo de caixa real (`cash balance`), de modo que quando um ciclo for liquidado em um sinal de venda, o valor integral da venda (capital principal + lucros acumulados) retorne ao caixa disponível da carteira, e as compras dos ciclos subsequentes utilizem prioritariamente esse saldo de caixa existente antes de exigir qualquer injeção de dinheiro novo do bolso.

**Why this priority**: Evita a distorção de considerar cada compra subsequente como um aporte externo infinito vindo do bolso. Quando o investidor vende uma posição, esse dinheiro não desaparece; ele fica líquido no caixa pronto para financiar as próximas compras da estratégia.

**Independent Test**: Simular uma série com 2 ciclos completos de operações. 
- Ciclo 1 começa com R$ 3.000 de caixa inicial, faz 3 compras de R$ 1.000 e vende tudo a R$ 3.600 (+20% de lucro). O caixa agora tem R$ 3.600.
- Ciclo 2 faz 2 compras de R$ 1.000. Como o caixa já possuía R$ 3.600, essas 2 compras devem ser debitadas do caixa existente, sem exigir nenhum centavo adicional de capital externo.
- Ao final, validar que o "Capital Investido do Bolso" permaneceu em R$ 3.000 (e não R$ 5.000), e a rentabilidade reflete o crescimento real da carteira a partir do capital que de fato saiu do bolso.

**Acceptance Scenarios**:
1. **Given** um ciclo que é encerrado por um sinal de venda, **When** a liquidação é executada a mercado, **Then** 100% dos recursos financeiros gerados pela venda retornam imediatamente ao saldo de caixa livre (`cash`).
2. **Given** um novo sinal de compra (seja início de novo ciclo ou compra adicional em ciclo aberto), **When** a ordem é executada, **Then** o sistema debita prioritariamente o valor do saldo de caixa livre existente. Apenas se o saldo de caixa for insuficiente para cobrir o aporte exigido (`cash < valor_aporte`), a diferença é registrada como injeção de capital novo vindo do bolso (`capital_do_bolso += valor_aporte - cash`).
3. **Given** a curva de evolução patrimonial no gráfico e o KPI de "Capital Investido", **Then** a linha de capital investido reflete estritamente o montante acumulado de dinheiro externo que saiu do bolso do investidor, permanecendo estável quando novas compras são financiadas por lucros/capital de vendas anteriores.
4. **Given** a apuração de retorno global da estratégia, **Then** a rentabilidade percentual é calculada com rigor sobre o capital total que de fato saiu do bolso:
   $$\text{Retorno Global (\%)} = \frac{\text{Patrimônio Final} - \text{Capital do Bolso}}{\text{Capital do Bolso}} \times 100$$

---

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: O motor `simulate_cycle_trade` MUST gerenciar um estado explícito de fluxo de caixa (`cash: float`), inicializado com o capital inicial configurado pelo usuário.
- **FR-002**: Cada execução de compra MUST debitar o valor da compra do saldo de `cash`. Se `cash` for insuficiente para o montante do aporte, a deficiência MUST ser adicionada ao acumulador de capital externo desembolsado do bolso (`total_external_capital`).
- **FR-003**: Cada execução de venda MUST creditar integralmente o valor bruto da liquidação (`shares * sell_price`) de volta no saldo de `cash`.
- **FR-004**: O patrimônio líquido instantâneo em cada barra $i$ MUST ser apurado causalmente como:
  $$\text{Equity}_i = \text{Cash}_i + (\text{Shares}_i \times \text{Close}_i)$$
- **FR-005**: O KPI "Capital Investido" e a série temporal `timeline_invested` no gráfico MUST representar o dinheiro externo efetivamente desembolsado do bolso ao longo do tempo.
- **FR-006**: Cada trade individual no histórico MUST continuar reportando com transparência seu capital alocado naquele ciclo, cotas, preço médio ponderado e retorno da operação individual.
