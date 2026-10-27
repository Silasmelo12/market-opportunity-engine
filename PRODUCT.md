# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
- **Investidores e Traders Quantitativos Autônomos:** Focados no mercado brasileiro (Ações B3, FIIs, BDRs internacionais e macro global como Ouro/S&P500), buscando assimetrias matemáticas e pontos de inflexão/fundos estatísticos.
- **Gestores e Consultores de Carteiras / Family Offices Independentes:** Profissionais e parceiros que precisam de visões de alocação quantitativa, rebalanceamento por faixas de risco/pesos ideais e histórico de desempenho.
- **Desenvolvedor / Quant Principal:** O próprio criador do sistema, que opera análises profundas, calibra estratégias e necessita de visualização irrestrita de dados brutos e métricas avançadas.

## Product Purpose
O **Market Opportunity & Bottom Statistical Engine** é um terminal web quantitativo e motor de decisão financeira desenhado para filtrar ruído do mercado e transformar séries temporais complexas em sinais práticos de alocação e compra em fundos estatísticos (*bottom detector*). Seu sucesso reside em fornecer convicção matemática para montagem e balanceamento de carteiras multiativo com agilidade.

## Positioning
Diferente de home brokers convencionais poluídos ou ferramentas puramente gráficas, o sistema une **detecção estatística de fundos (Z-Score, RSI extremo, volatilidade histórica e desvio padrão)** a um **simulador de rebalanceamento de carteira prático** com suporte a ordens propostas, importação e exportação de custódia via CSV e testes de cenários.

## Operating Context
- **Implantação em Produção:** Já hospedado em nuvem (Render), com acesso compartilhado para colegas e primeiros usuários/clientes (fase de transição para produto SaaS/FinTech).
- **Ambiente de Uso Primário:** Terminal Web Desktop-first, adaptável para telas amplas, operando sob o pregão da B3 e fechamento de mercados internacionais.
- **Bimodalidade de Interface (Visão Executiva vs. Visão Analítica Profunda):**
  - **Camada Executiva:** Dashboard limpo e moderno, estruturado em cartões executivos (KPI cards), resumos diretos de decisão ("o que comprar / o que rebalancear hoje") e indicadores de saúde da carteira.
  - **Camada Analítica de Alta Densidade (Modo Terminal Quant):** Painéis detalhados com gráficos TradingView Lightweight Charts, Plotly.js, heatmaps de correlação, tabelas de múltiplos e matriz de backtest, preservados na íntegra para inspeção analítica profunda.

## Capabilities and Constraints
- **Universo de Ativos:** 194+ ativos rastreados (Ações B3 Ibovespa/Small Caps, FIIs de tijolo e papel, BDRs americanas/globais e commodities macro).
- **Módulos Centrais:**
  - *Radar Quantitativo / Scanner de Oportunidades:* Score composto de sobrevenda e assimetria estatística.
  - *Simulador de Carteira & Rebalanceamento:* Diagnóstico de alocação atual vs. ideal, geração de lotes de ordens e reversão com botão Desfazer.
  - *Playbook & Backtest:* Matriz de regras estatísticas e validação histórica.
  - *Custódia & Dados:* Persistência rápida, upload e download direto de arquivos CSV de carteira.
- **Restrição de Confiabilidade:** Desempenho rápido e confiável no carregamento de dados e renderização assíncrona para usuários finais remotos.

## Brand Commitments
- **Nome:** Market Opportunity & Bottom Statistical Engine.
- **Identidade:** Terminal analítico profissional e institucional, combinando clareza de decisão executiva com rigor de engenharia quantitativa.
- **Tema:** Light mode padrão (superfícies Investidor10) com dark mode completo de alto contraste; ambos os temas compartilham os mesmos tokens semânticos.

## Evidence on Hand
- Base de código completa em FastAPI com endpoints REST e arquitetura de componentes modulares.
- Motor de cálculo estatístico implementado e testado (91+ testes unitários/integração automatizados).
- Template de carteira real com suporte a BDRs, FIIs, Ouro e Ações (`minha_carteira.csv`).

## Product Principles
1. **Clareza Executiva na Superfície, Rigor Estatístico na Profundidade:** Apresentar primeiro a resposta acionável (resumo executivo), mantendo o detalhe matemático e o gráfico a apenas um clique ou toggle de distância.
2. **Decisão Baseada em Dados, Sem Ruído:** Evitar poluição visual desnecessária; cada métrica, badge ou cor na tela deve carregar significado financeiro ou estatístico direto.
3. **Controle Total e Reversibilidade:** O investidor precisa de total transparência nas ordens sugeridas, validações de segurança e capacidade de desfazer alterações instantaneamente.
4. **Pronto para Escala e Uso por Terceiros:** A interface deve ser acessível e compreensível para colegas e clientes do produto, sem perder o poder de fogo de uma ferramenta de desenvolvedor quant.
