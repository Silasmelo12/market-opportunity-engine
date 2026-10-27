# Feature Specification: Redesign da Interface Web Estilo Investidor10

**Feature Branch**: `021-investidor10-ui`
**Created**: 2026-10-23
**Last Updated**: 2026-10-24
**Status**: Fase 1 Homologada | Fase 2 (2A e 2B) Especificada para Execucao Incremental
**Input**: Requisitos de UX/UI lapidados a partir da auditoria tecnica, diretrizes de produto e homologacao visual da Visao Geral.

---

## 1. Visao Geral e Historico das Fases

O objetivo deste projeto e modernizar a arquitetura de informacao e os componentes visuais do **Market Opportunity & Bottom Statistical Engine** com base nas diretrizes do [DESIGN.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/DESIGN.md) (estilo Investidor10), garantindo:
1. **Semantica Financeira Precisa**: Proibicao de terminologias vagas ou enganosas.
2. **Separacao Funcional Clara**: Distincao objetiva entre Acompanhamento Patrimonial (Minha Carteira) e Investigacao Tecnica (Analise Quantitativa).
3. **Fidelidade aos Dados e Transparencia de Limitacoes**: Nenhuma metrica ficticia ou estimativa silenciosa.
4. **Execucao Incremental em Fases Independentes**:
   - **Fase 1 (Concluida e Homologada)**: Tela-Piloto da Visao Geral (`#tab-overview`), com 4 KPIs auditados, graficos de Aportes e Alocacao por Classe via Plotly, suporte dual claro/escuro e eliminacao de metricas residuais sem suporte contabil.
   - **Fase 2A (Especificada)**: Reorganizacao da Navegacao Global em Dois Ambientes Operacionais, subnavegacao contextual, precedencia rigorosa de roteamento (URL Hash > LocalStorage > Default) e redimensionamento de graficos.
   - **Fase 2B (Futura / Trabalho Separado)**: Interacoes contextuais profundas entre telas (Carteira -> Grafico com ticker selecionado, Radar -> Simulador e atalhos contextuais para o Playbook).

---

## 2. Auditoria e Semantica Rigorosa dos KPIs da Visao Geral (Fase 1 - Homologada)

A homologacao da Fase 1 estabeleceu a semantica rigorosa dos 4 cards de topo em `src/web/app.js`:

### Mapeamento Tecnico de Variaveis em `app.js`:
- `costBasis = sum(shares * avg_price)`: Soma estrita do custo de aquisicao das **posicoes atualmente em custodia**. Nao inclui ativos encerrados nem caixa livre.
- `marketValue = sum(shares * current_price)`: Valor a mercado atual das posicoes em custodia.
- `capitalGain = marketValue - costBasis`: Ganho ou perda de capital **nao realizado (em aberto)** das posicoes atuais.
- `priceReturnPct = (capitalGain / costBasis) * 100`: Rentabilidade de preco nao realizada sobre o custo da custodia atual (exibe `N/A` com nota "Sem custo em custodia" quando `costBasis === 0`).
- `cash = state.portfolioState.availableCash || 0`: Saldo em dinheiro liquido livre.
- `totalEquity = cash + marketValue`: Patrimonio bruto total (posicoes a mercado + caixa livre).
- `totalIncome = state.portfolioState.b3TotalIncome`: Soma bruta de proventos nominais historicos registrados nos extratos importados.

### Definicao dos Quatro KPIs Aprovados:
1. **Card 1: Patrimonio Total**: `totalEquity = cash + marketValue` com sub-rotulo "Custo em custodia: R$ X".
2. **Card 2: Resultado Nao Realizado**: `capitalGain = marketValue - costBasis` com sub-rotulo "Saldo bruto s/ IR | Sobre custo: R$ X".
3. **Card 3: Proventos Registrados no Historico Importado**: `totalIncome` com identificacao do numero real de meses com registros ("X meses com registros"). *O badge arbitrario `#overview-card5-yield` foi eliminado por ausencia de sustentacao contabil*.
4. **Card 4: Ativos Acima do Preco Medio**: Proporcao de ativos com cotacao > preco medio, com barra bicoloreada e legenda descritiva de contagem de papeis.

---

## 3. Diretriz para Cotacoes Falhas, Desatualizadas ou Estimadas

