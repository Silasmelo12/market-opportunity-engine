// Módulo de Modais Interativos (Importar B3 e Novo Lançamento), Custódia Penpot e Barra Mobile
// Implementa as telas 02, 09, 10, 11, 12 e 13 do arquivo oficial do Penpot.

let _b3ModalSelectedFiles = [];
let _custodyCategoryFilter = 'ALL';

function _classifyTickerCategory(ticker) {
  const t = String(ticker || '').toUpperCase();
  if (t.includes('34.SA') || t.includes('34') || t === 'NVDA' || t === 'AAPL') return 'BDRs';
  if (t.includes('11.SA') || t.includes('11')) return 'FIIs';
  if (t.includes('BTC') || t.includes('ETH') || t.includes('SOL') || t.includes('GC=F') || t.includes('CL=F') || t.includes('^GSPC')) return 'Cripto';
  return 'Ações';
}

function _formatBrlModal(val) {
  const n = Number(val) || 0;
  return 'R$ ' + n.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/**
 * Renderiza a tabela "Ativos em destaque" na Visão Geral (Penpot Screen 01) e a legenda do Donut.
 */
function renderOverviewPenpotWidgets(holdings, quotesMap, totalEquity) {
  // 1. Legenda dinâmica do Donut (#overview-donut-legend)
  const legendEl = document.getElementById('overview-donut-legend');
  if (legendEl) {
    let valAcoes = 0;
    let valFiis = 0;
    let valBdrs = 0;
    let valCripto = 0;
    (holdings || []).forEach(h => {
      const sh = Number(h.shares) || 0;
      const avgP = Number(h.average_buy_price) || 0;
      const q = (quotesMap || {})[(h.ticker || '').toUpperCase()] || (quotesMap || {})[`${(h.ticker || '').toUpperCase()}.SA`];
      const curP = (q && Number(q.price) > 0) ? Number(q.price) : avgP;
      const v = sh * curP;
      const cat = _classifyTickerCategory(h.ticker);
      if (cat === 'FIIs') valFiis += v;
      else if (cat === 'BDRs') valBdrs += v;
      else if (cat === 'Cripto') valCripto += v;
      else valAcoes += v;
    });
    const denom = Math.max(1, totalEquity || (valAcoes + valFiis + valBdrs + valCripto));
    const items = [
      { label: 'Ações Brasil', val: valAcoes, pct: ((valAcoes / denom) * 100).toFixed(1), dot: 'bg-sky-500' },
      { label: 'Fundos Imobiliários (FIIs)', val: valFiis, pct: ((valFiis / denom) * 100).toFixed(1), dot: 'bg-amber-400' },
      { label: 'BDRs & Exterior', val: valBdrs, pct: ((valBdrs / denom) * 100).toFixed(1), dot: 'bg-emerald-500' },
      { label: 'Cripto & Macro', val: valCripto, pct: ((valCripto / denom) * 100).toFixed(1), dot: 'bg-purple-500' },
    ];
    legendEl.innerHTML = items.map(it => `
      <div class="flex items-center justify-between text-xs">
        <span class="flex items-center gap-2 text-muted font-medium">
          <span class="w-2.5 h-2.5 rounded-full ${it.dot}"></span>
          ${it.label}
        </span>
        <span class="font-mono font-bold text-strong">${it.pct.replace('.', ',')}%</span>
      </div>
    `).join('');
  }

  // 2. Tabela "Ativos em destaque" (#overview-highlights-tbody)
  const tbody = document.getElementById('overview-highlights-tbody');
  if (!tbody) return;

  if (!Array.isArray(holdings) || holdings.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="4" class="px-3 py-4 text-center text-subtle font-mono text-xs">
          Importe seus extratos da B3 ou registre um lançamento para exibir seus ativos em destaque.
        </td>
      </tr>
    `;
    return;
  }

  const enriched = holdings.map(h => {
    const sh = Number(h.shares) || 0;
    const avgP = Number(h.average_buy_price) || 0;
    const cost = sh * avgP;
    const q = (quotesMap || {})[(h.ticker || '').toUpperCase()] || (quotesMap || {})[`${(h.ticker || '').toUpperCase()}.SA`];
    const hasQuote = Boolean(q && Number(q.price) > 0);
    const curP = hasQuote ? Number(q.price) : avgP;
    const val = sh * curP;
    const pct = (hasQuote && cost > 0) ? ((val - cost) / cost) * 100 : null;
    const weight = totalEquity > 0 ? (val / totalEquity) * 100 : 0;
    return { ticker: h.ticker, curP, hasQuote, pct, weight, val };
  }).sort((a, b) => b.val - a.val).slice(0, 6);

  tbody.innerHTML = enriched.map(item => {
    const pctText = item.pct !== null
      ? `${item.pct >= 0 ? '+' : ''}${item.pct.toFixed(2).replace('.', ',')}%`
      : 'Sem cotação';
    const pctClass = item.pct === null ? 'text-muted' : (item.pct >= 0 ? 'text-positive' : 'text-negative');
    return `
      <tr class="hover-surface">
        <td class="px-3 py-2.5 font-bold text-strong font-mono">${item.ticker}</td>
        <td class="px-3 py-2.5 text-right font-mono text-strong">${_formatBrlModal(item.curP)}</td>
        <td class="px-3 py-2.5 text-right font-mono font-bold ${pctClass}">${pctText}</td>
        <td class="px-3 py-2.5 text-right font-mono text-info font-semibold">${item.weight.toFixed(1).replace('.', ',')}%</td>
      </tr>
    `;
  }).join('');
}

/**
 * Renderiza os 4 KPIs de Custódia e os cards de categorias dinâmicos na aba Posições & Custódia (Penpot Screen 02).
 */
function renderCustodyPenpotView() {
  const appState = (typeof window !== 'undefined' && window.appState) ? window.appState : null;
  if (!appState || !appState.portfolioState) return;

  const ps = appState.portfolioState;
  const holdings = Array.isArray(ps.holdings) ? ps.holdings : [];
  const quotesMap = ps.quotesCache || {};

  let totalCost = 0;
  let totalMarket = 0;

  holdings.forEach(h => {
    const sh = Number(h.shares) || 0;
    const avgP = Number(h.average_buy_price) || 0;
    totalCost += sh * avgP;
    const q = quotesMap[(h.ticker || '').toUpperCase()] || quotesMap[`${(h.ticker || '').toUpperCase()}.SA`];
    const curP = (q && Number(q.price) > 0) ? Number(q.price) : avgP;
    totalMarket += sh * curP;
  });

  const pnlVal = totalMarket - totalCost;
  const pnlPct = totalCost > 0 ? (pnlVal / totalCost) * 100 : 0;

  const badgeCount = document.getElementById('pos-total-count-badge');
  if (badgeCount) badgeCount.textContent = String(holdings.length);

  const elInv = document.getElementById('custody-kpi-invested');
  const elCost = document.getElementById('custody-kpi-cost');
  const elPnl = document.getElementById('custody-kpi-pnl');
  const elPnlSub = document.getElementById('custody-kpi-pnl-sub');
  const elCount = document.getElementById('custody-kpi-count');

  if (elInv) elInv.textContent = _formatBrlModal(totalMarket);
  if (elCost) elCost.textContent = _formatBrlModal(totalCost);
  if (elPnl) {
    const sign = pnlVal >= 0 ? '+' : '';
    elPnl.textContent = `${sign}${_formatBrlModal(pnlVal)}`;
    elPnl.className = `text-xl sm:text-2xl font-extrabold font-mono ${pnlVal >= 0 ? 'text-positive' : 'text-negative'}`;
  }
  if (elPnlSub) {
    const sign = pnlPct >= 0 ? '+' : '';
    elPnlSub.textContent = totalCost > 0 ? `${sign}${pnlPct.toFixed(2).replace('.', ',')}% sobre o custo` : 'Sem custo base';
  }
  if (elCount) elCount.textContent = `${holdings.length} ${holdings.length === 1 ? 'ativo' : 'ativos'}`;

  // Render dynamic category cards inside #investidor10-positions-categories
  const catContainer = document.getElementById('investidor10-positions-categories');
  if (!catContainer) return;

  const filteredHoldings = holdings.filter(h => {
    if (_custodyCategoryFilter === 'ALL') return true;
    return _classifyTickerCategory(h.ticker) === _custodyCategoryFilter;
  });

  if (filteredHoldings.length === 0) {
    catContainer.innerHTML = `
      <div class="card-surface category-card overflow-hidden">
        <div class="category-header p-4 flex items-center justify-between">
          <div>
            <h3 class="category-title font-bold text-sm">Nenhuma posição encontrada</h3>
            <span class="section-subtitle">Importe seus extratos da B3 ou clique em "+ Novo lançamento" para cadastrar ativos.</span>
          </div>
          <span class="font-mono text-xs text-muted">R$ 0,00</span>
        </div>
      </div>
    `;
    return;
  }

  const groups = {};
  filteredHoldings.forEach(h => {
    const cat = _classifyTickerCategory(h.ticker);
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(h);
  });

  const catTitles = {
    'Ações': 'Ações Brasileiras (B3)',
    'FIIs': 'Fundos Imobiliários (FIIs)',
    'BDRs': 'BDRs & Internacional',
    'Cripto': 'Criptomoedas & Macro',
  };

  catContainer.innerHTML = Object.entries(groups).map(([catKey, items], idx) => {
    let grpCost = 0;
    let grpVal = 0;
    const rowsHtml = items.map(h => {
      const sh = Number(h.shares) || 0;
      const avgP = Number(h.average_buy_price) || 0;
      const cost = sh * avgP;
      const q = quotesMap[(h.ticker || '').toUpperCase()] || quotesMap[`${(h.ticker || '').toUpperCase()}.SA`];
      const curP = (q && Number(q.price) > 0) ? Number(q.price) : avgP;
      const val = sh * curP;
      grpCost += cost;
      grpVal += val;
      const diff = val - cost;
      const diffPct = cost > 0 ? (diff / cost) * 100 : 0;
      const weight = totalMarket > 0 ? (val / totalMarket) * 100 : 0;
      const pnlClass = diff >= 0 ? 'text-positive' : 'text-negative';
      return `
        <tr class="hover-surface">
          <td class="px-3 py-2.5 font-bold text-strong font-mono">${h.ticker}</td>
          <td class="px-3 py-2.5 text-right font-mono text-strong">${sh.toLocaleString('pt-BR')}</td>
          <td class="px-3 py-2.5 text-right font-mono text-muted">${_formatBrlModal(avgP)}</td>
          <td class="px-3 py-2.5 text-right font-mono text-strong">${_formatBrlModal(curP)}</td>
          <td class="px-3 py-2.5 text-right font-mono font-bold ${pnlClass}">${diff >= 0 ? '+' : ''}${diffPct.toFixed(2).replace('.', ',')}%</td>
          <td class="px-3 py-2.5 text-right font-mono text-info font-semibold">${weight.toFixed(1).replace('.', ',')}%</td>
          <td class="px-3 py-2.5 text-right">
            <button type="button" class="btn-custody-open-chart btn-contextual text-info hover-primary text-xs font-semibold px-2 py-0.5 rounded surface-subtle border border-default cursor-pointer" data-ticker="${h.ticker}">
              Abrir gráfico
            </button>
          </td>
        </tr>
      `;
    }).join('');

    const grpDiff = grpVal - grpCost;
    const grpPct = grpCost > 0 ? (grpDiff / grpCost) * 100 : 0;
    const bodyId = `custody-cat-body-${idx}`;

    return `
      <div class="card-surface category-card overflow-hidden">
        <div class="category-header p-4 flex items-center justify-between cursor-pointer" data-target="${bodyId}">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg surface-subtle flex items-center justify-center font-bold text-info text-xs">${catKey.slice(0, 2).toUpperCase()}</div>
            <div>
              <h3 class="category-title font-bold text-sm">${catTitles[catKey] || catKey}</h3>
              <span class="section-subtitle">${items.length} ${items.length === 1 ? 'ativo em custódia' : 'ativos em custódia'}</span>
            </div>
          </div>
          <div class="flex items-center gap-6 text-xs">
            <div class="text-right">
              <span class="text-[11px] text-subtle font-semibold block uppercase">Valor Total</span>
              <span class="font-bold text-strong text-xs font-mono">${_formatBrlModal(grpVal)}</span>
            </div>
            <div class="text-right">
              <span class="text-[11px] text-subtle font-semibold block uppercase">Resultado</span>
              <span class="font-bold ${grpDiff >= 0 ? 'text-positive' : 'text-negative'} text-xs font-mono">${grpPct >= 0 ? '+' : ''}${grpPct.toFixed(2).replace('.', ',')}%</span>
            </div>
            <span class="custody-cat-chevron text-subtle">▼</span>
          </div>
        </div>
        <div id="${bodyId}" class="custody-cat-body table-scroll touch-scroll border-t border-default" tabindex="0">
          <table class="table-standard w-full text-left text-xs text-muted">
            <thead class="surface-canvas text-muted uppercase text-[11px] font-mono">
              <tr>
                <th class="px-3 py-2">Ativo</th>
                <th class="px-3 py-2 text-right">Qtd.</th>
                <th class="px-3 py-2 text-right">Preço Médio</th>
                <th class="px-3 py-2 text-right">Cotação</th>
                <th class="px-3 py-2 text-right">Resultado</th>
                <th class="px-3 py-2 text-right">Peso</th>
                <th class="px-3 py-2 text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-default font-mono text-[11px]">
              ${rowsHtml}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }).join('');

  catContainer.querySelectorAll('.category-header').forEach(hdr => {
    hdr.addEventListener('click', () => {
      const targetId = hdr.getAttribute('data-target');
      const body = document.getElementById(targetId);
      const chev = hdr.querySelector('.custody-cat-chevron');
      if (body) {
        body.classList.toggle('hidden');
        if (chev) chev.textContent = body.classList.contains('hidden') ? '▶' : '▼';
      }
    });
  });

  catContainer.querySelectorAll('.btn-custody-open-chart').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const t = btn.getAttribute('data-ticker');
      if (typeof openChartForHolding === 'function') {
        openChartForHolding(t, 'carteira/posicoes');
      }
    });
  });
}

