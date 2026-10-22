# Feature Specification: Gestor, Consultor de Rebalanceamento e Simulador Multiativos de Carteira

**Feature Branch**: `016-portfolio-manager-simulator`

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "Criar uma nova aba principal Carteira (Gestor, Rebalanceador e Simulador Multiativos de Carteira) no terminal web e novos endpoints na API FastAPI (/api/portfolio/advise e /api/portfolio/simulate). O sistema deve permitir ao usuario informar seu caixa disponivel (ex: R$ 10.000,00) e suas posicoes atuais (ticker, quantidade de cotas e preco medio, com persistencia em localStorage), alem de selecionar o universo alvo de ativos (Destaques, Acoes Brasil, FIIs Brasil, Acoes EUA, Criptomoedas ou lista personalizada de tickers), tempo grafico, periodo e limite maximo de concentracao por ativo (ex: 20% ou 25% do patrimonio). Para cada ativo do universo, o motor quantitativo deve identificar automaticamente o par de estrategias Campeao (Compra + Venda com melhor resultado historico no ativo) e calcular um Score de Potencial (0 a 100) combinando Win Rate, Retorno Esperado, Profit Factor e status de Timing (priorizando sinais em zona IDEAL). O modulo deve operar em duas frentes integradas: (1) Consultor de Rebalanceamento Hoje (Plano de Acao Atual), gerando recomendacoes acionaveis e detalhadas com acao (COMPRAR, VENDER TOTAL, VENDER PARCIAL / REBALANCEAR, ROTACIONAR ou MANTER), estrategia campea acionada, Score de Potencial, preco de referencia, quantidade exata de cotas, valor financeiro em R$ e peso atual vs. peso alvo na carteira; e (2) Simulador Historico de Carteira Multiativos (Backtest Causal Zero Look-Ahead Bias), simulando barra a barra a alocacao dinamica do capital inicial (ex: R$ 10k) proporcionalmente ao Score de Potencial (respeitando o teto por ativo) e executando 3 regras de saida/rebalanceamento: (a) venda de 100% da posicao no sinal de Venda (Topo) da estrategia campea do ativo, (b) venda parcial de rebalanceamento quando a posicao ultrapassar o teto maximo + banda de tolerancia, e (c) rotacao tatica de capital quando nao houver caixa livre e surgir um ativo com sinal de Compra em Timing IDEAL e Score de Potencial significativamente superior a uma posicao estagnada na carteira. A interface deve exibir KPIs institucionais da carteira (Patrimonio Final, Lucro Liquido, Retorno %, Alfa vs. Buy & Hold Equal-Weight da cesta, Max Drawdown %, Win Rate e Total de Rotacoes), grafico interativo de evolucao patrimonial e distribuicao de ativos (Plotly.js compativel com Light/Dark Mode) e tabela completa de historico de trades e rebalanceamentos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultor de Rebalanceamento Hoje & Plano de Ação Acionável (Priority: P1)

Como investidor com um capital disponível (ex: R$ 10.000,00 em caixa e/ou posições já abertas em ativos), quero informar minha carteira atual na nova aba principal **"Carteira"** e receber instantaneamente um **Plano de Ação de Hoje** que me diga o que comprar, quando/a que preço comprar, quanto comprar (em valor financeiro e quantidade de cotas), o que vender, quanto vender e como rebalancear minha carteira visando os ativos com maior potencial de valorização segundo as estratégias campeãs de cada ativo.

**Why this priority**: Resolve diretamente a dor principal do investidor na tomada de decisão prática ("tenho R$ 10k ou uma carteira em andamento, o que faço agora?"), transformando os motores estatísticos individuais do sistema em recomendações de alocação de portfólio completas e prontas para execução.

**Independent Test**: Acessar a aba "Carteira", informar R$ 10.000,00 de caixa (ou adicionar 2 ativos em carteira + caixa), escolher o universo "Destaques" ou "Ações Brasil", clicar em "Analisar & Rebalancear Carteira" e verificar a geração da boleta/tabela de ordens (`COMPRAR`, `VENDER TOTAL`, `VENDER PARCIAL / REBALANCEAR`, `ROTACIONAR`, `MANTER`) com estratégia campeã, Score de Potencial (0–100), quantidades, valores em R$ e pesos atuais vs. pesos-alvo somando no máximo 100% do patrimônio.