1. **Proibicao de Substituicao Silenciosa**: Proibido utilizar o preco medio (`average_buy_price`) como se fosse a cotacao a mercado sem sinalizar visualmente a contingencia.
2. **Sinalizacao de Fallback**: Quando `/api/portfolio/quotes` falhar para um ticker ou retornar preco zerado/invalido:
   - Exibir badge explicativo no Card 4 e subtitulo com a quantidade de ativos elegiveis com cotacao apurada.
3. **Comunicacao de Latencia**: O rodape da secao de KPIs da Visao Geral exibe aviso de que as cotacoes a mercado via Yahoo Finance estao sujeitas a latencia operacional.

---

## 4. Diretriz de Proventos e Cobertura Historica

1. **Rotulo Condicionado a Cobertura Real**:
   - Proibido denominar "Proventos 12M" quando o usuario tiver importado intervalo menor que 12 meses.
   - O indicador exibe o montante consolidado do extrato sob o rotulo "Proventos registrados no historico importado", e a quantidade de competencias com lancamentos e explicitada ("X meses com registros").
2. **Diferenciacao Estrita de Valores Realizados vs. Projetados**:
   - Apenas lancamentos constantes nas planilhas de movimentacao da B3 sao exibidos. Projecoes futuras nao sao misturadas aos valores realizados.

---

## 5. Fase 2: Arquitetura de Informacao e Navegacao Global em Dois Ambientes

### 5.1 Os Dois Ambientes Operacionais (Modelos Mentais)
A plataforma atende a duas atividades financeiras distintas que nao devem concorrer na mesma barra plana de navegacao:
1. **Minha Carteira (Acompanhamento Patrimonial & Custodia)**: Foco no patrimonio acumulado, alocacao em classes de ativos, evolucao dos aportes e historico de proventos da B3.
2. **Analise Quantitativa (Terminal Quant & Estrategias)**: Foco na identificacao de oportunidades estatisticas, sinais de fundo/topo 2x2, analise grafica tecnica de candlestick, backtesting e catalogo de estrategias.

### 5.2 Mapeamento das 8 Funcionalidades Atuais nos Dois Ambientes
Nenhuma funcionalidade existente sera removida. O ambiente ativo no cabecalho determina o conjunto de subabas contextuais visiveis:

```
Ambiente 1: MINHA CARTEIRA
├── 1.1 Visao Geral            (#tab-overview / #tab-pane-resumo) - Dashboard executivo da Fase 1
├── 1.2 Posicoes & Custodia     (#tab-portfolio / #tab-pane-posicoes) - Detalhamento por classe e boleta
├── 1.3 Proventos & Renda       (#tab-pane-proventos) - Grafico detalhado mensal/anual de proventos
└── 1.4 Evolucao Patrimonial    (#tab-pane-patrimonio) - Historico analitico cronologico ampliado

Ambiente 2: ANALISE QUANTITATIVA
├── 2.1 Radar de Mercado        (#tab-pane-radar) - Varredura de sinais de compra/venda e scores
├── 2.2 Grafico Interativo      (#tab-terminal) - Terminal TradingView com overlays de estrategias
├── 2.3 Simulador & Backtest    (#tab-simulator) - Backtest de trade compra->venda e acumulacao DCA
└── 2.4 Playbook                (#tab-playbook) - Catalogo tecnico das 48 estrategias documentadas
```

### 5.3 Diferenciacao Semantica e Preservacao de "Evolucao Patrimonial"
- **Diferenciacao**:
  - Na **Visao Geral**, o grafico "Aportes acumulados" (`#overview-stacked-bar-chart`) e um resumo executivo dos aportes e patrimonio das ultimas 12 competencias.
  - Na subarea **Evolucao Patrimonial** (`#tab-pane-patrimonio`), o container `#chart-patrimonio-detailed` destina-se a serie historica cronologica ampliada de longo prazo.
- **Preservacao sem Redundancia Desnecessaria**:
  - A Evolucao Patrimonial permanece acessivel como subaba de Minha Carteira e por meio do link contextual "Ver serie completa" no card de Aportes da Visao Geral.
  - Nenhum grafico ou serie existente e excluido.

### 5.4 Precedencia Rigorosa de Roteamento e Sincronizacao de Historico
A resolucao do destino ativo na inicializacao e navegacao deve seguir estritamente a seguinte ordem:
1. **Prioridade 1 (Precedencia Maxima): Rota / Hash Explicito na URL**:
   - Se a URL contiver hash valido (ex.: `#resumo`, `#posicoes`, `#proventos`, `#patrimonio`, `#radar`, `#simulador`, `#playbook`, `#tradingview` ou as novas rotas `#carteira/visao-geral`, etc.), este determina imediatamente o ambiente e a subaba ativa, sobrepondo qualquer preferencia armazenada localmente.
