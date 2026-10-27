# Research: Layout Profissional e Unificado da Interface Web

**Feature**: 023-professional-ui-layout
**Date**: 2026-10-27
**Input**: [spec.md](./spec.md)

## Contexto da Auditoria

A auditoria do frontend atual identificou:

- `src/web/index.html` com ~2.148 linhas, contendo dois sistemas de layout (Investidor10 claro e terminal escuro legado) e um header antigo oculto.
- `src/web/styles.css` com ~2.012 linhas, incluindo blocos extensos de overrides para converter telas escuras em claras e vice-versa.
- `src/web/app.js` com ~4.748 linhas, mantendo tema, navegação, renderização de telas e funções globais consumidas por testes.
- 230 ocorrências de artefatos de encoding no `index.html` e 77 no `app.js` (ex.: `EstratÃ©gia`, `AnÃ¡lise`, `â†’`).
- 93 usos de `text-[10px]` no `index.html`, abaixo do piso de 11px definido no design do projeto.
- 169 usos de classes `fintech-*` e 87 de classes `slate-*` no `index.html`, evidência da convivência entre as duas linguagens visuais.
- Divergência de offset do menu sticky: `61px` no markup e `68px` no CSS.
- Testes E2E dependem de IDs estáveis (`#pillar-btn-*`, `#subnav-group-*`, `[data-tab]`, `#tab-*`), de `window.appState` e de `window.applyTheme`.

## Decisões de Pesquisa

### D1 — Estratégia de unificação visual

**Decision**: Consolidar a interface nos tokens semânticos já existentes no projeto, criar uma camada única de componentes visuais e migrar o markup das áreas quantitativas para essa camada. Remover os overrides de tema que compensam a estética legada.

**Rationale**: Os tokens atuais já cobrem superfícies, bordas, tipografia, cores semânticas, sombras e raios. A convivência de duas linguagens é a causa raiz das inconsistências. A migração para uma camada única reduz manutenção, simplifica os temas e garante previsibilidade visual.

**Alternatives considered**:
- Manter os dois sistemas e ampliar os overrides: rejeitado por perpetuar a dívida visual e aumentar o custo de cada nova tela.
- Introduzir um framework de componentes ou build step: rejeitado pela constituição e pelo escopo de manter a SPA estática sem bundler.

### D2 — Tema padrão e persistência

**Decision**: Adotar o tema claro como padrão inicial, persistir a escolha em `localStorage` (`terminal_theme`) e manter a atualização dos gráficos na troca de tema.

**Rationale**: A spec e o `DESIGN.md` definem o tema claro como identidade executiva principal. A persistência já existe e evita retrabalho. A atualização de gráficos já é suportada por `updateChartsTheme`.

**Alternatives considered**:
- Manter escuro como padrão: rejeitado por contrariar a identidade visual e a expectativa da feature.
- Seguir apenas a preferência do sistema sem preferência explícita: rejeitado como padrão inicial; a escolha do usuário deve prevalecer após a primeira interação.

### D3 — Navegação e compatibilidade

**Decision**: Preservar a arquitetura de dois ambientes, rotas hash, precedência URL > `localStorage` > padrão, sincronização com histórico e os IDs/funções globais existentes. O trabalho é visual e estrutural, não uma reescrita do roteador.

**Rationale**: Os testes E2E cobrem essa arquitetura e ela atende à spec. Alterar o roteador aumentaria o risco sem benefício visual.

**Alternatives considered**:
- Reimplementar a navegação com um novo roteador: rejeitado por risco e por violar o princípio de mudança incremental.
- Remover o header legado sem inventário de IDs: rejeitado; é necessário mapear bindings antes de qualquer remoção.

### D4 — Correção de encoding

**Decision**: Aplicar um reparo controlado de strings visíveis usando a conversão `cp1252 → UTF-8` (equivalente a `texto.encode('cp1252').decode('utf-8')`), com diff revisado e teste de ausência de artefatos. Não aplicar a dados, contratos ou conteúdo que já esteja correto.

