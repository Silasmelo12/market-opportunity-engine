# Feature Specification: B3 Multi-Spreadsheet Import & Production Cleanup

**Feature Branch**: `019-b3-multi-spreadsheet-import`

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "pode remover esse sincronizar B3, pois imagine que isso vai para produção futuramente. crie o /speckit-specify dessa funcionalidade de seleção multipla"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Importação Unificada de Múltiplas Planilhas B3 via Botão Único (Priority: P1) 🎯 MVP

Como investidor na aplicação em produção, quero poder clicar em um único botão de importação e selecionar múltiplos arquivos de uma só vez (ex: `negociacao.xlsx` e `movimentacao.xlsx`, ou múltiplos extratos mensais), para que o sistema leia, interprete e consolide tudo automaticamente em uma carteira unificada.

**Why this priority**: É a funcionalidade central solicitada. Usuários em produção fazem upload direto pelo navegador através de arquivos locais de sua máquina, sem depender de pastas locais do servidor.

**Independent Test**: Clicar no botão "Importar B3 / CSV", selecionar simultaneamente os dois arquivos `B3/negociacao desde 04-08-2026.xlsx` e `B3/movimentacao desde 04-08-2026.xlsx` e verificar se a API processa a combinação e exibe tanto as operações de negociação (ex: TSLA34) quanto os proventos e movimentações do extrato.

**Acceptance Scenarios**:

1. **Given** que o usuário clica no botão de importação, **When** o seletor de arquivos do sistema operacional abre, **Then** o campo de arquivo permite seleção múltipla de arquivos (`multiple`, aceitando `.xlsx`, `.xls`, `.csv`).
2. **Given** múltiplos arquivos selecionados, **When** o upload é disparado, **Then** o backend processa cada planilha de acordo com seu layout (Movimentação vs Negociação), agrega os resultados cronologicamente e retorna o total consolidado de ativos em custódia e proventos acumulados.

---

### User Story 2 - Suporte Nativo a Planilhas de "Negociação - Resumo" da B3 (Priority: P1)

Como investidor, quero que o parser entenda nativamente a planilha oficial de **Negociação - Resumo** da B3 (colunas `Código de Negociação`, `Quantidade (Compra)`, `Quantidade (Venda)`, `Quantidade (Líquida)`, `Preço Médio (Compra)`, etc.), para que compras e vendas executadas no pregão sejam computadas mesmo quando o extrato de movimentação não cobrir o histórico.

**Why this priority**: A B3 gera planilhas separadas de Negociação e Movimentação. O motor precisa suportar ambos os formatos de forma transparente.

**Independent Test**: Executar teste unitário em `tests/unit/test_b3_parser.py` fornecendo o arquivo `B3/negociacao desde 04-08-2026.xlsx` e validando a extração das posições líquidas e preços médios informados pela B3.

**Acceptance Scenarios**:

1. **Given** uma planilha com a aba `Negociação - Resumo`, **When** o parser é executado, **Then** ele identifica os ativos com `Quantidade (Líquida) > 0`, normaliza os tickers (ex: `TSLA34` -> `TSLA34.SA`), atribui o Preço Médio de Compra e ignora ativos com saldo zero ou instrumentos futuros zerados (ex: `WINQ26`).
2. **Given** uma combinação de planilha de Negociação e planilha de Movimentação, **When** ambas são processadas juntas, **Then** os proventos da movimentação são somados e as posições de negociação são consolidadas sem duplicação de dados.

---

### User Story 3 - Remoção do Botão "Sincronizar B3" (Ajuste para Produção) (Priority: P2)

Como mantenedor do sistema pronto para produção na nuvem, quero que o botão de sincronização com o disco local do servidor (`Sincronizar B3`) seja removido da interface e seus endpoints restritos ou isolados, garantindo que a aplicação seja 100% voltada para upload pelo usuário no navegador.

**Why this priority**: Em ambientes de produção (Docker, Cloud, VPS), o usuário acessa o sistema pelo browser e envia suas próprias planilhas; caminhos locais de disco não existem no cliente.

**Independent Test**: Inspecionar a interface web e confirmar que o botão "Sincronizar B3" não está visível, restando apenas o botão limpo e universal "Importar B3 / CSV".

**Acceptance Scenarios**:

1. **Given** a aba Carteira e a aba Visão Geral, **When** o usuário visualiza as ações de importação, **Then** apenas o botão unificado de importação com suporte múltiplo está presente.
2. **Given** a inicialização da aplicação sem arquivos prévios no LocalStorage, **When** a página carrega, **Then** ela não falha nem gera alertas de erro por ausência de arquivos em disco no servidor.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O input de arquivo em `src/web/index.html` DEVE conter o atributo `multiple` e aceitar `.xlsx, .xls, .csv`.
- **FR-002**: O backend em `src/api/server.py` DEVE disponibilizar endpoint `POST /api/b3/parse` aceitando uma lista de arquivos (`files: List[UploadFile] = File(...)`).
- **FR-003**: O módulo `src/data_loader/b3_parser.py` DEVE detectar automaticamente o tipo de cada arquivo B3:
  - Tipo A: **Movimentação** (`Data`, `Movimentação`, `Produto`, `Valor da Operação`, etc.)
  - Tipo B: **Negociação** (`Código de Negociação`, `Quantidade (Compra)`, `Quantidade (Líquida)`, `Preço Médio (Compra)`, etc.)
  - Tipo C: **CSV Legado de Carteira** (`Ticker, Quantidade, Preço Médio`)
- **FR-004**: O parser DEVE consolidar todos os arquivos enviados em um único objeto de resposta `B3ParseResult`:
  - Se houver planilhas de Negociação e Movimentação sobrepostas, a custódia prioritária e proventos devem ser unificados sem redundância.
- **FR-005**: O botão `btn-portfolio-sync-b3` DEVE ser removido da interface do usuário (`src/web/index.html` e `src/web/app.js`), mantendo o design limpo para produção.

---

## Non-Functional Requirements

- **NFR-001**: O processamento combinado de múltiplos arquivos no endpoint `POST /api/b3/parse` DEVE responder em menos de 1 segundo.
- **NFR-002**: A interface DEVE exibir toast ou barra de progresso durante o envio e parsing dos múltiplos arquivos.