2. **Prioridade 2 (Fallback): Preferencia Armazenada em `localStorage`**:
   - Apenas se a URL for raiz `/` sem hash (ou com hash vazio), o sistema le `mo_active_tab` e `mo_active_pillar` do `localStorage` para restaurar o ultimo estado utilizado.
3. **Prioridade 3 (Default do Sistema)**:
   - Se nao houver hash e o `localStorage` estiver vazio/invalido, o padrao e o ambiente **Minha Carteira** na subaba **Visao Geral**.
4. **Sincronizacao com o Historico do Navegador (`popstate` / `hashchange`)**:
   - Navegacoes via botoes "Voltar" e "Avancar" do navegador, bem como reloads (F5), devem atualizar em sincronia:
     - O seletor de ambiente ativo no cabecalho;
     - A barra de subnavegacao contextual exibida;
     - O painel (`.tab-view`) ativo no DOM (garantindo exatamente 1 painel visivel por vez);
     - O titulo/ARIA attributes correspondentes (`aria-selected="true"`).

### 5.5 Divisao em Duas Entregas Independentes

#### Entrega Fase 2A: Navegacao Global, Subnavegacao Contextual e Roteamento
- **Escopo Autorizado da 2A**:
  - Implementacao visual e funcional do alternador de ambientes no topo (Minha Carteira vs. Analise Quantitativa).
  - Subnavegacao dinamica associada ao ambiente ativo.
  - Implementacao da precedencia estrita de rotas (URL Hash > LocalStorage > Default).
  - Sincronizacao de historico (`popstate`, recarregamento, botao voltar/avancar).
  - Redimensionamento automatico dos graficos Plotly e TradingView na abertura (`resizeChartResponsive`, `fitContent`, `Plotly.relayout`).
  - Preservacao rigorosa de todos os IDs de contrato do DOM e ausencia de IDs duplicados.
  - Nenhuma tela interna recebe redesign visual nesta etapa.
- **Fica Fora da 2A**:
  - Novos benchmarks (CDI, Ibovespa).
  - Projecoes futuras de proventos ou datas-com.
  - Alteracoes nas telas internas do Radar, Simulador, Posicoes ou Playbook.
  - Deep-linking de ativos especificos da carteira para o grafico (adiado para a Fase 2B).

#### Entrega Fase 2B: Integracao Contextual entre Telas (Trabalho Separado)
- **Escopo Planejado para a 2B**:
  - *Carteira -> Grafico*: Botao na linha de posicao para abrir o Grafico TradingView com o ticker selecionado e botao de retorno funcional ("Voltar para Custodia").
  - *Radar -> Grafico e Simulador*: Botoes na linha do Radar para carregar o ticker no Grafico ou no Simulador com o par campeao.
  - *Playbook Contextual*: Atalho a partir dos badges de estrategias no Radar/Grafico para exibir a ficha tecnica no Playbook.
- **Dependencias Tecnicas Identificadas para a 2B (Ainda Nao Comprovadas)**:
  - Criacao de funcao unificada de despacho `navigateToChart(ticker, options)`. Atualmente, `elements.inputTicker` e manipulado via evento de input isolado.
  - Parametros de estrategia no Simulador dependem de sincronizacao entre `#sim-buy-strategy`, `#sim-sell-strategy` e o catalogo retornado por `/api/strategies`.
  - O Playbook atual e um bloco estatico de HTML sem ancoras por estrategia (`id="strategy-xxx"`).

---

## 6. Criterios de Aceite da Fase 2A (Verificaveis)

