# Data Model: Layout Profissional e Unificado da Interface Web

**Feature**: 023-professional-ui-layout
**Date**: 2026-10-27
**Input**: [spec.md](./spec.md) | [research.md](./research.md)

Este modelo descreve entidades conceituais de interface, navegação e validação visual. Não representa tabelas de banco de dados nem altera contratos de API.

## 1. Environment (Ambiente)

Agrupamento superior de navegação.

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `id` | string | Sim | Valores estáveis: `carteira`, `quant`. |
| `label` | string | Sim | Rótulo visível: “Minha Carteira” ou “Análise Quantitativa”. |
| `order` | integer | Sim | Ordem de exibição no alternador. |
| `defaultAreaId` | string | Sim | Área aberta quando o ambiente é selecionado sem rota explícita. |
| `areaIds` | lista de strings | Sim | Exatamente quatro áreas, na ordem de exibição. |

**Validações**:
- Exatamente dois ambientes.
- Cada ambiente possui exatamente quatro áreas.
- Nenhuma área pertence a mais de um ambiente.

## 2. Area (Área da Plataforma)

Cada uma das oito subáreas navegáveis.

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `id` | string | Sim | Identificador estável usado pela navegação e pelos testes. |
| `environmentId` | string | Sim | Referencia um `Environment`. |
| `label` | string | Sim | Rótulo visível na subnavegação. |
| `route` | string | Sim | Rota hash canônica. |
| `panelId` | string | Sim | Identificador do painel correspondente no DOM. |
| `title` | string | Sim | Título principal da área. |
| `purpose` | string | Sim | Descrição curta do valor da área. |
| `emptyState` | `EmptyState` | Não | Estado exibido quando não há dados. |
| `preservedContractIds` | lista de strings | Sim | IDs que não podem ser removidos/renomeados. |

**Mapeamento obrigatório**:

| Ambiente | Área | Rota canônica | Painel |
|---|---|---|---|
| Minha Carteira | Resumo | `carteira/visao-geral` | `#tab-overview` |
| Minha Carteira | Posições & Ativos | `carteira/posicoes` | `#tab-portfolio` |
| Minha Carteira | Proventos | `carteira/proventos` | `#tab-pane-proventos` |
| Minha Carteira | Evolução Patrimonial | `carteira/patrimonio` | `#tab-pane-patrimonio` |
| Análise Quantitativa | Radar | `quant/radar` | `#tab-pane-radar` |
| Análise Quantitativa | Gráfico | `quant/grafico` | `#tab-terminal` |
| Análise Quantitativa | Simulador | `quant/simulador` | `#tab-simulator` |
| Análise Quantitativa | Playbook | `quant/playbook` | `#tab-playbook` |

**Validações**:
- Exatamente oito áreas.
- Cada `panelId` é único no documento.
- Cada `route` é única e resolvível.
- Rotas legadas continuam aceitas quando já existirem.

## 3. NavigationState (Estado de Navegação)

Estado corrente de ambiente, área e origem da decisão.

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `environmentId` | string | Sim | Deve corresponder a um `Environment`. |
| `areaId` | string | Sim | Deve pertencer ao ambiente ativo. |
| `routeSource` | enum | Sim | `url`, `storage` ou `default`. |
| `isHistorySynchronized` | boolean | Sim | Verdadeiro quando ambiente, subnav e painel estão alinhados. |

**Precedência de resolução**:
1. `url` — hash/rota explícita válida.
2. `storage` — `mo_active_tab` e `mo_active_pillar`, quando não há rota explícita.
3. `default` — `carteira/visao-geral`.

**Invariantes**:
- Exatamente um `areaId` ativo.
- Exatamente um painel visível.
- Exatamente um item de subnavegação com `aria-selected="true"`.
- Exatamente um botão de ambiente com `aria-selected="true"`.
- Voltar/avançar e recarregamento preservam a consistência.

**Transições**:
- `url → NavigationState`: aplica rota e sincroniza histórico.
- `storage → NavigationState`: restaura última área válida.
- `default → NavigationState`: abre Resumo quando não há URL nem storage.
- `toggle environment`: seleciona `defaultAreaId` do novo ambiente, salvo rota explícita.
- `hashchange/popstate`: recalcula a partir da URL e sincroniza o DOM.

## 4. ThemePreference (Preferência de Tema)

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `value` | enum | Sim | `light` ou `dark`. |
| `source` | enum | Sim | `default`, `user`, `storage`. |
| `persisted` | boolean | Sim | Verdadeiro quando salvo em `localStorage`. |
| `chartsUpdated` | boolean | Sim | Verdadeiro quando gráficos refletem o tema. |

**Validações**:
- Valor padrão: `light`.
- Persistência em `terminal_theme`.
- Alternância deve refletir em todas as áreas e gráficos sem recarregar.
- Valor inválido em storage cai para `light` sem erro visível.

**Transições**:
- `init`: storage válido → aplica; ausente/inválido → `light`.
- `toggle`: `light ↔ dark`, persiste e atualiza gráficos.
- `reload`: restaura o último valor válido.

