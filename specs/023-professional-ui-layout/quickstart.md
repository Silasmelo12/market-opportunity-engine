# Quickstart: Validação do Layout Profissional e Unificado

**Feature**: 023-professional-ui-layout
**Date**: 2026-10-27
**References**: [spec.md](./spec.md) · [plan.md](./plan.md) · [data-model.md](./data-model.md) · [contracts/ui-layout-contract.md](./contracts/ui-layout-contract.md)

Este guia descreve como executar a aplicação e validar a feature de ponta a ponta. Ele não contém a implementação nem a suíte completa de testes.

## 1. Pré-requisitos

- Python 3.11+ (o repositório está validado em Python 3.14).
- Dependências de runtime e desenvolvimento instaladas.
- Navegador moderno para validação manual.
- Playwright com navegador Chromium para os testes E2E.

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m playwright install chromium
```

## 2. Executar a aplicação

Opção A — entrypoint do projeto:

```bash
python run_server.py
```

Opção B — Uvicorn direto:

```bash
PYTHONPATH=. python -m uvicorn src.api.server:app --host 127.0.0.1 --port 8000
```

Abrir: `http://127.0.0.1:8000`.

## 3. Validar contratos automatizados

### 3.1 Suíte unitária e de contratos

```bash
PYTHONPATH=. python -m pytest tests/unit -v
```

**Esperado**: todos os testes passam; nenhuma regressão nos contratos de UI/API.

### 3.2 Navegação e layout E2E

```bash
PYTHONPATH=. python -m pytest tests/e2e -v
```

**Esperado**: todos os cenários de navegação, tema, painel único, IDs e responsividade passam.

### 3.3 Suíte completa

```bash
PYTHONPATH=. python -m pytest tests/ -v
```

**Esperado**: mesma linha de base ou melhor; zero falhas novas.

### 3.4 Garantia de que o backend não foi alterado

```bash
git diff --stat -- src/api
```

**Esperado**: saída vazia. Nenhum arquivo em `src/api/` deve aparecer no diff da feature.

## 4. Auditorias rápidas de conteúdo e tipografia

### 4.1 Artefatos de encoding

```bash
grep -nP "Ã|â†|â–|ð" src/web/index.html src/web/app.js src/web/modules/*.js
```

**Esperado**: nenhuma ocorrência.

### 4.2 Piso tipográfico

```bash
grep -n "text-\[10px\]" src/web/index.html
```

**Esperado**: nenhuma ocorrência em texto funcional. Casos decorativos, se existirem, devem ser justificados e não podem ser labels, botões ou metadados acionáveis.

### 4.3 IDs duplicados

```bash
grep -o 'id="[^"]*"' src/web/index.html | sort | uniq -d
```

**Esperado**: saída vazia.

## 5. Matriz de validação visual

Executar as 8 áreas nas 4 larguras e nos 2 temas: **64 verificações**.

| Área | 375px | 768px | 1366px | 1920px |
|---|---|---|---|---|
| Resumo | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |
| Posições & Ativos | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |
| Proventos | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |
| Evolução Patrimonial | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |
| Radar | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |
| Gráfico | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |
| Simulador | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |
| Playbook | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |

### Checklist por verificação

- Sem sobreposição, corte ou rolagem horizontal global.
- Tabelas largas rolam apenas no próprio contêiner, com indicativo.
- Tipografia legível; nenhum texto funcional abaixo de 11px.
- Contraste AA em texto, labels e controles.
- Cabeçalho, ambiente, subnav e ações utilizáveis.
- Estados ativo, hover, foco e desabilitado visíveis.
- Gráficos ocupam a largura do contêiner e não colapsam.
- Estado vazio/onboarding coerente com a presença ou ausência de dados.

## 6. Cenários funcionais obrigatórios

### 6.1 Navegação

1. Abrir `/#carteira/visao-geral` e confirmar ambiente “Minha Carteira” + subaba Resumo.
2. Alternar para “Análise Quantitativa” e percorrer as quatro subabas.
3. Recarregar a página e confirmar restauração da última área.
4. Usar voltar/avançar do navegador e confirmar sincronização.
5. Inserir hash inválido e confirmar fallback previsível.
6. Verificar que existe exatamente um painel visível e nenhum ID duplicado.