| ID | Criterio | Tipo de Validacao | Comando / Metodo de Verificacao | Condicao de Aprovacao |
|---|---|---|---|---|
| **AC-2A-01** | **Dois Ambientes Distintos** | Inspecao DOM / E2E | Verificacao de seletores de ambiente no topo | Alternador permite alternar entre "Minha Carteira" e "Analise Quantitativa" |
| **AC-2A-02** | **Subnavegacao Contextual** | E2E Playwright | `pytest tests/e2e/test_dashboard_navigation.py` | Ambiente "Minha Carteira" exibe as 4 subabas de carteira; "Analise Quantitativa" exibe as 4 subabas quantitativas |
| **AC-2A-03** | **Todas as 8 Areas Acessiveis** | E2E Playwright | Iteracao sobre todas as 8 rotas | Cada subaba torna visivel exatamente o seu respectivo painel (`#tab-overview`, `#tab-portfolio`, `#tab-pane-proventos`, `#tab-pane-patrimonio`, `#tab-pane-radar`, `#tab-terminal`, `#tab-simulator`, `#tab-playbook`) |
| **AC-2A-04** | **Precedencia de Rota (Hash > Storage)** | E2E Playwright | Navegar com hash na URL tendo preferencia oposta no `localStorage` | O hash da URL prevalece e abre a tela solicitada |
| **AC-2A-05** | **Sincronia de Historico e Reload** | E2E Playwright | Teste de recarregamento (F5) e navegacao Voltar/Avancar | O ambiente, a subnav e o painel visivel permanecem perfeitamente alinhados |
| **AC-2A-06** | **Painel Unico Ativo** | E2E Playwright | `document.querySelectorAll('.tab-view:not(.hidden)').length` | Exatamente 1 painel visivel a qualquer momento |
| **AC-2A-07** | **Zero IDs Duplicados** | E2E Playwright | Varredura de unicidade de IDs no DOM | Nenhum ID repetido |
| **AC-2A-08** | **Redimensionamento dos Graficos** | E2E Playwright | Abertura do TradingView e dos graficos Plotly | Grafico ajusta largura ao container sem colapsar para 0px (`fitContent` e `Plotly.relayout` executados) |
| **AC-2A-09** | **Preservacao de Temas e Acessibilidade** | E2E Playwright | Alternador de tema `#btn-theme-toggle` | Alternancia clara/escura funciona perfeitamente nos dois ambientes; foco via teclado (`Tab` / `Enter`) funcional |
| **AC-2A-10** | **Escopo Restrito (Sem Redesign Interno)** | Inspecao de Diff | `git diff --stat` | Nenhuma alteracao de layout nas tabelas internas do Radar, Simulador ou Playbook |

---

## 7. Baseline de Testes e Preservacao de Falhas Conhecidas

Para assegurar rigor tecnico sem enfraquecer testes ou mascarar falhas:
1. **Suite Unitaria (`tests/unit/`)**:
   - Baseline: **95 aprovados, 2 skipped** (testes de planilhas locais ausentes em `test_b3_parser.py`). Tolerancia zero a novas falhas.
2. **Suite E2E de Navegacao (`tests/e2e/test_dashboard_navigation.py`)**:
   - Baseline: **6 aprovados**. Deve ser expandido para validar a nova hierarquia em 2 pilares, precedencia de hash e sincronia de historico.
3. **Suite E2E de Proventos (`tests/e2e/test_proventos_layout.py`) - Baseline Separado de Falhas Conhecidas**:
   - Baseline: **3 falhas conhecidas** decorrentes de restricoes geometricas de layout herdadas de versoes anteriores da aba proventos (`test_proventos_chart_stays_inside_its_card`, `test_proventos_toggle_and_labels`, `test_no_mojibake_in_visible_text`).
   - **Diretriz Mandatoria**: Nao enfraquecer assertivas nem declarar toda a suite E2E aprovada com base apenas no arquivo de navegacao do dashboard. As falhas de `test_proventos_layout.py` devem ser mantidas documentadas e tratadas apenas quando houver intervencao especifica na aba de proventos.


---

## 8. Fase 3A — Especificação da Identidade Visual Quant-Executiva e Limites de Escopo

### 8.1 Objetivos e Inspirações Visuais Aprovadas (Diretriz Visual vs. Escopo de Dados)
A Fase 3A estabelece a governança visual e o conjunto de design tokens para unificar o sistema sob a **Identidade Quant-Executiva**:
1. **Pilar "Minha Carteira" (Referência Investidor10 Clean)**:
   - Apresentação executiva com cartões respirados, tipografia nítida, KPIs principais bem destacados e agrupamento por classes de ativos em acordeões, garantindo leitura rápida da posição patrimonial.
