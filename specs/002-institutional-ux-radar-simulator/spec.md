# Feature Specification: Institutional UX/UI Design, Multi-Timeframe Intraday, Radar Scanner, Simulador de Acumulação e Guia de Estratégias

**Feature Branch**: `002-institutional-ux-radar-simulator`

**Created**: 2026-10-20

**Status**: Ready for Planning

**Input**: User description: "Criar a Feature 002 ('Institutional UX/UI Design, Multi-Timeframe Intraday, Radar Scanner, Simulador de Acumulação e Guia de Estratégias'), elevando o sistema para uma experiência de usuário (UX/UI) de nível institucional (estilo TradingView / Koyfin) sem quebrar os motores matemáticos validados na Feature 001."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Radar de Mercado & Semáforo de Timing ("Comprei Atrasado?") (Priority: P1)

Como investidor monitorando múltiplos ativos, quero abrir uma tela inicial de Radar que liste em tempo real as oportunidades acionadas recentemente e exiba um Semáforo de Timing objetivo, para que eu saiba instantaneamente se o preço atual ainda está em zona de compra ideal ou se o movimento já estendeu e devo aguardar recuo.

**Why this priority**: É a porta de entrada da experiência institucional. Resolve a maior dor operacional de investidores: a ansiedade de execução e o risco de entrar no topo de um repique pós-sinal.

**Independent Test**: Pode ser testado de forma autônoma acessando a Aba 1 ("🌐 Radar de Mercado & Oportunidades"), verificando se a lista de ativos exibe o badge do Semáforo (Verde, Amarelo ou Vermelho), o percentual de distância do preço atual em relação ao preço recomendado, e se clicar em um ativo navega diretamente para o terminal de análise.

**Acceptance Scenarios**:

1. **Given** um ativo com sinal recente ou reteste em andamento cujo preço atual esteja até `+1.5%` acima de $P_{exec}$ (ou aguardando toque na linha), **When** o Radar processa os dados, **Then** o ativo exibe o badge "🟢 ZONA IDEAL / DESCONTO" com a distância percentual exata.
2. **Given** um ativo cujo preço atual esteja entre `+1.5%` e `+4.0%` acima de $P_{exec}$, **When** exibido no Radar, **Then** o sistema classifica como "🟡 ESTENDIDO (CAUTELA)" recomendando aguardar pullback.
3. **Given** um ativo cujo preço atual esteja `> +4.0%` acima de $P_{exec}$ (ou consumiu mais de 30% do retorno médio esperado), **When** exibido no Radar, **Then** o sistema classifica como "🔴 ATRASADO (BONDE ANDOU)".
4. **Given** a tabela do Radar, **When** o usuário clica no nome de um ativo, **Then** a aplicação atualiza o estado de sessão e abre imediatamente o terminal de análise daquele ativo.

---

### User Story 2 - Terminal de Análise Institucional e Gráficos Refinados (Priority: P2)

Como analista quantitativo e investidor visual, quero inspecionar qualquer ativo com layout profissional escuro (FinTech Dark `#0B0E14`), com gráficos de barras horizontais sem corte de rótulos em 100%, matriz de Risco x Retorno com quadrantes e tabela interativa com barras de progresso, para ter clareza analítica sem fadiga visual.

**Why this priority**: Converte métricas brutas em visualizações de alto impacto para tomada de decisão fundamentada e auditável.

**Independent Test**: Pode ser testado selecionando um ativo e verificando o tema escuro sem elementos brancos desajustados, conferindo se os rótulos de 100% no Ranking aparecem completos com $N$ entradas (ex: `85.7% (14 entradas)`), e inspecionando o Scatter Plot com linhas de quadrante e sem textos sobrepostos.

**Acceptance Scenarios**:

1. **Given** a renderização do Ranking de Eficiência, **When** uma estratégia alcança 100% de Win Rate, **Then** a barra e o texto `100.0% (N entradas)` permanecem totalmente visíveis dentro da área do gráfico sem truncamento no eixo X.
2. **Given** a Matriz Risco x Retorno (Scatter Plot), **When** renderizada na tela, **Then** linhas de referência dividem os quadrantes (média de retorno e média de calor), identificando visualmente as estratégias no "Quadrante de Ouro" (Alto Retorno e Baixo Calor/MAE).
3. **Given** os nomes das estratégias na interface, **When** exibidos em qualquer painel, **Then** o sistema utiliza estritamente o Dicionário de Nomes Comerciais Amigáveis (ex: "Negação Barra Anterior (Entrada Reteste)", "Varredura de Liquidez (Wyckoff Spring)").

---

### User Story 3 - Simulador de Acumulação e Patrimônio ("Se eu tivesse aportado R$ X...") (Priority: P3)

Como investidor de perfil Holder/Acumulação, quero simular o resultado financeiro de aportes fixos (ex: R$ 100 ou US$ 100 a cada sinal disparado) ao longo do tempo para comparar o patrimônio acumulado final contra o total desembolsado do bolso, para validar a viabilidade prática da estratégia na formação de capital.

