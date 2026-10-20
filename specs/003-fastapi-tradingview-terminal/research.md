# Research & Technical Decisions: Feature 003

**Feature**: `003-fastapi-tradingview-terminal`
**Date**: 2026-10-20

## Technical Decisions & Trade-offs

### 1. Arquitetura SPA Integrada com FastAPI (Zero-Build / Zero-Node)
- **Decision**: Servidor FastAPI com montagem de arquivos estáticos na raiz (`app.mount("/", StaticFiles(directory="src/web", html=True), name="web")`), servindo um SPA puro em HTML5/ES6 com Tailwind CSS, TradingView Lightweight Charts e Plotly.js carregados via CDN.
- **Rationale**: Elimina completamente a dependência de Node.js, npm, webpack ou Vite. O usuário executa `python -m src.api.server` ou `uvicorn src.api.server:app` e a aplicação completa roda com aceleração nativa Canvas no navegador.
- **Alternatives Considered**: Aplicação separada em React/Next.js (exigiria Node.js instalado, build steps e portas separadas, violando a simplicidade single-repo e aumentando atrito para o usuário).

### 2. Filtragem Instantânea 0ms (Client-Side State Engine)
- **Decision**: O endpoint `GET /api/analyze` entrega o payload consolidado contendo os candles e todos os sinais das 24 estratégias pré-calculados. O JavaScript armazena esse payload na memória local e gerencia a visibilidade de marcadores no canvas do TradingView (`markers`), assim como a re-renderização dos gráficos Plotly e da tabela através de filtragem de arrays em 0ms.
- **Rationale**: No Streamlit, marcar ou desmarcar um checkbox provocava reload do script em Python. No SPA, ligar ou desligar uma estratégia filtra os dados em memória em menos de 10 milissegundos a 60fps.

### 3. Expansão de Velas em `mql5_candles.py` (14 Padrões)
- **Decision**: Adicionar 6 novos padrões clássicos de reversão altista/fundo vetorizados em `mql5_candles.py`:
  1. `inverted_hammer`: corpo pequeno no fundo, sombra superior $\ge 2 \times Body$, sombra inferior pequena;
  2. `tweezer_bottom`: duas barras com mínimas equivalentes em suporte (tolerância $\le 0.1\%$) com reversão;
  3. `dragonfly_doji`: Open e Close quase idênticos na máxima da barra com sombra inferior longa;
  4. `abandoned_baby_bullish`: estrela da manhã rara com gap na mínima entre as três velas;
  5. `bullish_kicker`: vela de baixa seguida de salto/gap de alta com vela de alta forte;
  6. `climactic_pinbar`: pinbar com cauda longa e volume expressivo ($> 1.5 \times SMA(Volume, 20)$).
- **Rationale**: Eleva o poder preditivo do agrupamento de velas sem quebrar a assinatura ou o Zero Look-Ahead Bias existente.

### 4. Concorrência no Radar Multi-Ativos
- **Decision**: Utilizar `concurrent.futures.ThreadPoolExecutor` com cache em memória `lru_cache` com TTL em `src/api/server.py` para processar em paralelo a cesta de 8 a 15 ativos em menos de 1 segundo.
- **Rationale**: Requisições de rede para cotações em lote se tornam ultra-rápidas aproveitando o I/O concorrente.