2. **Pilar "Análise Quantitativa" (Inspirações Visuais: JSE Stock Radar & Market Insight)**:
   - **Diretriz de Design**: Superfícies grafite/navy profundas, acentos funcionais em ciano e verde-azulado, tabelas de alta densidade perfeitamente legíveis e cartões de métricas consistentes.
   - **Separação Estrita entre Design e Funcionalidades Novas**:
     - As imagens de referência servem como **norte estético** (paleta, contraste, tipografia, bordas e espaçamentos), e **NÃO** como justificativa automática para introdução de novas funcionalidades ou cálculos.
     - **Não serão criados**: medidores circulares de cobertura sem dados reais (`% Coverage`), barras fictícias de breadth de mercado, carrosséis de cotações em tempo real (*ticker tape*) externos, boletas simuladas de compra/venda ou quaisquer dados que não tenham API comprovada, fonte confiável e utilidade testada.
     - **Reutilização Integral de Dados Existentes**: O Radar de Mercado continua utilizando exclusivamente os dados providos por `/api/radar` (4 KPIs existentes do deck superior: Oportunidades em Compra, Topos em Alerta, Maior Assimetria e Regime/Horário). O Gráfico Interativo continua utilizando os candles e sinais reais de `/api/analyze`.

### 8.2 Diagnóstico da Auditoria Impeccable (Tratamento Racional)
A auditoria técnica (`impeccable detect src/web`) serve como ferramenta de **diagnóstico de qualidade**, não como mandato para intervenções cegas:
1. **Dissonância Bipolar de Superfícies**: Foco principal da Fase 3B — corrigir a incompatibilidade entre classes Tailwind estáticas (`bg-white` vs `bg-fintech-surface`), permitindo que ambos os temas (claro e escuro) funcionem harmonicamente por meio de tokens semânticos universais (`var(--canvas)`, `var(--surface)`, `var(--border)`, `var(--text-main)`).
2. **Piso Tipográfico e Legibilidade**: Adequação orientada a legibilidade, eliminando fontes excessivamente miniaturizadas (`text-[10px]`) em cabeçalhos de tabelas e metadados funcionais, estabelecendo o piso de 11px onde houver prejuízo à leitura.
3. **Cartões e Profundidade**: Desaninhamento cirúrgico de cartões redundantes (`nested-cards`) onde criam ruído visual, preservando a semântica dos agrupamentos existentes.
4. **Foco e Teclado**: Introdução sistemática de `:focus-visible` em controles e formulários para conformidade WCAG AA.

### 8.3 Tokens Universais e Regras Estruturais
1. **Consumo Exclusivo de Tokens Semânticos**: A interface migra gradualmente do uso de cores hexadecimais fixas para as variáveis CSS semânticas documentadas em `DESIGN.md`.
2. **Preservação de IDs de Contrato e Estrutura**: Todos os identificadores de painéis (`tab-overview`, `tab-portfolio`, `tab-pane-radar`, `tab-terminal`, `tab-simulator`, `tab-playbook`), inputs e botões de ação são preservados na íntegra.
3. **Semântica Não Dependente Apenas de Cor**: Todo indicador direcional mantém reforço por texto ou glifo (`▲` / `▼`).

### 8.4 Critérios de Aceitação da Fase 3A (Verificáveis)

| ID | Critério | Tipo de Validação | Comando / Método de Verificação | Condição de Aprovação |
| :--- | :--- | :--- | :--- | :--- |
| **AC-3A-01** | **Documentação Completa de Tokens** | Inspeção de Documento | Leitura de `DESIGN.md` | Tokens para superfícies, tipografia, bordas, sombras e botões documentados em ambos os temas. |
| **AC-3A-02** | **Limites Claros de Escopo (Sem Dados Fictícios)** | Inspeção de Especificação | Verificação de `spec.md` e `plan.md` | Rejeição explícita de novos indicadores sem dados comprovados (sem medidores fictícios de coverage ou tickers externos). |
| **AC-3A-03** | **Reutilização de Dados Existentes** | Inspeção de Contratos | Confronto com `/api/radar` e `/api/analyze` | Toda a renovação visual do Radar e Gráfico consome exclusivamente os endpoints existentes. |
| **AC-3A-04** | **Piso Tipográfico Racional** | Inspeção de Regras | Verificação em `DESIGN.md` | Piso de 11px formalizado para cabeçalhos e metadados funcionais. |
| **AC-3A-05** | **Dupla Codificação em Sinais Quantitativos** | Verificação Semântica | Inspeção de contratos de UI | Sinais mantêm texto/glifo explícito junto com a cor. |
| **AC-3A-06** | **Foco e Acessibilidade (WCAG AA)** | Verificação de Tokens | Inspeção de `:focus-visible` e tokens de contraste | Contraste mínimo de 4.5:1 documentado para pares texto/fundo. |
| **AC-3A-07** | **Preservação Integral de Código e Cálculos** | Conformidade de Escopo | `git diff --stat` | Nenhuma linha de código JS/HTML/CSS alterada nesta fase documental. |
