# Contract: UI Navigation & Sidebar Filtering

## 1. Contrato de Roteamento por Hash de URL

A SPA suporta sincronização reativa com a barra de endereços do navegador:

| Hash de URL | ID da Seção no DOM | Nome da Aba |
|---|---|---|
| `#/` ou `#radar` | `#tab-radar` | Radar de Oportunidades |
| `#terminal` ou `#grafico` | `#tab-terminal` | Terminal Gráfico (TradingView) |
| `#simulator` ou `#simulador` | `#tab-simulator` | Simulador & Otimizador |
| `#playbook` | `#tab-playbook` | Playbook de Estratégias |

### 1.1 Comportamento ao Recarregar (F5)
1. O navegador dispara `DOMContentLoaded`.
2. A aplicação inspeciona `window.location.hash`.
3. Se a hash for `#terminal`, `#tab-terminal` é exibida, seu botão de navegação recebe `.active`, e o gráfico ajusta o tamanho automaticamente.
4. Se a hash for vazia, a aplicação lê `localStorage.getItem('market_engine_active_tab')`. Se existir, chaveia para ela; caso contrário, abre `#tab-radar`.

---

## 2. Contrato de Filtragem por Direção da Barra Lateral

Ao invocar `updateSidebarDirectionFilter(direction)`:
- Se `direction === 'BUY'`:
  - Todos os elementos `.strategy-group-wrapper[data-direction="BUY"]` removem a classe `hidden`.
  - Todos os elementos `.strategy-group-wrapper[data-direction="SELL"]` recebem a classe `hidden`.
- Se `direction === 'SELL'`:
  - Elementos `BUY` recebem `hidden`, elementos `SELL` removem `hidden`.
- Se `direction === 'BOTH'`:
  - Todos os elementos removem `hidden`.
