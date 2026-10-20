# Feature Specification: Market Opportunity & Bottom Statistical Engine

**Feature Branch**: `001-market-opportunity-engine`

**Created**: 2026-10-19

**Status**: Ready for Planning

**Input**: User description: "Construir um sistema analítico e visual no navegador que funcione como um Indicador Geral de Oportunidades de Mercado e Avaliador Estatístico de Fundos para perfil Holder/Acumulação, operando nos timeframes Diário (1d) e Semanal (1wk) com dados do Yahoo Finance (yfinance). O sistema deve analisar qualquer ativo selecionado (Ações EUA, Brasil, FIIs, Cripto, Commodities/Minérios) e processar 8 famílias de estratégias de compra (incluindo a Estratégia Proprietária de Negação de Rompimento em 4 variações e 8 sub-padrões MQL5), calculando a eficiência estatística histórica de cada uma por ativo."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Análise Estatística de Estratégias e Avaliação de Fundo (Priority: P1)

Como investidor de perfil Holder/Acumulação, quero selecionar qualquer ativo multi-mercado e timeframe (Diário ou Semanal) e visualizar a avaliação estatística histórica de acerto de fundo para 8 famílias de estratégias de compra, para que eu possa identificar quais regras têm maior probabilidade de sucesso e menor calor no ativo selecionado.

**Why this priority**: É a essência do valor da aplicação: calcular métricas quantitativas de acerto e retorno futuro em janelas pós-compra ($X$ barras) sem viés de antecipação.

**Independent Test**: Pode ser testado de forma autônoma selecionando um ativo (ex: `AAPL` ou `PETR4.SA`) com horizonte $X=60$ barras e conferindo a tabela/cards com Total de Compras, Win Rate, Forward Return e MAE.

**Acceptance Scenarios**:

1. **Given** um ativo carregado e um horizonte de $X$ barras (ex: 60 barras), **When** o motor de cálculo processa as estratégias, **Then** o sistema exibe para cada estratégia o número total de execuções $N$, a taxa de acerto (`Close[t_exec + X] > P_exec`), o retorno médio e mediano em $X$ barras, e a Excursão Máxima Adversa (`MAE %`).
2. **Given** a execução da Estratégia Proprietária em modo Reteste, **When** o preço recua até a Linha de Referência dentro da janela $M$ e tolerância, **Then** a compra é contabilizada na barra exata do reteste e a métrica de Taxa de Reteste reflete a proporção de sinais que executaram vs. os que continuaram em alta sem retorno.

---

### User Story 2 - Gráfico Interativo com Pistas Visuais da Negação de Rompimento (Priority: P2)

Como usuário visual de análise técnica, quero visualizar o gráfico de Candlesticks do ativo selecionado com marcadores de compra e linhas horizontais de referência da Estratégia Proprietária de Negação de Rompimento, para auditar visualmente a transição entre o rompimento, a negação e a execução do sinal.

**Why this priority**: A auditabilidade visual reforça a confiança do investidor ao inspecionar o comportamento dos preços em torno da Linha de Referência rompida e negada.

**Independent Test**: Pode ser testado selecionando o gráfico principal e ativando a Estratégia Proprietária, verificando se as linhas horizontais pontilhadas conectam a mínima rompida até a barra de negação/compra.

**Acceptance Scenarios**:

1. **Given** um sinal de Negação de Rompimento identificado, **When** o usuário inspeciona o gráfico principal, **Then** uma linha de referência horizontal tracejada é renderizada a partir da barra de rompimento até a barra de negação/execução, com um marcador indicando o preço e momento de compra.
2. **Given** a seleção de filtros de visibilidade na barra lateral, **When** o usuário desmarca uma estratégia, **Then** apenas os marcadores das estratégias ativas permanecem renderizados no gráfico.

---

### User Story 3 - Painéis Estatísticos Comparativos e Risco x Retorno (Priority: P3)

Como analista quantitativo, quero examinar gráficos comparativos de Ranking de Eficiência e dispersão de Risco x Retorno (Calor MAE vs. Retorno Médio), para comparar diretamente as 4 variações da Estratégia Proprietária, os 8 padrões MQL5 e os demais modelos sistemáticos.

