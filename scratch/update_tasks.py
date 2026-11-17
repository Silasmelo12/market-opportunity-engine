import pathlib

p = pathlib.Path('specs/021-investidor10-ui-redesign/tasks.md')
lines = p.read_text(encoding='utf-8').splitlines()

idx = None
for i, line in enumerate(lines):
    if line.startswith('- [ ] **T036:'):
        idx = i
        break

assert idx is not None, 'T036 line not found'

new_block = [
    '- [x] **T036: [Prioridade 4 - Quality Gate] Verificação Visual Dual Theme, A11y e Testes Automatizados**',
    '  - *Ação*:',
    '    1. Executar `node --check src/web/app.js` e `git diff --check`.',
    '    2. Executar auditoria visual Impeccable detect (`.agents/skills/impeccable/scripts/impeccable.cmd detect src/web`).',
    '    3. Executar `python -m pytest tests/unit -v` (95 passed, 2 skipped em planilhas B3 opcionais).',
    '    4. Executar suíte completa de testes E2E (`python -m pytest tests/e2e -v`, 18 passed: 15 em navegação/contraste/responsividade/roteamento e 3 em layout e alternância de Proventos).',
    '    5. Capturar 24 screenshots de comprovação visual cobrindo as 6 telas principais (Visão Geral, Radar, Gráfico Interativo, Simulador, Playbook e Custódia) em 1600px desktop e 768px tablet nos modos Claro e Escuro.',
    '  - *Validação*: 100% dos testes unitários e E2E aprovados (95 unitários + 18 E2E = 113 testes automatizados). Conformidade estrita com o `DESIGN.md`.',
    '  - *Status*: Concluído na Fase 3B.'
]

lines = lines[:idx] + new_block
p.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('Updated tasks.md successfully')
