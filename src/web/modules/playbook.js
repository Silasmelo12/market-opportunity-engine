// Módulo do Playbook de Estratégias (Aba #tab-playbook)
// Implementa busca interativa, filtro por direção/categoria e cards do catálogo (Penpot 08 — Playbook).

const PLAYBOOK_FEATURED_CARDS = [
  {
    id: 't1_open',
    title: 'Fundo 2x2 · Abertura',
    category: 'Proprietária',
    direction: 'BUY',
    badgeLabel: 'SINAL DE COMPRA',
    badgeClass: 'bg-success-soft text-positive',
    description: 'Violação da mínima de T-1 com fechamento de volta acima do suporte e entrada confirmada na abertura de T+1 (Zero Look-Ahead).',
    rule: 'Low[t] < Low[t-1] e Close[t] > Low[t-1] → Execução Open[t+1]'
  },
  {
    id: 't1_retest',
    title: 'Fundo 2x2 · Reteste',
    category: 'Proprietária',
    direction: 'BUY',
    badgeLabel: 'SINAL DE COMPRA',
    badgeClass: 'bg-success-soft text-positive',
    description: 'Após negação de fundo em T, aguarda retorno de liquidez à linha de referência dentro da janela de M barras com tolerância.',
    rule: 'Reteste na linha Low[t-1] em até M barras → Execução Limit'
  },
  {
    id: 'wyckoff_spring',
    title: 'Wyckoff Spring Institucional',
    category: 'Price Action',
    direction: 'BUY',
    badgeLabel: 'SINAL DE COMPRA',
    badgeClass: 'bg-success-soft text-positive',
    description: 'Varredura de liquidez abaixo do suporte estrutural de N barras seguida de rejeição imediata e volume acima da média.',
    rule: 'Sweep de suporte + rejeição de pavio inferior + Volume > SMA(20)'
  },
  {
    id: 'double_bottom_bos',
    title: 'Fundo Duplo + Quebra de Estrutura (BOS)',
    category: 'Price Action',
    direction: 'BUY',
    badgeLabel: 'SINAL DE COMPRA',
    badgeClass: 'bg-success-soft text-positive',
    description: 'Dois fundos em zona simétrica com filtro de tendência prévia de baixa, RSI não exausto e confirmação de rompimento do neckline.',
    rule: 'Fundo 1 ≈ Fundo 2 + Close > Neckline + RSI ≤ 60'
  },
  {
    id: 'zscore_extreme',
    title: 'Excesso Estatístico Z-Score / Bandas',
    category: 'Quantitativo',
    direction: 'BUY',
    badgeLabel: 'SINAL DE COMPRA',
    badgeClass: 'bg-success-soft text-positive',
    description: 'Desvio estatístico extremo (> 2σ abaixo da média móvel) combinado com fechamento de retorno para dentro da banda.',
    rule: 'Z-Score < -2.0 e retorno para dentro da Banda de Bollinger'
  },
  {
    id: 'sell_t1_open',
    title: 'Topo 2x2 · Negação de Resistência',
    category: 'Proprietária',
    direction: 'SELL',
    badgeLabel: 'SINAL DE VENDA',
    badgeClass: 'bg-danger-soft text-negative',
    description: 'Violação da máxima anterior ou máxima de N barras com fechamento de rejeição abaixo da resistência (armadilha de topo).',
    rule: 'High[t] > High[t-1] e Close[t] < High[t-1] → Saída Open[t+1]'
  },
  {
    id: 'sell_wyckoff_upthrust',
    title: 'Wyckoff Upthrust (UTAD)',
    category: 'Price Action',
    direction: 'SELL',
    badgeLabel: 'SINAL DE VENDA',
    badgeClass: 'bg-danger-soft text-negative',
    description: 'Rompimento falso de resistência institucional com exaustão compradora e fechamento na metade inferior da barra.',
    rule: 'Falso rompimento de topo + perda da mínima de gatilho'
  },
  {
    id: 'rebal_rf_rv',
    title: 'Controle de Risco & Rebalanceamento por Bandas',
    category: 'Risco & Alocação',
    direction: 'RISK',
    badgeLabel: 'GESTÃO DE RISCO',
    badgeClass: 'bg-warning-soft text-warning',
    description: 'Limita concentração máxima por ativo (ex.: 25%) e realiza vendas parciais quando o peso ultrapassa a banda de tolerância.',
    rule: 'Peso Ativo > Meta + Banda (5%) → Realização Parcial / Rotação'
  },
];

let _playbookFilter = 'ALL';
let _playbookQuery = '';

function renderPlaybookCards() {
  const grid = document.getElementById('playbook-cards-grid');
  const countEl = document.getElementById('playbook-results-count');
  if (!grid) return;

  const q = (_playbookQuery || '').toLowerCase().trim();
  const filtered = PLAYBOOK_FEATURED_CARDS.filter(card => {
    if (_playbookFilter !== 'ALL' && card.direction !== _playbookFilter) return false;
    if (!q) return true;
    return (
      card.title.toLowerCase().includes(q) ||
      card.category.toLowerCase().includes(q) ||
      card.description.toLowerCase().includes(q) ||
      card.rule.toLowerCase().includes(q)
    );
  });

  if (countEl) {
    countEl.textContent = `${filtered.length} ${filtered.length === 1 ? 'estratégia destacada' : 'estratégias destacadas'}`;
  }

  if (filtered.length === 0) {
    grid.innerHTML = `
      <div class="card-surface p-6 text-center text-subtle text-xs col-span-full">
        Nenhuma estratégia encontrada para o filtro selecionado.
      </div>
    `;
  } else {
    grid.innerHTML = filtered.map(c => `
      <article class="playbook-strategy-card card-surface p-4 flex flex-col justify-between gap-3">
        <div class="space-y-2">
          <div class="flex items-center justify-between gap-2">
            <span class="px-2 py-0.5 rounded text-[11px] font-bold ${c.badgeClass}">${c.badgeLabel}</span>
            <span class="text-[11px] font-mono text-muted">${c.category}</span>
          </div>
          <h3 class="text-sm font-bold text-strong">${c.title}</h3>
          <p class="text-xs text-muted leading-relaxed">${c.description}</p>
        </div>
        <div class="pt-2 border-t border-default text-[11px] font-mono text-info">
          ${c.rule}
        </div>
      </article>
    `).join('');
  }

  // Also filter the 4 group cards below if search query is active
  document.querySelectorAll('#tab-playbook .playbook-group-card').forEach(groupCard => {
    if (!q) {
      groupCard.classList.remove('hidden');
      return;
    }
    const text = (groupCard.textContent || '').toLowerCase();
    groupCard.classList.toggle('hidden', !text.includes(q));
  });
}

function setupPlaybookControls() {
  const searchInput = document.getElementById('playbook-search-input');
  const filterBtns = document.querySelectorAll('#playbook-filter-pills .playbook-filter-btn');

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      _playbookQuery = searchInput.value || '';
      renderPlaybookCards();
    });
  }

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      _playbookFilter = btn.getAttribute('data-filter') || 'ALL';
      filterBtns.forEach(b => {
        const isActive = (b.getAttribute('data-filter') === _playbookFilter);
        b.classList.toggle('active-cat', isActive);
        b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
      });
      renderPlaybookCards();
    });
  });

  renderPlaybookCards();
}

if (typeof window !== 'undefined') {
  window.setupPlaybookControls = setupPlaybookControls;
  window.renderPlaybookCards = renderPlaybookCards;
  window.renderPlaybookPenpotCards = renderPlaybookCards;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { setupPlaybookControls, renderPlaybookCards };
}
