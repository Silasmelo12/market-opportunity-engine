// Funções puras de formatação e utilitários de ativos
// Extraído de src/web/app.js (Etapa 2 da Modularização - Spec 022)

function stripCorporateSuffix(name) {
  if (!name) return '';
  const parts = String(name).split(/\s+/);
  const clean = parts.filter(p => {
    const up = p.toUpperCase().replace(/[.,-]+$/, '');
    return up !== 'S.A' && up !== 'S/A' && up !== 'SA';
  });
  return clean.join(' ').replace(/^[ ,-]+|[ ,-]+$/, '');
}

function resolveTicker(input) {
  if (!input) return input;
  const clean = String(input).trim().toUpperCase();
  const aliases = (typeof TICKER_ALIASES !== 'undefined')
    ? TICKER_ALIASES
    : (typeof window !== 'undefined' && window.TICKER_ALIASES ? window.TICKER_ALIASES : {});
  return aliases[clean] || clean;
}

function getAssetName(ticker) {
  if (!ticker) return '';
  const names = (typeof ASSET_NAMES !== 'undefined')
    ? ASSET_NAMES
    : (typeof window !== 'undefined' && window.ASSET_NAMES ? window.ASSET_NAMES : {});
  return names[ticker.toUpperCase()] || ticker;
}

function formatNumber(value, decimals = 2) {
  const num = Number(value);
  if (!Number.isFinite(num)) return '-';
  return num.toLocaleString('pt-BR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
}

function formatPercent(value, decimals = 1, withSign = false) {
  const num = Number(value);
  if (!Number.isFinite(num)) return '-';
  const sign = withSign && num > 0 ? '+' : '';
  return `${sign}${formatNumber(num, decimals)}%`;
}

function formatCurrency(value, decimals = 2) {
  const num = Number(value);
  if (!Number.isFinite(num)) return '-';
  return `R$ ${formatNumber(num, decimals)}`;
}

function formatPrice(price, ticker = null, category = null) {
  if (price === null || price === undefined || isNaN(price)) return '-';
  const num = Number(price);
  const fallbackTicker = (typeof state !== 'undefined' && state && state.currentTicker)
    ? state.currentTicker
    : (typeof window !== 'undefined' && window.appState && window.appState.currentTicker ? window.appState.currentTicker : '');
  const t = (ticker || fallbackTicker || '').toUpperCase();
  const c = (category || '').toLowerCase();

  if (t === '^BVSP' || t === 'WIN') {
    return `${Math.round(num).toLocaleString('pt-BR')} pts`;
  }
  if (t === 'USDBRL=X' || t === 'WDO') {
    return `R$ ${num.toLocaleString('pt-BR', { minimumFractionDigits: 4, maximumFractionDigits: 4 })}`;
  }

  const isForex = t.endsWith('=X') || c.includes('forex') || c.includes('fx');
  const isUS = (!t.endsWith('.SA') && !t.endsWith('=F') && !isForex && !c.includes('brasil') && !c.includes('fii'));
  const isCommodity = t.endsWith('=F') || c.includes('commodit');
  const isCrypto = t.includes('BTC') || t.includes('ETH') || t.includes('SOL') || c.includes('cripto') || c.includes('crypto');

  if (isForex) {
    return num.toFixed(4);
  } else if (isUS || isCommodity || isCrypto) {
    return `$ ${num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  } else {
    return `R$ ${num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
}

function sanitizeTickerParam(raw) {
  if (!raw || typeof raw !== 'string') return null;
  const clean = raw.trim().toUpperCase();
  if (!clean) return null;
  if (!/^[A-Z0-9\.\=\-\^]+$/.test(clean)) return null;
  return resolveTicker(clean);
}

// Exposição compatível para navegador (window) e Node.js (module.exports)
if (typeof window !== 'undefined') {
  window.stripCorporateSuffix = stripCorporateSuffix;
  window.resolveTicker = resolveTicker;
  window.getAssetName = getAssetName;
  window.formatPrice = formatPrice;
  window.formatNumber = formatNumber;
  window.formatPercent = formatPercent;
  window.formatCurrency = formatCurrency;
  window.sanitizeTickerParam = sanitizeTickerParam;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    stripCorporateSuffix,
    resolveTicker,
    getAssetName,
    formatPrice,
    formatNumber,
    formatPercent,
    formatCurrency,
    sanitizeTickerParam
  };
}
