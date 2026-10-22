# Feature Specification: Pacote de Estratégias Quantitativas com Indicadores Técnicos

**Feature Branch**: `013-quantitative-indicators-package`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Pacote de Estrategias Quantitativas com Indicadores Tecnicos de Reversao a Media, Divergencia de Osciladores, Fluxo de Volume e Volatilidade"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Exploração de Estratégias de Reversão à Média no Radar e Simulador (Priority: P1)

Como analista quantitativo ou investidor, quero selecionar estratégias estatísticas de reversão à média (Bandas de Bollinger Fechou Fora/Dentro, Keltner Squeeze e Z-Score de Preço em extremos) para identificar fundos e topos de mercado em ações, fundos imobiliários, índices e criptoativos com base em esticamento estatístico de preços.

**Why this priority**: A reversão à média é um dos pilares estatísticos mais robustos para captura de fundos e topos; fornece pontos claros de exaustão e gatilhos objetivos sem subjetividade.

**Independent Test**: Pode ser testado de forma independente selecionando qualquer uma das estratégias de reversão à média no Radar ou no Simulador (tanto modo Trade quanto modo Acumulação DCA) e verificando que os sinais de compra (fundos) e venda (topos) são gerados respeitando o contrato padrão e sem viés de antecipação.

**Acceptance Scenarios**:
1. **Given** um ativo com velas diárias onde o fechamento anterior foi abaixo da Banda Inferior de Bollinger (ou Z-score < -2.0) e a vela atual fecha de volta dentro da banda, **When** a estratégia "Bollinger Fechou Fora/Dentro" for executada, **Then** o sistema gera um sinal de compra na vela $t$ para execução na abertura de $t+1$.
2. **Given** um ativo que entra em compressão de volatilidade (Bandas de Bollinger dentro dos Canais de Keltner - Squeeze) e rompe para cima ou para baixo, **When** a estratégia "Keltner Squeeze" for avaliada, **Then** os sinais de expansão de volatilidade de alta/baixa são marcados corretamente no gráfico e na listagem de oportunidades.
3. **Given** o módulo Simulador no modo Acumulação DCA, **When** o usuário escolhe a estratégia "Z-Score Extremo de Fundo", **Then** os aportes periódicos são simulados exclusivamente nas barras de gatilho de sobrevenda estatística.

---

### User Story 2 - Estratégias de Divergência e Exaustão com Osciladores (Priority: P2)

Como investidor, quero identificar divergências regulares (Bullish / Bearish) em IFR/RSI, níveis de sobrevenda/sobrecompra no Estocástico Lento e inflexões de momentum no Histograma MACD para antecipar reversões de tendência com alta confluência estatística.

**Why this priority**: Divergências entre preço e oscilador revelam perda de momentum antes que o preço reverta formalmente, sendo amplamente utilizadas para encontrar assimetrias de risco/retorno favoráveis.

**Independent Test**: Pode ser testado escolhendo "Divergência de IFR", "Estocástico Lento em Extremos" ou "MACD Histogram Momentum" no Simulador/Radar, validando se picos/vales de oscilador e preço são mapeados sem look-ahead bias e se os sinais correspondentes disparam nas coordenadas corretas.

**Acceptance Scenarios**:
1. **Given** um ativo formando nova mínima no preço enquanto o IFR/RSI forma uma mínima mais alta (Divergência de Alta / Bullish Divergence), **When** a estratégia "Divergência de IFR" é processada, **Then** um sinal de compra é gerado no fechamento da barra de confirmação do pivô, com execução na barra subsequente.
2. **Given** o Estocástico Lento caindo abaixo de 20 (sobrevenda) e em seguida cruzando sua média móvel de volta para cima, **When** a estratégia "Estocástico Lento em Extremos" for selecionada, **Then** um gatilho de compra é emitido com `strategy_sub_id` descritivo.
3. **Given** o Histograma MACD registrando barras decrescentes no campo negativo (perda de força vendedora e inflexão para cima), **When** a estratégia "MACD Momentum" for ativada, **Then** o sinal de virada de momentum é detectado.

---

### User Story 3 - Estratégias de Fluxo Institucional de Volume e Volatilidade (Priority: P3)

Como trader/alocador, quero utilizar bandas de ancoragem por volume (Bandas de VWAP), detecção de Volume Clímax (Volume Spread Analysis - VSA / Absorção de Fundos) e rastreamento de volatilidade dinâmica (SuperTrend / Canais ATR) para validar a presença de grandes participantes e gerenciar saídas dinâmicas.

