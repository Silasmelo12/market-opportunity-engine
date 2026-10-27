// Módulo de Proventos (Aba #tab-pane-proventos)
// Extraído de src/web/app.js (Etapa 4 da Modularização - Spec 022)

/**
 * Renderiza o gráfico detalhado de proventos (mensal ou anual) com Plotly.
 * @param {'mensal' | 'anual'} mode
 */
function renderProventosTabChart(mode = 'mensal') {
  const container = document.getElementById('chart-proventos-detailed');
  if (!container || !window.Plotly) return;

  const btnMensal = document.getElementById('btn-proventos-view-mensal');
  const btnAnual = document.getElementById('btn-proventos-view-anual');
  if (btnMensal) btnMensal.setAttribute('aria-pressed', mode === 'anual' ? 'false' : 'true');
  if (btnAnual) btnAnual.setAttribute('aria-pressed', mode === 'anual' ? 'true' : 'false');

  const appState = (typeof window !== 'undefined' && window.appState)
    ? window.appState
    : ((typeof state !== 'undefined') ? state : null);

  const monthly = (appState && appState.portfolioState && appState.portfolioState.b3MonthlyIncome) || [];
  let labels = [];
  let values = [];

  if (Array.isArray(monthly) && monthly.length > 0) {
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
  } else {
    labels = ['11/25', '12/25', '01/26', '02/26', '03/26', '04/26', '05/26', '06/26', '07/26', '08/26', '09/26', '10/26'];
    values = [35.20, 142.50, 38.00, 45.10, 180.20, 46.00, 52.30, 220.40, 58.10, 61.40, 245.90, 68.20];
  }

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
    xaxis: { type: 'category', tickfont: { family: 'Plus Jakarta Sans, sans-serif', size: 11, color: '#64748b' }, gridcolor: 'transparent' },
    yaxis: { tickfont: { family: 'Plus Jakarta Sans, sans-serif', size: 11, color: '#64748b' }, gridcolor: '#f1f5f9', zerolinecolor: '#e2e8f0' },
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
    btnAnual.className = 'px-3 py-1 text-xs font-semibold rounded-lg bg-slate-900 text-white shadow-sm';
    btnMensal.className = 'px-3 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-600 hover:bg-slate-200';
    renderProventosTabChart('anual');
  });
}

// Exposição compatível para navegador (window) e Node.js (module.exports)
if (typeof window !== 'undefined') {
  window.renderProventosTabChart = renderProventosTabChart;
  window.setupProventosControls = setupProventosControls;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    renderProventosTabChart,
    setupProventosControls
  };
}
