// Módulo de Proventos & Renda (Aba #tab-pane-proventos)
// Implementação fiel ao Penpot (03 — Proventos) e integridade contábil sem dados fictícios.

function _getProventosState() {
  const appState = (typeof window !== 'undefined' && window.appState)
    ? window.appState
    : ((typeof state !== 'undefined') ? state : null);
  return (appState && appState.portfolioState) ? appState.portfolioState : {};
}

function _formatBrlProventos(val) {
  const n = Number(val) || 0;
  return 'R$ ' + n.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/**
 * Atualiza os 4 KPIs de Proventos, a composição por tipo e a tabela de últimos proventos (Penpot Screen 03).
 */
function renderProventosSummaryAndTable() {
  const ps = _getProventosState();
  const monthly = Array.isArray(ps.b3MonthlyIncome) ? ps.b3MonthlyIncome : [];

  let sumDiv = 0;
  let sumJcp = 0;
  let sumRend = 0;
  let sumTotal = 0;

  monthly.forEach(item => {
    const d = Number(item.dividendos) || 0;
    const j = Number(item.jcp) || 0;
    const r = Number(item.rendimentos) || 0;
    const t = Number(item.total) || (d + j + r);
    sumDiv += d;
    sumJcp += j;
    sumRend += r;
    sumTotal += t;
  });

  if (sumTotal === 0 && Number(ps.b3TotalIncome) > 0) {
    sumTotal = Number(ps.b3TotalIncome);
    sumDiv = sumTotal;
  }

  const elTotal = document.getElementById('prov-kpi-total');
  const elTotalSub = document.getElementById('prov-kpi-total-sub');
  const elDiv = document.getElementById('prov-kpi-dividendos');
  const elDivSub = document.getElementById('prov-kpi-dividendos-sub');
  const elJcp = document.getElementById('prov-kpi-jcp');
  const elJcpSub = document.getElementById('prov-kpi-jcp-sub');
  const elRend = document.getElementById('prov-kpi-rendimentos');
  const elRendSub = document.getElementById('prov-kpi-rendimentos-sub');

  if (elTotal) elTotal.textContent = _formatBrlProventos(sumTotal);
  if (elTotalSub) {
    elTotalSub.textContent = monthly.length > 0
      ? `${monthly.length} ${monthly.length === 1 ? 'competência registrada' : 'competências registradas'}`
      : 'Importe extratos B3';
  }

  const pctDiv = sumTotal > 0 ? ((sumDiv / sumTotal) * 100).toFixed(1) : '0.0';
  const pctJcp = sumTotal > 0 ? ((sumJcp / sumTotal) * 100).toFixed(1) : '0.0';
  const pctRend = sumTotal > 0 ? ((sumRend / sumTotal) * 100).toFixed(1) : '0.0';

  if (elDiv) elDiv.textContent = _formatBrlProventos(sumDiv);
  if (elDivSub) elDivSub.textContent = `${pctDiv.replace('.', ',')}% do total`;
  if (elJcp) elJcp.textContent = _formatBrlProventos(sumJcp);
  if (elJcpSub) elJcpSub.textContent = `${pctJcp.replace('.', ',')}% do total`;
  if (elRend) elRend.textContent = _formatBrlProventos(sumRend);
  if (elRendSub) elRendSub.textContent = `${pctRend.replace('.', ',')}% do total`;

  // Composição da renda bars/legend
  const compEl = document.getElementById('prov-composition-list');
  if (compEl) {
    const rows = [
      { label: 'Dividendos', val: sumDiv, pct: pctDiv, color: 'bg-emerald-500' },
      { label: 'Juros Sobre Capital Próprio (JCP)', val: sumJcp, pct: pctJcp, color: 'bg-sky-500' },
      { label: 'Rendimentos FII / Outros', val: sumRend, pct: pctRend, color: 'bg-amber-500' },
    ];
    compEl.innerHTML = rows.map(r => `
      <div class="space-y-1">
        <div class="flex items-center justify-between text-xs">
          <span class="font-semibold text-strong">${r.label}</span>
          <span class="font-mono text-muted">${_formatBrlProventos(r.val)} (${r.pct.replace('.', ',')}%)</span>
        </div>
        <div class="w-full h-2 surface-subtle rounded-full overflow-hidden">
          <div class="h-full ${r.color} rounded-full" style="width: ${Math.min(100, Number(r.pct) || 0)}%"></div>
        </div>
      </div>
    `).join('');
  }

  // Tabela Últimos proventos
  const tbody = document.getElementById('prov-history-tbody');
  if (tbody) {
    if (monthly.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="4" class="px-4 py-6 text-center text-subtle font-mono text-xs">
            Nenhum evento de provento importado. Importe a planilha de Movimentação da B3 para listar os pagamentos.
          </td>
        </tr>
      `;
    } else {
      const reversed = [...monthly].reverse().slice(0, 12);
      tbody.innerHTML = reversed.map(m => {
        const d = Number(m.dividendos) || 0;
        const j = Number(m.jcp) || 0;
        const r = Number(m.rendimentos) || 0;
        let tipo = 'Proventos Consolidados';
        if (d > 0 && j === 0 && r === 0) tipo = 'Dividendo';
        else if (j > 0 && d === 0 && r === 0) tipo = 'JCP';
        else if (r > 0 && d === 0 && j === 0) tipo = 'Rendimento FII';
        return `
          <tr class="hover-surface">
            <td class="px-3 py-2.5 font-mono text-muted">${m.month_year || '--'}</td>
            <td class="px-3 py-2.5 font-semibold text-strong">${m.ticker || 'Custódia B3'}</td>
            <td class="px-3 py-2.5 text-info">${tipo}</td>
            <td class="px-3 py-2.5 text-right font-mono font-bold text-positive">${_formatBrlProventos(m.total)}</td>
          </tr>
        `;
      }).join('');
    }
  }
}

/**
 * Renderiza o gráfico detalhado de proventos (mensal ou anual) com Plotly.
 * @param {'mensal' | 'anual'} mode
 */
function renderProventosTabChart(mode = 'mensal') {
  renderProventosSummaryAndTable();

  const container = document.getElementById('chart-proventos-detailed');
  if (!container || !window.Plotly) return;

  const btnMensal = document.getElementById('btn-proventos-view-mensal');
  const btnAnual = document.getElementById('btn-proventos-view-anual');
  if (btnMensal) btnMensal.setAttribute('aria-pressed', mode === 'anual' ? 'false' : 'true');
  if (btnAnual) btnAnual.setAttribute('aria-pressed', mode === 'anual' ? 'true' : 'false');

  const ps = _getProventosState();
  const monthly = ps.b3MonthlyIncome || [];
  let labels = [];
  let values = [];

  if (!Array.isArray(monthly) || monthly.length === 0) {
    Plotly.purge(container);
    container.innerHTML = `
      <div class="flex items-center justify-center h-full p-6 text-center text-subtle font-mono text-xs">
        Nenhum provento registrado no histórico importado. Importe seus extratos da B3 para visualizar a série mensal e anual.
      </div>
    `;
    return;
  }

  if (mode === 'anual') {
    const yearMap = {};
    monthly.forEach(m => {
      let yr = '2026';
      if (m.month_year) {
        const match = String(m.month_year).match(/^(\d{4})/);
        if (match) yr = match[1];
        else if (m.month_year.includes('/')) yr = '20' + m.month_year.split('/')[1];
      }
      yearMap[yr] = (yearMap[yr] || 0) + (Number(m.total) || 0);
    });
    labels = Object.keys(yearMap);
    values = Object.values(yearMap);
  } else {
    labels = monthly.map(m => {
      if (!m.month_year) return '';
      const match = String(m.month_year).match(/^(\d{4})[-/](\d{2})/);
      if (match) return `${match[2]}/${match[1].slice(2)}`;
      return m.month_year;
    });
    values = monthly.map(m => Number(m.total) || 0);
  }

  const isDark = (document.documentElement.getAttribute('data-theme') || 'light') === 'dark';
  const tickColor = isDark ? '#94a3b8' : '#64748b';
  const gridColor = isDark ? 'rgba(51, 65, 85, 0.35)' : '#f1f5f9';

  const trace = {
    x: labels,
    y: values,
    name: 'Proventos Recebidos',
    type: 'bar',
    marker: { color: '#0284c7', line: { color: '#0369a1', width: 1 } },
    hovertemplate: '<b>%{x}</b><br>Proventos: R$ %{y:,.2f}<extra></extra>'
  };

  const layout = {
    autosize: true,
    height: container.clientHeight || 288,
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    margin: { t: 15, r: 15, b: 35, l: 45 },
    xaxis: { type: 'category', tickfont: { family: 'Plus Jakarta Sans, sans-serif', size: 11, color: tickColor }, gridcolor: 'transparent' },
    yaxis: { tickfont: { family: 'Plus Jakarta Sans, sans-serif', size: 11, color: tickColor }, gridcolor: gridColor, zerolinecolor: gridColor },
    showlegend: false
  };

  container.innerHTML = '';
  Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
  requestAnimationFrame(() => { if (window.Plotly && container.data) Plotly.Plots.resize(container); });
}

/**
 * Configura os botões de alternância Mensal/Anual do gráfico de proventos.
 */
function setupProventosControls() {
  const btnMensal = document.getElementById('btn-proventos-view-mensal');
  const btnAnual = document.getElementById('btn-proventos-view-anual');
  if (!btnMensal || !btnAnual) return;

  btnMensal.addEventListener('click', () => {
    btnMensal.setAttribute('aria-pressed', 'true');
    btnAnual.setAttribute('aria-pressed', 'false');
    btnMensal.className = 'btn-primary';
    btnAnual.className = 'btn-secondary';
    renderProventosTabChart('mensal');
  });

  btnAnual.addEventListener('click', () => {
    btnAnual.setAttribute('aria-pressed', 'true');
    btnMensal.setAttribute('aria-pressed', 'false');
    btnAnual.className = 'btn-primary';
    btnMensal.className = 'btn-secondary';
    renderProventosTabChart('anual');
  });
}

if (typeof window !== 'undefined') {
  window.renderProventosTabChart = renderProventosTabChart;
  window.renderProventosSummaryAndTable = renderProventosSummaryAndTable;
  window.setupProventosControls = setupProventosControls;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    renderProventosTabChart,
    renderProventosSummaryAndTable,
    setupProventosControls,
  };
}