**Why this priority**: Permite responder objetivamente à pergunta clássica de execução: "Vale a pena esperar o reteste na linha ou comprar na abertura seguinte?" através da comparação empírica de MAE e retorno.

**Independent Test**: Pode ser testado gerando o gráfico de dispersão e confirmando se cada ponto representa uma estratégia/variação com coordenadas $(MAE\%, Retorno\%)$.

**Acceptance Scenarios**:

1. **Given** o processamento completo das estratégias, **When** o usuário navega pelo painel estatístico, **Then** um gráfico de barras ordenadas exibe o ranking de Win Rate (%) de todas as estratégias e variações.
2. **Given** o gráfico de dispersão Risco x Retorno, **When** o usuário compara a variante de Abertura versus a variante de Reteste da Estratégia Proprietária, **Then** as coordenadas mostram a diferença de calor médio suportado e de retorno médio obtido.

---

### User Story 4 - Monitor de Estado Atual e Oportunidades em Aberto (Priority: P4)

Como investidor acompanhando o mercado no dia a dia, quero consultar um card de status em tempo real que indique qual é a Linha de Referência Ativa corrente (aguardando negação) e se há sinais recém-disparados na última barra do ativo, para tomar decisões imediatas de alocação.

**Why this priority**: Fornece utilidade prática para o momento presente da análise, sem exigir que o usuário rastreie manualmente a barra atual.

**Independent Test**: Pode ser testado carregando um ativo e verificando se o card de confluência exibe o status de espera de negação com o preço exato da linha ativa da última barra.

**Acceptance Scenarios**:

1. **Given** um ativo cujo último rompimento ainda não foi negado, **When** o usuário visualiza o card de estado, **Then** o sistema exibe o nível de preço da Linha de Referência Ativa e a distância percentual do preço atual até ela.
2. **Given** um ativo que acabou de negar um rompimento na última barra fechada, **When** o card é renderizado, **Then** um alerta visual sinaliza a oportunidade de compra ou início da janela de reteste.

---

### Edge Cases