**Why this priority**: Preço sem volume carece de validação institucional. As estratégias de VWAP Bands e Clímax de Volume separam movimentos falsos de absorções reais de liquidez, enquanto SuperTrend fornece tendências limpas de volatilidade.

**Independent Test**: Pode ser testado selecionando as estratégias de VWAP, Volume Clímax ou SuperTrend no seletor de compra/venda do Simulador e do Radar, verificando se os cálculos incorporam volume ponderado e desvios de ATR em conformidade matemática.

**Acceptance Scenarios**:
1. **Given** uma vela de amplitude acima da média com volume no percentil 95+ (clímax) apresentando cauda inferior de rejeição / absorção, **When** a estratégia "Volume Clímax / VSA" é acionada, **Then** um sinal de compra por absorção é catalogado.
2. **Given** um ativo negociando abaixo do desvio inferior das Bandas de VWAP (ex: -2 desvios), **When** o preço cruza de volta para o canal da VWAP, **Then** um sinal de retorno à média de preço institucional é disparado.
3. **Given** uma posição aberta acompanhada pela estratégia "SuperTrend / ATR Trailing", **When** o fechamento do preço cruza a linha de stop de volatilidade, **Then** o sinal de saída é acionado na barra seguinte.

---

### User Story 4 - Integração Completa no Otimizador de Estratégias e UI (Priority: P4)

Como usuário final do Terminal Web, quero visualizar e combinar qualquer um dos novos indicadores no Radar de Oportunidades, no Simulador Clássico (Par Compra-Venda) e no Otimizador DCA ("Mais Lucrativa"), observando métricas de win rate, retorno acumulado e preço médio sem quebras de interface.

**Why this priority**: A usabilidade unificada garante que as novas estratégias não fiquem isoladas, mas sim totalmente interoperáveis com todo o ecossistema existente da plataforma.

**Independent Test**: Executar uma varredura de ranking no Radar e uma otimização no Simulador verificando que todas as 10 novas estratégias aparecem nos menus suspensos e podem ser avaliadas com sucesso.

**Acceptance Scenarios**:
1. **Given** o seletor de estratégias no Radar ou Simulador, **When** a lista suspensa é aberta, **Then** todas as novas estratégias aparecem agrupadas ou catalogadas com nomes claros em português/inglês amigável.
2. **Given** a execução do otimizador de estratégias "Mais Lucrativa" (tanto no modo trade quanto no modo acumulação), **When** o algoritmo testa as combinações, **Then** as novas estratégias competem no ranking exibindo rentabilidade, drawdown e assertividade corretos.

---

### Edge Cases

- **Janela de Dados Insuficiente**: O que acontece quando um ativo recém-listado (IPO recente ou contrato novo) não possui velas suficientes para calcular médias longas, canais de Keltner ou desvios padrão (ex: menos de 20 a 50 velas)? O motor deve descartar com segurança sem lançar exceções não tratadas, retornando zero sinais.
- **Volume Nulo ou Ausente**: Ativos como certos índices ou pares sem feed de volume no provedor (ou volume = 0 contínuo) que tentarem rodar estratégias de VWAP ou Volume Clímax: o sistema deve emitir um aviso informativo ou fallback gracioso sem travar a API.
- **Alta Volatilidade com Gaps**: Se a vela $t+1$ abrir com forte gap acima ou abaixo do preço de gatilho, a execução deve registrar o preço exato de abertura da barra de execução (`Open[t+1]`), garantindo realismo estrito de backtesting.
- **Sinais Consecutivos (Saturação)**: Em períodos de forte tendência contínua (ex: mercado em queda livre com 10 dias seguidos de sobrevenda), o sistema deve tratar se gera sinais repetidos ou se aguarda saída prévia/rearme do gatilho antes de registrar novo evento.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer um catálogo modular de estratégias quantitativas baseadas em indicadores técnicos, subdividido em 4 famílias operacionais:
  - *Família 1: Reversão à Média* (Bandas de Bollinger Fechou Fora/Dentro, Keltner Squeeze, Z-Score de Preço);
  - *Família 2: Osciladores e Divergências* (Divergência Regular de IFR/RSI, Estocástico Lento em Extremos, MACD Histogram Momentum);
  - *Família 3: Volume & Fluxo Institucional* (Bandas de VWAP, Money Flow Index - MFI, Volume Clímax / VSA Absorção);
  - *Família 4: Volatilidade & Tendência Dinâmica* (SuperTrend / Canais de ATR).
