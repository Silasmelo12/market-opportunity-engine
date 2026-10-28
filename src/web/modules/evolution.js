// Módulo de Evolução Patrimonial (Aba #tab-pane-patrimonio)
// Implementação fiel ao Penpot (04 — Evolução Patrimonial): filtro 12 meses / Tudo,
// gráfico Patrimônio x Aportes, card Resumo do período e tabela Histórico de aportes e eventos.

let _patrimonioPeriodMode = 'all';

function _formatBrlPat(val) {
  const n = Number(val) || 0;
  return 'R$ ' + n.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function setupPatrimonioControls() {
  const btn12m = document.getElementById('btn-patrimonio-12m');
  const btnAll = document.getElementById('btn-patrimonio-all');
  if (!btn12m || !btnAll) return;

  btn12m.addEventListener('click', () => {
    _patrimonioPeriodMode = '12m';
    btn12m.setAttribute('aria-pressed', 'true');
    btnAll.setAttribute('aria-pressed', 'false');
    btn12m.className = 'btn-primary text-xs px-3 py-1.5';
    btnAll.className = 'btn-secondary text-xs px-3 py-1.5';
    renderPatrimonioDetailedChart('12m');
  });

  btnAll.addEventListener('click', () => {
    _patrimonioPeriodMode = 'all';
    btnAll.setAttribute('aria-pressed', 'true');
    btn12m.setAttribute('aria-pressed', 'false');
    btnAll.className = 'btn-primary text-xs px-3 py-1.5';
    btn12m.className = 'btn-secondary text-xs px-3 py-1.5';
    renderPatrimonioDetailedChart('all');
  });
}

function renderPatrimonioDetailedChart(mode = null) {
  const activeMode = mode || _patrimonioPeriodMode || 'all';
  const container = document.getElementById('chart-patrimonio-detailed');
  const appState = (typeof window !== 'undefined' && window.appState) ? window.appState : null;
  const ps = (appState && appState.portfolioState) ? appState.portfolioState : {};

  const rawTimeline = Array.isArray(ps.b3Timeline) ? ps.b3Timeline : [];
  const holdings = Array.isArray(ps.holdings) ? ps.holdings : [];
  const monthlyIncome = Array.isArray(ps.b3MonthlyIncome) ? ps.b3MonthlyIncome : [];

  const slicedTimeline = activeMode === '12m' && rawTimeline.length > 12
    ? rawTimeline.slice(-12)
    : rawTimeline;

  // Compute current holdings market value & cost for summary
  const quotesMap = ps.quotesCache || {};
  let totalCost = 0;
  let totalMarketVal = 0;
  holdings.forEach(h => {
    const sh = Number(h.shares) || 0;
    const avgP = Number(h.average_buy_price) || 0;
    totalCost += sh * avgP;
    const q = quotesMap[(h.ticker || '').toUpperCase()] || quotesMap[`${(h.ticker || '').toUpperCase()}.SA`];
    const curP = (q && Number(q.price) > 0) ? Number(q.price) : avgP;
    totalMarketVal += sh * curP;
  });
  const cash = Number(ps.availableCash) || 0;
  const currentEquity = cash + totalMarketVal;

  const finalInvested = slicedTimeline.length > 0
    ? (Number(slicedTimeline[slicedTimeline.length - 1].invested) || totalCost)
    : totalCost;
  const finalPatrimonio = currentEquity > 0 ? currentEquity : finalInvested;
  const varPatrimonial = finalPatrimonio - finalInvested;
  const retPct = finalInvested > 0 ? ((varPatrimonial / finalInvested) * 100) : 0;

  // Populate Resumo do período card (Penpot Screen 04)
  const elFinal = document.getElementById('pat-summary-final');
  const elInv = document.getElementById('pat-summary-invested');
  const elVar = document.getElementById('pat-summary-var');
  const elRet = document.getElementById('pat-summary-return');
  const elDd = document.getElementById('pat-summary-dd');

  if (elFinal) elFinal.textContent = _formatBrlPat(finalPatrimonio);
  if (elInv) elInv.textContent = _formatBrlPat(finalInvested);
  if (elVar) {
    const sign = varPatrimonial >= 0 ? '+' : '';
    elVar.textContent = `${sign}${_formatBrlPat(varPatrimonial)}`;
    elVar.className = `font-mono font-bold ${varPatrimonial >= 0 ? 'text-positive' : 'text-negative'}`;
  }
  if (elRet) {
    const sign = retPct >= 0 ? '+' : '';
    elRet.textContent = finalInvested > 0 ? `${sign}${retPct.toFixed(2).replace('.', ',')}%` : 'N/A';
    elRet.className = `font-mono font-bold ${retPct >= 0 ? 'text-positive' : 'text-negative'}`;
  }
  if (elDd) {
    elDd.textContent = varPatrimonial < 0 && finalInvested > 0
      ? `${((varPatrimonial / finalInvested) * 100).toFixed(2).replace('.', ',')}%`
      : '0,00%';
  }

  // Populate Histórico de aportes e eventos table
  const tbody = document.getElementById('pat-history-tbody');
  if (tbody) {
    if (slicedTimeline.length === 0 && holdings.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="4" class="px-4 py-6 text-center text-subtle font-mono text-xs">
            Nenhum aporte ou movimentação registrado. Importe seus extratos da B3 ou adicione um lançamento.
          </td>
        </tr>
      `;
    } else if (slicedTimeline.length > 0) {
      const incomeByMonth = {};
      monthlyIncome.forEach(m => {
        if (m.month_year) incomeByMonth[String(m.month_year).slice(0, 7)] = Number(m.total) || 0;
      });
      const rows = [...slicedTimeline].reverse().slice(0, 12);
      tbody.innerHTML = rows.map((pt, idx) => {
        const label = pt.label || pt.date || '--';
        const inv = Number(pt.invested) || 0;
        const ym = String(pt.date || label).slice(0, 7);
        const prov = incomeByMonth[ym] || 0;
        const eq = idx === 0 && finalPatrimonio > 0 ? finalPatrimonio : inv;
        return `
          <tr class="hover-surface">
            <td class="px-3 py-2.5 font-mono text-muted">${label}</td>
            <td class="px-3 py-2.5 text-right font-mono text-strong">${_formatBrlPat(inv)}</td>
            <td class="px-3 py-2.5 text-right font-mono text-positive">${_formatBrlPat(prov)}</td>
            <td class="px-3 py-2.5 text-right font-mono font-bold text-strong">${_formatBrlPat(eq)}</td>
          </tr>
        `;
      }).join('');
    } else {
      tbody.innerHTML = `
        <tr class="hover-surface">
          <td class="px-3 py-2.5 font-mono text-muted">Posição Atual</td>
          <td class="px-3 py-2.5 text-right font-mono text-strong">${_formatBrlPat(totalCost)}</td>
          <td class="px-3 py-2.5 text-right font-mono text-positive">${_formatBrlPat(ps.b3TotalIncome || 0)}</td>
          <td class="px-3 py-2.5 text-right font-mono font-bold text-strong">${_formatBrlPat(finalPatrimonio)}</td>
        </tr>
      `;
    }
  }

  if (!container || !window.Plotly) return;

  if (slicedTimeline.length === 0) {
    Plotly.purge(container);
    container.innerHTML = `
      <div class="p-8 text-center text-subtle font-mono text-xs">
        Nenhum dado de evolução patrimonial importado. Importe seus extratos da B3 para visualizar a série temporal.
      </div>
    `;
    return;
  }

  const isDark = (document.documentElement.getAttribute('data-theme') || 'light') === 'dark';
  const bgColor = isDark ? '#151924' : '#FFFFFF';
  const textColor = isDark ? '#8B98A5' : '#0F172A';
  const gridColor = isDark ? 'rgba(38, 43, 56, 0.5)' : '#F1F5F9';

  const xDates = slicedTimeline.map(pt => pt.label || pt.date);
  const yInvested = slicedTimeline.map(pt => Number(pt.invested) || 0);

  const trace = {
    x: xDates,
    y: yInvested,
    name: 'Total Aplicado',
    type: 'bar',
    marker: { color: '#059669' },
    hovertemplate: '<b>%{x}</b><br>Aplicado: R$ %{y:,.2f}<extra></extra>'
  };

  const layout = {
    autosize: true,
    height: 320,
    paper_bgcolor: bgColor,
    plot_bgcolor: bgColor,
    font: { family: 'Plus Jakarta Sans, sans-serif', size: 11, color: textColor },
    margin: { t: 20, r: 20, b: 40, l: 65 },
    xaxis: { gridcolor: gridColor },
    yaxis: { gridcolor: gridColor, tickprefix: 'R$ ' }
  };

  container.innerHTML = '';
  Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
}

if (typeof window !== 'undefined') {
  window.renderPatrimonioDetailedChart = renderPatrimonioDetailedChart;
  window.setupPatrimonioControls = setupPatrimonioControls;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { renderPatrimonioDetailedChart, setupPatrimonioControls };
}