**Why this priority**: O investidor holder pensa em reais e cotas acumuladas. A simulação financeira converte estatísticas abstratas (Win Rate) em valor monetário palpável.

**Independent Test**: Pode ser testado definindo um valor de aporte (ex: R$ 100,00), selecionando uma estratégia e conferindo se a curva de patrimônio, o lucro líquido acumulado e o preço médio são computados instantaneamente sem recarregar a tela inteira (`@st.fragment`).

**Acceptance Scenarios**:

1. **Given** um valor de aporte $V$ por entrada e um histórico de sinais executados, **When** o simulador calcula a evolução, **Then** o sistema gera a curva temporal comparativa entre o "Total Tirado do Bolso" ($N \times V$) e o "Patrimônio Acumulado" ($\sum Cotas \times PreçoAtual$).
2. **Given** o ajuste de parâmetros do simulador (valor de aporte ou horizonte temporal), **When** o usuário altera os controles, **Then** apenas o fragmento do simulador é recalculado instantaneamente sem recarregar a página global (`@st.fragment`).
3. **Given** múltiplas estratégias avaliadas no ativo, **When** o simulador processa o ranking financeiro, **Then** uma tabela ordenada exibe qual estratégia gerou o maior patrimônio final acumulado e o menor preço médio de compra.

---

### User Story 4 - Multi-Timeframe Intraday e Agregação Matemática (Priority: P4)

Como trader de prazos mais curtos ou investidor acompanhando barras intraday, quero selecionar timeframes de `5m` a `12h` além de `1d` e `1wk`, para que o motor quantitativo processe dados de menor granularidade mantendo o histórico consistente através de agregação temporal (resampling).

**Why this priority**: Expande a versatilidade analítica do sistema sem quebrar os limites da API do Yahoo Finance.

**Independent Test**: Pode ser testado selecionando timeframes como `15m`, `1h` ou `4h` e verificando se os dados são baixados com o teto adequado (60 dias para minutos, base 1h agregada para 2h/4h/12h) e calculam as estratégias normalmente.

**Acceptance Scenarios**:

1. **Given** a seleção de timeframes de minutos (`5m`, `15m`, `30m`), **When** o `data_loader` consulta o feed, **Then** o período histórico é ajustado automaticamente para no máximo 60 dias para respeitar as restrições da API.
2. **Given** a seleção de timeframes intermediários (`2h`, `4h`, `12h`), **When** os dados são requisitados, **Then** o sistema realiza o download da base horária (`1h`) e aplica agregação matemática (Resampling: `Open=first`, `High=max`, `Low=min`, `Close=last`, `Volume=sum`) sem gerar barras faltantes ou com dados futuros.

---

### User Story 5 - Guia de Estratégias & Playbook Educacional (Priority: P5)

Como usuário buscando capacitação técnica, quero consultar uma enciclopédia interativa (Aba 4) explicando o racional conceitual, a regra matemática de entrada, a psicologia por trás do fundo e as boas práticas de cada família operacional, para operar com total convicção e sem improvisação.

**Why this priority**: Democratiza o conhecimento quantitativo institucional e fornece documentação viva diretamente na interface da aplicação.

**Independent Test**: Pode ser testado navegando até a Aba 4 e verificando a presença de cards estruturados com seções padronizadas para cada uma das 18 variações de estratégias.

**Acceptance Scenarios**:

1. **Given** a abertura da Aba "📘 Guia de Estratégias & Playbook", **When** o usuário seleciona uma estratégia, **Then** um card estruturado apresenta: Conceito Simples, Regra Matemática Exata, Racional Psicológico de Fundo, Perfil Ideal (Frequência vs. Precisão) e Regra Anti-Atraso.

---

### Edge Cases

- **Ativos sem sinais recentes no Radar**: Ativos monitorados sem nenhum sinal nas últimas $N$ barras devem ser exibidos em seção de "Aguardando Oportunidades", com a última Linha de Referência Ativa conhecida.
- **Divisão por zero em ativos sem volume intraday**: Em barras agregadas onde o volume seja 0, cálculos que dependem de volume (como Wyckoff Spring) devem ignorar a condição de volume ou emitir flag correspondente sem abortar o processamento.
- **Ativo com apenas 1 compra no Simulador**: Os cálculos de rentabilidade, preço médio e curva de evolução devem tratar séries unitárias sem quebras de indexação.
- **Transição de Ativo via Radar**: Ao clicar em um ativo no Radar, a troca de contexto no `session_state` deve limpar caches voláteis e renderizar o Terminal com o ativo clicado na primeira tentativa.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE adotar um Design System Institucional FinTech Dark com paleta formalizada: fundo `#0B0E14`, superfície de cards `#151924`, bordas `#262B38`, verde `#00E676`, vermelho `#FF5252`, âmbar `#FFC107`, azul `#2962FF` e tipografia tabular para números.
- **FR-002**: O sistema DEVE organizar a navegação em 4 abas superiores persistentes:
  1. `🌐 Radar de Mercado & Oportunidades`
  2. `📈 Terminal de Análise & Gráficos`
  3. `💰 Simulador de Patrimônio & Aportes`
  4. `📘 Guia de Estratégias & Playbook`
