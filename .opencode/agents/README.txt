# Agentes de projeto

Equipe reutilizável do Market Opportunity Engine, definida no formato V2 do OpenCode (`.opencode/agents/*.md`). Nenhum agente fixa modelo: todos herdam o modelo da sessão principal (DeepSeek 4.1).

| Agente | Modo | Escrita | Shell | Uso |
|---|---|---|---|---|
| `product-ux-auditor` | subagent | negada | negada | Produto, fluxos, IA, hierarquia e usabilidade |
| `architecture-auditor` | subagent | negada | negada | Arquitetura, contratos, dependências e regressões |
| `investment-data-auditor` | subagent | negada | negada | Dados financeiros, unidades, moedas e cálculos |
| `security-auditor` | subagent | negada | negada | Auth, CORS, upload, exposição e cadeia de suprimentos |
| `accessibility-reviewer` | subagent | negada | negada | Semântica, teclado, contraste, responsividade |
| `frontend-implementer` | subagent | apenas `src/web/**` | negada | Tarefas de interface |
| `backend-data-implementer` | subagent | apenas `src/api/**`, `src/data_loader/**`, `src/evaluator/**`, `src/strategies/**`, requisitos | negada | Backend e dados |
| `qa-test-engineer` | subagent | apenas `tests/**` | negada | Testes e critérios de aceitação |
| `final-reviewer` | subagent | negada | negada | Revisão independente do diff |

## Regras de operação

- O agente principal é o único responsável por Git, branches, commits, shell, testes, servidores e integração.
- Apenas um implementador com escrita deve atuar por vez.
- Auditores e revisores não executam comandos; quando um comportamento depende de runtime, o agente principal deve fornecer a evidência.
- Nenhum subagente pode fazer commit, push, merge, reset, clean ou stash.
- Mudanças de regra financeira exigem requisito documentado e evidência; caso contrário, o comportamento atual é preservado e a decisão é registrada.
