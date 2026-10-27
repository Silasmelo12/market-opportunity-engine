# Implementation Plan: Layout Profissional e Unificado da Interface Web

**Branch**: `feat/professional-ui-layout` | **Date**: 2026-10-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/023-professional-ui-layout/spec.md`

## Summary

Unificar as oito áreas da SPA em uma única linguagem visual profissional, corrigindo textos corrompidos, padronizando tipografia, ícones, componentes, temas claro/escuro, navegação e responsividade. A abordagem é incremental: consolidar a fundação visual existente (tokens e componentes), reconstruir o shell de navegação, migrar as telas de carteira e depois as telas quantitativas, finalizando com auditoria de conteúdo, acessibilidade e matriz visual de 64 verificações.

Nenhuma API, regra financeira, rota ou identificador de contrato será alterado. A implementação permanece em HTML, CSS e JavaScript vanilla sobre a SPA estática já servida pelo FastAPI, sem novos frameworks, bundlers ou dependências de runtime.

## Technical Context

**Language/Version**: HTML5, CSS3, JavaScript ES2020 (vanilla); Python 3.14 no backend e nos testes.

**Primary Dependencies**: FastAPI + Uvicorn (inalterados), Tailwind CSS via CDN (já existente), Plotly.js 2.32.0, TradingView Lightweight Charts 4.1.3, pytest e Playwright para validação. Nenhuma dependência nova de runtime.

**Storage**: `localStorage` do navegador para tema (`terminal_theme`), aba ativa (`mo_active_tab`) e pilar ativo (`mo_active_pillar`); estado da carteira permanece no fluxo atual. Sem migração de dados ou alteração de esquema.

**Testing**: `pytest` para contratos e regressões; Playwright para navegação, temas e invariantes de DOM; auditoria visual manual/automatizada na matriz de 8 áreas × 4 larguras × 2 temas.

**Target Platform**: Navegadores modernos em desktop, tablet e celular; SPA servida pelo backend FastAPI atual.

**Project Type**: Aplicação web single-repository com backend Python e frontend estático.

**Performance Goals**: Manter o desempenho percebido atual, sem requisições adicionais de runtime, sem layout shift perceptível na troca de tema/área e com gráficos redimensionando de forma responsiva.

**Constraints**: Sem alterações de backend/API/contratos de dados; sem novos frameworks ou build step; piso tipográfico de 11px; contraste WCAG AA; preservação de IDs, rotas e funções globais consumidas pelos testes; exatamente um painel visível por vez.

**Scale/Scope**: 8 áreas navegáveis, 2 ambientes, 2 temas, 4 larguras de referência (375/768/1366/1920) e 64 verificações visuais de aceitação. Base atual: `index.html` com ~2.148 linhas, `styles.css` com ~2.012 linhas e `app.js` com ~4.748 linhas, além dos módulos em `src/web/modules/`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio / Gate | Avaliação | Evidência / Ação |
|---|---|---|
| **I. Arquitetura Python (FastAPI) + Web SPA** | **PASS** | Alterações restritas a `src/web/`; backend FastAPI inalterado; sem novos frameworks, bundlers ou migração para Streamlit. Tailwind CDN, Plotly e Lightweight Charts permanecem como estão. |
| **I. Performance e cache** | **PASS** | Nenhuma chamada de API nova; filtros e dados continuam no fluxo atual; gráficos mantêm redimensionamento responsivo; sem CDN adicional. |
| **II. Rigor Financeiro e Zero Look-Ahead Bias** | **PASS** | Nenhum cálculo, indicador, sinal ou regra de negócio é alterado. Rótulos e semântica financeira são preservados; a spec proíbe mudança de significado. |
| **III. Robustez Multi-Mercado & Fallback** | **PASS** | Nenhuma alteração em ingestão, normalização de tickers, fallback quantitativo ou dados de mercado. |
| **IV. Modularidade e Contratos** | **PASS** | Mudanças concentradas na camada `web`; API não contém lógica de estratégia e permanece intocada; IDs de contrato e funções globais usadas por testes são preservados. |
| **Quality Gate — Contratos de API** | **PASS** | Nenhum endpoint ou schema será alterado; contrato de UI será documentado em `contracts/`. |
| **Quality Gate — Testes** | **PASS (com verificação)** | A suíte existente deve continuar passando; novos testes de contrato visual/navegação serão adicionados sem enfraquecer os atuais. |
| **Quality Gate — Commit por Tarefa** | **PASS** | O `tasks.md` será executado com um commit por tarefa concluída, no formato exigido pela constituição. |
| **Sem violações que exijam justificativa** | **PASS** | Nenhum item em Complexity Tracking. |

## Project Structure

### Documentation (this feature)

```text
specs/023-professional-ui-layout/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 validation guide
├── contracts/
│   └── ui-layout-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
src/
├── api/                     # Backend FastAPI — NÃO ALTERAR
│   ├── server.py
│   ├── schemas.py
│   └── cache.py
└── web/                     # Escopo da feature
    ├── index.html           # Shell, navegação e markup das 8 áreas
    ├── styles.css           # Tokens, componentes, temas e responsividade
    ├── app.js               # Tema, navegação, estado e renderização existente
    └── modules/
        ├── constants.js
        ├── formatters.js
        ├── proventos.js
        └── toast.js

