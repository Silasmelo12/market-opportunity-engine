# Research & Technical Decisions: Feature 002

**Feature**: `002-institutional-ux-radar-simulator`
**Date**: 2026-10-20

## Technical Decisions & Trade-offs

### 1. Resampling Intraday e Limites da API Yahoo Finance
- **Decision**:
  - Para `5m`, `15m` e `30m`: download direto via `yfinance` impondo teto dinâmico de `period="60d"`.
  - Para `1h`: download direto com teto de `period="730d"`.
  - Para `2h`, `4h`, `12h`: download da base horária (`1h`, até 730d) e aplicação de agregação temporal (`pandas.DataFrame.resample`) utilizando a regra padrão OHLCV:
    ```python
    resampled = df.resample(rule).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "dividends": "sum"
    }).dropna(subset=["open", "close"])
    ```
- **Rationale**: `yfinance` não fornece nativamente barras de 2h, 4h e 12h. O resampling matemático na base horária produz séries limpas, contíguas e sem barras fantasmas fora dos horários de pregão.
- **Alternatives Considered**: Usar apenas timeframes pré-definidos do yfinance (restringiria a análise e ignoraria o clássico gráfico de 4h amplamente utilizado em cripto e commodities).

### 2. Otimização de Performance e Reatividade com `@st.fragment`
- **Decision**: Encapsular os blocos que possuem controles independentes de filtro (Simulador de Aporte com controle de valor/datas e filtros do gráfico) usando o decorador `@st.fragment` do Streamlit 1.37+.
- **Rationale**: O recarregamento integral da página ao deslizar um slider de capital gerava latência de re-renderização desnecessária. O `@st.fragment` permite que o Streamlit reexecute apenas o componente isolado em < 100ms.
- **Alternatives Considered**: `st.form` com botão de submit (exige clique manual do usuário para atualizar, prejudicando a fluidez institucional).

### 3. Semáforo de Timing de Entrada ("Comprei Atrasado?")
- **Decision**: Avaliar a distância percentual $Dist\% = (Close_{atual} / P_{exec}) - 1.0$:
  - 🟢 **IDEAL / DESCONTO**: $Dist\% \le +1.5\%$ (ou em reteste aguardando toque na linha);
  - 🟡 **ESTENDIDO / CAUTELA**: $+1.5\% < Dist\% \le +4.0\%$;
  - 🔴 **ATRASADO / BONDE ANDOU**: $Dist\% > +4.0\%$ OU $Dist\% > 0.30 \times MeanForwardReturn$.
- **Rationale**: Impede que o investidor compre no topo de esticadas pós-sinal e fornece orientação imediata no Radar.

### 4. Dicionário Centralizado de Rótulos Comerciais
- **Decision**: Criar `src/ui/theme.py` contendo o mapa imutável `STRATEGY_LABELS_PT`, garantindo que todas as tabelas, gráficos, legendas e tooltips usem os mesmos termos em português sem vazamento de strings técnicas (ex: `t1_retest`).
