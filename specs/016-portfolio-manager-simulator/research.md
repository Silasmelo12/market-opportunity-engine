# Phase 0 Research: Gestor, Consultor de Rebalanceamento e Simulador Multiativos de Carteira

**Feature**: `016-portfolio-manager-simulator`  
**Date**: 2026-10-22

---

## 1. Formulação Matemática do Score de Potencial (0 a 100) por Ativo

- **Decision**: Calcular para cada ativo do universo alvo (e da carteira atual) um `potential_score` contínuo no intervalo `[0.0, 100.0]` combinando 4 pilares ortogonais extraídos do Par de Estratégias Campeão (`optimize_strategy_pairs`) e do classificador de Timing (`classify_timing_status`):
  $$\text{Score} = \text{clip}\Big(0.35 \cdot S_{\text{win}} + 0.30 \cdot S_{\text{ret}} + 0.15 \cdot S_{\text{dd}} + 0.20 \cdot S_{\text{timing}},\; 0,\; 100\Big)$$
  onde:
  - $S_{\text{win}} = \min(100,\; \max(0,\; \text{win\_rate\_pct}))$ (0 a 100, peso 35%);
  - $S_{\text{ret}} = \min(100,\; \max(0,\; \frac{\text{total\_return\_pct}}{150.0} \times 100))$ (normaliza retornos históricos de 0% a 150%+ na escala 0–100, peso 30%);
  - $S_{\text{dd}} = \min(100,\; \max(0,\; 100 - |\text{max\_drawdown\_pct}| \times 2.0))$ (penaliza drawdowns severos; drawdown 0% = 100 pts, drawdown $\ge 50\%$ = 0 pts, peso 15%);
  - $S_{\text{timing}}$ (peso 20%):
    - `100.0` se houver sinal de compra ativo em timing `IDEAL` (formado na última barra, em reteste válido ou distância $|\Delta| \le 2.5\%$);
    - `55.0` se o sinal de compra estiver em timing `EXTENDED`;
    - `15.0` se estiver em timing `LATE` ou sem sinal recente de compra.
- **Rationale**:
  - Combina assertividade estatística histórica (*Win Rate*), magnitude de geração de valor (*Total Return*), resiliência de risco (*Max Drawdown*) e oportunidade tática imediata (*Timing*).
  - Totalmente determinístico, rápido ($O(1)$ após a avaliação do par campeão) e imune a outliers extremos graças à normalização limitada em `[0, 100]`.
- **Alternatives Considered**:
  - *Apenas retorno passado bruto*: descartado porque um ativo volátil com 1 único trade de +300% e drawdown de -70% distorceria toda a alocação da carteira.
  - *Apenas Z-Score de queda de preço*: descartado porque ignora qual estratégia específica funciona melhor naquele ativo.

---

## 2. Algoritmo de Dimensionamento de Posição (Score-Weighted com Teto por Ativo)

- **Decision**: Distribuir o capital alocável proporcionalmente ao `potential_score` dos ativos candidatos elegíveis (aqueles com sinal de compra ativo em timing `IDEAL` ou `EXTENDED` e score $\ge 50.0$), aplicando projeção iterativa com teto (`max_weight_pct`, padrão `25%`):
  1. Para um conjunto de candidatos elegíveis $C$, o peso bruto inicial de cada ativo $i \in C$ sobre o capital livre é $w_i = \frac{\text{Score}_i}{\sum_{j \in C} \text{Score}_j}$.
  2. Nenhum ativo pode ultrapassar `max_weight_pct` do Patrimônio Total da Carteira (`total_equity = cash + sum(market_value)`). Se o ativo já possui peso atual $w_i^{\text{atual}}$ na carteira, o espaço adicional máximo para compra é $\max(0,\; \text{max\_weight\_pct} - w_i^{\text{atual}})$.
  3. Caso existam poucos candidatos (ex: apenas 2 ativos com sinal de compra ativo e teto de 25%), cada um recebe até 25% do patrimônio total e os 50% restantes permanecem em **Caixa (Liquidez)** até surgirem novos sinais, evitando concentração forçada.
  4. Para tickers brasileiros (`.SA`), a quantidade recomendada de cotas é truncada/arredondada para inteiro ($\lfloor \text{Valor Alocado} / \text{Preço} \rfloor$) garantindo que o custo financeiro nunca supere o caixa disponível; para criptomoedas (`-USD`) e ativos fracionários, arredonda-se para 4 casas decimais.
- **Rationale**:
  - Respeita rigorosamente o controle de risco institucional (nunca concentrar além do teto por ativo) e conserva 100% da integridade contábil do caixa.