**Acceptance Scenarios**:

1. **Given** que o investidor possui R$ 10.000,00 100% em caixa e nenhuma posição aberta, **When** solicita a análise da carteira para um universo alvo (ex: "Destaques"), **Then** o sistema identifica os ativos com sinal de compra ativo em melhor Timing (`IDEAL` prioritariamente), ranqueia-os pelo Score de Potencial (0–100) da estratégia campeã de cada ativo e recomenda ordens `COMPRAR` proporcionais ao Score, respeitando o limite máximo de concentração por ativo (ex: 25% = máx. R$ 2.500,00 por ativo) e exibindo preço de referência, cotas e valor financeiro.
2. **Given** que o investidor já possui um ativo em carteira cujo par de estratégia campeã acaba de confirmar um sinal de Venda (Topo), **When** o plano de rebalanceamento é gerado, **Then** o sistema emite uma recomendação `VENDER TOTAL` (100% das cotas daquele ativo), liberando o montante financeiro correspondente para o caixa disponível ou para realocação imediata em novas oportunidades de compra.
3. **Given** que um ativo em carteira valorizou fortemente e seu peso atual ultrapassou o teto máximo configurado mais a banda de tolerância (ex: teto de 25% + banda de 5% = acima de 30% do patrimônio total), **When** o plano de rebalanceamento é calculado, **Then** o sistema emite uma recomendação `VENDER PARCIAL / REBALANCEAR` indicando a quantidade exata de cotas e valor a vender para reconduzir o ativo ao seu peso-alvo.
4. **Given** que o investidor está com o caixa próximo de zero e todas as posições preenchidas, mas surge no universo alvo um novo ativo em Timing `IDEAL` com Score de Potencial significativamente superior (pelo menos +15 pontos acima) a um ativo estagnado na carteira atual, **When** a análise é executada, **Then** o sistema emite uma recomendação pareada `ROTACIONAR` (venda do ativo de menor potencial/estagnado e compra do novo ativo de alto potencial), explicando o diferencial de Score e a estratégia acionada.
5. **Given** que o usuário cadastra ou edita seu caixa e suas posições atuais (Ticker, Quantidade, Preço Médio), **When** recarrega a página ou alterna entre abas, **Then** os dados da carteira permanecem salvos localmente no navegador do usuário.

---

### User Story 2 - Simulador Histórico Multiativos de Carteira com Rebalanceamento Dinâmico (Priority: P2)

Como investidor ou analista quantitativo, quero simular historicamente (backtest causal sem *look-ahead bias*) como o sistema teria gerenciado um capital inicial (ex: R$ 10.000,00) ao longo do tempo dentro do universo selecionado, comprando automaticamente os ativos com melhor Score de Potencial em suas estratégias campeãs, vendendo nos topos e rebalanceando a carteira nos momentos oportunos.

**Why this priority**: Comprova estatisticamente a eficácia das regras de alocação, dimensionamento e rotação de carteira no longo prazo, permitindo comparar se a gestão dinâmica supera a simples manutenção passiva (*Buy & Hold Equal-Weight*) dos mesmos ativos.

**Independent Test**: Configurar R$ 10.000,00 de capital inicial, selecionar o universo "Destaques", período "2y" e tempo gráfico "1d", executar a simulação histórica da carteira e validar a exibição dos KPIs consolidados, da curva diária de evolução patrimonial (Carteira Dinâmica vs. Buy & Hold da Cesta vs. Capital Investido) e do histórico cronológico de todas as compras, vendas e rebalanceamentos.

**Acceptance Scenarios**:

1. **Given** um capital inicial (ex: R$ 10.000,00), universo de ativos, intervalo e período selecionados, **When** o usuário executa a simulação histórica da carteira, **Then** o motor processa barra a barra (estritamente sem viés de antecipação temporal, executando ordens na abertura da barra seguinte à confirmação do sinal) alocando o caixa nos ativos com sinal de compra confirmado segundo a prioridade do Score de Potencial e o teto máximo por ativo.
2. **Given** uma simulação histórica em andamento com posições abertas em múltiplos ativos, **When** qualquer ativo em carteira confirma um sinal de venda da sua estratégia campeã, ultrapassa a banda de peso máximo ou sofre rotação tática para uma oportunidade de Score superior, **Then** o motor registra o evento no log histórico (data, ativo, tipo de operação, estratégia, preço, cotas, valor, lucro/prejuízo realizzato e peso antes/depois) e atualiza imediatamente o saldo em caixa para reinvestimento.
3. **Given** a conclusão do backtest multiativos, **When** os resultados são exibidos na tela, **Then** o usuário visualiza os cards de KPIs institucionais: Patrimônio Final, Lucro Líquido (R$), Retorno Global (%), Retorno Buy & Hold da Cesta (%) e Alfa Gerado (%), Max Drawdown da Carteira (%), Taxa de Acerto (Win Rate %) das operações fechadas e Total de Operações/Rotações realizadas.

---

### User Story 3 - Visualização Gráfica de Evolução Patrimonial, Alocação de Ativos e Ergonomia Temática (Priority: P3)

Como usuário do terminal, quero visualizar gráficos interativos da evolução do patrimônio da minha carteira comparada ao benchmark e a distribuição percentual atual/alvo por ativo, com suporte nativo aos temas Claro e Escuro e navegação fluida na barra principal do sistema.

**Why this priority**: Entrega clareza visual imediata sobre o risco/retorno histórico da carteira e a exposição atual por ativo, mantendo o padrão executivo institucional do terminal.

**Independent Test**: Alternar para a aba "Carteira", rodar uma análise/simulação, verificar a renderização do gráfico de evolução patrimonial e do gráfico/barra de composição da carteira por ativo, e clicar no botão de alternância de tema (Claro/Escuro) constatando adaptação cromática imediata sem perda de estado.

**Acceptance Scenarios**:

1. **Given** o cabeçalho principal do terminal, **When** o usuário visualiza a navegação superior, **Then** a 5ª aba principal **"Carteira"** está disponível ao lado de Radar, Gráfico, Simulador e Playbook, ocultando contextualmente o seletor global de direção (Compra/Venda/Ambos) quando ativa.
2. **Given** uma simulação e análise de carteira concluídas, **When** o usuário inspeciona a área visual da aba "Carteira", **Then** são exibidos o gráfico comparativo de evolução patrimonial (Curva da Carteira Gerenciada, Curva Buy & Hold da Cesta e Linha de Capital Investido/Caixa) e a visualização de distribuição de pesos por ativo (incluindo percentual em Caixa).
3. **Given** os gráficos e tabelas renderizados na aba "Carteira", **When** o usuário alterna entre Modo Escuro e Modo Claro, **Then** todas as cores de superfície, textos, badges de ordens e eixos dos gráficos se adaptam instantaneamente ao tema ativo.

---

### Edge Cases

