# Feature Specification: B3 Spreadsheet Integration & Portfolio Tracking

**Feature Branch**: `018-b3-spreadsheet-integration`

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "Para facilitar todo o processo, eu baixei a planilha de movimentação do site da B3. e gostaria que a partir dela, voce criasse todos os dashboards, ao inves daquela planilha minha_carteira.csv seria a B3/movimentacao-2026-10-22-13-32-52.xlsx entendeu? antes de alterar qualquer coisa me comunique."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Integração e Leitura Automática da Planilha Oficial da B3 (Priority: P1)

Como investidor, quero que o sistema processe automaticamente minha planilha oficial de movimentação exportada da B3 (`.xlsx` em `B3/` ou via upload) em vez do arquivo manual `minha_carteira.csv`, para que todo o cálculo de patrimônio, custódia e proventos reflita fidedignamente o histórico da bolsa.

**Why this priority**: É a fundação do pedido. Sem o parser das 693+ linhas de movimentações da B3, nenhum dashboard conseguirá extrair a custódia líquida e o preço médio fiscal.

**Independent Test**: Pode ser testado independentemente executando o endpoint de leitura `/api/b3/custodia` ou carregando a planilha diretamente no backend/frontend, retornando a lista exata de ativos em custódia com quantidades e preços médios calculados.

**Acceptance Scenarios**:

1. **Given** que o arquivo `B3/movimentacao-2026-10-22-13-32-52.xlsx` está presente na pasta `B3/`, **When** o sistema inicializa ou o usuário clica em sincronizar, **Then** o sistema processa cronologicamente todas as linhas de Compra, Venda, Transferência e Proventos, apurando os ativos em custódia líquida (> 0) e seus respectivos Preços Médios fiscais ponderados.
2. **Given** o frontend web em execução, **When** o usuário arrasta ou faz upload de um novo arquivo `.xlsx` da B3 pelo botão de importação, **Then** o sistema aceita tanto `.xlsx` quanto `.csv`, atualizando a carteira e o armazenamento local de forma reativa.

---

### User Story 2 - Alimentação Completa da Aba Visão Geral com Dados da B3 (Priority: P1)

Como investidor, quero que a aba **Visão Geral** já existente (com suas sub-abas Resumo, Posições, Patrimônio e Metas) seja alimentada e enriquecida automaticamente pelos dados da planilha da B3, para que eu visualize meu Patrimônio Investido, Valor Atual a Mercado, Lucro/Prejuízo e Renda Passiva Recebida sem precisar digitar nada manualmente.

**Why this priority**: O usuário expressou preocupação direta com a preservação da aba Visão Geral. Ela deve permanecer visualmente familiar, porém abastecida com a riqueza analítica dos dados oficiais da B3.

**Independent Test**: Navegar para a aba "Visão Geral" e verificar se os cards de Resumo (Patrimônio Total, Custo de Aquisição, Variação R$ e %, Proventos Totais) e a tabela de Posições exibem os valores reais extraídos da B3.

**Acceptance Scenarios**:

1. **Given** os dados processados da B3, **When** o usuário acessa a aba Visão Geral (sub-aba Resumo), **Then** o card de Proventos Totais exibe o montante consolidado de dividendos, JCP e rendimentos de FIIs da planilha (R$ 683,39+), e o gráfico de alocação divide as classes (Ações, FIIs, BDRs) conforme a custódia real.
2. **Given** a sub-aba Posições da Visão Geral, **When** visualizada, **Then** lista os tickers reais em carteira (ex: PETR4, MXRF11, TGAR11, BRKM5, etc.) com suas quantidades, preços médios da B3, cotação atual e rentabilidade não realizada.

---

### User Story 3 - Sincronização com Radar, Terminal Gráfico e Rebalanceamento (Priority: P2)

