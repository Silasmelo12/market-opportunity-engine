# Feature Specification: Matemática Genérica Multi-Buy, Tema Claro Integral e Simulação Multi-Timeframe (5m)

**Feature Branch**: `008-multibuy-math-full-light-theme-multitimeframe`  
**Created**: 2026-10-21  
**Status**: Draft  

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rigor Matemático Genérico para Múltiplas Compras (K Sinais) (Priority: P1)

Como investidor ou analista quantitativo, quero que a simulação no modo ciclo de trade calcule de forma 100% precisa o capital total investido e o retorno percentual de cada ciclo e da carteira geral quando ocorrerem $K$ sinais de compra antes de 1 sinal de venda, somando os aportes reais desembolsados do bolso (evitando rentabilidades astronômicas e irreais).

**Why this priority**: Fundamental para a veracidade e credibilidade financeira dos relatórios. Sem isso, retornos distorcidos (como +22.791%) invalidam a confiança do usuário e de recrutadores/investidores.

**Independent Test**: Simular um ativo com aportes de R$ 1.000 por sinal em que ocorram 3 compras (R$ 10, R$ 8, R$ 6) e 1 venda a R$ 10. Validar que o Capital Investido do ciclo é exatamente R$ 3.000, o preço médio ponderado é R$ 7,66 e o retorno do ciclo é rigorosamente +30,5%. No resumo global, o Capital Total Investido deve ser a soma exata de todos os aportes feitos em todos os ciclos.

**Acceptance Scenarios**:
1. **Given** um ciclo com $K$ sinais de compra antes de uma venda, **When** o ciclo é concluído, **Then** o capital investido naquele ciclo é exatamente $\sum_{i=1}^K C_i$, o preço médio ponderado é $\frac{\sum C_i}{\sum Q_i}$ e o retorno percentual da operação é $\frac{P_{\text{venda}} - \text{Preço Médio}}{\text{Preço Médio}} \times 100$.
2. **Given** múltiplos ciclos ao longo do período, **When** o resumo geral do simulador é apurado, **Then** o KPI "Capital Investido" reflete a soma real de todos os aportes desembolsados (ou o capital total de pico alocado), e o retorno global da estratégia reflete com exatidão o lucro líquido sobre o capital real aportado.

---

### User Story 2 - Tema Claro Integral e Consistência Visual em Todo o Sistema (Priority: P1)

Como usuário do terminal, quero que ao ativar o Tema Claro (Light Theme), absolutamente **toda a interface** (sidebar, cabeçalho, inputs, dropdowns, tabelas, cards, modais, acordions e gráficos) comute para uma paleta clara limpa e coerente (estilo fintech slate/white), sem deixar nenhum card ou container preto/escuro residual.

**Why this priority**: Atualmente o tema claro estava atuando primariamente no canvas do gráfico, mantendo blocos do sistema escuros, o que gerava inconsistência estética e quebra visual.

**Independent Test**: Alternar para o Tema Claro e inspecionar todas as abas (Terminal, Radar, Simulador, Playbook), verificando que todos os containers, fundos e textos possuem contraste harmônico sem nenhum bloco com fundo preto desajustado.

**Acceptance Scenarios**:
1. **Given** a aplicação aberta no Tema Claro, **Then** todos os elementos de fundo possuem tons claros (`#F8FAFC` / `#FFFFFF`), bordas sutis (`#E2E8F0`) e textos com legibilidade perfeita (`#0F172A` / `#334155`).
2. **Given** o Tema Claro ativo, **Then** badges semânticos (verde para compra/lucro, vermelho para venda/prejuízo, amarelo para neutro/aviso) adaptam seus fundos para versões suaves com bordas legíveis no fundo branco.

---

### User Story 3 - Simulação e Análise em Múltiplos Tempos Gráficos (Intraday 5m, 15m, 60m) (Priority: P2)

Como trader e analista tático, quero executar o simulador e o terminal em diferentes tempos gráficos (ex.: `5m`, `15m`, `60m`, `1d`), para avaliar o comportamento das estratégias de reversão e múltiplos aportes em horizontes operacionais intradiários.

**Why this priority**: Permite validar estratégias em day trade e swing trade curto, ampliando dramaticamente a utilidade prática do motor quantitativo.

**Independent Test**: Selecionar tempo gráfico de 5 minutos (`5m`) no simulador/terminal e rodar a análise, validando que o motor processa as barras intradiárias causalmente, detecta sinais e executa o backtest multi-buy.

**Acceptance Scenarios**:
1. **Given** o seletor de tempo gráfico no simulador ou terminal, **When** o usuário seleciona `5m` (ou `15m`/`60m`), **Then** o backend carrega os dados históricos intradiários correspondentes e roda o pipeline causal de sinais e simulação.
2. **Given** séries intradiárias de 5m, **Then** o sistema respeita as limitações de janela do provedor de dados de forma transparente, exibindo claramente as datas abrangidas.

---

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: O cálculo de retorno de cada ciclo de trade individual MUST ser rigorosamente derivado do preço médio ponderado das $K$ compras e do preço de liquidação da venda.
- **FR-002**: O KPI geral de "Capital Investido" no simulador MUST refletir o somatório monetário de todos os aportes realizados nas $K$ compras ao longo de todos os ciclos, e o retorno global da estratégia MUST ser calculado sobre este montante real.
- **FR-003**: A alternância para Tema Claro MUST cobrir integralmente 100% dos seletores CSS de cards, sidebars, tabelas, inputs e textos do sistema.
- **FR-004**: O sistema MUST suportar no backend e frontend intervalos intradiários (`5m`, `15m`, `60m`) com sanitização e causalidade estrita.
- **FR-005**: A cada tarefa concluída durante a implementação, um commit git atômico MUST ser efetuado.