- **Ausência de Mínima Anterior / Histórico Insuficiente**: Se o ativo tiver menos histórico que a janela necessária (ex: menos de 200 barras para SMA ou menos de $N$ barras para o Candle B), os indicadores correspondentes devem exibir aviso explícito e não crashar a aplicação.
- **Rompimentos Sucessivos sem Negação**: Se múltiplos candles fecharem consecutivamente abaixo das mínimas anteriores, a Linha de Referência Ativa deve ser atualizada para o último rompimento verificado, descartando as referências anteriores sobrepostas.
- **Reteste que não ocorre dentro da janela de $M$ barras**: Na variação de reteste, se o preço não recuar até a Linha de Referência (com tolerância) em até $M$ barras após a negação, a oportunidade expira e nenhuma compra é registrada.
- **Novo Rompimento durante a janela de reteste**: Se antes de tocar a linha com sucesso um candle fechar abaixo da Linha de Referência, o setup de compra é invalidado e uma nova Linha de Referência é estabelecida.
- **Ativos sem dados fundamentalistas longos**: Em criptos, commodities ou ações com balanços parciais, o sistema deve acionar automaticamente os proxies quantitativos (Mayer Multiple ou Dividend Yield Rolling + Desconto de SMA) sem interrupção.
- **Sinais Próximos ao Fim da Série Temporal**: Sinais ocorridos a menos de $X$ barras do candle mais recente não possuem histórico completo para avaliação de acerto; devem ser listados como pendentes ou excluídos do cálculo fechado de Win Rate e marcados com advertência.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir a seleção de ativos através de busca por ticker ou seleção de lista pré-configurada abrangendo 5 classes de mercado: Ações EUA, Ações B3 (`.SA`), FIIs B3 (`.SA`), Criptomoedas (`-USD`) e Commodities/Minérios (`=F`).
- **FR-002**: O sistema DEVE suportar os timeframes Diário (`1d`) e Semanal (`1wk`) para todas as análises e gráficos.
- **FR-003**: O sistema DEVE implementar cache local obrigatório para os dados de cotações históricos para evitar sobrecarga de requisições externas e garantir agilidade na troca de parâmetros.
- **FR-004**: O sistema DEVE implementar a Estratégia Proprietária de Negação de Rompimento como uma máquina de estados finitos $O(N)$ operando nas 4 combinações:
  - Tipo 1 + Execução em Abertura (`t-1` + `Open t+1`);
  - Tipo 1 + Execução em Reteste (`t-1` + `Reteste em M barras`);
  - Tipo 2 + Execução em Abertura (`Fundo N` + `Open t+1`);
  - Tipo 2 + Execução em Reteste (`Fundo N` + `Reteste em M barras`).
  - **Regras Matemáticas Operacionais de Reteste & Borda:**
    1. *Simultaneidade de Toque e Fechamento Abaixo*: Se dentro da janela $M$ a barra atingir a condição de toque (`Low[t+k] <= Linha * (1 + tol)`), a compra é preenchida no preço da linha, mesmo que o fechamento daquela mesma barra termine abaixo da linha.
    2. *Comportamento com Gap de Baixa*: Se a barra $t+k$ abrir em gap já abaixo do nível de reteste (`Open[t+k] < Linha * (1 + tol)`), o preço de execução $P_{exec}$ DEVE ser registrado no valor real de abertura `Open[t+k]`.
    3. *Ciclo Único de Preenchimento*: A avaliação da janela $[t+1, t+M]$ é sequencial estrita; o primeiro toque na barra $t+k$ consome a ordem e encerra o ciclo de compra (sem recompras acumuladas nas barras restantes de $M$). Se nenhuma barra tocar até $t+M$, a ordem expira.
    4. *Preço e Momento de Execução para Padrões Clássicos e Price Action*: Nos 8 padrões MQL5 (CCandlePattern) e nos setups de Price Action (Fundo Duplo/BOS e Wyckoff Spring), a execução de compra ocorre rigorosamente na abertura da barra seguinte à confirmação do padrão (`Open[t_final + 1]`), garantindo Zero Look-Ahead Bias.
- **FR-005**: O sistema DEVE permitir a configuração dos parâmetros da Estratégia Proprietária: lookback de fundo $N$ (default: 10), janela de reteste $M$ (default: 5) e percentual de tolerância do toque na linha (default: 0.0% a 1.0%).
- **FR-006**: O sistema DEVE processar a estratégia de DCA Dinâmico disparando compra quando `Close < SMA(200) - k * StdDev(200)` ou `RSI(14) < 30`.
- **FR-007**: O sistema DEVE processar a estratégia de Rebalanceamento Renda Fixa vs. Variável, simulando rebalanceamento por faixas de tolerância baseadas em drawdown da cotação.
- **FR-008**: O sistema DEVE processar a estratégia de Rebalanceamento por Força Relativa comparando o ativo com um benchmark de referência e disparando compra quando o Z-Score de 60 períodos atinge $\le -2.0$ com inflexão positiva.
- **FR-009**: O sistema DEVE processar a estratégia Value Proxy / Fundamentalista aplicando percentil de Dividend Yield Rolling + Desconto de SMA para ações/FIIs, e Mayer Multiple $\le 15\%$ para criptomoedas/commodities.
- **FR-010**: O sistema DEVE processar a estratégia de Fundo Duplo com Falha de Continuação e Break of Structure (BOS / CHoCH).
- **FR-011**: O sistema DEVE processar a estratégia de Falso Rompimento de Mínima (Spring / Liquidity Sweep) com rejeição e volume acima da média de 20 períodos.
- **FR-012**: O sistema DEVE processar os 8 padrões clássicos de velas de reversão altista (CCandlePattern MQL5 Artigo 101) com filtro prévio de tendência de baixa (`Close < SMA(20)`): Martelo, Engolfo de Alta, Linha Perfurante, Estrela da Manhã, Harami de Alta, Três Por Dentro de Alta, Três Por Fora de Alta e Três Soldados Brancos.
- **FR-013**: O sistema DEVE avaliar todas as compras com base no Critério Holder em horizonte configurável $X$ barras (default: 20, 60, 120 ou 252 barras), computando:
  - Total de Compras Executadas ($N$);
  - Taxa de Execução de Reteste (para estratégias de reteste);
  - Taxa de Acerto (`Holder Win Rate %` onde `Close[t_exec + X] > P_exec`);
  - Retorno Prospectivo Médio e Mediano (`Forward Return %`);
  - Excursão Máxima Adversa (`MAE %` médio e máximo durante a janela);
  - Score Geral de Eficiência Ponderado por Ativo.
