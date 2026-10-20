# Research & Architecture Decisions: Feature 004

**Feature**: `004-bidirectional-top-bottom-engine`  
**Date**: 2026-10-20  

## Technical Decisions & Trade-offs

### 1. Extensão do Contrato `SignalRecord` com `direction`
- **Decision**: Adicionar o campo `direction: str = "BUY"` (com default `"BUY"` para total compatibilidade retroativa) à dataclass `SignalRecord` em `src/strategies/base.py`.
- **Rationale**: Permite que o pipeline inteiro (motores, avaliador estatístico, esquemas FastAPI e frontend JS) diferencie imediatamente operações de compra de operações de venda sem ambiguidades nos identificadores.

### 2. Espelhamento Matemático da Estratégia Proprietária de Topo
- **Decision**: Criar `ProprietaryTopReversalEngine` (ou unificar em modo direcional em `ProprietaryReversalEngine`) mantendo a mesma complexidade $O(N)$ vetorial com arrays NumPy.
- **Rationale**:
  - *Fundo (Compra)*: Monitora rompimento de mínima (`Close < Low_Ref`) e nega com fechamento acima (`Close > active_ref_line`).
  - *Topo (Venda)*: Monitora rompimento de máxima (`Close > High_Ref`) e nega com fechamento abaixo (`Close < active_ref_line`).
  - Ambos compartilham a mesma invariante de cancelamento da linha anterior em novos rompimentos e ciclo único de execução com reteste em janela $M$.

### 3. Fórmulas Simétricas no Avaliador Estatístico
- **Decision**:
  - Para `BUY`:
    $$\text{Forward Return \%} = \frac{\text{Close}[t_{\text{exec}} + X] - P_{\text{exec}}}{P_{\text{exec}}} \times 100$$
    $$\text{MAE \%} = \min\left(0, \frac{\min(\text{Low}[t_{\text{exec}} : t_{\text{exec}} + X + 1]) - P_{\text{exec}}}{P_{\text{exec}}}\right) \times 100$$
  - Para `SELL`:
    $$\text{Forward Return \%} = \frac{P_{\text{exec}} - \text{Close}[t_{\text{exec}} + X]}{P_{\text{exec}}} \times 100$$
    $$\text{MAE \%} = -\max\left(0, \frac{\max(\text{High}[t_{\text{exec}} : t_{\text{exec}} + X + 1]) - P_{\text{exec}}}{P_{\text{exec}}}\right) \times 100$$
- **Rationale**: A convenção financeira dita que em posições vendidas (short), ganha-se com a queda de preço e perde-se com a alta. Manter o MAE negativo permite que o Scatter Plot continue mapeando o "calor/risco" no quadrante negativo do eixo X de forma uniforme e intuitiva para o usuário.

### 4. Filtragem Client-Side Instantânea (0ms) no Terminal Web
- **Decision**: O endpoint `GET /api/analyze` retornará todos os sinais calculados (tanto de compra quanto de venda) devidamente etiquetados com `"direction": "BUY"` e `"direction": "SELL"`.
- **Rationale**: O seletor de 3 estados (`🟢 Compra`, `🔴 Venda`, `⚡ Ambos`) opera inteiramente na memória do navegador filtrando a lista `analysisData.signals` em $< 5\text{ms}$, redesenhando os marcadores no TradingView Lightweight Charts e recalculando as tabelas sem causar qualquer requisição HTTP adicional.