- **Nenhum Ativo com Sinal de Compra Ativo Hoje**: Se no momento atual nenhum ativo do universo alvo estiver com sinal de compra válido (ou todos estiverem em Timing `LATE` / em tendência de queda sem fundo confirmado), o Consultor de Rebalanceamento NÃO deve forçar compras; deve recomendar manter a parcela correspondente em **Caixa (Liquidez)** aguardando oportunidade ideal.
- **Capital Insuficiente ou Ativos com Lote/Cota Unitária Inteira vs. Fracionária**: Para ações e FIIs brasileiros (`.SA`), o cálculo de quantidade a comprar/vender deve arredondar para números inteiros de cotas ($\ge 1$ cota) sem jamais exceder o caixa disponível; para Criptomoedas (`-USD`) e ativos que permitem frações na simulação, suportar até 4 casas decimais. Se o valor alocado a um ativo for menor que o preço de 1 cota inteira (em ativos inteiros), o saldo permanece em caixa ou é redistribuído.
- **Universo com Poucos Ativos ou Ativo sem Histórico Suficiente**: Se o usuário informar uma lista personalizada com menos ativos que o necessário para atingir 100% da carteira dado o teto por ativo (ex: 2 ativos com teto de 25% cada), o sistema respeita o teto de 25% por ativo (alocando 50% no total) e preserva os 50% restantes em caixa, avisando claramente o usuário. Ativos com dados inválidos ou sem sinais históricos mínimos são ignorados graciosamente sem interromper o processamento dos demais.
- **Empate de Score de Potencial entre Candidatos**: Caso dois ativos candidatos apresentem exatamente o mesmo Score de Potencial na mesma barra/data, o critério de desempate determinístico deve priorizar: (1) maior Taxa de Acerto histórica (*Win Rate*), (2) maior *Profit Factor* e (3) ordem alfabética do ticker.
- **Proteção contra Giro Excessivo (Anti-Churning na Rotação Tática)**: Uma posição recém-aberta não deve ser imediatamente trocada no pregão seguinte por oscilações mínimas de score; a rotação por custo de oportunidade exige que o novo ativo candidato esteja em Timing `IDEAL`, possua diferencial mínimo de Score (padrão $\ge 15$ pontos acima do ativo mais fraco em carteira) e que o ativo a ser substituído esteja estagnado/no prejuízo ou com perda de momentum após período mínimo de maturação (ex: $\ge 3$ barras em carteira).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE disponibilizar uma nova aba principal denominada **"Carteira"** no menu superior de navegação, ocultando contextualmente o seletor global de direção ("Compra / Venda / Ambos") quando esta aba estiver ativa.
- **FR-002**: A aba "Carteira" DEVE fornecer um painel configurável para o usuário informar e editar:
  1. **Caixa Disponível / Capital Inicial** (valor monetário $> 0$, padrão `10000.00`);
  2. **Posições Atuais em Carteira** (lista dinâmica onde o usuário pode adicionar/remover ativos informando `Ticker`, `Quantidade de Cotas` e `Preço Médio de Compra`, ou iniciar 100% em caixa);
  3. **Universo Alvo de Oportunidades** (`Destaques`, `Ações Brasil`, `FIIs Brasil`, `Ações EUA`, `Commodities`, `Criptomoedas` ou `Lista Personalizada de Tickers`);
  4. **Tempo Gráfico** (`1d`, `1wk`, `1h`, `15m`, `5m`) e **Período Histórico** (`6mo`, `1y`, `2y`, `5y`);
  5. **Limite Máximo por Ativo (%)** (teto de concentração individual sobre o patrimônio total, configurável entre `10%` e `100%`, padrão `25%`).
- **FR-003**: Os dados da carteira atual do usuário (caixa, posições cadastradas e parâmetros de alocação) DEVEM ser persistidos automaticamente no armazenamento local do navegador, restaurando o estado ao reabrir a aplicação.
- **FR-004**: Para cada ativo pertencente à carteira atual e ao universo alvo selecionado, o motor quantitativo DEVE identificar automaticamente o **Par de Estratégias Campeão** (combinação de 1 estratégia de Compra + 1 estratégia de Venda com melhor desempenho histórico no ativo para o tempo gráfico selecionado) e calcular um **Score de Potencial (0 a 100)** determinístico baseado em:
  - Taxa de Acerto histórica (*Win Rate %*);
  - Retorno Histórico / Expectativa Matemática da estratégia campeã no ativo;
  - Fator de Lucro (*Profit Factor*) e controle de *Max Drawdown*;
  - Qualidade do *Timing* atual do sinal (`IDEAL` recebe pontuação máxima; `EXTENDED` recebe penalização moderada; `LATE` bloqueia novas entradas de compra).
- **FR-005**: O módulo **Consultor de Rebalanceamento Hoje** DEVE avaliar o estado atual da carteira frente aos sinais mais recentes do universo alvo e gerar um **Plano de Ação Atual** contendo ordens classificadas em cinco categorias semânticas:
  1. `COMPRAR`: Nova entrada ou reforço em ativo com sinal de Compra em Timing favorável, dimensionado proporcionalmente ao Score de Potencial até o limite máximo por ativo;
  2. `VENDER TOTAL`: Liquidação de 100% da posição de um ativo em carteira que confirmou sinal de Venda (Topo) pela sua estratégia campeã;
  3. `VENDER PARCIAL / REBALANCEAR`: Redução parcial de posição de um ativo cujo peso atual no patrimônio total excedeu o limite máximo por ativo somado à banda de tolerância (padrão `+5%` absolutos sobre o teto, ex: peso $> 30\%$ quando o teto é $25\%$);
  4. `ROTACIONAR`: Ordem combinada de venda de um ativo estagnado/fraco da carteira atual (mantido há pelo menos 3 barras e sem ganho relevante) para financiar a compra de um novo candidato em Timing `IDEAL` cujo Score de Potencial supere o ativo atual em pelo menos `15` pontos;
  5. `MANTER`: Posições atuais que permanecem em tendência saudável sem gatilho de venda de topo, excesso de peso ou substituição tática.