Como investidor, quero que os ativos da minha planilha da B3 estejam disponíveis nos filtros do Radar de Oportunidades, no seletor do Terminal Gráfico (com linha de Preço Médio) e na aba Carteira (Rebalanceamento), para que eu possa analisar o timing estatístico das minhas ações e fundos reais.

**Why this priority**: Dá utilidade prática e quantitativa aos dados da B3 dentro do ecossistema do Market Engine.

**Independent Test**: Abrir o Radar ou o Terminal Gráfico, selecionar um ativo da carteira B3 (ex: PETR4) e confirmar que o gráfico exibe os sinais estatísticos junto com o preço médio do investidor.

**Acceptance Scenarios**:

1. **Given** a seleção de um ativo no Terminal Gráfico que pertence à carteira B3, **When** o gráfico de candles é renderizado, **Then** uma linha horizontal com o Preço Médio de aquisição é destacada para comparar com as cotações atuais e suportes/fundos estatísticos.
2. **Given** a aba Carteira (Rebalanceamento), **When** o usuário consulta as recomendações, **Then** as ordens sugeridas tomam como base a posição real da B3 e os caixas apurados.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer um parser robusto em Python (`src/data_loader/b3_parser.py`) capaz de ler planilhas Excel `.xlsx` e CSVs no padrão oficial de exportação de movimentações da B3 (com colunas `Entrada/Saída`, `Data`, `Movimentação`, `Produto`, `Instituição`, `Quantidade`, `Preço unitário`, `Valor da Operação`).
- **FR-002**: O parser DEVE calcular a posição líquida cronológica e o Preço Médio ponderado conforme as regras fiscais vigentes (compras agregam volume e custo; vendas reduzem quantidade mantendo o preço médio; zeragem reseta o preço médio).
- **FR-003**: O parser DEVE segregar e totalizar o histórico de Proventos (Dividendos, JCP e Rendimentos de Fundos Imobiliários).
- **FR-004**: A aba **Visão Geral** DEVE permanecer intacta em termos de layout e estrutura (Resumo, Posições, Patrimônio, Metas), consumindo agora a estrutura da B3 como fonte primária de dados.
- **FR-005**: A interface web DEVE disponibilizar no cabeçalho ou nas abas de carteira um controle que permita selecionar ou carregar o arquivo `.xlsx` da B3, além de sincronizar automaticamente com arquivos localizados na pasta `B3/`.
- **FR-006**: Os tickers extraídos da B3 DEVEM ser automaticamente normalizados para sufixos de mercado compatíveis com a API de cotações (ex: `PETR4` -> `PETR4.SA`, BDRs e FIIs correspondentes).
- **FR-007**: A integração NÃO DEVE quebrar compatibilidade com o formato legado `minha_carteira.csv` caso o usuário opte por carregar um CSV manual simples.

### Key Entities & Data Schemas

- **B3Movement**:
  - `data`: string/datetime da operação
  - `tipo_movimentacao`: Compra, Venda, Dividendo, JCP, Rendimento, etc.
  - `ticker`: código do ativo limpo (ex: `PETR4`, `MXRF11`)
  - `quantidade`: float
  - `preco_unitario`: float
  - `valor_total`: float
- **B3Position**:
  - `ticker`: string
  - `ticker_sa`: string com sufixo `.SA` para cotações
  - `quantidade`: float
  - `preco_medio`: float
  - `total_investido`: float
  - `tipo_ativo`: Ação, FII ou BDR
- **B3PortfolioSummary**:
  - `posicoes`: Dict[str, B3Position]
  - `total_aportado`: float
  - `total_proventos`: float
  - `historico_proventos_mensal`: List[Dict]

---

## Non-Functional Requirements

- **NFR-001**: O parsing de uma planilha com até 5.000 linhas da B3 deve levar menos de 500ms no backend.
- **NFR-002**: Tolerância a caracteres especiais, acentuação e formatos numéricos brasileiros (vírgula como separador decimal).
- **NFR-003**: Todas as alterações devem ser comunicadas e validadas antes de modificar qualquer código de produção.