**Rationale**: A auditoria confirmou que as sequências são mojibake clássico e a conversão recupera corretamente exemplos como `EstratÃ©gia → Estratégia`, `AnÃ¡lise → Análise` e `â†’ → →`. O reparo é determinístico e verificável.

**Alternatives considered**:
- Substituição manual de cada string: rejeitado por volume e risco de omissões.
- Adicionar dependência de correção automática: rejeitado por escopo e por evitar nova dependência de runtime.

### D5 — Sistema de ícones

**Decision**: Utilizar o sprite SVG inline já presente no documento, expandindo-o com ícones lineares consistentes. Emojis deixam de ser usados como ícones funcionais.

**Rationale**: O sprite já é parte da aplicação e não adiciona dependência. Ícones lineares têm peso visual uniforme e funcionam nos dois temas via `currentColor`.

**Alternatives considered**:
- Manter emojis: rejeitado por inconsistência entre sistemas operacionais e aparência pouco profissional.
- Fonte de ícones via CDN: rejeitado por dependência externa adicional.

### D6 — Estado vazio e onboarding

**Decision**: Exibir a orientação de primeiro uso do Resumo somente quando não houver dados de carteira/importação. Com dados presentes, o espaço é ocupado por conteúdo operacional.

**Rationale**: O banner permanente compete com os KPIs e reduz a densidade útil. A condicionalidade melhora a experiência inicial sem sacrificar a operação diária.

**Alternatives considered**:
- Manter o banner sempre visível: rejeitado por ruído visual.
- Criar uma tela separada de onboarding: rejeitado por ampliar o escopo.

### D7 — Responsividade e tabelas

**Decision**: Usar grids fluidos com largura máxima consistente e encapsular tabelas largas em contêineres com rolagem horizontal e indicativo visual.

**Rationale**: Atende à matriz de 375/768/1366/1920 sem esconder dados nem provocar overflow global. O padrão já é usado parcialmente no Radar.

**Alternatives considered**:
- Colapsar tabelas em cartões no mobile: rejeitado nesta fase por aumentar o escopo e o risco de perda de colunas.
- Permitir overflow global: rejeitado por prejudicar a navegação.

### D8 — Acessibilidade

**Decision**: Aplicar foco visível, ordem de tabulação lógica, estados ARIA nos controles de navegação, contraste AA, suporte a zoom 200% e movimento reduzido.

**Rationale**: São requisitos da spec e boas práticas para uma interface financeira profissional. A base já possui `role="tab"`/`aria-selected`; o trabalho é tornar o comportamento consistente e verificável.

**Alternatives considered**:
- Tratar acessibilidade como fase futura: rejeitado por ser requisito transversal e mais barato de corrigir durante a migração.

### D9 — Validação visual

**Decision**: Validar com a suíte existente, novos contratos de UI e uma matriz de 64 verificações (8 áreas × 4 larguras × 2 temas), com capturas antes/depois.

**Rationale**: Critérios visuais precisam de evidência reproduzível. A matriz cobre os cenários críticos sem introduzir ferramenta de snapshot obrigatória.

**Alternatives considered**:
- Apenas inspeção manual final: rejeitado por baixa rastreabilidade.
- Snapshot visual automatizado como gate único: rejeitado por sensibilidade a fontes/renderização; pode complementar, mas não substituir a revisão.

### D10 — Ferramentas e restrições

**Decision**: Manter HTML/CSS/JS vanilla, Tailwind CDN, Plotly e Lightweight Charts. Usar pytest e Playwright para validação. Não adicionar dependências de runtime.

**Rationale**: A constituição exige SPA estática e proíbe novas funcionalidades em Streamlit, mas não exige reescrita. A estabilidade da stack é um ativo do projeto.

**Alternatives considered**:
- Migrar para React/Vue: rejeitado por violar o escopo e a constituição.
- Adicionar bundler: rejeitado por complexidade desnecessária.

## Unknowns Resolved

Nenhuma pendência de clarificação permanece. As decisões acima cobrem tema padrão, escopo, ícones, onboarding, encoding, responsividade, acessibilidade e validação.
