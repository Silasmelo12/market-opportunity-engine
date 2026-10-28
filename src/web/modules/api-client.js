// Módulo Cliente HTTP Centralizado (API Client)
// Arquitetura Modular (Fase 2 & Fase 3 - Market Opportunity Engine)

const ApiClient = {
  async fetchPortfolioQuotes(tickers) {
    if (!Array.isArray(tickers) || tickers.length === 0) return {};
    try {
      const res = await fetch('/api/portfolio/quotes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tickers }),
      });
      if (res.ok) {
        const data = await res.json();
        return data.quotes || {};
      }
    } catch (err) {
      console.warn('Erro ao buscar cotações da carteira:', err);
    }
    return {};
  },

  async fetchRadarPage(params) {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`/api/radar?${query}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return res.json();
  },

  async fetchAnalysis(params) {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`/api/analyze?${query}`);
    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      throw new Error(errJson.detail || `HTTP ${res.status}`);
    }
    return res.json();
  },

  async postSimulate(payload) {
    const res = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },

  async postOptimize(payload) {
    const res = await fetch('/api/simulate/optimize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },

  async postPortfolioAdvise(payload) {
    const res = await fetch('/api/portfolio/advise', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },

  async postPortfolioSimulate(payload) {
    const res = await fetch('/api/portfolio/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },

  async postB3Parse(files) {
    const formData = new FormData();
    Array.from(files || []).forEach(f => formData.append('files', f));
    const res = await fetch('/api/b3/parse', {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || 'Erro ao processar planilhas da B3.');
    }
    return res.json();
  },

  async fetchStrategiesCatalog() {
    const res = await fetch('/api/strategies');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
};

if (typeof window !== 'undefined') {
  window.ApiClient = ApiClient;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ApiClient };
}
