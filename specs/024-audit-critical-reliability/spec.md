# Feature Specification: Confiabilidade Crítica e Experiência Operacional

**Feature Branch**: `spec/024-audit-critical-reliability`

**Created**: 2026-10-27

**Status**: Draft

**Input**: User description: "Corrigir os problemas P0/P1 confirmados na auditoria de baseline, preservando a lógica financeira válida, melhorando a confiança dos dados e a experiência operacional, com testes e documentação."

## Contexto

A auditoria `docs/product-audit-baseline.md` confirmou falhas que impedem o uso confiável da plataforma com dados reais: importação B3 dependente de pacote ausente, caixa fictício após importação, simulação de acumulação que compra em sinais de venda, valuation que ignora `end_date`, radar com KPI inconsistente, gráfico de ranking que não renderiza, séries sintéticas exibidas como dados do usuário e superfícies de segurança/acessibilidade incompletas.

Esta feature trata apenas os problemas confirmados e seguros. Conversão cambial (BRL/USD), autenticação corporativa e redesenho amplo permanecem decisões pendentes e não serão inventados.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Importar extratos B3 com confiança (Priority: P1)

Como investidor, quero importar planilhas `.xlsx` da B3 e ver um patrimônio que reflita apenas os ativos e o caixa realmente informados, para não tomar decisões com valores inventados.

**Why this priority**: A importação é o principal caminho de entrada e hoje está bloqueada para o formato mais comum.

**Independent Test**: Em ambiente limpo, importar uma planilha `.xlsx` de fixture e conferir holdings, renda, caixa e patrimônio; repetir o mesmo arquivo e confirmar que a renda não duplica.

**Acceptance Scenarios**:

1. **Given** um ambiente com as dependências declaradas instaladas, **When** o usuário envia um `.xlsx` válido da B3, **Then** a importação conclui com holdings e renda coerentes, sem erro de pacote ausente.
2. **Given** uma importação B3 sem informação de caixa, **When** o resultado é aplicado, **Then** o caixa não permanece no valor padrão de R$ 10.000 e o patrimônio corresponde aos ativos importados.
3. **Given** o mesmo arquivo B3 enviado duas vezes na mesma importação, **When** o resultado é consolidado, **Then** os eventos e a renda não são contados em duplicidade.
4. **Given** uma carteira importada, **When** o usuário consulta o resumo, **Then** o caixa aparece como zero ou “não informado”, nunca como um valor fictício não sinalizado.

---

### User Story 2 - Simular acumulação sem look-ahead e sem comprar em vendas (Priority: P1)

Como analista, quero que o simulador de acumulação compre apenas em sinais de compra e valorize a posição no fim da janela solicitada, para que o backtest seja financeiramente válido.

**Why this priority**: O simulador produz resultados materialmente incorretos e viola o princípio de Zero Look-Ahead Bias.

**Independent Test**: Executar um cenário controlado com um BUY e um SELL e outro com `end_date` anterior ao último preço; comparar aportes, cotas, equity e preço final.

**Acceptance Scenarios**:

1. **Given** sinais de BUY e SELL no mesmo período, **When** a acumulação é simulada, **Then** apenas o BUY gera aporte e o número de aportes corresponde às compras executadas.
2. **Given** uma série com preços posteriores ao `end_date`, **When** a simulação é executada, **Then** a equity final usa o último preço dentro da janela.
3. **Given** uma simulação de acumulação, **When** os KPIs são exibidos, **Then** drawdown é calculado a partir da curva e métricas sem benchmark definido aparecem como indisponíveis, não como zero fabricado.

---

### User Story 3 - Ver o mesmo dado no radar, tabela e gráficos (Priority: P1)

Como usuário, quero que o deck executivo, a tabela e os gráficos mostrem a mesma informação, sem séries inventadas ou gráficos vazios.

**Why this priority**: Inconsistências entre componentes destroem a confiança e podem induzir a decisões erradas.

**Independent Test**: Abrir o radar com um item de win rate conhecido e comparar deck/tabela; abrir o gráfico de ranking e confirmar que ele renderiza; abrir uma carteira vazia e confirmar que não há série sintética não rotulada.

**Acceptance Scenarios**:

1. **Given** um item de radar com `historical_win_rate` igual a 43,5%, **When** o deck executivo é renderizado, **Then** ele exibe 43,5%, igual à tabela.
2. **Given** dados de estratégias disponíveis, **When** o gráfico de ranking é aberto, **Then** ele renderiza barras sem erro de console.
3. **Given** uma carteira sem timeline importada, **When** o resumo e proventos são abertos, **Then** o estado vazio é explícito e nenhuma série de 12 meses é apresentada como dado real.

---

### User Story 4 - Operar com segurança e acessibilidade básica (Priority: P2)

Como usuário, quero que a aplicação aceite apenas origens e arquivos previstos, tenha controles acessíveis e não exiba botões que não fazem nada.

**Why this priority**: A plataforma pode ser exposta publicamente; CORS amplo e upload sem limite aumentam o risco. Controles mortos e semântica incompleta reduzem a confiança.

**Independent Test**: Testar preflight de origem não autorizada, upload acima do limite/extensão inválida, navegação por teclado e leitura dos controles principais.

**Acceptance Scenarios**:

1. **Given** uma origem não permitida, **When** o navegador faz preflight para a API, **Then** a origem não é liberada.
2. **Given** um upload acima do limite ou com extensão não suportada, **When** a API recebe o arquivo, **Then** responde com erro claro antes do parsing.
3. **Given** as abas principais, **When** um leitor de tela ou teclado as percorre, **Then** cada painel tem semântica de `tabpanel` e os botões de ícone têm nome acessível.
4. **Given** a interface principal, **When** o usuário procura ações visíveis, **Then** não há controles sem handler ou alvo que aparentem funcionar.

---

### Edge Cases

- Upload de arquivo vazio, corrompido, extensão não suportada ou acima do limite.
- Arquivo B3 repetido integralmente e arquivos sobrepostos com períodos diferentes.
- Carteira sem caixa informado, com caixa manual e com ativos sem cotação.
- `end_date` anterior ao primeiro sinal, igual ao último bar e fora da série.
- Radar sem itens, com `historical_win_rate` ausente ou zero.
- Tema claro/escuro e viewport móvel com painéis e gráficos.
- Usuário sem JavaScript ou com Plotly indisponível: o estado deve ser legível e não simular dados.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST importar planilhas B3 `.xlsx` em ambiente limpo usando apenas dependências declaradas.
- **FR-002**: A importação B3 MUST NOT manter caixa fictício; caixa ausente MUST ser tratado como zero ou explicitamente “não informado”.
- **FR-003**: A consolidação de múltiplos arquivos B3 MUST deduplicar arquivos idênticos e não somar renda duplicada.
- **FR-004**: A simulação de acumulação MUST considerar apenas sinais de compra como aportes.
- **FR-005**: A valuation da simulação MUST usar o último preço dentro de `[start_date, end_date]`.
- **FR-006**: O drawdown da acumulação MUST ser derivado da curva de equity; métricas sem benchmark definido MUST aparecer como indisponíveis.
- **FR-007**: O deck do radar MUST usar `historical_win_rate` e exibir o mesmo valor da tabela.
- **FR-008**: O gráfico de ranking MUST renderizar quando houver dados, sem erro de console.
- **FR-009**: Estados vazios MUST NOT exibir séries, proventos ou patrimônio sintéticos sem rótulo explícito de demonstração.
- **FR-010**: A API MUST restringir CORS a origens configuradas e MUST limitar tamanho e extensão de uploads.
- **FR-011**: As abas MUST ter painéis com semântica `tabpanel` e associação ao controle; botões de ícone MUST ter nome acessível.
- **FR-012**: Controles visíveis sem comportamento MUST ser implementados ou removidos.
- **FR-013**: As mudanças MUST preservar rotas, IDs estáveis, contratos de dados válidos e o princípio de Zero Look-Ahead Bias.
- **FR-014**: Testes MUST cobrir cada correção P0/P1 e os estados de borda correspondentes.
- **FR-015**: A documentação de execução MUST registrar decisões, limitações e itens bloqueados.

### Key Entities

- **Resultado de importação B3**: holdings, renda total, renda mensal, timeline, arquivo e caixa associado.
- **Sinal de estratégia**: direção, preço de execução, barra e identificador da estratégia.
- **Resultado de simulação**: aportes, cotas, equity, preço final, drawdown e curva temporal.
- **Item de radar**: ativo, direção, win rate histórico, timing e estratégia.
- **Estado de interface**: dados, carregamento, erro, vazio e demonstração explícita.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos testes de importação `.xlsx` passam em ambiente limpo; nenhuma importação B3 sem caixa exibe R$ 10.000 de patrimônio fictício.
- **SC-002**: O cenário BUY+SELL passa a registrar exatamente 1 aporte e 10 cotas para R$ 100 a R$ 10; o cenário com `end_date` retorna R$ 150, não R$ 250.
- **SC-003**: O deck e a tabela do radar exibem o mesmo win rate em 100% dos itens com `historical_win_rate`.
- **SC-004**: O gráfico de ranking renderiza ao menos uma barra com dados e não registra `ReferenceError`.
- **SC-005**: Estados vazios não exibem nenhum valor sintético sem rótulo.
- **SC-006**: Preflight de origem não autorizada é rejeitado e upload acima do limite/extensão inválida retorna erro 4xx.
- **SC-007**: As 8 áreas mantêm navegação por teclado e sem overflow horizontal nas larguras de referência.

## Assumptions

- O produto pode operar localmente ou em deploy público; a configuração padrão deve ser segura para ambos.
- O caixa desconhecido será tratado como zero, com orientação para o usuário informar o valor manualmente.
- A moeda-base e a fonte de câmbio não estão definidas; conversão BRL/USD fica fora desta feature e será registrada como decisão pendente.
- O modelo de autenticação não está definido; esta feature limita CORS e uploads, sem inventar um provedor de identidade.
- O Streamlit é legado e não será removido nesta feature.
- Não serão adicionados dados fictícios, bibliotecas visuais ou dependências não justificadas.

## Out of Scope

- Conversão cambial e rebalanceamento multi-moeda.
- Autenticação corporativa, SSO ou gestão de usuários.
- Redesenho completo da SPA, troca de stack ou remoção do legado Streamlit.
- Novas funcionalidades de produto não previstas na auditoria.
