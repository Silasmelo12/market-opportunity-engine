# Feature Specification: Painel Executivo e Visão Geral da Carteira (Investidor10 Style)

**Feature Branch**: `017-overview-dashboard-investidor10`  
**Created**: 2026-10-22  
**Status**: Specified / Ready for Sync & Fixes  
**Input**: Especificação retroativa (Backfill) e alinhamento de requisitos para os 9 pontos de dados da aba Visão Geral, baseada no estilo de referência Investidor10.

---

## User Scenarios & Testing

### User Story 1 - Visão Geral Executiva com Cotações Periódicas Atualizadas (Priority: P1)

Como investidor da B3/Global, quero acessar a aba inicial **"Visão Geral"** e visualizar em tempo real o valor consolidado da minha carteira com base em cotações atualizadas a cada hora (com cache), para saber instantaneamente o patrimônio total, o valor investido, a variação percentual contábil real e o lucro líquido acumulado sem precisar executar simulações pesadas.

**Acceptance Scenarios**:
1. **Given** uma carteira importada (ex: `minha_carteira.csv`), **When** o usuário abre a aba "Visão Geral", **Then** o sistema consulta o endpoint de cotações periódicas (`/api/portfolio/quotes`), obtém o último preço de fechamento/mercado de cada ativo com cache de 1h e calcula:
   - Total Investido = soma(Cotas * Preço Médio)
   - Patrimônio Atual = soma(Cotas * Preço Mercado Atual) + Caixa
   - Variação Contábil (%) = ((Patrimônio Atual - Total Investido) / Total Investido) * 100
   - Lucro Estimado (R$) = Patrimônio Atual - Total Investido
2. **Given** que o ativo `BRKM5` possui preço médio de R$ 7,60 e cotação atual de R$ 5,80, **When** o card "Posições no Lucro" é renderizado, **Then** `BRKM5` é categorizado como posição no prejuízo, refletindo a proporção real (ex: N de 18 no lucro) na barra bi-color (verde/rosa).
3. **Given** o card "Destaques da Carteira", **When** há cotações válidas para os ativos, **Then** o sistema exibe no "Melhor ativo" o ticker com maior rentabilidade positiva (%) e no "Pior ativo" o ticker com menor rentabilidade/maior desvalorização (%), evitando repetir o mesmo ativo em ambos.

---

### User Story 2 - Subnavegação e Gestão de Metas Financeiras (Priority: P2)

Como usuário que planeja sua independência financeira, quero poder configurar minhas metas de patrimônio total (ex: R$ 100.000,00) e renda passiva de FIIs (ex: R$ 30.000,00) com persistência local, e alternar fluidamente entre as visualizações de Resumo, Posições, Patrimônio e Metas.

**Acceptance Scenarios**:
1. **Given** a subnavegação da Visão Geral (`Resumo`, `Posições`, `Patrimônio`, `Metas`), **When** o usuário clica em qualquer uma das abas, **Then** o sistema filtra os blocos correspondentes da tela sem recarregar a página e reajusta as dimensões dos gráficos interativos.
2. **Given** o painel de Metas da Carteira, **When** o usuário clica no botão de edição de metas, **Then** um modal permite informar os valores monetários desejados para a Meta Total e Meta de FIIs, salvando as preferências em `localStorage`.
3. **Given** a seção "Meus Ativos", **When** a página é carregada pela primeira vez, **Then** todos os acordeons de classes (Ações B3, FIIs, BDRs, Macro) iniciam **recolhidos por padrão**, exibindo as colunas de quantidade, preço médio, cotação atual, saldo, rentabilidade (R$ e %), % da carteira atual, % ideal e o badge de recomendação de compra de hoje.

---

### User Story 3 - Suporte Contínuo a Temas e Limpeza de Contexto (Priority: P3)

Como operador do terminal, quero que a interface respeite o contexto operacional, ocultando botões desnecessários na Visão Geral e adaptando perfeitamente todos os gráficos e contrastes visuais nos modos Claro e Escuro.

**Acceptance Scenarios**:
1. **Given** a aba "Visão Geral" ativa, **When** o cabeçalho superior é renderizado, **Then** o seletor global de direção analítica ("Compra", "Venda", "Ambos") é automaticamente ocultado.
2. **Given** a alternância para o Modo Claro (`[data-theme="light"]`), **When** os gráficos `overview-stacked-bar-chart` e `overview-donut-chart` são atualizados, **Then** o fundo dos gráficos migra para branco puro (`#FFFFFF`) e os textos/rótulos para ardósia escura (`#0F172A`), mantendo contraste >= 4.5:1.

---

## Requisitos Funcionais (FR-*)

- **FR-001**: O sistema DEVE disponibilizar o endpoint `POST /api/portfolio/quotes` para retornar as cotações mais recentes dos tickers solicitados com cache em memória de 1 hora.
- **FR-002**: O cálculo do Card 1 (Patrimônio Total) DEVE exibir a variação percentual contábil real com sinal (`+` ou `-`) e duas casas decimais com base no Total Investido.
- **FR-003**: O card de Destaques DEVE identificar estritamente o ativo com melhor e pior rentabilidade percentual a partir de cotações reais de mercado.
- **FR-004**: O seletor `#global-direction-selector` DEVE permanecer oculto quando a aba `tab-overview` estiver ativa.
- **FR-005**: O sistema DEVE permitir ao usuário personalizar e persistir suas Metas Financeiras (Patrimônio e FIIs) através de modal com salvamento em `localStorage`.
- **FR-006**: A tabela "Meus Ativos" DEVE exibir colunas explícitas de Lucro/Prejuízo (R$) e Rentabilidade (%), permitindo ao usuário auditar a performance individual de cada papel.
- **FR-007**: A função `updateChartsTheme` DEVE atualizar dinamicamente o layout dos gráficos Plotly da aba Visão Geral para manter legibilidade completa em Dark e Light Mode.
- **FR-008**: O modelo de importação de carteira DEVE suportar opcionalmente a coluna `Data_Compra` no CSV para cálculo de evolução patrimonial histórica real.

---

## Critérios de Sucesso (SC-*)

- **SC-001**: Carregamento da aba Visão Geral com cotações atualizadas em menos de 500ms para carteiras de até 30 ativos (via cache).
- **SC-002**: Zero divergência contábil entre a soma dos saldos dos ativos na tabela e o patrimônio total reportado no Card 1.
- **SC-003**: 100% de conformidade com o detector `impeccable detect` (0 warnings de contraste, padding ou hierarquia).