- **FR-014**: O sistema DEVE garantir rigor absoluto anti-viés (Zero Look-Ahead Bias): nenhum indicador ou sinal em $t$ pode utilizar dados de $t+1$, e compras por reteste só contam a partir da barra exata de toque.
- **FR-015**: O sistema DEVE exibir o gráfico principal de Candlesticks interativo com marcação das compras e linhas horizontais de referência da Estratégia Proprietária.
- **FR-016**: O sistema DEVE exibir painéis gráficos de comparação contendo o Ranking de Eficiência e o gráfico de dispersão Risco x Retorno (Calor MAE vs. Retorno Médio).
- **FR-017**: O sistema DEVE disponibilizar um monitor de estado atual exibindo o status da Linha de Referência Ativa do ativo e possíveis sinais em formação na barra presente.

### Key Entities

- **Ativo de Mercado (Market Asset)**: Representa o instrumento financeiro analisado. Atributos: Ticker, Classe (Ação EUA, Ação B3, FII, Cripto, Commodity), Timeframe (`1d`, `1wk`), Série Histórica OHLCV.
- **Sinal de Compra (Trade Signal)**: Representa um ponto de compra gerado por uma estratégia. Atributos: `signal_bar_index`, `execution_bar_index`, `execution_price`, `reference_line_price`, `strategy_sub_id`.
- **Avaliação Estatística (Statistical Evaluation)**: Métricas calculadas para uma estratégia em um ativo sobre uma janela $X$. Atributos: Total de Compras, Taxa de Reteste, Taxa de Acerto (Win Rate), Retorno Médio/Mediano, MAE Médio, Score de Eficiência.
- **Linha de Referência Ativa (Active Reference Line)**: Estado mantido pela máquina de estados da Estratégia Proprietária. Atributos: Nível de Preço, Barra de Rompimento, Status (Ativa aguardando negação, Negada aguardando reteste, Executada, Cancelada).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O processamento de dados e cálculo de todas as 8 famílias de estratégias para um ativo com 5 anos de histórico diário deve ser concluído e renderizado no navegador em menos de 2.5 segundos após a seleção do ticker.
- **SC-002**: O cálculo da máquina de estados da Estratégia Proprietária e avaliação estatística para 1000 barras deve ser executado em menos de 100 milissegundos, garantindo navegação sem engasgos na interface.
- **SC-003**: 100% dos sinais gerados devem ser auditáveis contra look-ahead bias, demonstrando equivalência estrita com execuções causais barra a barra.
- **SC-004**: O usuário consegue alternar entre timeframes (`1d` e `1wk`) e atualizar o horizonte de acumulação $X$ com atualização dos gráficos e tabelas em menos de 1.5 segundo através do reuso de dados em cache.
- **SC-005**: 100% dos ativos testados das 5 classes suportadas (EUA, Brasil, FIIs, Cripto e Commodities) devem carregar dados e calcular estratégias sem falhas não tratadas.

## Assumptions

- Os dados históricos fornecidos pelo feed público do `yfinance` contêm barras OHLCV consistentes e dados ajustados por proventos/splits.
- A granularidade temporal mínima suportada é a barra diária (`1d`), com dados intradiários fora do escopo desta versão.
- As compras são tratadas como aquisições à vista (sem alavancagem ou short) para montagem de posição Holder/Acumulação.
- Na simulação de rebalanceamento, custos operacionais e tributários são assumidos como neutros na versão base para focar na métrica estatística pura do comportamento do preço.