## 5. VisualTokenSet (Conjunto de Tokens Visuais)

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `colorRoles` | mapa | Sim | Superfícies, bordas, texto, primário, sucesso, perigo, aviso, info. |
| `typographyScale` | mapa | Sim | Display, título de seção, título de card, corpo, labels, metadados. |
| `spacingScale` | lista | Sim | Escala modular base 4px. |
| `radiusScale` | mapa | Sim | xs, sm, md, lg, xl. |
| `shadowScale` | mapa | Sim | sm, md, lg. |
| `themeVariants` | lista | Sim | `light`, `dark`. |

**Validações**:
- Todo texto funcional usa tamanho ≥ 11px.
- Valores financeiros usam algarismos tabulares/monoespaçados.
- Contraste de texto atende AA.
- Nenhum componente depende de cores hardcoded fora dos tokens.
- Tokens devem produzir resultado equivalente nos dois temas.

## 6. ComponentContract (Componente Visual Compartilhado)

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `name` | string | Sim | Ex.: cartão, botão, tabela, campo, badge, acordeão. |
| `variants` | lista | Não | Ex.: primário, secundário, contextual. |
| `states` | lista | Sim | default, hover, focus, active, disabled, loading, empty, error. |
| `accessibility` | `AccessibilityContract` | Sim | Papel, nome acessível, foco e teclado. |
| `themes` | lista | Sim | Deve funcionar em `light` e `dark`. |

**Validações**:
- Mesmo componente tem aparência e comportamento consistentes em todas as áreas.
- Estados de foco são visíveis.
- Componentes interativos têm área de toque adequada.
- Não há cartões aninhados redundantes.

## 7. AccessibilityContract

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `role` | string | Sim | Papel semântico correto. |
| `accessibleName` | string | Sim | Nome anunciado por tecnologia assistiva. |
| `keyboardReachable` | boolean | Sim | Alcançável por Tab. |
| `keyboardActivatable` | boolean | Sim | Ativável por Enter/Espaço quando aplicável. |
| `focusVisible` | boolean | Sim | Indicador de foco visível. |
| `contrastRatio` | number | Sim | ≥ 4.5:1 para texto normal. |
| `reducedMotion` | boolean | Sim | Respeita preferência por movimento reduzido. |
| `zoom200` | boolean | Sim | Funcional com zoom de 200%. |

## 8. EmptyState

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `areaId` | string | Sim | Área à qual se aplica. |
| `condition` | string | Sim | Ex.: ausência de carteira/importação. |
| `title` | string | Sim | Título orientativo. |
| `description` | string | Sim | Explicação do próximo passo. |
| `primaryAction` | string | Não | Ação principal, como importar extratos. |
| `visible` | boolean | Sim | Derivado da condição de dados. |

**Validações**:
- No Resumo, visível apenas quando não há dados de carteira/importação.
- Com dados presentes, não ocupa espaço operacional.
- Nunca substitui mensagens de erro ou indisponibilidade.

## 9. ScreenValidation (Verificação de Tela)

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `areaId` | string | Sim | Uma das oito áreas. |
| `width` | integer | Sim | 375, 768, 1366 ou 1920. |
| `theme` | enum | Sim | `light` ou `dark`. |
| `status` | enum | Sim | `pending`, `approved`, `rejected`. |
| `evidence` | string | Não | Referência à captura/observação. |
| `notes` | string | Não | Desvios e correções. |

**Cardinalidade**: 8 × 4 × 2 = 64 registros obrigatórios para aprovação final.

**Validações**:
- Nenhum registro `pending` ou `rejected` na entrega.
- Cada registro cobre ausência de overflow, legibilidade, alinhamento, contraste e estados interativos.

## 10. EncodingAudit (Auditoria de Conteúdo)

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `file` | string | Sim | Arquivo auditado. |
| `occurrencesBefore` | integer | Sim | Contagem inicial de artefatos. |
| `occurrencesAfter` | integer | Sim | Deve ser zero. |
| `reviewedDiff` | boolean | Sim | Diff revisado para não alterar conteúdo legítimo. |
| `status` | enum | Sim | `pending`, `clean`, `failed`. |

**Validações**:
- `occurrencesAfter = 0` em textos visíveis.
- Nenhuma alteração em dados, contratos ou APIs.
- Conteúdo em português permanece semanticamente idêntico.

## 11. Relationships

```text
Environment 1 ─── N Area
Area 1 ─── 0..1 EmptyState
Area 1 ─── N ScreenValidation
NavigationState N ─── 1 Environment
NavigationState N ─── 1 Area
ThemePreference 1 ─── 1 VisualTokenSet
ComponentContract N ─── 1 AccessibilityContract
EncodingAudit N ─── 1 file
```

## 12. Regras Globais

1. Nenhuma entidade pode alterar cálculos, séries ou semântica financeira.
2. Identificadores de contrato existentes são imutáveis.
3. Exatamente um painel visível e um estado ativo por vez.
4. Toda área deve funcionar nos dois temas e nas quatro larguras.
5. Todo texto funcional deve respeitar o piso de 11px.
6. Nenhuma API ou esquema de dados é criado, removido ou alterado.