- **Alternatives Considered**:
  - *Forçar 100% de alocação mesmo com 1 único sinal ativo*: rejeitado pois viola o limite máximo de concentração por ativo configurado pelo usuário.

---

## 3. Três Regras Causais de Saída e Rebalanceamento (Consultor Hoje & Simulador Histórico)

- **Decision**: Padronizar as mesmas 3 regras de gestão dinâmica tanto no Consultor Hoje (`/api/portfolio/advise`) quanto no Simulador Histórico (`/api/portfolio/simulate`):
  1. **Regra 1 — Venda Total no Sinal de Topo (`SELL_FULL`)**:
     - Quando o ativo em carteira confirma um sinal de `SELL` da sua estratégia de venda campeã (ou qualquer sinal de venda quando no modo amplo), liquida-se 100% das cotas na abertura da barra de execução (`execution_price`), retornando 100% do valor apurado para `portfolio_cash`.
  2. **Regra 2 — Venda Parcial por Excesso de Peso (`SELL_PARTIAL_REBALANCE`)**:
     - Se a valorização de mercado de um ativo em carteira fizer seu peso corrente $w_i^{\text{atual}} = \frac{\text{Valor}_i}{\text{Patrimônio Total}}$ ultrapassar $\text{max\_weight\_pct} + \text{rebalance\_band\_pct}$ (onde `rebalance_band_pct = 5.0%` por padrão, p.ex. passar de 30% quando o teto é 25%), vende-se parcialmente a diferença necessária para reconduzir o peso do ativo exatamente a `max_weight_pct`.
  3. **Regra 3 — Rotação Tática por Custo de Oportunidade (`ROTATE_OUT` / `ROTATE_IN`)**:
     - Disparada quando surge um candidato fora da carteira (ou sub-alocado) com sinal de compra confirmado em timing `IDEAL` e o caixa livre é insuficiente (menor que 5% do patrimônio total).
     - O motor verifica se existe em carteira uma posição "estagnada/fraca" que cumpra simultaneamente:
       - Tempo mínimo de permanência em carteira $\ge 3$ barras (anti-churning);
       - Retorno acumulado da posição aberta $\le +3.0\%$ (não interrompe vencedores em plena tendência de alta);
       - Diferencial de Score de Potencial: $\text{Score}_{\text{candidato}} - \text{Score}_{\text{atual}} \ge 15.0$ pontos.
     - Se elegível, vende a posição mais fraca (`ROTATE_OUT`) e utiliza o caixa liberado para comprar o novo ativo (`ROTATE_IN`).
- **Rationale**:
  - Impede giro excessivo (anti-churning) e protege posições altamente lucrativas (deixa os ganhos correrem até o sinal de topo ou rebalanceamento de banda), enquanto recicla capital preso em ativos laterais/fracos quando aparece uma oportunidade de fundo estatístico `IDEAL`.
- **Alternatives Considered**:
  - *Trocar ativos a cada barra por qualquer diferença de 1 ponto no Score*: rejeitado pois geraria overtrading e destruiria o retorno em oscilações laterais.

---

## 4. Alinhamento Temporal Multiativos e Garantia de Zero Look-Ahead Bias

- **Decision**: No simulador histórico multiativos (`simulate_portfolio_multi_asset`), alinhar as séries OHLCV dos $K$ ativos do universo através da união ordenada de seus timestamps (`master_timeline = np.union1d(...)`):
  - Para cada ativo $k$ e cada timestamp $t$ na `master_timeline`:
    - O preço de fechamento vigente para marcação a mercado (Mark-to-Market) é o último `Close` conhecido até $t$ (*forward-fill* estritamente causal, útil quando mercados como B3 e Cripto possuem calendários de feriados/fins de semana distintos).
    - Os sinais de compra e venda da estratégia campeã de cada ativo $k$ são avaliados exclusivamente em sua barra de execução causal `execution_bar_index` (onde a confirmação ocorreu em $t_{\text{sinal}} < t_{\text{exec}}$ e o preenchimento ocorre em `Open[t_exec]` ou nível de reteste causal).
  - Na otimização da estratégia campeã por ativo durante o backtest, para evitar lentidão e manter performance sub-segundo/poucos segundos, cada ativo do universo é processado em paralelo via `ThreadPoolExecutor` reutilizando o cache em memória/disco (`DataLoader` + cache de perfil de oportunidade do ativo).
- **Rationale**:
  - Cumpre estritamente o Princípio II da Constituição (Zero Look-Ahead Bias) e o Princípio III (Robustez Multi-Mercado, permitindo inclusive carteiras mistas com ações B3, EUA e Cripto).
- **Alternatives Considered**:
  - *Interseção estrita de datas (`inner join`)*: descartado porque descartaria sinais ocorridos em dias em que um mercado operou e outro esteve em feriado.
