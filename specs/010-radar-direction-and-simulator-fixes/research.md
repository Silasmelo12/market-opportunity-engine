# Research & Technical Decisions: Correção do Radar e Seletor de Modelo de Ciclo (1x vs Multi-Buy)

**Feature**: `010-radar-direction-and-simulator-fixes`  
**Date**: 2026-10-21  

---

## 1. Pesquisa 1: Mecanismo de Atualização Reativa da Direção no Radar

### Problema Identificado
Em `src/web/app.js` (linha 394), o manipulador de clique dos botões de direção ("Compra", "Venda", "Ambos") tentava acessar `state.lastRadarData`, variável que não existe no sistema (o estado real é gravado em `state.lastRadarPage`). Além disso, o backend `/api/radar` filtra no servidor por direção (`direction=BUY` inicial), de modo que os dados de Venda não estão no cliente no primeiro carregamento. Clicar em "Venda" não disparava `loadRadarData()`, tornando os botões inertes.

### Decisão Técnica
1. **Reset de Página**: Ao trocar a direção, redefinir `state.radarPage = 1` para iniciar na primeira página do novo filtro.
2. **Disparo Imediato de `loadRadarData(false)`**: Se o usuário estiver na aba do Radar (`state.activeTab === 'tab-radar'`), disparar imediatamente a busca com a chave de cache correspondente (`${tf}_${cat}_p1_${dir}_${stratCsv}`).
3. **Atualização Dinâmica do Dropdown de Estratégias**: Invocar `renderRadarStratMenu()`, que filtra o catálogo de estratégias de acordo com a direção ativa (`BUY`, `SELL` ou `BOTH`), garantindo que o menu só apresente estratégias relevantes.

### Alternativas Consideradas
- *Filtragem puramente client-side*: Rejeitada porque o backend pagina e filtra no servidor. Para suportar 150+ ativos em menos de 200ms com baixo consumo de memória, os itens de Venda só devem ser computados sob demanda pelo backend.

---

## 2. Pesquisa 2: Seletor de Modelo de Ciclo (`single_buy` vs `multi_buy`)

### Problema Identificado
O usuário apreciou tanto o modelo de **Compra Única (1x por Ciclo)** quanto o modelo de **Acumulação Multi-Buy (Nx por Ciclo)** e deseja poder alternar entre eles tanto no Simulador quanto no Otimizador ("Mais Lucrativa"). Hoje, o Simulador executa sempre Multi-Buy e o Otimizador executava Compra Única em loop simplificado, gerando a divergência observada (+22.5% vs +7.8%).

### Decisão Técnica
1. **Contrato de API (`cycle_entry_mode`)**:
   Adicionar o campo `cycle_entry_mode: str = "multi_buy"` (valores permitidos: `"multi_buy"` | `"single_buy"`) nos contratos Pydantic:
   - `SimulateRequest`
   - `OptimizeCombinationsRequest`
2. **Motor no Backend (`accumulation_simulator.py`)**:
   - `simulate_cycle_trade`:
     - Se `cycle_entry_mode == "single_buy"`: Enquanto `in_pos == True`, qualquer novo sinal de compra é sumariamente ignorado. O trade é encerrado e apurado no sinal de venda com a cota da 1ª compra.
     - Se `cycle_entry_mode == "multi_buy"`: Comportamento existente com compras adicionais acumulando cotas e recalculando preço médio ponderado.
   - `optimize_strategy_pairs`:
     - Parametrizar a rotina de ranking para receber `cycle_entry_mode`.
     - No modo `single_buy`: roda o modelo de 1 entrada por trade.
     - No modo `multi_buy`: roda o modelo multi-buy acumulado.
3. **Frontend (`index.html` e `app.js`)**:
   - Adicionar dropdown no painel do Simulador: `<select id="sim-cycle-mode">` com as opções:
     - `multi_buy`: "Acumulação Multi-Buy ($K$ Compras)" (Padrão)
     - `single_buy`: "Compra Única (1x por Ciclo)"
   - `runOptimizer()` e `runSimulation()` leem `sim-cycle-mode` e enviam no payload.
   - O card da campeã exibe um badge contextual do modo (ex: `1x Compra Única` ou `Nx Multi-Buy`).

### Alternativas Consideradas
- *Manter apenas uma abordagem fixa*: Rejeitada pela exigência explícita do usuário de selecionar livremente qualquer uma das duas filosofias.

---

## 3. Pesquisa 3: Sincronização Fiel de Tempo Gráfico e Métricas no Otimizador

### Problema Identificado
Em `runOptimizer()`, o frontend passava `interval: state.currentTimeframe` (tempo gráfico do gráfico do topo) em vez de ler o dropdown do próprio simulador (`sim-interval`), além de não limitar `period` para `60d` quando o tempo gráfico for intradiário (`5m`, `15m`, `60m`). Isso fazia o otimizador rodar em 1D (diário) enquanto o simulador rodava em 5m.

### Decisão Técnica
1. Em `runOptimizer()`, extrair o tempo gráfico de `document.getElementById('sim-interval').value || '1d'`.
2. Se o intervalo for intradiário (`5m`, `15m`, `60m`), definir automaticamente `period = '60d'`, idêntico ao que já é feito em `runSimulation()`.
3. Repassar `start_date`, `end_date`, `initial_capital` e `cycle_entry_mode` de forma idêntica entre `runOptimizer` e `runSimulation`.
4. Ao clicar em "Aplicar e Simular", todos esses parâmetros são preservados, garantindo **convergência de 100%** nos resultados numéricos.
