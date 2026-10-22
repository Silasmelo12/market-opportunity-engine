# Feature Specification: Suporte ao Timeframe 1h sem Erro 400 e Ocultação do Seletor de Direção no Simulador e Playbook

**Feature Branch**: `011-hourly-timeframe-and-direction-cleanup`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "1. faça essa solução sobre o timeframe de 1h. 2. retire o nome Compra, venda e ambos da aba simulador e playbook."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Simulação no Timeframe de 1 Hora sem Erro 400 (Priority: P1)

Como um operador ou pesquisador quantitativo,  
quero selecionar o tempo gráfico de **60 Minutos (1 Hora)** no Simulador e executar backtests ou otimizações com até 2 anos de histórico,  
para que o sistema carregue os candles horários e calcule os ciclos de trade sem disparar erro HTTP 400 ou falhas de dados vazios.

**Why this priority**: É o defeito funcional de execução relatado pelo usuário. Impede a utilização do timeframe de 1h no simulador.

**Independent Test**: Selecionar qualquer ativo (ex: `PETR4.SA` ou `NVDA`), escolher "60 Minutos (1 Hora)" no Simulador e clicar em "Simular". O sistema deve carregar os dados e exibir as métricas e a curva patrimonial com sucesso (HTTP 200).

**Acceptance Scenarios**:

1. **Given** que o usuário está no Simulador com o tempo gráfico "60 Minutos (1 Hora)" (`60m` / `1h`), **When** clica em "Simular", **Then** a requisição carrega os candles horários respeitando o teto de 730 dias do Yahoo Finance e retorna HTTP 200 com métricas completas.
2. **Given** que o usuário clica em "Mais Lucrativa" com tempo de 1h, **When** a otimização executa, **Then** as combinações são testadas sobre o histórico horário de até 730 dias sem falhas na API.

---

### User Story 2 - Ocultação Contextual do Seletor de Direção (Compra, Venda e Ambos) (Priority: P2)

Como um usuário navegando entre as abas do terminal,  
quero que o seletor de direção (**Compra**, **Venda** e **Ambos**) fique visível apenas nas abas onde ele tem função operacional (Radar e Gráfico),  
e que seja automaticamente ocultado nas abas **Simulador** e **Playbook**, para manter o cabeçalho limpo e evitar confusão de contexto.

**Why this priority**: Elimina ruído visual e inconsistência de interface em abas onde o seletor de direção não se aplica.

**Independent Test**: Clicar na aba "Simulador" e verificar que o botão segmented de "Compra, Venda, Ambos" desaparece do cabeçalho; clicar na aba "Playbook" e verificar que ele permanece oculto; clicar em "Radar" ou "Gráfico" e verificar que ele reaparece com o estado selecionado preservado.

**Acceptance Scenarios**:

1. **Given** que o usuário está no Radar ou Gráfico com o seletor de direção visível, **When** navega para a aba "Simulador", **Then** o componente `#global-direction-selector` é ocultado imediatamente.
2. **Given** que o usuário está no Simulador, **When** navega para o "Playbook", **Then** o componente `#global-direction-selector` permanece ocultado.
3. **Given** que o usuário está no Simulador ou Playbook, **When** retorna para "Radar" ou "Gráfico", **Then** o componente `#global-direction-selector` torna-se visível novamente mantendo a direção anteriormente selecionada.

---

### Edge Cases

- **Alternância rápida de abas**: A transição entre abas não deve causar travamento visual nem inconsistência na visibilidade do controle de direção.
- **Requisições de 1h com períodos maiores que 730d**: Caso o usuário envie `period="2y"` ou `period="5y"`, o backend deve ajustar automaticamente para `"730d"` (máximo suportado pelo Yahoo Finance para candles horários), prevenindo falha de download.
- **Normalização entre `60m` e `1h`**: A camada de dados deve tratar `"60m"` e `"1h"` de forma equivalente, garantindo compatibilidade entre componentes frontend e backend.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE reconhecer o intervalo `"60m"` como equivalente a `"1h"` e aplicar o teto de histórico de `"730d"` na tabela de limites do provedor de dados (`MAX_PERIODS`).
- **FR-002**: A camada de ingestão de dados (`DataLoader`) DEVE efetuar o download e cacheamento em Parquet de intervalos horários (`1h` / `60m`) limitando o período ao máximo de 730 dias para evitar recusas da API do Yahoo Finance.
- **FR-003**: Os endpoints `/api/simulate` e `/api/simulate/optimize` DEVEM processar requisições com `interval="60m"` ou `interval="1h"` retornando HTTP 200 com as séries causais e métricas de trade válidas.
- **FR-004**: O seletor de direção do cabeçalho (`#global-direction-selector`) DEVE ser visível exclusivamente nas abas "Radar" (`tab-radar`) e "Gráfico" (`tab-terminal`).
- **FR-005**: Ao alternar para a aba "Simulador" (`tab-simulator`) ou "Playbook" (`tab-playbook`), o seletor de direção DEVE ser ocultado da interface.
- **FR-006**: Ao retornar do Simulador ou Playbook para as abas Radar ou Gráfico, o seletor de direção DEVE ser reexibido preservando a seleção ativa anterior do usuário.

---

### Key Entities

- **TimeframeInterval**: Identificador de intervalo temporal da série (`5m`, `15m`, `30m`, `1h`, `60m`, `2h`, `4h`, `12h`, `1d`, `1wk`).
- **DirectionSelector**: Componente de interface de controle segmentado de direção com os botões `BUY` (Compra), `SELL` (Venda) e `BOTH` (Ambos).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das simulações executadas com o tempo gráfico de 1h (`60m`) retornam sucesso (HTTP 200) com série de candles preenchida e métricas apuradas, eliminando o erro HTTP 400.
- **SC-002**: O seletor de direção é ocultado com 0ms de atraso visual ao entrar no Simulador ou Playbook e restaurado ao entrar no Radar ou Gráfico.
- **SC-003**: Zero regressões na suíte de testes unitários do projeto.

---

## Assumptions

- O Yahoo Finance fornece com estabilidade até 730 dias para o intervalo horário (`1h` / `60m`).
- O estado de direção ativa (`state.activeDirection`) permanece inalterado em memória quando o controle é ocultado temporariamente nas abas Simulador e Playbook.