- **FR-006**: Cada recomendação do Plano de Ação DEVE detalhar: Ticker e nome do ativo, Ação recomendada, Estratégia Campeã de Compra/Venda vinculada, Score de Potencial (0–100), Status de Timing, Preço Atual / Preço de Referência, Quantidade exata de cotas a comprar ou vender, Valor financeiro da ordem (R$), Peso Atual na carteira (%) e Peso Alvo pós-rebalanceamento (%).
- **FR-007**: O módulo **Simulador Histórico de Carteira Multiativos** DEVE executar um backtest cronológico barra a barra sobre uma linha do tempo unificada dos ativos do universo selecionado, garantindo **Zero Look-Ahead Bias** (sinais confirmados no fechamento da barra $t$ são executados exclusivamente pelo preço de abertura da barra $t+1$ ou preço de reteste causal válido).
- **FR-008**: Durante o backtest multiativos, o motor DEVE gerenciar uma conta de caixa unificada da carteira (`portfolio_cash`) e o inventário de posições abertas em múltiplos ativos simultaneamente, aplicando a cada barra a seguinte ordem de precedência operacional:
  1. Processar liquidações de `VENDER TOTAL` para ativos em carteira com sinal de venda confirmado na barra;
  2. Processar vendas parciais de `REBALANCEAR` para ativos cujo peso de mercado na abertura da barra supere o teto máximo + banda de tolerância;
  3. Processar `ROTACIONAR` caso o caixa disponível seja insuficiente para uma nova oportunidade em Timing `IDEAL` que supere em $\ge 15$ pontos de Score uma posição estagnada elegível em carteira;
  4. Processar novas entradas `COMPRAR` utilizando o caixa disponível, distribuindo o capital entre os sinais de compra confirmados na barra proporcionalmente aos seus respectivos Scores de Potencial e respeitando estritamente o teto máximo por ativo.
- **FR-009**: O Simulador Histórico DEVE calcular um benchmark comparativo **Buy & Hold Equal-Weight da Cesta** (alocação inicial em partes iguais entre os ativos do universo no início do período mantendo-os até o final) e retornar as curvas temporais diárias de:
  - Evolução do Patrimônio Total da Carteira Gerenciada (Posições a Mercado + Caixa);
  - Evolução do Benchmark Buy & Hold Equal-Weight;
  - Evolução da parcela em Caixa vs. Capital Alocado;
  - Série de *Drawdown* percentual da carteira.
- **FR-010**: A interface da aba "Carteira" DEVE exibir cards de KPIs consolidados da simulação multiativos:
  1. **Patrimônio Final** e **Capital Inicial / Total Aportado**;
  2. **Lucro Líquido Total (R$)** e **Retorno Global da Carteira (%)**;
  3. **Comparativo vs. Buy & Hold da Cesta (%)** e **Alfa Gerado (%)**;
  4. **Taxa de Acerto da Carteira (Win Rate %)** com contagem de ciclos vencedores e perdedores;
  5. **Max Drawdown da Carteira (%)** e **Fator de Lucro (Profit Factor)**;
  6. **Total de Operações e Rebalanceamentos/Rotações executados**.
- **FR-011**: A interface DEVE apresentar uma tabela detalhada do **Histórico de Operações e Rebalanceamentos da Carteira**, listando cronologicamente cada operação com Data, Ativo, Tipo de Ação (`COMPRA`, `VENDA TOTAL`, `REBALANCEAMENTO PARCIAL`, `ROTAÇÃO`), Estratégia Acionada, Score no momento da decisão, Preço de Execução, Quantidade, Valor Financeiro, Resultado Realizado (R$ e %) e Saldo de Caixa remanescente.

### Key Entities