### 6.2 Tema

1. Confirmar tema claro como padrão em uma sessão sem preferência.
2. Alternar para escuro e confirmar atualização de todas as áreas e gráficos.
3. Recarregar e confirmar persistência.
4. Repetir a matriz visual nos dois temas.

### 6.3 Dados e estados

1. Testar com carteira vazia: banner de primeiro uso visível apenas nesse cenário.
2. Testar com carteira preenchida: banner não deve ocupar o espaço operacional.
3. Testar ticker/nome longo e valores extensos: sem sobreposição.
4. Testar falha/atraso de cotação: sinalizações de contingência visíveis.
5. Testar filtros, ordenação, paginação e simulação: comportamento preservado.

### 6.4 Acessibilidade

1. Percorrer a interface apenas com teclado.
2. Confirmar foco visível em todos os controles.
3. Confirmar ativação por Enter/Espaço nos controles aplicáveis.
4. Testar zoom de 200% sem perda de conteúdo.
5. Ativar preferência por movimento reduzido e confirmar supressão de animações não essenciais.
6. Verificar `aria-selected` nos controles de navegação.

## 7. Critérios de aceite

A feature é considerada validada quando:

- [ ] Suíte `pytest tests/` passa sem falhas novas.
- [ ] `src/api/` permanece sem alterações.
- [ ] Zero artefatos de encoding em textos visíveis.
- [ ] Zero IDs duplicados.
- [ ] Exatamente um painel visível por estado.
- [ ] 8/8 áreas aprovadas nos temas claro e escuro.
- [ ] 64/64 verificações visuais aprovadas.
- [ ] Nenhum texto funcional abaixo de 11px.
- [ ] Navegação por teclado e foco visível funcionando.
- [ ] Rotas, IDs e funções globais preservados.
- [ ] Nenhuma funcionalidade ou conteúdo removido.

## 8. Solução de problemas

- **Playwright não encontrado**: instalar `requirements-dev.txt` e executar `python -m playwright install chromium`.
- **Servidor não inicia**: verificar `PYTHONPATH=.` e a porta escolhida.
- **Gráfico não redimensiona**: confirmar que o contêiner tem largura/altura definidas e que o resize é chamado na abertura da área e na troca de tema.
- **Tema não persiste**: verificar a chave `terminal_theme` no `localStorage` e se `applyTheme` está acessível em `window`.
- **Rota não abre**: validar a precedência URL > `localStorage` > padrão e a existência do painel correspondente.

---

## 9. Diário de Execução da Implementação

### T001 — Baseline da suíte

- Branch: `feat/professional-ui-layout`
- Working tree inicial: apenas artefatos não rastreados de dados (`B3/`, `scratch/`, CSVs) e a própria pasta da spec.
- Baseline em 2026-10-27, com `venv/bin/python` (Python 3.14.4):
  - `PYTHONPATH=. python -m pytest tests/unit -q` → **95 passed, 2 skipped**.
  - `PYTHONPATH=. python -m pytest tests/e2e -q` → **18 passed**.
- Conclusão: linha de base verde; qualquer falha nova é regressão da feature.

### T002 — Baseline visual

- Captura automatizada das 8 áreas × 4 larguras (375/768/1366/1920) × 2 temas = **64 imagens**.
- Destino: `/tmp/023-ui-before/` (fora do repositório, conforme plano).
- Carteira sintética (PETR4.SA, TGAR11.SA, caixa e proventos) e respostas de `/api/radar`, `/api/analyze` e `/api/portfolio/quotes` mockadas para determinismo.

### T003 — Inventário de IDs, rotas e funções globais

- IDs do contrato presentes: todos, exceto `#b3-multi-file-input` (referenciado por `onclick` no banner de primeiro uso, porém ausente do DOM). **Lacuna registrada para correção.**
- Rotas canônicas e legadas: todas mapeadas em `src/web/modules/constants.js` (`CANONICAL_ROUTES` + `ROUTE_ALIASES`).
- Funções globais: `window.appState` explícito; `window.applyTheme` disponível por declaração de função de topo.
- IDs duplicados: nenhum (a checagem inicial por `grep 'id="'` gerou falsos positivos em `data-id`; a extração estrita de `id="..."` não encontrou duplicatas).