function setupCustodyControls() {
  const btnExpandAll = document.getElementById('btn-pos-expand-all');
  const btnCollapseAll = document.getElementById('btn-pos-collapse-all');

  if (btnExpandAll) {
    btnExpandAll.addEventListener('click', () => {
      document.querySelectorAll('#investidor10-positions-categories .custody-cat-body').forEach(el => el.classList.remove('hidden'));
      document.querySelectorAll('#investidor10-positions-categories .custody-cat-chevron').forEach(ch => { ch.textContent = '▼'; });
    });
  }

  if (btnCollapseAll) {
    btnCollapseAll.addEventListener('click', () => {
      document.querySelectorAll('#investidor10-positions-categories .custody-cat-body').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('#investidor10-positions-categories .custody-cat-chevron').forEach(ch => { ch.textContent = '▶'; });
    });
  }

  document.querySelectorAll('#custody-category-pills .custody-cat-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      _custodyCategoryFilter = pill.getAttribute('data-cat-filter') || 'ALL';
      document.querySelectorAll('#custody-category-pills .custody-cat-pill').forEach(p => {
        const active = p.getAttribute('data-cat-filter') === _custodyCategoryFilter;
        p.classList.toggle('active-cat', active);
        p.setAttribute('aria-pressed', active ? 'true' : 'false');
      });
      renderCustodyPenpotView();
    });
  });

  const btnExport = document.getElementById('btn-custody-export-csv');
  if (btnExport) {
    btnExport.addEventListener('click', () => {
      const appState = window.appState;
      const holdings = (appState && appState.portfolioState && appState.portfolioState.holdings) || [];
      if (holdings.length === 0) {
        if (typeof showToastNotification === 'function') {
          showToastNotification('Nenhuma posição na carteira para exportar.', false);
        }
        return;
      }
      const csvRows = ['Ticker,Quantidade,PrecoMedio'];
      holdings.forEach(h => {
        csvRows.push(`${h.ticker},${h.shares},${h.average_buy_price}`);
      });
      const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'carteira_market_opportunity.csv';
      a.click();
      URL.revokeObjectURL(url);
    });
  }
}