- **FR-003**: O sistema DEVE traduzir todos os identificadores técnicos para o Dicionário de Nomes Comerciais Amigáveis em todas as tabelas, gráficos, cards e tooltips.
- **FR-004**: O sistema DEVE implementar o Radar Scanner na Aba 1 monitorando uma cesta configurável de ativos, consolidando sinais ativos e aplicando a lógica de Semáforo de Timing:
  - 🟢 **ZONA IDEAL / DESCONTO**: até `+1.5%` acima de $P_{exec}$ ou aguardando reteste;
  - 🟡 **ESTENDIDO (CAUTELA)**: entre `+1.5%` e `+4.0%` acima de $P_{exec}$;
  - 🔴 **ATRASADO (BONDE ANDOU)**: acima de `+4.0%` ou $> 30\%$ do retorno médio consumido.
- **FR-005**: O sistema DEVE permitir a seleção interativa de um ativo na tabela do Radar para carregar instantaneamente sua visualização detalhada no Terminal de Análise via `st.session_state`.
- **FR-006**: O sistema DEVE aprimorar os gráficos do Terminal:
  - Ranking de Eficiência com `xaxis.range=[0, 118]`, escala de cores com clip no percentil 90 e texto `Win Rate % (N entradas)`;
  - Matriz Risco x Retorno (Scatter Plot) com linhas de referência nos eixos médios definindo o "Quadrante de Ouro", margens generosas e sem sobreposição de rótulos;
  - Tabela de dados utilizando `st.column_config` com `ProgressColumn` e formatação monetária.
- **FR-007**: O sistema DEVE implementar o Simulador de Acumulação na Aba 3 com isolamento reativo via `@st.fragment`, computando Valor Desembolsado, Patrimônio Acumulado Atual, Lucro Líquido, Rentabilidade e Preço Médio, plotando a curva temporal comparativa e tabela comparativa de estratégias.
- **FR-008**: O sistema DEVE disponibilizar na Aba 4 o Guia Educacional estruturado para as 18 variações de estratégias divididas em 4 grupos: Negação Proprietária 2x2, Price Action Institucional, Alocação/Holder e Padrões MQL5.
- **FR-009**: O sistema DEVE expandir o `data_loader` para suportar timeframes intraday (`5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `12h`, `1d`, `1wk`), respeitando limites de histórico do provedor e realizando Resampling temporal consistente para as barras de 2h, 4h e 12h a partir da base de 1h.
- **FR-010**: O sistema DEVE preservar rigorosamente todos os contratos matemáticos, anti-lookahead bias e testes unitários existentes da Feature 001.

### Key Entities

- **Cesta de Radar (Radar Basket)**: Conjunto de ativos monitorados na visualização macro com métricas resumidas e status de timing.
- **Semáforo de Timing (Timing Status)**: Classificação qualitativa da janela de compra baseada no desvio percentual do preço atual em relação ao preço recomendado ($P_{exec}$).
- **Simulação de Aporte (Accumulation Simulation)**: Estrutura contendo o histórico de cotas acumuladas, fluxo de caixa investido, preço médio ponderado e série temporal de patrimônio.
- **Playbook Entry**: Registro enciclopédico contendo explicação conceitual, fórmula de entrada, psicologia de mercado e perfil de risco de uma estratégia.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O carregamento da Aba 1 (Radar com até 8 ativos monitorados em cache) deve renderizar em menos de 3.0 segundos.
- **SC-002**: O ajuste de parâmetros no Simulador de Acumulação via `@st.fragment` deve atualizar os gráficos e KPIs em menos de 300 milissegundos sem causar reload na aplicação inteira.
- **SC-003**: 100% dos identificadores técnicos na interface visual são substituídos por nomes amigáveis em português, sem vazamento de strings brutas (ex: `t1_open`) para o usuário final.
- **SC-004**: 100% dos testes unitários da Feature 001 continuam passando sem regressão após a integração do novo layout e do suporte intraday.
- **SC-005**: Gráficos de barra em 100% de acerto nunca cortam o texto de porcentagem ou número de entradas em resoluções padrão desktop (1366x768 ou superior).

## Assumptions

- O Yahoo Finance gratuito oferece histórico de até 60 dias para timeframes de minutos (`5m`, `15m`, `30m`) e até 730 dias para base horária (`1h`), sendo aceitável a limitação temporal quando esses timeframes forem selecionados.
- Os cálculos do Simulador de Aportes assumem reinvestimento neutro de custos de corretagem para focar no ganho de capital e montagem de posição estatística.
- O tema institucional escuro é configurado diretamente em nível de componentes e estilos CSS integrados ao Streamlit, dispensando alterações globais no arquivo de configuração do sistema operacional do usuário.