tests/
├── unit/
│   ├── test_ui_contracts.py
│   └── ...                  # Contratos e regressões existentes
├── e2e/
│   ├── test_dashboard_navigation.py
│   ├── test_proventos_layout.py
│   └── conftest.py
└── ...                      # Testes de estratégia e API preservados
```

**Structure Decision**: Single-repository web application. O backend permanece isolado em `src/api/`; toda a entrega visual ocorre em `src/web/`. Nenhum novo diretório de aplicação, framework de frontend ou pipeline de build será introduzido.

## Phase 0 — Research Summary

As decisões completas estão em [research.md](./research.md). Resumo:

1. **Estratégia de unificação**: consolidar nos tokens semânticos já definidos no projeto, remover os remapeamentos de tema legado e migrar o markup das telas quantitativas para as classes semânticas. Alternativa descartada: manter dois sistemas com overrides, pois perpetua a dívida visual.
2. **Navegação**: manter a arquitetura atual de dois ambientes, rotas hash e persistência, preservando IDs e a precedência URL > `localStorage` > padrão.
3. **Tema**: adotar claro como padrão inicial, persistir a escolha e manter atualização de gráficos na troca. Alternativa descartada: tema escuro padrão, por contrariar a diretriz visual e a nova spec.
4. **Ícones**: usar o sprite SVG inline já existente, expandindo-o com ícones lineares. Alternativa descartada: emojis ou fonte de ícones externa.
5. **Correção de encoding**: aplicar uma passagem controlada de reparo `cp1252 → UTF-8` somente em strings visíveis, com verificação de diff e testes de ausência de artefatos.
6. **Estado vazio**: exibir orientação de primeiro uso apenas quando não houver carteira/importação; com dados, priorizar conteúdo operacional.
7. **Responsividade**: grids fluidos, largura máxima consistente e rolagem horizontal restrita a tabelas largas.
8. **Validação**: matriz de 64 capturas/verificações, testes de contrato de DOM e suíte existente.

## Implementation Strategy

A execução será incremental e reversível, em seis blocos. O `tasks.md` detalhará as tarefas atômicas e a ordem de dependência.

### Bloco A — Fundação visual
- Consolidar tokens de cor, tipografia, espaçamento, raios e sombras.
- Definir piso tipográfico de 11px, algarismos tabulares e hierarquia de títulos.
- Padronizar componentes base: cartões, botões, campos, selects, badges, tabelas, acordeões e estados de foco/hover/disabled.
- Remover os overrides de tema legado que hoje tentam converter as telas quantitativas em claras.
- Substituir emojis funcionais por ícones vetoriais do sprite.

**Critério de saída**: fundação aplicada sem alterar navegação ou IDs, com todos os testes existentes verdes.

### Bloco B — Shell e navegação
- Reorganizar o cabeçalho: marca, alternador de ambientes, ações principais e tema.
- Padronizar a subnavegação contextual dos dois ambientes.
- Corrigir offsets de sticky, comportamento mobile e estados ativos.
- Remover o header legado oculto, preservando IDs e funções consumidas por JavaScript/testes.
- Garantir foco visível, ordem de tabulação e semântica ARIA.

**Critério de saída**: E2E de navegação, precedência de rota, voltar/avançar e painel único continuam passando.

### Bloco C — Áreas de carteira
- Resumo: cabeçalho de página, KPIs, gráficos, acordeões e estado vazio condicional.
- Posições: cabeçalho, acordeões, tabelas e ações por linha.
- Proventos: cabeçalho, alternador mensal/anual e gráfico.
- Evolução Patrimonial: cabeçalho e gráfico.
- Uniformizar cartões, legendas, notas de rodapé e estados de contingência de cotação.

**Critério de saída**: consistência visual nas quatro áreas, ambos os temas, sem regressão de dados ou gráficos.

### Bloco D — Áreas quantitativas
- Radar: filtros, tabela, ordenação, paginação, estado vazio e responsividade.
- Gráfico: sidebar de controles, área do gráfico e retorno contextual.
- Simulador: grids de formulário, seletores, resultados e mensagens.
- Playbook: hierarquia de grupos, blocos e destaques.
- Migrar classes legadas para tokens semânticos e remover dependência dos overrides.

**Critério de saída**: nenhuma tela quantitativa com resíduo de paleta antiga; ambos os temas legíveis.

### Bloco E — Conteúdo, acessibilidade e encoding
- Corrigir todos os textos corrompidos no HTML/JS.
- Revisar rótulos visíveis e consistência de português.
- Auditar contraste AA, foco, zoom 200%, movimento reduzido e leitores de tela.
- Verificar ausência de `text-[10px]` em texto funcional.

**Critério de saída**: zero artefatos de encoding; checklist de acessibilidade aprovado.

### Bloco F — Validação final
- Executar suíte unitária, contratos e E2E.
- Gerar e revisar a matriz de 64 verificações visuais.
- Comparar antes/depois e registrar aprovação.
- Confirmar preservação de rotas, IDs, APIs e funcionalidades.

**Critério de saída**: todos os critérios de sucesso da spec atendidos e nenhuma regressão funcional.

## Testing Strategy

### Testes automatizados existentes
- `pytest tests/unit` — contratos de UI, API e regressões.
- `pytest tests/e2e` — navegação, temas, painel único, IDs e redimensionamento (requer Playwright).
- `pytest tests/` — suíte completa, incluindo estratégias e dados.

### Novos testes recomendados
- Contrato de ausência de artefatos de encoding em `index.html` e `app.js`.
- Contrato de piso tipográfico: nenhum texto funcional com classe abaixo de 11px.
- Contrato de tema: ambos os temas aplicáveis a todas as áreas, com atributos e persistência corretos.
- Contrato de responsividade estrutural: tabelas largas envoltas em contêiner rolável; nenhuma largura fixa proibida.
- Contrato de acessibilidade básica: controles de navegação com `aria-selected`, foco visível e ativação por teclado.

### Validação visual
- 8 áreas × 4 larguras × 2 temas = 64 verificações.
- Capturas antes/depois para revisão.
- Checklist manual de alinhamento, contraste, espaçamento, overflow, estados vazios e legibilidade.

## Risks and Mitigations

| Risco | Impacto | Mitigação |
|---|---|---|
| Correção de encoding alterar conteúdo legítimo | Alto | Reparo restrito a strings visíveis, diff revisado e testes de ausência de artefatos; não aplicar em dados ou contratos. |
| Remoção do header legado quebrar bindings antigos | Alto | Inventariar IDs/funções antes da remoção; manter compatibilidade ou aliases; rodar E2E após o bloco B. |
| Migração de classes das telas quantitativas quebrar seletores JS | Alto | Preservar IDs e contratos; migrar apenas classes visuais; validar com testes de UI e navegação. |
| Tema claro padrão alterar expectativa de usuários existentes | Médio | Persistir escolha do usuário; documentar mudança; manter alternância imediata. |
| Tabelas largas causarem overflow em mobile | Médio | Encapsular em contêiner rolável com indicativo visual; testar em 375px. |
| Regressão em gráficos Plotly/TradingView | Médio | Reutilizar `updateChartsTheme` e resize existentes; testar troca de tema e abertura de área. |
| Escopo visual amplo gerar diff excessivo | Médio | Execução em blocos, commits por tarefa e validação incremental por área. |

## Complexity Tracking

Nenhuma violação constitucional ou complexidade adicional identificada. Não há novos projetos, camadas, dependências de runtime ou mudanças de arquitetura.

## Post-Design Constitution Re-Check

| Gate | Status pós-design |
|---|---|
| I. FastAPI + SPA estática | **PASS** — nenhum framework/build novo. |
| I. Performance/cache | **PASS** — sem chamadas adicionais ou dependências de runtime. |
| II. Rigor financeiro | **PASS** — nenhum cálculo ou semântica alterada. |
| III. Multi-mercado/fallback | **PASS** — fora do escopo e intocado. |
| IV. Modularidade/contratos | **PASS** — mudanças em `src/web`; IDs e rotas preservados; contrato de UI documentado. |
| Quality gates | **PASS** — testes e commit por tarefa previstos. |