/**
 * Configura o Modal 09 (Importar extratos da B3) e o Modal 10 (Novo lançamento).
 */
function setupPenpotModals() {
  // 1. Modal Novo Lançamento (#modal-new-trade)
  const modalTrade = document.getElementById('modal-new-trade');
  const btnHeaderAddTrade = document.getElementById('btn-header-add-trade');
  const btnPosNewTrade = document.getElementById('btn-pos-new-trade');
  const btnTradeClose = document.getElementById('btn-modal-trade-close') || document.getElementById('btn-trade-modal-close');
  const btnTradeCancel = document.getElementById('btn-modal-trade-cancel') || document.getElementById('btn-trade-modal-cancel');
  const btnTradeSave = document.getElementById('btn-modal-trade-save') || document.getElementById('btn-trade-modal-save');
  const inType = document.getElementById('trade-input-type');
  const inTicker = document.getElementById('modal-trade-ticker') || document.getElementById('trade-input-ticker');
  const inDate = document.getElementById('modal-trade-date') || document.getElementById('trade-input-date');
  const inQty = document.getElementById('modal-trade-shares') || document.getElementById('trade-input-qty');
  const inPrice = document.getElementById('modal-trade-price') || document.getElementById('trade-input-price');
  const inFees = document.getElementById('modal-trade-fees') || document.getElementById('trade-input-fees');
  const previewTotal = document.getElementById('modal-trade-total-preview') || document.getElementById('trade-preview-total');
  let activeTradeType = 'BUY';

  document.querySelectorAll('#modal-new-trade .modal-trade-type-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      activeTradeType = btn.getAttribute('data-type') || 'BUY';
      document.querySelectorAll('#modal-new-trade .modal-trade-type-btn').forEach(b => {
        const isAct = (b.getAttribute('data-type') === activeTradeType);
        b.className = isAct
          ? 'modal-trade-type-btn btn-primary text-xs py-1.5 rounded-md font-bold'
          : 'modal-trade-type-btn btn-secondary text-xs py-1.5 rounded-md font-semibold';
        b.setAttribute('aria-pressed', isAct ? 'true' : 'false');
      });
      updateTradePreview();
    });
  });

  const updateTradePreview = () => {
    if (!previewTotal) return;
    const q = Math.max(0, Number(inQty ? inQty.value : 0) || 0);
    const p = Math.max(0, Number(inPrice ? inPrice.value : 0) || 0);
    const f = Math.max(0, Number(inFees ? inFees.value : 0) || 0);
    const t = (inType && inType.value) || activeTradeType || 'BUY';
    const total = t === 'BUY' ? (q * p + f) : Math.max(0, q * p - f);
    previewTotal.textContent = _formatBrlModal(total);
  };

  [inType, inQty, inPrice, inFees].forEach(el => {
    if (el) el.addEventListener('input', updateTradePreview);
  });

  const openTradeModal = () => {
    if (!modalTrade) return;
    if (inDate && !inDate.value) {
      inDate.value = new Date().toISOString().slice(0, 10);
    }
    updateTradePreview();
    modalTrade.classList.remove('hidden');
    if (inTicker) inTicker.focus();
  };

  const closeTradeModal = () => {
    if (modalTrade) modalTrade.classList.add('hidden');
  };

  if (btnHeaderAddTrade) btnHeaderAddTrade.addEventListener('click', openTradeModal);
  if (btnPosNewTrade) btnPosNewTrade.addEventListener('click', openTradeModal);
  if (btnTradeClose) btnTradeClose.addEventListener('click', closeTradeModal);
  if (btnTradeCancel) btnTradeCancel.addEventListener('click', closeTradeModal);

  if (btnTradeSave) {
    btnTradeSave.addEventListener('click', () => {
      const rawTicker = (inTicker ? inTicker.value : '').trim().toUpperCase();
      const ticker = typeof resolveTicker === 'function' ? resolveTicker(rawTicker) : rawTicker;
      const qty = Number(inQty ? inQty.value : 0);
      const price = Number(inPrice ? inPrice.value : 0);
      const fees = Math.max(0, Number(inFees ? inFees.value : 0) || 0);
      const tradeType = (inType && inType.value) || activeTradeType || 'BUY';
      const dateStr = (inDate && inDate.value) || new Date().toISOString().slice(0, 10);

      if (!ticker || qty <= 0 || price <= 0) {
        if (typeof showToastNotification === 'function') {
          showToastNotification('Informe o ativo, quantidade positiva e preço unitário válido.', false);
        }
        return;
      }

      const appState = window.appState;
      if (!appState || !appState.portfolioState) return;
      const ps = appState.portfolioState;
      if (!Array.isArray(ps.holdings)) ps.holdings = [];

      const idx = ps.holdings.findIndex(h => h.ticker.toUpperCase() === ticker.toUpperCase());
      if (tradeType === 'DIVIDEND') {
        if (!Array.isArray(ps.b3MonthlyIncome)) ps.b3MonthlyIncome = [];
        const ym = dateStr.slice(0, 7);
        const totalDiv = Number((qty * price).toFixed(2));
        ps.b3MonthlyIncome.push({ month: ym, dividendos: totalDiv, jcp: 0, rendimentos: 0, total: totalDiv });
        ps.b3TotalIncome = Number(((Number(ps.b3TotalIncome) || 0) + totalDiv).toFixed(2));
      } else if (tradeType === 'BUY') {
        const effectiveCost = (qty * price) + fees;
        const effectiveUnit = effectiveCost / qty;
        if (idx >= 0) {
          const prev = ps.holdings[idx];
          const oldShares = Number(prev.shares) || 0;
          const oldAvg = Number(prev.average_buy_price) || 0;
          const newShares = oldShares + qty;
          const newAvg = ((oldShares * oldAvg) + effectiveCost) / newShares;
          ps.holdings[idx] = {
            ticker,
            shares: Number(newShares.toFixed(4)),
            average_buy_price: Number(newAvg.toFixed(4)),
          };
        } else {
          ps.holdings.push({
            ticker,
            shares: Number(qty.toFixed(4)),
            average_buy_price: Number(effectiveUnit.toFixed(4)),
          });
        }
      } else {
        // SELL
        if (idx >= 0) {
          const prev = ps.holdings[idx];
          const remaining = (Number(prev.shares) || 0) - qty;
          if (remaining <= 0.0001) {
            ps.holdings.splice(idx, 1);
          } else {
            ps.holdings[idx].shares = Number(remaining.toFixed(4));
          }
        }
      }

      // Update timeline checkpoint
      if (!Array.isArray(ps.b3Timeline)) ps.b3Timeline = [];
      const totalInvNow = ps.holdings.reduce((acc, h) => acc + ((Number(h.shares) || 0) * (Number(h.average_buy_price) || 0)), 0);
      const ymLabel = dateStr.slice(5, 7) + '/' + dateStr.slice(2, 4);
      ps.b3Timeline.push({ date: dateStr, label: ymLabel, invested: Number(totalInvNow.toFixed(2)) });

      if (typeof savePortfolioStorage === 'function') savePortfolioStorage();
      if (typeof renderPortfolioHoldingsEditor === 'function') renderPortfolioHoldingsEditor();
      if (typeof renderOverviewDashboard === 'function') renderOverviewDashboard();
      renderCustodyPenpotView();
      if (typeof renderPatrimonioDetailedChart === 'function') renderPatrimonioDetailedChart();

      if (inTicker) inTicker.value = '';
      if (inQty) inQty.value = '100';
      if (inPrice) inPrice.value = '';
      if (inFees) inFees.value = '0';
      closeTradeModal();

      if (typeof showToastNotification === 'function') {
        showToastNotification(`Lançamento em ${ticker} registrado na carteira!`, false);
      }
    });
  }

  // 2. Modal Importar B3 (#modal-b3-import)
  const modalB3 = document.getElementById('modal-b3-import');
  const btnOpenB3Modal = document.getElementById('btn-open-b3-modal');
  const btnB3Close = document.getElementById('btn-modal-b3-close') || document.getElementById('btn-b3-modal-close');
  const btnB3Cancel = document.getElementById('btn-modal-b3-cancel') || document.getElementById('btn-b3-modal-cancel');
  const btnB3Select = document.getElementById('modal-b3-dropzone') || document.getElementById('btn-b3-modal-select');
  const btnB3Submit = document.getElementById('btn-modal-b3-process') || document.getElementById('btn-b3-modal-submit');
  const fileListEl = document.getElementById('modal-b3-files-list') || document.getElementById('b3-modal-file-list');
  const b3MultiInput = document.getElementById('b3-multi-file-input');

  const renderB3ModalFiles = () => {
    if (!fileListEl) return;
    if (_b3ModalSelectedFiles.length === 0) {
      fileListEl.innerHTML = `
        <div class="text-xs text-subtle font-mono py-2 text-center">
          Nenhum arquivo selecionado ainda. Selecione arquivos .xlsx ou .csv exportados da B3.
        </div>
      `;
      return;
    }
    fileListEl.innerHTML = _b3ModalSelectedFiles.map(f => `
      <div class="flex items-center justify-between p-2.5 rounded-lg surface-subtle border border-default text-xs">
        <span class="font-mono font-semibold text-strong truncate">${f.name}</span>
        <span class="px-2 py-0.5 rounded bg-success-soft text-positive font-bold text-[11px] shrink-0">Pronto para validar</span>
      </div>
    `).join('');
  };

  if (btnOpenB3Modal && modalB3) {
    btnOpenB3Modal.addEventListener('click', () => {
      renderB3ModalFiles();
      modalB3.classList.remove('hidden');
    });
  }
  if (btnB3Close && modalB3) btnB3Close.addEventListener('click', () => modalB3.classList.add('hidden'));
  if (btnB3Cancel && modalB3) btnB3Cancel.addEventListener('click', () => modalB3.classList.add('hidden'));

  // Escape key closes open Penpot modals
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (modalTrade && !modalTrade.classList.contains('hidden')) closeTradeModal();
      if (modalB3 && !modalB3.classList.contains('hidden')) modalB3.classList.add('hidden');
    }
  });

  if (btnB3Select && b3MultiInput) {
    btnB3Select.addEventListener('click', () => {
      b3MultiInput.value = '';
      b3MultiInput.click();
    });
    b3MultiInput.addEventListener('change', (e) => {
      _b3ModalSelectedFiles = Array.from(e.target.files || []);
      renderB3ModalFiles();
    });
  }

  if (btnB3Submit) {
    btnB3Submit.addEventListener('click', async () => {
      if (_b3ModalSelectedFiles.length === 0) {
        const csvInput = document.getElementById('portfolio-csv-file-input');
        if (csvInput) csvInput.click();
        return;
      }
      if (modalB3) modalB3.classList.add('hidden');
      if (typeof uploadMultipleB3Spreadsheets === 'function') {
        await uploadMultipleB3Spreadsheets(_b3ModalSelectedFiles);
        _b3ModalSelectedFiles = [];
        renderB3ModalFiles();
      }
    });
  }

  // 3. Mobile Bottom Navigation Bar (#mobile-bottom-nav)
  document.querySelectorAll('#mobile-bottom-nav .mobile-nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetRoute = btn.getAttribute('data-route');
      if (targetRoute && typeof navigateToRoute === 'function') {
        navigateToRoute(targetRoute);
      }
    });
  });
}