- **PortfolioHolding**: Representa uma posição atual informada pelo usuário ou mantida pelo simulador (`ticker`, `asset_name`, `shares`, `average_buy_price`, `current_price`, `market_value`, `unrealized_pnl_pct`, `current_weight_pct`, `entry_bar_index`).
- **AssetOpportunityProfile**: Perfil quantitativo calculado para cada ativo do universo (`ticker`, `champion_buy_strategy_id`, `champion_buy_label`, `champion_sell_strategy_id`, `champion_sell_label`, `historical_win_rate`, `historical_return_pct`, `profit_factor`, `timing_status`, `potential_score_0_100`, `active_signal_direction`).
- **PortfolioActionRecommendation**: Ordem acionável gerada pelo Consultor de Rebalanceamento Hoje (`ticker`, `action_type` [`BUY`, `SELL_FULL`, `SELL_PARTIAL_REBALANCE`, `ROTATE_OUT`, `ROTATE_IN`, `HOLD`], `reason_label`, `strategy_label`, `potential_score`, `reference_price`, `recommended_shares`, `recommended_value`, `current_weight_pct`, `target_weight_pct`).
- **PortfolioLedgerEvent**: Registro cronológico de uma operação executada durante o backtest histórico multiativos (`event_id`, `date`, `ticker`, `event_type`, `strategy_sub_id`, `strategy_label`, `potential_score`, `execution_price`, `shares_delta`, `trade_value`, `realized_pnl_value`, `realized_pnl_pct`, `portfolio_equity_after`, `cash_balance_after`).
- **PortfolioSimulationSummary**: Conjunto consolidado de métricas de performance, curvas patrimoniais e alocação final da carteira simulada.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um usuário com R$ 10.000,00 em caixa ou com posições abertas consegue obter o Plano de Ação completo (o que comprar, quanto comprar, o que vender, quanto vender e como rebalancear) e o Backtest Histórico para uma cesta padrão (ex: "Destaques" com 14 ativos) em menos de 5 segundos quando os dados OHLCV já estiverem em cache local.
- **SC-002**: 100% das recomendações de alocação geradas pelo Consultor de Rebalanceamento e pelo Simulador Histórico respeitam a conservação estrita de caixa (soma das compras recomendadas nunca excede o caixa disponível mais o produto líquido das vendas recomendadas no mesmo ciclo) e nunca alocam um peso inicial superior ao limite máximo por ativo configurado pelo usuário.
- **SC-003**: 100% das decisões de compra, venda total, venda parcial e rotação tática no Simulador Histórico obedecem ao princípio de *Zero Look-Ahead Bias*, comprovado por testes automatizados onde o truncamento de barras futuras em $t+1$ não altera nenhuma decisão nem o preço de execução até a barra $t$.
- **SC-004**: As informações da carteira cadastradas pelo usuário (caixa, posições atuais e parâmetros) persistem integralmente após recarregamento da página ou troca de tema Claro/Escuro sem perda de dados.
- **SC-005**: 100% da suíte de testes existente e os novos testes unitários e de integração do motor de carteira passam integralmente sem regressões.

---

## Assumptions

- O cálculo de custos operacionais segue o padrão limpo atual do simulador do projeto (sem corretagem fixa ou impostos retidos por padrão), mantendo comparabilidade direta de alfa bruto contra o Buy & Hold e os simuladores individuais existentes.
- Quando o usuário opta por uma categoria pronta (ex: `Destaques`, `Ações Brasil`, `FIIs Brasil`, `Criptomoedas`), o universo de ativos utiliza as mesmas cestas oficiais já catalogadas no Radar do sistema; para categorias muito extensas (ex: `Ações EUA` com 71 ativos), o motor pode avaliar prioritariamente os ativos da carteira do usuário mais os top ativos líquidos da categoria para assegurar resposta rápida.
- Para ativos negociados na B3 (`.SA`), as quantidades recomendadas no Consultor de Rebalanceamento Hoje são arredondadas para cotas inteiras ($\ge 1$ ação/cota no mercado fracionário/padrão), enquanto ativos globais e criptomoedas suportam frações de até 4 casas decimais.
- A banda padrão de tolerância para disparo de rebalanceamento por excesso de peso é de `+5%` absolutos acima do teto máximo por ativo configurado (por exemplo, se o teto por ativo é `25%`, a venda parcial de rebalanceamento ocorre quando o ativo ultrapassa `30%` do patrimônio total, reconduzindo-o para `25%`).