- **FR-002**: Todas as estratégias implementadas DEVEM respeitar estritamente o princípio de **Zero Look-Ahead Bias**: qualquer cálculo ou filtro na barra $t$ deve usar apenas informações disponíveis até o fechamento de $t$, e toda ordem a mercado correspondente DEVE ser executada estritamente na abertura da barra $t+1$ (`execution_price = Open[t+1]`).
- **FR-003**: Todas as funções de cálculo de indicadores e detecção de sinais DEVEM ser 100% vetorizadas utilizando arrays `numpy` e/ou `pandas`, sendo estritamente proibido o uso de `iterrows()` ou iterações lentas em Python puro nos caminhos críticos de execução.
- **FR-004**: Cada estratégia DEVE retornar uma estrutura padronizada contendo obrigatoriamente os campos do contrato de governança:
  - `signal_bar_index`: data/timestamp ou índice do sinal gerado;
  - `execution_bar_index`: data/timestamp ou índice da execução na barra subsequente;
  - `execution_price`: preço de execução efetivo;
  - `reference_line_price`: patamar de referência estatística (ex: valor da banda, nível de sobrecompra/sobrevenda ou linha de stop);
  - `strategy_sub_id`: identificador descritivo e amigável da subestratégia ou variante do sinal.
- **FR-005**: O sistema DEVE suportar a operação das estratégias em ambas as direções (identificação de fundos para compra e topos para venda/saída), permitindo seu uso no Radar de Oportunidades, no Simulador de Trades (Pares Compra-Venda) e no Simulador de Acumulação DCA (apenas entradas de fundos).
- **FR-006**: A API backend DEVE expor as novas estratégias na lista de estratégias disponíveis retornada pelo endpoint `/api/strategies` (ou equivalente utilizado pelo frontend).
- **FR-007**: O frontend web (SPA) DEVE atualizar dinamicamente os seletores de estratégia (Radar, Simulador Compra, Simulador Venda) para refletir o novo pacote de indicadores de maneira organizada e intuitiva.
- **FR-008**: O motor de otimização de estratégias (`/api/simulate/optimize`) DEVE ser capaz de avaliar os novos indicadores tanto no ranking de pares de trade quanto no ranking de acumulação DCA sem degradação perceptível de performance.
- **FR-009**: O cálculo de divergências (IFR/RSI e MACD) DEVE utilizar lógica puramente quantitativa e determinística (como detecção de extremos locais e comparação de inclinações) calculada sem viés de antecipação.

### Key Entities

- **QuantitativeIndicatorStrategy**: Definição da estratégia com metadados (id, nome legível, família estatística, direção permitida: Buy/Sell/Both, parâmetros padrão e descrição).
- **StrategySignalContract**: Registro tabular de ocorrências de sinal com timestamps de sinal e execução, preços de preenchimento, linhas de referência e identificador da subestratégia.
- **StrategyFamily**: Classificação categórica (Reversão à Média, Osciladores, Fluxo & Volume, Volatilidade).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das 10 estratégias quantitativas especificadas devem estar implementadas, registradas no catálogo de estratégias da API e acessíveis pelo frontend.
- **SC-002**: 100% dos testes unitários de validação anti-look-ahead bias devem ser aprovados com assertividade estrita ($t$ sinal vs $t+1$ execução).
- **SC-003**: A execução de uma varredura de sinais para 500 barras de histórico diário com qualquer uma das novas estratégias deve ser concluída em menos de 50 milissegundos por ativo.
- **SC-004**: O otimizador de combinações do simulador deve conseguir processar e rankear o conjunto expandido de estratégias para um ativo em menos de 3 segundos no ambiente local.
- **SC-005**: A suíte de testes automatizados existente deve permanecer com 100% de aprovação (zero regressões no radar, simulador e acumulação DCA).

---

## Assumptions

- O usuário utilizará as novas estratégias principalmente nos timeframes diário (`1d`), semanal (`1wk`) e 60 minutos (`60m`), que já são suportados pelo sistema de download e cache.
- Séries de preços fornecidas pelo módulo `data_loader` já vêm sanitizadas com colunas `Open`, `High`, `Low`, `Close`, `Volume` e `Adj Close`.
- Para ativos sem volume confiável (ex: moedas fiat ou certos índices sintéticos), estratégias dependentes de volume apresentarão retorno vazio ou log amigável sem travar a aplicação.
- Parâmetros padrão dos indicadores adotarão valores amplamente consolidados na literatura quantitativa (ex: Bollinger 20 períodos / 2 desvios; IFR 14 períodos com 30/70; Estocástico Lento 14, 3, 3; MACD 12, 26, 9; Keltner 20 períodos / 1.5 ATR; SuperTrend 10 períodos / 3.0 ATR).