function syncMobileBottomNav(canonicalRoute) {
  document.querySelectorAll('#mobile-bottom-nav .mobile-nav-btn').forEach(btn => {
    const r = btn.getAttribute('data-route');
    const isActive = (r === canonicalRoute) ||
      (r === 'carteira/visao-geral' && (canonicalRoute === 'carteira/proventos' || canonicalRoute === 'carteira/patrimonio')) ||
      (r === 'quant/radar' && (canonicalRoute === 'quant/simulador' || canonicalRoute === 'quant/playbook'));
    btn.classList.toggle('text-info', isActive);
    btn.classList.toggle('font-bold', isActive);
    btn.classList.toggle('text-muted', !isActive);
    btn.setAttribute('aria-current', isActive ? 'page' : 'false');
  });
}

if (typeof window !== 'undefined') {
  window.renderOverviewPenpotWidgets = renderOverviewPenpotWidgets;
  window.renderCustodyPenpotView = renderCustodyPenpotView;
  window.setupCustodyControls = setupCustodyControls;
  window.setupPenpotModals = setupPenpotModals;
  window.syncMobileBottomNav = syncMobileBottomNav;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    renderOverviewPenpotWidgets,
    renderCustodyPenpotView,
    setupCustodyControls,
    setupPenpotModals,
    syncMobileBottomNav,
  };
}
