
function stripCorporateSuffix(name) {
  if (!name) return '';
  const parts = String(name).split(/\s+/);
  const clean = parts.filter(p => {
    const up = p.toUpperCase().replace(/[.,-]+$/, '');
    return up !== 'S.A' && up !== 'S/A' && up !== 'SA';
  });
  return clean.join(' ').replace(/^[ ,-]+|[ ,-]+$/, '');
}
/**
 * Market Opportunity & Top/Bottom Statistical Engine
 * 60fps TradingView Lightweight Charts & Zero-Latency Client-Side Bidirectional Filtering.
 */

// Global Window State
window.appState = {
  currentTicker: 'PETR4.SA',
  currentTimeframe: '1d',
  currentPeriod: '2y',
  radarTimeframe: '1d',
  radarActiveCategory: 'featured',
  radarCategoryCache: {},
  radarPage: 1,
  radarPageSize: 20,
  radarTotalPages: 1,
  radarTotalAssets: 0,
  radarStrategies: new Set(),
  radarSortField: null,
  radarSortOrder: 'desc',
  lookbackN: 10,
  retestM: 5,
  horizonX: 60,
  activeTab: 'tab-radar',
  activeDirection: 'BUY', // 'BUY' (default as per spec) | 'SELL' | 'BOTH'
  analysisData: null,
  activeStrategies: new Set([]), // Start completely unchecked by default
  chart: null,
  candleSeries: null,
  refLineSeriesList: []
};

const state = window.appState;

// Ticker Aliases for Brazilian Mini Futures & Commodities
const TICKER_ALIASES = {
  'WIN': '^BVSP',
  'WDO': 'USDBRL=X',
  'XAUUSD': 'GC=F',
  'GOLD': 'GC=F',
};

function resolveTicker(input) {
  if (!input) return input;
  const clean = String(input).trim().toUpperCase();
  return TICKER_ALIASES[clean] || clean;
}

// DOM Elements
const elements = {
  loadingOverlay: document.getElementById('loading-spinner'),
  loadingText: document.getElementById('loading-text'),
  radarTableBody: document.getElementById('radar-table-body'),
  signalsTableBody: document.getElementById('signals-table-body'),
  headerStatusBadge: document.getElementById('header-status-badge'),
  inputTicker: document.getElementById('input-ticker'),
  selectPeriod: document.getElementById('select-period'),
  inputLookbackN: document.getElementById('input-lookback-n'),
  inputRetestM: document.getElementById('input-retest-m'),
  inputHorizonX: document.getElementById('input-horizon-x'),
  btnLoadAnalysis: document.getElementById('btn-load-analysis'),
  btnRefreshData: document.getElementById('btn-refresh-data'),
  btnRadarRescan: document.getElementById('btn-radar-rescan'),
  activeMarkerCount: document.getElementById('active-marker-count'),
  btnRunSimulation: document.getElementById('btn-run-simulation'),
  simTicker: document.getElementById('sim-ticker'),
  simMode: document.getElementById('sim-mode'),
  simBuyStrategy: document.getElementById('sim-buy-strategy'),
  simSellStrategy: document.getElementById('sim-sell-strategy'),
  btnOptimizeCombinations: document.getElementById('btn-optimize-combinations'),
  simOptimizerContainer: document.getElementById('sim-optimizer-container'),
  btnApplyChampion: document.getElementById('btn-apply-champion'),
  simTopCombosTableBody: document.getElementById('sim-top-combos-table-body'),
  simTradesTableBody: document.getElementById('sim-trades-table-body'),
  strategySimTableBody: document.getElementById('strategy-simulation-table-body'),
};

// Institutional Portuguese Asset Names Mapping
const ASSET_NAMES = {
  // Futuros B3 & Commodities Globais
  '^BVSP': 'Mini Índice / Ibovespa (WIN)',
  'WIN': 'Mini Índice / Ibovespa (WIN)',
  'USDBRL=X': 'Mini Dólar (WDO / USDBRL)',
  'WDO': 'Mini Dólar (WDO / USDBRL)',
  'GC=F': 'Gold (Ouro / XAUUSD)',
  'XAUUSD': 'Gold (Ouro / XAUUSD)',
  'GOLD': 'Gold (Ouro / XAUUSD)',
  'SI=F': 'Silver (Prata)',
  'CL=F': 'Crude Oil WTI (Petróleo)',
  'BZ=F': 'Brent Oil (Petróleo Brent)',
  'HG=F': 'Copper (Cobre)',
  'NG=F': 'Natural Gas (Gás Natural)',
  'ZC=F': 'Corn (Milho)',
  'ZS=F': 'Soybeans (Soja)',
  'ZW=F': 'Wheat (Trigo)',
  'KC=F': 'Coffee (Café Arábica)',
  'CT=F': 'Cotton (Algodão)',
  'SB=F': 'Sugar (Açúcar)',
  'LE=F': 'Live Cattle (Boi Gordo)',
  'HE=F': 'Lean Hogs (Suínos)',
  // Forex
  'EURUSD=X': 'EUR/USD',
  'GBPUSD=X': 'GBP/USD',
  'USDJPY=X': 'USD/JPY',
  'USDCHF=X': 'USD/CHF',
  'AUDUSD=X': 'AUD/USD',
  'USDCAD=X': 'USD/CAD',
  'NZDUSD=X': 'NZD/USD',
  'EURJPY=X': 'EUR/JPY',
  'GBPJPY=X': 'GBP/JPY',
  'EURCHF=X': 'EUR/CHF',
  // Criptomoedas
  'BTC-USD': 'Bitcoin',
  'ETH-USD': 'Ethereum',
  'SOL-USD': 'Solana',
  // Ações Brasil
  'PETR4.SA': 'Petrobras PN',
  'VALE3.SA': 'Vale ON',
  'ITUB4.SA': 'Itaú Unibanco PN',
  'BBDC4.SA': 'Bradesco PN',
  'BBAS3.SA': 'Banco do Brasil ON',
  'ABEV3.SA': 'Ambev ON',
  'WEGE3.SA': 'WEG ON',
  'RENT3.SA': 'Localiza ON',
  'EGIE3.SA': 'Engie Brasil ON',
  'PRIO3.SA': 'PRIO ON',
  'BRSR6.SA': 'Banrisul PNB',
  'KLBN4.SA': 'Klabin PN',
  'CXSE3.SA': 'Caixa Seguridade ON',
  'BMGB4.SA': 'Banco BMG PN',
  'BRKM5.SA': 'Braskem PNA',
  'TASA4.SA': 'Taurus Armas PN',
  'PMAM3.SA': 'Paranapanema ON',
  'CMIG4.SA': 'Cemig PN',
  'CPFE3.SA': 'CPFL Energia ON',
  'POMO4.SA': 'Marcopolo PN',
  'TAEE11.SA': 'Taesa Unit',
  'BBSE3.SA': 'BB Seguridade ON',
  'SUZB3.SA': 'Suzano ON',
  'GGBR4.SA': 'Gerdau PN',
  'CSNA3.SA': 'Siderúrgica Nacional ON',
  // FIIs Brasil
  'HGLG11.SA': 'CSHG Logística',
  'KNRI11.SA': 'Kinea Renda Imob.',
  'MXRF11.SA': 'Maxi Renda',
  'VISC11.SA': 'Vinci Shopping',
  'BTLG11.SA': 'BTG Logística',
  'HGRE11.SA': 'CSHG Real Estate',
  'KNIP11.SA': 'Kinea Índices',
  'HSML11.SA': 'HSI Malls',
  'GGRC11.SA': 'GGR Covepi',
  'RBRR11.SA': 'RBR Rendimento',
  'RBVA11.SA': 'Rio Bravo Renda',
  'SNCI11.SA': 'Suno Recebíveis',
  'TRXF11.SA': 'TRX Real Estate',
  'XPLG11.SA': 'XP Log',
  'CPTS11.SA': 'Capitânia Securities',
  'VGIR11.SA': 'Valora RE',
  'VRTA11.SA': 'Fator Verita',
  'VINO11.SA': 'Vinci Offices',
  'RECR11.SA': 'REC Renda Imob.',
  'HFOF11.SA': 'Hedge FOF',
  'BTAL11.SA': 'BTG Agro Logística',
  // BDRs Brasil
  'NVDC34.SA': 'Nvidia BDR',
  'AAPL34.SA': 'Apple BDR',
  'MSFT34.SA': 'Microsoft BDR',
  'GOGL34.SA': 'Alphabet (Google) BDR',
  'AMZO34.SA': 'Amazon BDR',
  'M1TA34.SA': 'Meta Platforms BDR',
  'TSLA34.SA': 'Tesla BDR',
  'AVGO34.SA': 'Broadcom BDR',
  'TSMC34.SA': 'TSMC BDR',
  'A1MD34.SA': 'AMD BDR',
  'TMCO34.SA': 'Toyota BDR',
  'BERK34.SA': 'Berkshire Hathaway BDR',
  'JPMC34.SA': 'JPMorgan Chase BDR',
  'VISA34.SA': 'Visa BDR',
  'MSCD34.SA': 'Mastercard BDR',
  'BOAC34.SA': 'Bank of America BDR',
  'GSGI34.SA': 'Goldman Sachs BDR',
  'WALM34.SA': 'Walmart BDR',
  'COCA34.SA': 'Coca-Cola BDR',
  'PEPB34.SA': 'PepsiCo BDR',
  'MCDC34.SA': 'McDonald\'s BDR',
  'DISB34.SA': 'Disney BDR',
  'NFLX34.SA': 'Netflix BDR',
  'NIKE34.SA': 'Nike BDR',
  'COWC34.SA': 'Costco BDR',
  'LILY34.SA': 'Eli Lilly BDR',
  'N1VO34.SA': 'Novo Nordisk BDR',
  'JNJB34.SA': 'Johnson & Johnson BDR',
  'UNHH34.SA': 'UnitedHealth BDR',
  'PFIZ34.SA': 'Pfizer BDR',
  'EXXO34.SA': 'Exxon Mobil BDR',
  'CHVX34.SA': 'Chevron BDR',
  'CATP34.SA': 'Caterpillar BDR',
  'BOEI34.SA': 'Boeing BDR',
  'IVVB11.SA': 'iShares S&P 500 Fundo de Índice',
  'BIVB39.SA': 'iShares Core S&P 500 BDR',
  'NASD11.SA': 'Trend ETF Nasdaq 100',
  'BNDA39.SA': 'Invesco QQQ Trust BDR',
  'ACWI11.SA': 'Trend ETF MSCI ACWI',
  'BACW39.SA': 'iShares MSCI ACWI BDR',
  'SPCX34.SA': 'SpaceX BDR (Space Exploration)',
  // Ações EUA
  'AAPL': 'Apple',
  'MSFT': 'Microsoft',
  'GOOGL': 'Google (Alphabet)',
  'AMZN': 'Amazon',
  'NVDA': 'Nvidia',
  'META': 'Meta Platforms',
  'TSLA': 'Tesla',
  'BRK-B': 'Berkshire Hathaway',
  'JPM': 'JPMorgan Chase',
  'V': 'Visa',
  'JNJ': 'Johnson & Johnson',
  'WMT': 'Walmart',
  'PG': 'Procter & Gamble',
  'MA': 'Mastercard',
  'UNH': 'UnitedHealth',
  'HD': 'Home Depot',
  'DIS': 'Disney',
  'ADBE': 'Adobe',
  'NFLX': 'Netflix',
  'CRM': 'Salesforce',
  'KO': 'Coca-Cola',
  'AMD': 'AMD',
  'INTC': 'Intel',
  'CSCO': 'Cisco',
  'ABBV': 'AbbVie',
  'CVX': 'Chevron',
  'XOM': 'Exxon Mobil',
  'PFE': 'Pfizer',
  'IBM': 'IBM',
  'MMM': '3M',
  'VZ': 'Verizon',
  'T': 'AT&T',
  'BA': 'Boeing',
  'CAT': 'Caterpillar',
  'GE': 'General Electric',
  'GM': 'General Motors',
  'F': 'Ford',
  'UBER': 'Uber',
  'LYFT': 'Lyft',
  'TM': 'Toyota',
  'SNAP': 'Snap',
  'PINS': 'Pinterest',
  'PYPL': 'PayPal',
  'SHOP': 'Shopify',
  'ZM': 'Zoom',
  'DOCU': 'DocuSign',
  'CRWD': 'CrowdStrike',
  'NET': 'Cloudflare',
  'O': 'Realty Income',
  'SPG': 'Simon Property',
  'PLD': 'Prologis',
  'AMT': 'American Tower',
  'CCI': 'Crown Castle',
  'EQIX': 'Equinix',
  'PSA': 'Public Storage',
  'DLR': 'Digital Realty',
  'WELL': 'Welltower',
  'AVB': 'AvalonBay',
  'EQR': 'Equity Residential',
  'BXP': 'Boston Properties',
  'VTR': 'Ventas',
  'ARE': 'Alexandria RE',
  'MAA': 'Mid-America Apt.',
  'UDR': 'UDR Inc.',
  'KIM': 'Kimco Realty',
  'REG': 'Regency Centers',
  'HST': 'Host Hotels',
  'FRT': 'Federal Realty',
  'NNN': 'NNN REIT',
  'WPC': 'W. P. Carey',
  'GLPI': 'Gaming and Leisure',
};

function getAssetName(ticker) {
  if (!ticker) return '';
  return ASSET_NAMES[ticker.toUpperCase()] || ticker;
}

function formatPrice(price, ticker = null, category = null) {
  if (price === null || price === undefined || isNaN(price)) return '-';
  const num = Number(price);
  const t = (ticker || state.currentTicker || '').toUpperCase();
  const c = (category || '').toLowerCase();

  if (t === '^BVSP' || t === 'WIN') {
    return `${Math.round(num).toLocaleString('pt-BR')} pts`;
  }
  if (t === 'USDBRL=X' || t === 'WDO') {
    return `R$ ${num.toFixed(4)}`;
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

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  setupNavigationTabs();
  setupDirectionSelector();
  updateSidebarDirectionFilter();
  setupAccordions();
  setupMobileStrategiesToggle();
  setupTimeframeButtons();
  setupRadarTimeframeButtons();
  setupRadarCategoryPills();
  setupRadarStrategyFilter();
  setupRadarTableSorting();
  setupGranularStrategyCheckboxes();
  initTradingViewChart();
  setupSimulationTab();
  setupPortfolioTab();
  setupOverviewSubNav();
  setupOverviewMetasModal();

  // Holdings are loaded purely from storage or user uploads


  window.addEventListener('hashchange', () => {
    const targetTab = getTabFromHash();
    if (targetTab && targetTab !== state.activeTab) {
      switchTab(targetTab, false);
    }
  });

  // Initial tab restoration from URL hash or localStorage
  const initialTab = getTabFromHash();
  switchTab(initialTab, true);

  if (initialTab !== 'tab-radar') {
    // Also preload radar in background for 0ms tab switches
    loadRadarData();
  }


  // Listeners
  elements.btnLoadAnalysis.addEventListener('click', () => {
    state.currentTicker = resolveTicker(elements.inputTicker.value.trim().toUpperCase());
    elements.inputTicker.value = state.currentTicker;
    if (elements.simTicker) elements.simTicker.value = state.currentTicker;
    state.currentPeriod = elements.selectPeriod.value;
    state.lookbackN = parseInt(elements.inputLookbackN.value) || 10;
    state.retestM = parseInt(elements.inputRetestM.value) || 5;
    state.horizonX = parseInt(elements.inputHorizonX.value) || 60;
    loadAnalysisData(false);
  });

  // Auto trigger analysis on picking from datalist
  elements.inputTicker.addEventListener('change', () => {
    const val = resolveTicker(elements.inputTicker.value.trim().toUpperCase());
    elements.inputTicker.value = val;
    if (val && val !== state.currentTicker) {
      state.currentTicker = val;
      if (elements.simTicker) elements.simTicker.value = val;
      loadAnalysisData(false);
    }
  });

  // Auto trigger analysis immediately on changing period
  elements.selectPeriod.addEventListener('change', () => {
    state.currentPeriod = elements.selectPeriod.value;
    loadAnalysisData(false);
  });

  elements.btnRefreshData.addEventListener('click', () => {
    if (state.activeTab === 'tab-radar') {
      loadRadarData(true, state.radarActiveCategory);
    } else {
      loadAnalysisData(true);
    }
  });

  const btnOverviewRefresh = document.getElementById('btn-overview-refresh');
  if (btnOverviewRefresh) {
    btnOverviewRefresh.addEventListener('click', async () => {
      showLoading('Atualizando cotações e métricas da carteira...');
      try {
        state.portfolioState.quotesCache = null; // force fresh quotes
        await renderOverviewDashboard();
        if (typeof runPortfolioAdviseAndSimulate === 'function') {
          await runPortfolioAdviseAndSimulate();
          await renderOverviewDashboard();
        }
        showToastNotification('Carteira e cotações atualizadas com sucesso!', false);
      } catch (err) {
        console.warn('Erro ao atualizar carteira:', err);
      } finally {
        hideLoading();
      }
    });
  }

  const btnOverviewOpenRadar = document.getElementById('btn-overview-open-radar');
  if (btnOverviewOpenRadar) {
    btnOverviewOpenRadar.addEventListener('click', () => {
      switchTab('tab-radar');
    });
  }

  const btnOverviewApply = document.getElementById('btn-overview-apply-orders');
  if (btnOverviewApply) {
    btnOverviewApply.addEventListener('click', () => {
      openPreFlightOrderModal();
    });
  }

  const btnOverviewConfig = document.getElementById('btn-overview-config-ideal');
  if (btnOverviewConfig) {
    btnOverviewConfig.addEventListener('click', () => {
      switchTab('tab-portfolio');
    });
  }

  const btnOverviewOpenMetas = document.getElementById('btn-overview-open-metas');
  if (btnOverviewOpenMetas) {
    btnOverviewOpenMetas.addEventListener('click', () => {
      const modal = document.getElementById('modal-overview-metas');
      const inPat = document.getElementById('input-meta-patrimonio');
      const inRenda = document.getElementById('input-meta-renda');
      if (modal) {
        const m = getUserMetas();
        if (inPat) inPat.value = m.metaTotal;
        if (inRenda) inRenda.value = m.metaFII;
        modal.classList.remove('hidden');
      }
    });
  }

  const btnOverviewImport = document.getElementById('btn-overview-import-csv');
  if (btnOverviewImport) {
    btnOverviewImport.addEventListener('click', () => {
      const fileInput = document.getElementById('portfolio-csv-file-input');
      if (fileInput) fileInput.click();
    });
  }

  const btnOverviewGotoRadar = document.getElementById('btn-overview-goto-radar');
  if (btnOverviewGotoRadar) {
    btnOverviewGotoRadar.addEventListener('click', () => {
      switchTab('tab-radar');
    });
  }

  elements.btnRadarRescan.addEventListener('click', () => {
    loadRadarData(true, state.radarActiveCategory);
  });

  const btnRadarPrev = document.getElementById('btn-radar-prev');
  const btnRadarNext = document.getElementById('btn-radar-next');
  if (btnRadarPrev) {
    btnRadarPrev.addEventListener('click', () => {
      if (state.radarPage > 1) {
        state.radarPage -= 1;
        loadRadarData(false, state.radarActiveCategory);
      }
    });
  }
  if (btnRadarNext) {
    btnRadarNext.addEventListener('click', () => {
      if (state.radarPage < state.radarTotalPages) {
        state.radarPage += 1;
        loadRadarData(false, state.radarActiveCategory);
      }
    });
  }
});

// UI: Direction Selector (Compra, Venda, Ambos)


const TAB_HASH_MAP = {
  '#overview': 'tab-overview',
  '#dashboard': 'tab-overview',
  '#/': 'tab-overview',
  '#radar': 'tab-radar',
  '#terminal': 'tab-terminal',
  '#grafico': 'tab-terminal',
  '#simulator': 'tab-simulator',
  '#simulador': 'tab-simulator',
  '#playbook': 'tab-playbook',
  '#portfolio': 'tab-portfolio',
  '#carteira': 'tab-portfolio',
};

const TAB_TO_HASH_MAP = {
  'tab-overview': '#overview',
  'tab-radar': '#radar',
  'tab-terminal': '#terminal',
  'tab-simulator': '#simulator',
  'tab-playbook': '#playbook',
  'tab-portfolio': '#portfolio',
};

function getTabFromHash() {
  const hash = (window.location.hash || '').toLowerCase();
  if (TAB_HASH_MAP[hash]) return TAB_HASH_MAP[hash];
  const saved = localStorage.getItem('market_engine_active_tab');
  if (saved && TAB_TO_HASH_MAP[saved]) return saved;
  return 'tab-overview';
}

function getHashFromTab(tabId) {
  return TAB_TO_HASH_MAP[tabId] || '#overview';
}


function sortRadarItems(items) {
  if (!state.radarSortField || !items || items.length === 0) return items;
  const field = state.radarSortField;
  const isAsc = state.radarSortOrder === 'asc';

  return [...items].sort((a, b) => {
    let valA = a[field] != null ? a[field] : (isAsc ? Infinity : -Infinity);
    let valB = b[field] != null ? b[field] : (isAsc ? Infinity : -Infinity);

    if (valA < valB) return isAsc ? -1 : 1;
    if (valA > valB) return isAsc ? 1 : -1;
    return 0;
  });
}

function updateSidebarDirectionFilter() {
  const dir = state.activeDirection || 'BUY';
  document.querySelectorAll('.strategy-group-wrapper').forEach(wrapper => {
    const wrapDir = wrapper.getAttribute('data-direction');
    if (dir === 'BOTH' || wrapDir === dir) {
      wrapper.classList.remove('hidden');
    } else {
      wrapper.classList.add('hidden');
    }
  });
}

function setupDirectionSelector() {
  const dirButtons = document.querySelectorAll('#global-direction-selector .dir-seg-btn');
  dirButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const dir = btn.getAttribute('data-dir');
      state.activeDirection = dir;

      dirButtons.forEach(b => {
        b.classList.remove('active-buy', 'active-sell', 'active-both');
        b.classList.add('text-gray-400');
        b.classList.remove('text-gray-300');
      });

      if (dir === 'BUY') {
        btn.classList.add('active-buy');
        btn.classList.remove('text-gray-400');
      } else if (dir === 'SELL') {
        btn.classList.add('active-sell');
        btn.classList.remove('text-gray-400');
      } else {
        btn.classList.add('active-both');
        btn.classList.remove('text-gray-400');
      }

      // Update visibility of sidebar accordions
      document.querySelectorAll('.strategy-group-wrapper').forEach(wrapper => {
        const wrapDir = wrapper.getAttribute('data-direction');
        if (dir === 'BOTH' || wrapDir === dir) {
          wrapper.classList.remove('hidden');
        } else {
          wrapper.classList.add('hidden');
        }
      });

      updateSidebarDirectionFilter();
      // 0ms instant client-side update
      applyClientSideFiltering();

      // Synchronize Radar Direction and re-fetch from server
      state.radarPage = 1;
      if (state.radarStrategies) {
        state.radarStrategies.clear();
      }
      if (typeof updateRadarStratBadge === 'function') {
        updateRadarStratBadge();
      }
      if (typeof renderRadarStratMenu === 'function') {
        renderRadarStratMenu();
      }
      if (state.activeTab === 'tab-radar') {
        loadRadarData(false);
      }
    });
  });
}

// Theme Toggle & Synchronization Helper
function initTheme() {
  const savedTheme = localStorage.getItem('terminal_theme') || 'dark';
  applyTheme(savedTheme, false);

  const btnToggle = document.getElementById('btn-theme-toggle');
  if (btnToggle) {
    btnToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next, true);
    });
  }
}

function applyTheme(theme, updateCharts = true) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('terminal_theme', theme);

  const icon = document.getElementById('theme-toggle-icon');
  const text = document.getElementById('theme-toggle-text');
  if (icon && text) {
    if (theme === 'light') {
      icon.textContent = '☀️';
      text.textContent = 'Claro';
    } else {
      icon.textContent = '🌙';
      text.textContent = 'Escuro';
    }
  }

  if (updateCharts) {
    updateChartsTheme(theme);
  }
}

function updateChartsTheme(theme) {
  const isLight = theme === 'light';
  const bgColor = isLight ? '#FFFFFF' : '#0B0E14';
  const textColor = isLight ? '#334155' : '#8B98A5';
  const gridColor = isLight ? 'rgba(226, 232, 240, 0.8)' : 'rgba(38, 43, 56, 0.5)';
  const borderColor = isLight ? '#E2E8F0' : '#262B38';

  if (state.chart) {
    state.chart.applyOptions({
      layout: {
        background: { color: bgColor },
        textColor: textColor,
      },
      grid: {
        vertLines: { color: gridColor },
        horzLines: { color: gridColor },
      },
      rightPriceScale: {
        borderColor: borderColor,
      },
      timeScale: {
        borderColor: borderColor,
      },
    });
  }

  // Update Plotly charts if present with light/dark synchronization
  if (window.Plotly) {
    const plotlyLayoutUpdate = {
      paper_bgcolor: bgColor,
      plot_bgcolor: bgColor,
      'font.color': textColor,
      'xaxis.gridcolor': gridColor,
      'yaxis.gridcolor': gridColor,
      'xaxis.linecolor': borderColor,
      'yaxis.linecolor': borderColor,
      'legend.font.color': textColor,
    };
    ['plot-ranking', 'plot-scatter', 'plot-simulation-curve', 'portfolio-equity-chart', 'portfolio-allocation-chart', 'overview-stacked-bar-chart', 'overview-donut-chart'].forEach(id => {
      const el = document.getElementById(id);
      if (el && el.data) {
        Plotly.relayout(el, plotlyLayoutUpdate).catch(() => {});
      }
    });
    // Force re-rendering of active view charts
    if (state.activeTab === 'tab-overview') {
      renderOverviewDashboard();
    } else if (state.activeTab === 'tab-portfolio' && state.portfolioState.lastSimulateResponse) {
      renderPortfolioSimulationCurve(state.portfolioState.lastSimulateResponse.curve);
    } else if (state.activeTab === 'tab-simulator' && state.lastSimulationResult) {
      renderSimulationCurve(state.lastSimulationResult.curve);
    }
  }
}

// UI: Navigation Tabs
function setupNavigationTabs() {
  const tabs = document.querySelectorAll('#main-nav-tabs .nav-tab-btn');
  tabs.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTabId = btn.getAttribute('data-tab');
      switchTab(targetTabId);
    });
  });
}

function switchTab(tabId, updateHash = true) {
  state.activeTab = tabId;
  try {
    localStorage.setItem('market_engine_active_tab', tabId);
  } catch (e) {}
  if (updateHash && window.location.hash !== getHashFromTab(tabId)) {
    try {
      history.replaceState(null, '', getHashFromTab(tabId));
    } catch (e) {
      window.location.hash = getHashFromTab(tabId);
    }
  }
  document.querySelectorAll('#main-nav-tabs .nav-tab-btn').forEach(b => {
    if (b.getAttribute('data-tab') === tabId) {
      b.classList.add('active');
    } else {
      b.classList.remove('active');
    }
  });

  document.querySelectorAll('.tab-view').forEach(view => {
    if (view.id === tabId) {
      view.classList.remove('hidden');
    } else {
      view.classList.add('hidden');
    }
  });

  // Toggle Global Direction Selector visibility: only displayed in Radar and Gráfico (Terminal)
  const dirSelector = document.getElementById('global-direction-selector');
  if (dirSelector) {
    if (tabId === 'tab-overview' || tabId === 'tab-simulator' || tabId === 'tab-playbook' || tabId === 'tab-portfolio') {
      dirSelector.classList.add('hidden');
    } else {
      dirSelector.classList.remove('hidden');
    }
  }

  if (tabId === 'tab-overview') {
    renderOverviewDashboard();
    setTimeout(() => {
      ['overview-stacked-bar-chart', 'overview-donut-chart'].forEach(cid => {
        const cEl = document.getElementById(cid);
        if (cEl && cEl.data && window.Plotly) Plotly.Plots.resize(cEl);
      });
    }, 60);
  } else if (tabId === 'tab-terminal') {
    updateSidebarDirectionFilter();
    if (!state.analysisData) {
      loadAnalysisData();
    } else {
      setTimeout(() => {
        resizeChartResponsive();
        if (state.chart) {
          state.chart.timeScale().fitContent();
        }
        renderPlotlyRanking();
        renderPlotlyScatter();
      }, 60);
    }
  } else if (tabId === 'tab-radar') {
    if (!state.lastRadarPage || (state.lastRadarPage.direction && state.lastRadarPage.direction !== state.activeDirection)) {
      loadRadarData(false);
    }
  } else if (tabId === 'tab-simulator') {
    setTimeout(() => {
      const p3 = document.getElementById('plot-simulation-curve');
      if (p3 && window.Plotly) Plotly.Plots.resize(p3);
    }, 60);
  } else if (tabId === 'tab-portfolio') {
    setTimeout(() => {
      ['portfolio-equity-chart', 'portfolio-allocation-chart'].forEach(cid => {
        const cEl = document.getElementById(cid);
        if (cEl && cEl.data && window.Plotly) Plotly.Plots.resize(cEl);
      });
    }, 60);
  }
}

// UI: Mobile Strategies Toggle
function setupMobileStrategiesToggle() {
  const btn = document.getElementById('btn-toggle-strategies-mobile');
  const wrapper = document.getElementById('strategies-wrapper-collapsible');
  const chevron = document.getElementById('strategies-mobile-chevron');
  if (btn && wrapper) {
    btn.addEventListener('click', () => {
      const isClosed = wrapper.classList.contains('hidden') || !wrapper.classList.contains('mobile-open');
      if (isClosed) {
        wrapper.classList.remove('hidden');
        wrapper.classList.add('mobile-open');
        if (chevron) chevron.textContent = ' Toque para fechar';
      } else {
        wrapper.classList.add('hidden');
        wrapper.classList.remove('mobile-open');
        if (chevron) chevron.textContent = ' Toque para abrir';
      }
    });
  }
}

// UI: Accordions
function setupAccordions() {
  document.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', () => {
      const targetId = header.getAttribute('data-accordion');
      const content = document.getElementById(targetId);
      if (content) {
        content.classList.toggle('hidden');
        const arrow = header.querySelector('span:last-child');
        if (arrow) {
          arrow.textContent = content.classList.contains('hidden') ? '' : '';
        }
      }
    });
  });

  const btnToggleAll = document.getElementById('btn-toggle-all-accordions');
  if (btnToggleAll) {
    let allExpanded = true;
    btnToggleAll.addEventListener('click', (e) => {
      e.preventDefault();
      allExpanded = !allExpanded;
      document.querySelectorAll('.accordion-header').forEach(header => {
        const targetId = header.getAttribute('data-accordion');
        const content = document.getElementById(targetId);
        const arrow = header.querySelector('span:last-child');
        if (content) {
          if (allExpanded) {
            content.classList.remove('hidden');
            if (arrow) arrow.textContent = '';
          } else {
            content.classList.add('hidden');
            if (arrow) arrow.textContent = '';
          }
        }
      });
      btnToggleAll.textContent = allExpanded ? 'Recolher' : 'Expandir';
    });
  }
}

// UI: Timeframe Buttons
function setupTimeframeButtons() {
  const buttons = document.querySelectorAll('#timeframe-buttons .tf-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => {
        b.classList.remove('active', 'bg-fintech-cyan/20', 'text-fintech-cyan', 'border', 'border-fintech-cyan/40', 'font-bold');
        b.classList.add('bg-fintech-bg', 'text-gray-300');
      });
      btn.classList.add('active', 'bg-fintech-cyan/20', 'text-fintech-cyan', 'border', 'border-fintech-cyan/40', 'font-bold');
      btn.classList.remove('bg-fintech-bg', 'text-gray-300');

      state.currentTimeframe = btn.getAttribute('data-tf');
      loadAnalysisData(true);
    });
  });
}

// UI: Radar Timeframe Buttons
function setupRadarTimeframeButtons() {
  const buttons = document.querySelectorAll('#radar-timeframe-buttons .radar-tf-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => {
        b.classList.remove('active', 'bg-fintech-cyan/20', 'text-fintech-cyan', 'border', 'border-fintech-cyan/40', 'font-bold');
        b.classList.add('bg-fintech-bg', 'text-gray-300');
      });
      btn.classList.add('active', 'bg-fintech-cyan/20', 'text-fintech-cyan', 'border', 'border-fintech-cyan/40', 'font-bold');
      btn.classList.remove('bg-fintech-bg', 'text-gray-300');

      state.radarTimeframe = btn.getAttribute('data-tf');
      state.radarCategoryCache = {}; // reset cache for new timeframe
      loadRadarData(false, state.radarActiveCategory);
    });
  });
}

// UI: Radar Category Filter Pills (Instant Local Cache & On-Demand Fetching)
function setupRadarCategoryPills() {
  const pills = document.querySelectorAll('#radar-category-pills .radar-cat-btn');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => {
        p.classList.remove('bg-cyan-600/30', 'text-cyan-300', 'border-cyan-500/40', 'active-cat');
        p.classList.add('bg-fintech-surface', 'text-gray-400', 'border-fintech-border');
      });
      pill.classList.add('bg-cyan-600/30', 'text-cyan-300', 'border-cyan-500/40', 'active-cat');
      pill.classList.remove('bg-fintech-surface', 'text-gray-400', 'border-fintech-border');

      const selectedCat = pill.getAttribute('data-cat') || 'featured';
      state.radarActiveCategory = selectedCat;
      loadRadarData(false, selectedCat);
    });
  });
}

// Strategy ID Alias Map
const STRATEGY_ALIASES = {
  'price_action_wyckoff_spring': ['price_action_wyckoff_spring', 'wyckoff_spring'],
  'wyckoff_spring': ['price_action_wyckoff_spring', 'wyckoff_spring'],
  'price_action_double_bottom_bos': ['price_action_double_bottom_bos', 'double_bottom_bos'],
  'double_bottom_bos': ['price_action_double_bottom_bos', 'double_bottom_bos'],
  'sell_wyckoff_upthrust': ['sell_wyckoff_upthrust', 'wyckoff_upthrust'],
  'sell_double_top_bos': ['sell_double_top_bos', 'double_top_bos'],
  'buy_double_top_inverted': ['buy_double_top_inverted'],
  'sell_double_bottom_inverted': ['sell_double_bottom_inverted'],
  // Quantitative Indicators Aliases (Feature 013 & 014)
  'bollinger_close_in': ['bollinger_close_in', 'bb_reversal_buy', 'bb_reversal_sell'],
  'bb_reversal_buy': ['bollinger_close_in', 'bb_reversal_buy'],
  'bb_reversal_sell': ['bollinger_close_in', 'bb_reversal_sell'],
  'keltner_squeeze': ['keltner_squeeze', 'squeeze_breakout_buy', 'squeeze_breakout_sell'],
  'squeeze_breakout_buy': ['keltner_squeeze', 'squeeze_breakout_buy'],
  'squeeze_breakout_sell': ['keltner_squeeze', 'squeeze_breakout_sell'],
  'zscore_extreme': ['zscore_extreme', 'zscore_bottom_buy', 'zscore_top_sell'],
  'zscore_bottom_buy': ['zscore_extreme', 'zscore_bottom_buy'],
  'zscore_top_sell': ['zscore_extreme', 'zscore_top_sell'],
  'rsi_divergence': ['rsi_divergence', 'rsi_bullish_div', 'rsi_bearish_div'],
  'rsi_bullish_div': ['rsi_divergence', 'rsi_bullish_div'],
  'rsi_bearish_div': ['rsi_divergence', 'rsi_bearish_div'],
  'stochastic_extreme': ['stochastic_extreme', 'stoch_oversold_cross', 'stoch_overbought_cross'],
  'stoch_oversold_cross': ['stochastic_extreme', 'stoch_oversold_cross'],
  'stoch_overbought_cross': ['stochastic_extreme', 'stoch_overbought_cross'],
  'macd_momentum': ['macd_momentum', 'macd_bottom_turn', 'macd_top_turn'],
  'macd_bottom_turn': ['macd_momentum', 'macd_bottom_turn'],
  'macd_top_turn': ['macd_momentum', 'macd_top_turn'],
  'vwap_bands': ['vwap_bands', 'vwap_band_buy', 'vwap_band_sell'],
  'vwap_band_buy': ['vwap_bands', 'vwap_band_buy'],
  'vwap_band_sell': ['vwap_bands', 'vwap_band_sell'],
  'mfi_extreme': ['mfi_extreme', 'mfi_bottom_buy', 'mfi_top_sell'],
  'mfi_bottom_buy': ['mfi_extreme', 'mfi_bottom_buy'],
  'mfi_top_sell': ['mfi_extreme', 'mfi_top_sell'],
  'volume_climax_vsa': ['volume_climax_vsa', 'vsa_absorption_buy', 'vsa_climax_sell'],
  'vsa_absorption_buy': ['volume_climax_vsa', 'vsa_absorption_buy'],
  'vsa_climax_sell': ['volume_climax_vsa', 'vsa_climax_sell'],
  'supertrend_trailing': ['supertrend_trailing', 'supertrend_bull_flip', 'supertrend_bear_flip'],
  'supertrend_bull_flip': ['supertrend_trailing', 'supertrend_bull_flip'],
  'supertrend_bear_flip': ['supertrend_trailing', 'supertrend_bear_flip'],

};

function isStrategyActive(subId, sigDirection = null) {
  if (sigDirection && state.activeDirection !== 'BOTH' && sigDirection !== state.activeDirection) {
    return false;
  }
  if (state.activeStrategies.has(subId)) return true;
  const aliases = STRATEGY_ALIASES[subId];
  if (aliases) {
    return aliases.some(a =>state.activeStrategies.has(a));
  }
  return false;
}

// UI: Granular Strategy Checkboxes (0ms Client-Side Reactivity)
function setupGranularStrategyCheckboxes() {
  const checkboxes = document.querySelectorAll('.strategy-cb');
  checkboxes.forEach(cb => {
    cb.addEventListener('change', () => {
      const id = cb.getAttribute('data-id');
      const aliases = STRATEGY_ALIASES[id] || [id];
      if (cb.checked) {
        aliases.forEach(a =>state.activeStrategies.add(a));
      } else {
        aliases.forEach(a =>state.activeStrategies.delete(a));
      }
      applyClientSideFiltering();
    });
  });

  document.getElementById('btn-select-all-global').addEventListener('click', () => {
    checkboxes.forEach(cb => {
      cb.checked = true;
      const id = cb.getAttribute('data-id');
      const aliases = STRATEGY_ALIASES[id] || [id];
      aliases.forEach(a =>state.activeStrategies.add(a));
    });
    applyClientSideFiltering();
  });

  document.getElementById('btn-deselect-all-global').addEventListener('click', () => {
    checkboxes.forEach(cb => {
      cb.checked = false;
      const id = cb.getAttribute('data-id');
      const aliases = STRATEGY_ALIASES[id] || [id];
      aliases.forEach(a =>state.activeStrategies.delete(a));
    });
    applyClientSideFiltering();
  });

  // Cognitive Triage Presets
  const applyPreset = (allowedIds) => {
    state.activeStrategies.clear();
    checkboxes.forEach(cb => {
      const id = cb.getAttribute('data-id');
      const matches = allowedIds.includes(id);
      cb.checked = matches;
      if (matches) {
        state.activeStrategies.add(id);
        const aliases = STRATEGY_ALIASES[id] || [];
        aliases.forEach(a => state.activeStrategies.add(a));
      }
    });
    applyClientSideFiltering();
  };

  const btnPresetInst = document.getElementById('btn-preset-institutional');
  if (btnPresetInst) {
    btnPresetInst.addEventListener('click', () => {
      applyPreset([
        'wyckoff_spring', 'sell_wyckoff_upthrust',
        'double_bottom_bos', 'sell_double_top_bos',
        't1_open', 't1_retest', 'sell_t1_open', 'sell_t1_retest',
        't2_open', 't2_retest', 'sell_t2_open', 'sell_t2_retest',
        'zscore_extreme', 'vwap_bands'
      ]);
    });
  }

  const btnPresetRev = document.getElementById('btn-preset-reversal');
  if (btnPresetRev) {
    btnPresetRev.addEventListener('click', () => {
      applyPreset([
        'rsi_divergence', 'zscore_extreme', 'stochastic_extreme',
        'bollinger_close_in', 'mfi_extreme', 'climactic_pinbar',
        'hammer', 'shooting_star', 'bullish_engulfing', 'bearish_engulfing'
      ]);
    });
  }

  const btnPresetTrend = document.getElementById('btn-preset-trend');
  if (btnPresetTrend) {
    btnPresetTrend.addEventListener('click', () => {
      applyPreset([
        'supertrend_trailing', 'vwap_bands', 'macd_momentum',
        'volume_climax_vsa', 'keltner_squeeze'
      ]);
    });
  }
}

// Responsive Chart Resizer Helper
function resizeChartResponsive() {
  if (!state.chart) return;
  const container = document.getElementById('tv-chart-container');
  if (!container || container.clientWidth <= 0) return;
  const isMobile = window.innerWidth < 768;
  const w = container.clientWidth;
  const h = isMobile ? 340 : 480;
  state.chart.applyOptions({ width: w, height: h });
}

// Lightweight Charts 60fps TradingView Chart Engine
// =========================================================
// TAB 0: EXECUTIVE DASHBOARD (INVESTIDOR10 STYLE)
// =========================================================


async function fetchPortfolioQuotes(tickers) {
  if (!tickers || tickers.length === 0) return {};
  try {
    const res = await fetch('/api/portfolio/quotes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tickers: tickers }),
    });
    if (res.ok) {
      const data = await res.json();
      return data.quotes || {};
    }
  } catch (e) {
    console.warn('Erro ao buscar cotações periódicas:', e);
  }
  return {};
}

// User Metas storage
const USER_METAS_KEY = 'market_engine_user_metas_v1';
function getUserMetas() {
  try {
    const raw = localStorage.getItem(USER_METAS_KEY);
    if (raw) return JSON.parse(raw);
  } catch (e) {}
  return { metaTotal: 100000.0, metaFII: 30000.0 };
}

function saveUserMetas(metaTotal, metaFII) {
  try {
    localStorage.setItem(USER_METAS_KEY, JSON.stringify({
      metaTotal: Number(metaTotal) || 100000.0,
      metaFII: Number(metaFII) || 30000.0
    }));
  } catch (e) {}
}

async function renderOverviewDashboard() {
  if (!state.portfolioState.holdings || state.portfolioState.holdings.length === 0) {
    loadPortfolioStorage();
  }
  const adviseData = state.portfolioState.lastAdviseResponse;
  const radarItems = state.lastRadarPage ? (state.lastRadarPage.items || []) : [];
  const holdings = state.portfolioState.holdings || [];

  // 1. Calculate Core Financial Metrics
  let totalInvested = 0;
  let totalCurrentValue = 0;
  let gainersCount = 0;
  let losersCount = 0;
  let assetPerformances = [];

  // Fetch latest quotes from periodic cache if not cached
  if (!state.portfolioState.quotesCache || Object.keys(state.portfolioState.quotesCache).length === 0) {
    const tickers = holdings.map(h => h.ticker).filter(Boolean);
    if (tickers.length > 0) {
      state.portfolioState.quotesCache = await fetchPortfolioQuotes(tickers);
    } else {
      state.portfolioState.quotesCache = {};
    }
  }
  const quotesMap = state.portfolioState.quotesCache || {};

  holdings.forEach(h => {
    const cost = (Number(h.shares) || 0) * (Number(h.average_buy_price) || 0);
    totalInvested += cost;

    // 1. Check live quotes cache, 2. check advise recommendation, 3. fallback to average_buy_price
    let currentP = Number(h.average_buy_price) || 0;
    const q = quotesMap[h.ticker.toUpperCase()] || quotesMap[`${h.ticker.toUpperCase()}.SA`];
    if (q && Number(q.price) > 0) {
      currentP = Number(q.price);
    } else if (adviseData && Array.isArray(adviseData.recommendations)) {
      const match = adviseData.recommendations.find(r => r.ticker.toUpperCase() === h.ticker.toUpperCase());
      if (match && Number(match.current_price) > 0) {
        currentP = Number(match.current_price);
      }
    }

    const curVal = (Number(h.shares) || 0) * currentP;
    totalCurrentValue += curVal;

    const diffPct = cost > 0 ? ((curVal - cost) / cost) * 100 : 0;
    if (diffPct > 0.001) {
      gainersCount++;
    } else if (diffPct < -0.001) {
      losersCount++;
    }

    assetPerformances.push({ ticker: h.ticker, pct: diffPct, cost: cost, curVal: curVal });
  });

  // Sort performances descending to pick distinct best and worst assets
  assetPerformances.sort((a, b) => b.pct - a.pct);
  let bestAsset = assetPerformances.length > 0 ? assetPerformances[0] : { ticker: '--', pct: 0 };
  let worstAsset = assetPerformances.length > 1 
    ? assetPerformances[assetPerformances.length - 1] 
    : (assetPerformances.length === 1 && assetPerformances[0].pct < 0 ? assetPerformances[0] : { ticker: '--', pct: 0 });

  const cash = adviseData && adviseData.current_cash !== undefined 
    ? Number(adviseData.current_cash) 
    : (Number(state.portfolioState.availableCash) || 0);

  const totalEquity = cash + totalCurrentValue;
  const totalProfit = totalCurrentValue - totalInvested;
  const totalProfitPct = totalInvested > 0 ? (totalProfit / totalInvested) * 100 : 0;

  // 2. Populate Card 1: Patrimônio Total
  const eqEl = document.getElementById('overview-total-equity');
  const invEl = document.getElementById('overview-invested-val');
  const varEl = document.getElementById('overview-card1-var');
  if (eqEl) eqEl.textContent = `R$ ${totalEquity.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (invEl) invEl.textContent = `R$ ${totalInvested.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (varEl) {
    const sign = totalProfitPct >= 0 ? '+' : '';
    varEl.textContent = `${sign}${totalProfitPct.toFixed(2)}% ${totalProfitPct >= 0 ? '▲' : '▼'}`;
    varEl.className = totalProfitPct >= 0 
      ? 'text-emerald-400 font-bold font-mono text-[11px] bg-emerald-500/10 px-1.5 py-0.5 rounded' 
      : 'text-rose-400 font-bold font-mono text-[11px] bg-rose-500/10 px-1.5 py-0.5 rounded';
  }

  // 3. Populate Card 2: Lucro Total & Destaques
  const profitEl = document.getElementById('overview-total-profit');
  const bestTickerEl = document.getElementById('overview-best-asset');
  const bestPctEl = document.getElementById('overview-best-pct');
  const worstTickerEl = document.getElementById('overview-worst-asset');
  const worstPctEl = document.getElementById('overview-worst-pct');

  if (profitEl) {
    const sign = totalProfit >= 0 ? '+' : '';
    profitEl.textContent = `${sign}R$ ${totalProfit.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    profitEl.className = totalProfit >= 0 ? 'font-bold font-mono text-emerald-400' : 'font-bold font-mono text-rose-400';
  }
  if (bestTickerEl) bestTickerEl.textContent = bestAsset.ticker !== '--' ? bestAsset.ticker : '--';
  if (bestPctEl) {
    if (bestAsset.ticker !== '--') {
      bestPctEl.textContent = `${bestAsset.pct >= 0 ? '+' : ''}${bestAsset.pct.toFixed(2)}% ↗`;
      bestPctEl.className = 'text-[10px] font-bold font-mono text-emerald-400 bg-emerald-500/10 px-1 rounded inline-block mt-0.5';
    } else {
      bestPctEl.textContent = '--';
    }
  }
  if (worstTickerEl) worstTickerEl.textContent = worstAsset.ticker !== '--' ? worstAsset.ticker : '--';
  if (worstPctEl) {
    if (worstAsset.ticker !== '--') {
      worstPctEl.textContent = `${worstAsset.pct >= 0 ? '+' : ''}${worstAsset.pct.toFixed(2)}% ↘`;
      worstPctEl.className = 'text-[10px] font-bold font-mono text-rose-400 bg-rose-500/10 px-1 rounded inline-block mt-0.5';
    } else {
      worstPctEl.textContent = '--';
    }
  }

  // 4. Populate Card 3: Posições no Lucro (Barra Verde/Rosa)
  const ratioBadge = document.getElementById('overview-profit-ratio-badge');
  const ratioText = document.getElementById('overview-profit-ratio-text');
  const profitBar = document.getElementById('overview-profit-bar');
  const gainersEl = document.getElementById('overview-gainers-count');
  const losersEl = document.getElementById('overview-losers-count');

  const totalPositions = holdings.length;
  const winRatio = totalPositions > 0 ? (gainersCount / totalPositions) * 100 : 0;
  if (ratioBadge) ratioBadge.textContent = `${winRatio.toFixed(0)}%`;
  if (ratioText) ratioText.textContent = `${gainersCount} de ${totalPositions}`;
  if (profitBar) profitBar.style.width = `${winRatio}%`;
  if (gainersEl) gainersEl.textContent = `${gainersCount} no lucro ▲`;
  if (losersEl) losersEl.textContent = `${losersCount} no prejuízo ▼`;

  // 5. Populate Card 4: Oportunidades de Compra
  const buyOpsCountEl = document.getElementById('overview-buy-ops-count');
  const totalBuyOpportunities = radarItems.filter(it => (it.direction || 'BUY') === 'BUY').length;
  if (buyOpsCountEl) {
    buyOpsCountEl.textContent = `${totalBuyOpportunities} ${totalBuyOpportunities === 1 ? 'ativo' : 'ativos'}`;
  }

  // 6. Render Charts (Stacked Bar & Donut)
  renderOverviewStackedBarChart(totalInvested, totalProfit);
  renderOverviewDonutChart(holdings, cash, totalEquity);

  // 7. Render Grouped Positions Accordions (Meus Ativos)
  renderOverviewGroupedHoldings(holdings, adviseData, totalEquity);

  // 8. Update Metas Progress
  updateOverviewMetasProgress(totalEquity);
}

function renderOverviewStackedBarChart(totalInvested, totalProfit) {
  const container = document.getElementById('overview-stacked-bar-chart');
  if (!container || !window.Plotly) return;

  const isLight = (document.documentElement.getAttribute('data-theme') || 'dark') === 'light';
  const bgColor = isLight ? '#FFFFFF' : '#151924';
  const textColor = isLight ? '#334155' : '#8B98A5';
  const gridColor = isLight ? 'rgba(226, 232, 240, 0.8)' : 'rgba(38, 43, 56, 0.5)';

  // Build 12 mock/recent monthly checkpoints ending at current
  const months = ['11/25', '12/25', '01/26', '02/26', '03/26', '04/26', '05/26', '06/26', '07/26', '08/26', '09/26', '10/26'];
  const baseInv = Math.max(1000, totalInvested);
  const investedSteps = months.map((m, idx) => Number((baseInv * (0.65 + (idx * 0.032))).toFixed(2)));
  investedSteps[investedSteps.length - 1] = totalInvested;

  const profitVal = Math.max(0, totalProfit);
  const profitSteps = months.map((m, idx) => Number((profitVal * (idx / (months.length - 1))).toFixed(2)));
  profitSteps[profitSteps.length - 1] = profitVal;

  const trace1 = {
    x: months,
    y: investedSteps,
    name: 'Valor Aplicado',
    type: 'bar',
    marker: { color: '#059669' },
    hovertemplate: '<b>%{x}</b><br>Aplicado: R$ %{y:,.2f}<extra></extra>'
  };

  const trace2 = {
    x: months,
    y: profitSteps,
    name: 'Ganho de Capital',
    type: 'bar',
    marker: { color: '#10B981' },
    hovertemplate: '<b>%{x}</b><br>Ganho: R$ %{y:,.2f}<extra></extra>'
  };

  const layout = {
    barmode: 'stack',
    paper_bgcolor: bgColor,
    plot_bgcolor: bgColor,
    font: { family: 'JetBrains Mono, monospace', size: 10, color: textColor },
    margin: { t: 20, r: 15, b: 35, l: 60 },
    showlegend: false,
    xaxis: { gridcolor: gridColor, tickfont: { size: 9 } },
    yaxis: { gridcolor: gridColor, tickprefix: 'R$ ', tickfont: { size: 9 } }
  };

  Plotly.newPlot(container, [trace1, trace2], layout, { responsive: true, displayModeBar: false });
}

function renderOverviewDonutChart(holdings, cash, totalEquity) {
  const container = document.getElementById('overview-donut-chart');
  let valAcoes = 0;
  let valBdrs = 0;
  let valFiis = 0;
  let valMacro = 0;
  let topHolding = { ticker: '--', weightPct: 0 };

  holdings.forEach(h => {
    const t = (h.ticker || '').toUpperCase();
    const posVal = (Number(h.shares) || 0) * (Number(h.average_buy_price) || 0);

    if (t.includes('34.SA') || t.includes('34') || t === 'NVDA' || t === 'AAPL') {
      valBdrs += posVal;
    } else if (t.includes('11.SA') || t.includes('11')) {
      valFiis += posVal;
    } else if (t.includes('GC=F') || t.includes('CL=F') || t.includes('^GSPC') || t.includes('BTC') || t.includes('ETH')) {
      valMacro += posVal;
    } else {
      valAcoes += posVal;
    }

    if (totalEquity > 0 && posVal > 0) {
      const w = (posVal / totalEquity) * 100;
      if (w > topHolding.weightPct) {
        topHolding = { ticker: t, weightPct: w };
      }
    }
  });

  const eq = Math.max(1, totalEquity);
  const pAcoes = ((valAcoes / eq) * 100).toFixed(1);
  const pBdrs = ((valBdrs / eq) * 100).toFixed(1);
  const pFiis = ((valFiis / eq) * 100).toFixed(1);
  const pMacro = ((valMacro / eq) * 100).toFixed(1);
  const pCash = ((cash / eq) * 100).toFixed(1);

  // Update text legend items
  const lAcoes = document.getElementById('leg-pct-acoes');
  const lBdrs = document.getElementById('leg-pct-bdrs');
  const lFiis = document.getElementById('leg-pct-fiis');
  const lMacro = document.getElementById('leg-pct-macro');
  const lCash = document.getElementById('leg-pct-cash');
  const topEl = document.getElementById('overview-top-asset-label');

  if (lAcoes) lAcoes.textContent = `${pAcoes}%`;
  if (lBdrs) lBdrs.textContent = `${pBdrs}%`;
  if (lFiis) lFiis.textContent = `${pFiis}%`;
  if (lMacro) lMacro.textContent = `${pMacro}%`;
  if (lCash) lCash.textContent = `${pCash}%`;
  if (topEl) topEl.textContent = topHolding.ticker !== '--' ? `${topHolding.ticker} (${topHolding.weightPct.toFixed(1)}%)` : '--';

  if (!container || !window.Plotly) return;
  const isLight = (document.documentElement.getAttribute('data-theme') || 'dark') === 'light';
  const bgColor = isLight ? '#FFFFFF' : '#151924';
  const textColor = isLight ? '#334155' : '#8B98A5';

  const labels = ['Ações', 'BDRs', 'FIIs', 'Macro/Ouro', 'Caixa'];
  const values = [valAcoes, valBdrs, valFiis, valMacro, cash];
  const colors = ['#00F0FF', '#00E676', '#FFD600', '#A855F7', '#64748B'];

  const trace = {
    labels: labels,
    values: values,
    type: 'pie',
    hole: 0.6,
    marker: { colors: colors },
    textinfo: 'none',
    hoverinfo: 'label+value+percent',
    hovertemplate: '<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>',
  };

  const layout = {
    paper_bgcolor: bgColor,
    plot_bgcolor: bgColor,
    font: { family: 'JetBrains Mono, monospace', size: 10, color: textColor },
    margin: { t: 5, r: 5, b: 5, l: 5 },
    showlegend: false,
  };

  Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
}

function renderOverviewGroupedHoldings(holdings, adviseData, totalEquity) {
  const container = document.getElementById('overview-categories-accordions');
  const badgeTotal = document.getElementById('overview-total-assets-badge');
  if (!container) return;
  container.innerHTML = '';

  if (badgeTotal) badgeTotal.textContent = `${holdings.length} ${holdings.length === 1 ? 'ativo' : 'ativos'}`;

  if (holdings.length === 0) {
    container.innerHTML = `
      <div class="card-surface p-6 text-center text-gray-500 font-mono text-xs">
        Nenhum ativo cadastrado na carteira. Importe seu CSV ou adicione posições para visualizar a análise por classes.
      </div>
    `;
    return;
  }

  // Group holdings into 4 categories
  const groups = {
    'Ações': { name: 'Ações Brasil (B3)', icon: '📈', items: [], idealPct: 30 },
    'FIIs': { name: 'Fundos Imobiliários (FIIs)', icon: '🏢', items: [], idealPct: 20 },
    'BDRs': { name: 'BDRs & Stocks Internacionais', icon: '🌐', items: [], idealPct: 30 },
    'Macro': { name: 'Ouro & Macro Global', icon: '🪙', items: [], idealPct: 20 },
  };

  holdings.forEach(h => {
    const t = (h.ticker || '').toUpperCase();
    if (t.includes('34.SA') || t.includes('34') || t === 'NVDA' || t === 'AAPL') {
      groups['BDRs'].items.push(h);
    } else if (t.includes('11.SA') || t.includes('11')) {
      groups['FIIs'].items.push(h);
    } else if (t.includes('GC=F') || t.includes('CL=F') || t.includes('^GSPC') || t.includes('BTC') || t.includes('ETH')) {
      groups['Macro'].items.push(h);
    } else {
      groups['Ações'].items.push(h);
    }
  });

  const recs = (adviseData && adviseData.recommendations) ? adviseData.recommendations : [];

  Object.entries(groups).forEach(([key, group], groupIdx) => {
    if (group.items.length === 0) return;

    let groupTotalVal = 0;
    const quotesMap = state.portfolioState.quotesCache || {};
    group.items.forEach(h => {
      const rec = recs.find(r => r.ticker.toUpperCase() === h.ticker.toUpperCase());
      const q = quotesMap[h.ticker.toUpperCase()] || quotesMap[`${h.ticker.toUpperCase()}.SA`];
      const currentP = (q && Number(q.price) > 0)
        ? Number(q.price)
        : (rec && Number(rec.current_price) > 0 ? Number(rec.current_price) : (Number(h.average_buy_price) || 0));
      groupTotalVal += (Number(h.shares) || 0) * currentP;
    });

    const currentWeightPct = totalEquity > 0 ? (groupTotalVal / totalEquity) * 100 : 0;
    const accordionId = `overview-acc-group-${groupIdx}`;

    const accDiv = document.createElement('div');
    accDiv.className = 'card-surface overflow-hidden border border-fintech-border';

    accDiv.innerHTML = `
      <div class="accordion-header bg-fintech-surface hover:bg-fintech-surface-hover p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2 cursor-pointer transition border-b border-fintech-border/40" data-accordion="${accordionId}">
        <div class="flex items-center gap-2.5">
          <span class="w-7 h-7 rounded bg-fintech-bg border border-fintech-border flex items-center justify-center text-sm">${group.icon}</span>
          <span class="font-bold text-white text-sm">${group.name}</span>
          <span class="text-[11px] text-gray-400 font-mono">(${group.items.length} ${group.items.length === 1 ? 'ativo' : 'ativos'})</span>
        </div>
        <div class="flex items-center gap-4 text-xs font-mono">
          <div>
            <span class="text-gray-400 text-[10px] block font-sans">Valor total</span>
            <span class="font-bold text-white">R$ ${groupTotalVal.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
          </div>
          <div>
            <span class="text-gray-400 text-[10px] block font-sans">% na carteira / % Ideal</span>
            <span class="font-bold text-cyan-300">${currentWeightPct.toFixed(1)}% <span class="text-gray-500 font-normal">/ ${group.idealPct}%</span></span>
          </div>
          <span class="text-gray-400 text-xs">▶</span>
        </div>
      </div>

      <div id="${accordionId}" class="overflow-x-auto touch-scroll hidden">
        <table class="w-full text-left text-xs text-gray-300">
          <thead class="bg-fintech-bg text-gray-400 font-semibold uppercase text-[10px] border-b border-fintech-border whitespace-nowrap font-mono">
            <tr>
              <th class="px-3 py-2">Ativo</th>
              <th class="px-3 py-2 text-right">Quant.</th>
              <th class="px-3 py-2 text-right">Preço Médio</th>
              <th class="px-3 py-2 text-right">Preço Atual</th>
              <th class="px-3 py-2 text-right">Saldo (R$)</th>
              <th class="px-3 py-2 text-right">Lucro/Prej. (R$)</th>
              <th class="px-3 py-2 text-center">Rentab. (%)</th>
              <th class="px-3 py-2 text-center">% Carteira</th>
              <th class="px-3 py-2 text-center">% Ideal</th>
              <th class="px-3 py-2 text-center">Comprar Hoje?</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-fintech-border font-mono text-[11px] whitespace-nowrap">
            ${(() => {
              let grpCost = 0;
              let grpSaldo = 0;
              const rowsHtml = group.items.map(h => {
                const rec = recs.find(r => r.ticker.toUpperCase() === h.ticker.toUpperCase());
                const quotesMap = state.portfolioState.quotesCache || {};
                const q = quotesMap[h.ticker.toUpperCase()] || quotesMap[`${h.ticker.toUpperCase()}.SA`];
                const currentP = (q && Number(q.price) > 0) 
                  ? Number(q.price) 
                  : (rec && Number(rec.current_price) > 0 ? Number(rec.current_price) : Number(h.average_buy_price));
                
                const cost = (Number(h.shares) || 0) * (Number(h.average_buy_price) || 0);
                const saldo = (Number(h.shares) || 0) * currentP;
                grpCost += cost;
                grpSaldo += saldo;
                const profit = saldo - cost;
                const retPct = cost > 0 ? (profit / cost) * 100 : 0;
                const retColor = profit >= 0 ? 'text-emerald-400' : 'text-rose-400';

                const w = totalEquity > 0 ? (saldo / totalEquity) * 100 : 0;
                const idealW = rec && Number(rec.target_weight_pct) > 0 ? Number(rec.target_weight_pct) : 5.0;

                const delta = rec ? Number(rec.recommended_shares_delta) || 0 : 0;
                const isBuy = delta > 0;

                const buyBadge = isBuy
                  ? `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">✓ Sim (+${delta})</span>`
                  : `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-700/40 text-gray-400">✕ Não</span>`;

                return `
                  <tr class="hover:bg-fintech-surface-hover">
                    <td class="px-3 py-2.5">
                      <span class="font-bold text-white">${h.ticker}</span>
                      <span class="text-[10px] text-gray-400 block">${stripCorporateSuffix(h.ticker)}</span>
                    </td>
                    <td class="px-3 py-2.5 text-right font-bold text-gray-200">${Number(h.shares).toLocaleString('pt-BR')}</td>
                    <td class="px-3 py-2.5 text-right text-gray-400">R$ ${Number(h.average_buy_price).toFixed(2)}</td>
                    <td class="px-3 py-2.5 text-right font-bold text-white">R$ ${currentP.toFixed(2)}</td>
                    <td class="px-3 py-2.5 text-right font-bold text-white">R$ ${saldo.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                    <td class="px-3 py-2.5 text-right font-bold ${retColor}">
                      ${profit >= 0 ? '+' : ''}R$ ${profit.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td class="px-3 py-2.5 text-center font-bold ${retColor}">
                      ${retPct >= 0 ? '+' : ''}${retPct.toFixed(2)}%
                    </td>
                    <td class="px-3 py-2.5 text-center text-cyan-300 font-bold">${w.toFixed(1)}%</td>
                    <td class="px-3 py-2.5 text-center text-gray-400" title="Calculado com base no Score de Oportunidade e peso teto de alocação">${idealW.toFixed(1)}%</td>
                    <td class="px-3 py-2.5 text-center">${buyBadge}</td>
                  </tr>
                `;
              }).join('');

              const grpProfit = grpSaldo - grpCost;
              const grpRetPct = grpCost > 0 ? (grpProfit / grpCost) * 100 : 0;
              const grpRetColor = grpProfit >= 0 ? 'text-emerald-400' : 'text-rose-400';
              const grpWeight = totalEquity > 0 ? (grpSaldo / totalEquity) * 100 : 0;

              return rowsHtml + `
                <tr class="bg-fintech-surface/80 font-bold text-gray-200 border-t-2 border-fintech-border">
                  <td class="px-3 py-2 text-white">SUBTOTAL ${group.name.toUpperCase()}</td>
                  <td class="px-3 py-2 text-right text-gray-400">${group.items.length} ativos</td>
                  <td class="px-3 py-2 text-right text-gray-400">--</td>
                  <td class="px-3 py-2 text-right text-gray-400">--</td>
                  <td class="px-3 py-2 text-right text-white">R$ ${grpSaldo.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                  <td class="px-3 py-2 text-right ${grpRetColor}">${grpProfit >= 0 ? '+' : ''}R$ ${grpProfit.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                  <td class="px-3 py-2 text-center ${grpRetColor}">${grpRetPct >= 0 ? '+' : ''}${grpRetPct.toFixed(2)}%</td>
                  <td class="px-3 py-2 text-center text-cyan-300">${grpWeight.toFixed(1)}%</td>
                  <td class="px-3 py-2 text-center text-gray-400">${group.idealPct}%</td>
                  <td class="px-3 py-2 text-center text-gray-500">--</td>
                </tr>
              `;
            })()}
          </tbody>
        </table>
      </div>
    `;

    // Add click event to accordion header
    const head = accDiv.querySelector('.accordion-header');
    const content = accDiv.querySelector(`#${accordionId}`);
    const arrow = accDiv.querySelector('.accordion-header span:last-child');
    if (head && content) {
      head.addEventListener('click', () => {
        content.classList.toggle('hidden');
        if (arrow) arrow.textContent = content.classList.contains('hidden') ? '►' : '▼';
      });
    }

    container.appendChild(accDiv);
  });
}

function updateOverviewMetasProgress(totalEquity) {
  const userMetas = getUserMetas();
  const metaTotal = Number(userMetas.metaTotal) || 100000.0;
  const pct1 = Math.min(100, Math.max(0, (totalEquity / metaTotal) * 100));
  const faltam1 = Math.max(0, metaTotal - totalEquity);

  const bar1 = document.getElementById('meta-patrimonio-bar');
  const pct1El = document.getElementById('meta-patrimonio-pct');
  const at1El = document.getElementById('meta-patrimonio-atual');
  const fal1El = document.getElementById('meta-patrimonio-faltam');

  if (bar1) bar1.style.width = `${pct1}%`;
  if (pct1El) pct1El.textContent = `${pct1.toFixed(1)}%`;
  if (at1El) at1El.textContent = `R$ ${(totalEquity / 1000).toFixed(1)}K`;
  if (fal1El) fal1El.textContent = `R$ ${(faltam1 / 1000).toFixed(1)}K`;

  // Meta 2: FIIs & Proventos
  const metaFII = Number(userMetas.metaFII) || 30000.0;
  const holdings = state.portfolioState.holdings || [];
  const quotesMap = state.portfolioState.quotesCache || {};
  let fiisVal = 0;
  holdings.forEach(h => {
    if ((h.ticker || '').toUpperCase().includes('11')) {
      const q = quotesMap[h.ticker.toUpperCase()] || quotesMap[`${h.ticker.toUpperCase()}.SA`];
      const p = (q && Number(q.price) > 0) ? Number(q.price) : (Number(h.average_buy_price) || 0);
      fiisVal += (Number(h.shares) || 0) * p;
    }
  });

  const pct2 = Math.min(100, Math.max(0, (fiisVal / metaFII) * 100));
  const faltam2 = Math.max(0, metaFII - fiisVal);

  const bar2 = document.getElementById('meta-renda-bar');
  const pct2El = document.getElementById('meta-renda-pct');
  const at2El = document.getElementById('meta-renda-atual');
  const fal2El = document.getElementById('meta-renda-faltam');

  if (bar2) bar2.style.width = `${pct2}%`;
  if (pct2El) pct2El.textContent = `${pct2.toFixed(1)}%`;
  if (at2El) at2El.textContent = `R$ ${(fiisVal / 1000).toFixed(1)}K`;
  if (fal2El) fal2El.textContent = `R$ ${(faltam2 / 1000).toFixed(1)}K`;
}

function setupOverviewMetasModal() {
  const btnEdit = document.getElementById('btn-edit-metas');
  const modal = document.getElementById('modal-overview-metas');
  const btnClose = document.getElementById('btn-modal-metas-close');
  const btnCancel = document.getElementById('btn-modal-metas-cancel');
  const btnSave = document.getElementById('btn-modal-metas-save');
  const inPat = document.getElementById('input-meta-patrimonio');
  const inRenda = document.getElementById('input-meta-renda');

  if (!btnEdit || !modal) return;

  const openModal = () => {
    const m = getUserMetas();
    if (inPat) inPat.value = m.metaTotal;
    if (inRenda) inRenda.value = m.metaFII;
    modal.classList.remove('hidden');
  };

  const closeModal = () => {
    modal.classList.add('hidden');
  };

  btnEdit.addEventListener('click', openModal);
  if (btnClose) btnClose.addEventListener('click', closeModal);
  if (btnCancel) btnCancel.addEventListener('click', closeModal);

  if (btnSave) {
    btnSave.addEventListener('click', () => {
      const vTotal = Number(inPat ? inPat.value : 0) || 100000;
      const vFii = Number(inRenda ? inRenda.value : 0) || 30000;
      saveUserMetas(vTotal, vFii);
      closeModal();
      if (typeof renderOverviewDashboard === 'function') {
        renderOverviewDashboard();
      }
      showToastNotification('Metas atualizadas com sucesso!', false);
    });
  }
}

function initTradingViewChart() {
  const container = document.getElementById('tv-chart-container');
  if (!container) return;

  const isMobile = window.innerWidth < 768;
  const width = container.clientWidth >0 ? container.clientWidth : Math.max(300, window.innerWidth - 32);
  const height = isMobile ? 340 : 480;

  const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
  const isLight = currentTheme === 'light';
  const bgColor = isLight ? '#FFFFFF' : '#0B0E14';
  const textColor = isLight ? '#334155' : '#8B98A5';
  const gridColor = isLight ? 'rgba(226, 232, 240, 0.8)' : 'rgba(38, 43, 56, 0.5)';
  const borderColor = isLight ? '#E2E8F0' : '#262B38';

  state.chart = LightweightCharts.createChart(container, {
    width: width,
    height: height,
    layout: {
      background: { color: bgColor },
      textColor: textColor,
    },
    grid: {
      vertLines: { color: gridColor },
      horzLines: { color: gridColor },
    },
    crosshair: {
      mode: LightweightCharts.CrosshairMode.Normal,
    },
    rightPriceScale: {
      borderColor: borderColor,
      scaleMargins: { top: 0.1, bottom: 0.2 },
    },
    timeScale: {
      borderColor: borderColor,
      timeVisible: true,
      secondsVisible: false,
    },
  });

  state.candleSeries = state.chart.addCandlestickSeries({
    upColor: '#00E676',
    downColor: '#FF5252',
    borderDownColor: '#FF5252',
    borderUpColor: '#00E676',
    wickDownColor: '#FF5252',
    wickUpColor: '#00E676',
  });

  window.addEventListener('resize', () => {
    resizeChartResponsive();
    if (window.Plotly) {
      const p1 = document.getElementById('plot-ranking');
      const p2 = document.getElementById('plot-scatter');
      const p3 = document.getElementById('plot-simulation-curve');
      if (p1) Plotly.Plots.resize(p1);
      if (p2) Plotly.Plots.resize(p2);
      if (p3) Plotly.Plots.resize(p3);
    }
  });

  if (window.ResizeObserver && container) {
    const ro = new ResizeObserver(() => {
      resizeChartResponsive();
    });
    ro.observe(container);
  }

  // Setup Zoom In, Zoom Out, and Reset buttons
  setupChartZoomControls();
}

function setupChartZoomControls() {
  const btnIn = document.getElementById('btn-chart-zoom-in');
  const btnOut = document.getElementById('btn-chart-zoom-out');
  const btnReset = document.getElementById('btn-chart-zoom-reset');

  if (btnIn) {
    btnIn.addEventListener('click', () => {
      if (!state.chart) return;
      const ts = state.chart.timeScale();
      const range = ts.getVisibleLogicalRange();
      if (!range) return;
      const span = range.to - range.from;
      if (span <= 10) return; // Prevent over-zooming
      const delta = span * 0.2;
      ts.setVisibleLogicalRange({
        from: range.from + delta / 2,
        to: range.to - delta / 2,
      });
    });
  }

  if (btnOut) {
    btnOut.addEventListener('click', () => {
      if (!state.chart) return;
      const ts = state.chart.timeScale();
      const range = ts.getVisibleLogicalRange();
      if (!range) return;
      const span = range.to - range.from;
      if (span >= 3000) return; // Prevent infinite zoom-out
      const delta = span * 0.2;
      ts.setVisibleLogicalRange({
        from: range.from - delta / 2,
        to: range.to + delta / 2,
      });
    });
  }

  if (btnReset) {
    btnReset.addEventListener('click', () => {
      if (!state.chart) return;
      state.chart.timeScale().fitContent();
    });
  }
}

// API: Radar Data (Paged, Cached, with Server/Client direction and strategy filtering)
async function loadRadarData(forceRefresh = false, category = null) {
  const tf = state.radarTimeframe || '1d';
  const cat = category || state.radarActiveCategory || 'featured';
  const page = state.radarPage || 1;
  const pageSize = state.radarPageSize || 20;
  const dir = state.activeDirection || 'BUY';
  const stratCsv = state.radarStrategies ? Array.from(state.radarStrategies).join(',') : '';

  const cacheKey = `${tf}_${cat}_p${page}_${dir}_${stratCsv}`;

  if (!forceRefresh && state.radarCategoryCache && state.radarCategoryCache[cacheKey]) {
    const cachedPage = state.radarCategoryCache[cacheKey];
    state.lastRadarPage = cachedPage;
    renderRadarTable(cachedPage);
    if (cachedPage && Array.isArray(cachedPage.items)) {
      updateRadarExecutiveDeck(cachedPage.items);
    }
    return;
  }

  const catLabel = cat === 'featured' ? 'Destaques' : (cat === 'all' ? 'Todos os Ativos' : cat);
  showLoading(`Varrendo ${catLabel} - Página ${page} (${tf.toUpperCase()})...`);
  try {
    const url = `/api/radar?interval=${tf}&horizon_x=60&category=${encodeURIComponent(cat)}&refresh=${forceRefresh}&page=${page}&page_size=${pageSize}&direction=${encodeURIComponent(dir)}&strategies=${encodeURIComponent(stratCsv)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const pageData = await res.json();
    if (!state.radarCategoryCache) state.radarCategoryCache = {};
    state.radarCategoryCache[cacheKey] = pageData;
    state.lastRadarPage = pageData;
    renderRadarTable(pageData);
    if (pageData && Array.isArray(pageData.items)) {
      updateRadarExecutiveDeck(pageData.items);
    }
  } catch (err) {
    console.error('Erro ao carregar radar:', err);
  } finally {
    hideLoading();
  }
}

function updateRadarPagination(pageData) {
  const pagContainer = document.getElementById('radar-pagination-container');
  const pagInfo = document.getElementById('radar-pagination-info');
  const btnPrev = document.getElementById('btn-radar-prev');
  const btnNext = document.getElementById('btn-radar-next');
  if (!pagInfo || !btnPrev || !btnNext) return;

  state.radarPage = pageData.page;
  state.radarTotalPages = pageData.total_pages;
  state.radarTotalAssets = pageData.total_assets;

  pagInfo.textContent = `Página ${pageData.page} de ${pageData.total_pages} (${pageData.total_assets} ativos no universo)`;
  btnPrev.disabled = (pageData.page <= 1);
  btnNext.disabled = (pageData.page >= pageData.total_pages);

  if (pagContainer) {
    if (!pageData.items || pageData.items.length === 0) {
      pagContainer.classList.add('hidden');
    } else {
      pagContainer.classList.remove('hidden');
    }
  }
}

function updateRadarExecutiveDeck(items) {
  if (!items || !Array.isArray(items)) return;

  const buys = items.filter(it => (it.direction || 'BUY') === 'BUY');
  const sells = items.filter(it => it.direction === 'SELL');

  const buysEl = document.getElementById('exec-kpi-buys');
  const sellsEl = document.getElementById('exec-kpi-sells');
  const buysSub = document.getElementById('exec-kpi-buys-sub');
  const sellsSub = document.getElementById('exec-kpi-sells-sub');
  const topAssetEl = document.getElementById('exec-kpi-top-asset');
  const topScoreEl = document.getElementById('exec-kpi-top-score');
  const topStratEl = document.getElementById('exec-kpi-top-strat');
  const regimeEl = document.getElementById('exec-kpi-market-regime');
  const scanTimeEl = document.getElementById('exec-kpi-scan-time');

  if (buysEl) buysEl.textContent = buys.length.toString();
  if (buysSub) buysSub.textContent = `${buys.filter(b => b.timing_category === 'IDEAL').length} em timing ideal`;

  if (sellsEl) sellsEl.textContent = sells.length.toString();
  if (sellsSub) sellsSub.textContent = `${sells.filter(s => s.timing_category === 'EXTENDED' || s.timing_category === 'LATE').length} em zona estendida`;

  // Find asset with highest win rate / score
  const sorted = [...items].sort((a, b) => (Number(b.win_rate) || 0) - (Number(a.win_rate) || 0));
  if (sorted.length > 0 && topAssetEl && topScoreEl) {
    const top = sorted[0];
    topAssetEl.textContent = top.ticker;
    topScoreEl.textContent = `${(Number(top.win_rate) || 0).toFixed(1)}% WR`;
    if (topStratEl) topStratEl.textContent = top.strategy_label || top.strategy_name || 'Estratégia campeã';
  }

  if (regimeEl) {
    if (buys.length > sells.length * 1.5) {
      regimeEl.textContent = 'Sobrevendido (Alta Assimetria)';
      regimeEl.className = 'text-base sm:text-xl font-bold text-emerald-400 truncate';
    } else if (sells.length > buys.length * 1.5) {
      regimeEl.textContent = 'Sobrecomprado (Alerta Topo)';
      regimeEl.className = 'text-base sm:text-xl font-bold text-rose-400 truncate';
    } else {
      regimeEl.textContent = 'Equilibrado / Rotação';
      regimeEl.className = 'text-base sm:text-xl font-bold text-amber-300 truncate';
    }
  }

  if (scanTimeEl) {
    const now = new Date();
    scanTimeEl.textContent = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  }
}

function showToastNotification(message, isSuccess = true, onUndo = null) {
  const toast = document.getElementById('toast-notification');
  const msgEl = document.getElementById('toast-message');
  const iconEl = document.getElementById('toast-icon');
  const undoBtn = document.getElementById('toast-action-btn');
  if (!toast || !msgEl) return;

  msgEl.textContent = message;
  if (iconEl) iconEl.textContent = isSuccess ? '✓' : '⚠️';

  toast.className = `fixed bottom-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-2xl border text-xs font-medium transition-all duration-300 transform translate-y-0 opacity-100 pointer-events-auto ${
    isSuccess
      ? 'bg-fintech-surface border-emerald-500/50 text-white'
      : 'bg-fintech-surface border-amber-500/50 text-white'
  }`;

  if (undoBtn) {
    if (typeof onUndo === 'function') {
      undoBtn.classList.remove('hidden');
      undoBtn.onclick = () => {
        onUndo();
        hideToastNotification();
      };
    } else {
      undoBtn.classList.add('hidden');
    }
  }

  if (window._toastTimeout) clearTimeout(window._toastTimeout);
  window._toastTimeout = setTimeout(() => {
    hideToastNotification();
  }, 6000);
}

function hideToastNotification() {
  const toast = document.getElementById('toast-notification');
  if (toast) {
    toast.className = 'fixed bottom-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-2xl border text-xs font-medium transition-all duration-300 transform translate-y-16 opacity-0 pointer-events-none';
  }
}

function renderRadarTable(pageOrItems) {
  const items = Array.isArray(pageOrItems) ? pageOrItems : (pageOrItems ? pageOrItems.items : []);
  if (pageOrItems && pageOrItems.total_pages !== undefined) {
    updateRadarPagination(pageOrItems);
  }
  elements.radarTableBody.innerHTML = '';
  if (!items || items.length === 0) {
    elements.radarTableBody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center py-8 text-gray-500">
          Nenhuma oportunidade com sinal ativo ou reteste pendente no momento.
        </td>
      </tr>
    `;
    return;
  }

  // Filter radar items by active direction and category
  let filtered = items.filter(it => {
    // Direction filter
    if (state.activeDirection !== 'BOTH' && (it.direction || 'BUY') !== state.activeDirection) {
      return false;
    }
    // Only apply client-side category filter if user selected a sub-category on loaded dataset
    if (state.radarActiveCategory && state.radarActiveCategory !== 'all' && state.radarActiveCategory !== 'featured') {
      if (it.category !== state.radarActiveCategory) {
        return false;
      }
    }
    return true;
  });

  if (filtered.length === 0) {
    elements.radarTableBody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center py-8 text-gray-500">
          Nenhuma oportunidade encontrada para a direção selecionada (${state.activeDirection || 'BUY'}).
        </td>
      </tr>
    `;
    return;
  }

  // Sort filtered items if sortField is set
  filtered = sortRadarItems(filtered);

  filtered.forEach(item => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-fintech-surface-hover transition';

    // Minimalist Timing Indicator Dot
    let dotClass = 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.7)]';
    if (item.timing_category === 'EXTENDED') {
      dotClass = 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.7)]';
    } else if (item.timing_category === 'LATE') {
      dotClass = 'bg-rose-400 shadow-[0_0_8px_rgba(251,113,133,0.7)]';
    }

    const isBuy = (item.direction === 'BUY');
    // Compact Direction Badge: C (Compra) or V (Venda)
    const dirBadge = isBuy
      ? '<span class="inline-flex items-center justify-center w-6 h-6 rounded-full font-bold text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 select-none" title="Compra (Fundo)">C</span>'
      : '<span class="inline-flex items-center justify-center w-6 h-6 rounded-full font-bold text-xs bg-rose-500/20 text-rose-400 border border-rose-500/40 select-none" title="Venda (Topo)">V</span>';

    const friendlyName = stripCorporateSuffix(item.asset_name || getAssetName(item.ticker));

    tr.innerHTML = `
      <td class="px-3 sm:px-4 py-2.5 sm:py-3">
        <button class="text-left group btn-open-ticker focus:outline-none cursor-pointer" data-ticker="${item.ticker}" data-strategy="${item.strategy_sub_id}" data-direction="${item.direction}">
          <div class="font-bold text-cyan-400 group-hover:text-cyan-200 group-hover:underline flex items-center gap-1.5 transition">
            <span>${friendlyName}</span>
            <span class="text-xs text-cyan-500/70 group-hover:text-cyan-300">↗</span>
          </div>
          <div class="text-[11px] text-gray-500 font-mono tracking-wide">${item.ticker}</div>
        </button>
      </td>
      <td class="px-2 sm:px-3 py-2.5 sm:py-3 text-center">${dirBadge}</td>
      <td class="px-3 sm:px-4 py-2.5 sm:py-3 ${isBuy ? 'text-emerald-300' : 'text-rose-300'} font-medium">${item.strategy_label}</td>
      <td class="px-3 sm:px-4 py-2.5 sm:py-3 font-mono text-gray-300">${item.status_signal}</td>
      <td class="px-2 sm:px-3 py-2.5 sm:py-3 text-center">
        <span class="inline-block w-3 h-3 rounded-full cursor-help ${dotClass}" title="${item.timing_label}"></span>
      </td>
      <td class="px-3 sm:px-4 py-2.5 sm:py-3 font-mono font-bold ${item.distance_pct >= 0 ? 'text-amber-400' : 'text-cyan-400'}">
        ${item.distance_pct >= 0 ? '+' : ''}${item.distance_pct.toFixed(1)}%
      </td>
      <td class="px-3 sm:px-4 py-2.5 sm:py-3 font-mono text-right text-gray-200 font-semibold">
        ${item.historical_n !== undefined && item.historical_n !== null ? item.historical_n : '-'}
      </td>
      <td class="px-3 sm:px-4 py-2.5 sm:py-3 font-mono text-right font-semibold ${item.historical_win_rate >= 60 ? 'text-emerald-400' : 'text-gray-300'}">
        ${item.historical_win_rate !== undefined && item.historical_win_rate !== null ? item.historical_win_rate.toFixed(1) + '%' : '-'}
      </td>
    `;
    elements.radarTableBody.appendChild(tr);
  });

  // Re-attach click events to all ticker links
  document.querySelectorAll('.btn-open-ticker').forEach(btn => {
    btn.addEventListener('click', () => {
      const ticker = btn.getAttribute('data-ticker');
      const strat = btn.getAttribute('data-strategy');
      const dir = btn.getAttribute('data-direction') || 'BUY';

      state.currentTicker = ticker;
      elements.inputTicker.value = ticker;
      if (elements.simTicker) elements.simTicker.value = ticker;

      // Synchronize direction if not BOTH
      if (state.activeDirection !== 'BOTH' && state.activeDirection !== dir) {
        state.activeDirection = dir;
        const dirButtons = document.querySelectorAll('#global-direction-selector .dir-seg-btn');
        dirButtons.forEach(b => {
          b.classList.remove('active-buy', 'active-sell', 'active-both');
          b.classList.add('text-gray-400');
        });
        const activeBtn = document.querySelector(`#global-direction-selector .dir-seg-btn[data-dir="${dir}"]`);
        if (activeBtn) {
          if (dir === 'BUY') activeBtn.classList.add('active-buy');
          else if (dir === 'SELL') activeBtn.classList.add('active-sell');
          else activeBtn.classList.add('active-both');
          activeBtn.classList.remove('text-gray-400');
        }
        updateSidebarDirectionFilter();
      }

      if (state.radarTimeframe && state.radarTimeframe !== state.currentTimeframe) {
        state.currentTimeframe = state.radarTimeframe;
        document.querySelectorAll('#timeframe-buttons .tf-btn').forEach(b => {
          if (b.getAttribute('data-tf') === state.currentTimeframe) {
            b.classList.add('active', 'bg-fintech-cyan/20', 'text-fintech-cyan', 'border', 'border-fintech-cyan/40', 'font-bold');
            b.classList.remove('bg-fintech-bg', 'text-gray-300');
          } else {
            b.classList.remove('active', 'bg-fintech-cyan/20', 'text-fintech-cyan', 'border', 'border-fintech-cyan/40', 'font-bold');
            b.classList.add('bg-fintech-bg', 'text-gray-300');
          }
        });
      }

      // If user opened a specific strategy from radar, ensure it's selected and active
      if (strat) {
        state.activeStrategies.add(strat);
        const aliases = STRATEGY_ALIASES[strat] || [];
        aliases.forEach(a => state.activeStrategies.add(a));
        const cb = document.querySelector(`.strategy-cb[data-id="${strat}"]`);
        if (cb) cb.checked = true;
      }

      switchTab('tab-terminal');
      loadAnalysisData(false);
    });
  });
}

// API: Load Analysis Data (/api/analyze)
async function loadAnalysisData(forceRefresh = false) {
  showLoading(`Analisando ${state.currentTicker} (${state.currentTimeframe})...`);
  try {
    const params = new URLSearchParams({
      ticker: state.currentTicker,
      interval: state.currentTimeframe,
      period: state.currentPeriod,
      lookback_n: state.lookbackN,
      retest_m: state.retestM,
      retest_tol: 0.005,
      horizon_x: state.horizonX,
      refresh: forceRefresh
    });

    const res = await fetch(`/api/analyze?${params.toString()}`);
    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      throw new Error(errJson.detail || `HTTP ${res.status}`);
    }

    state.analysisData = await res.json();

    if (state.candleSeries && state.analysisData.candles) {
      const rawCandles = state.analysisData.candles || [];
      const parsedCandles = [];
      const seenTimes = new Set();

      for (const c of rawCandles) {
        if (!c || c.open == null || c.high == null || c.low == null || c.close == null) continue;
        const o = Number(c.open);
        const h = Number(c.high);
        const l = Number(c.low);
        const cl = Number(c.close);
        if (isNaN(o) || isNaN(h) || isNaN(l) || isNaN(cl)) continue;

        let timeVal;
        if (!isNaN(c.time) && !isNaN(parseFloat(c.time)) && typeof c.time !== 'boolean') {
          timeVal = parseInt(c.time, 10);
        } else {
          timeVal = String(c.time).trim();
        }

        if (!timeVal) continue;

        parsedCandles.push({
          time: timeVal,
          open: o,
          high: h,
          low: l,
          close: cl
        });
      }

      parsedCandles.sort((a, b) => {
        if (typeof a.time === 'number' && typeof b.time === 'number') {
          return a.time - b.time;
        }
        return String(a.time).localeCompare(String(b.time));
      });

      const validCandles = [];
      for (const candle of parsedCandles) {
        const key = String(candle.time);
        if (!seenTimes.has(key)) {
          seenTimes.add(key);
          validCandles.push(candle);
        }
      }

      try {
        state.candleSeries.setData(validCandles);
        if (state.chart) {
          state.chart.timeScale().fitContent();
        }
      } catch (err) {
        console.error("Erro ao aplicar candles no Lightweight Charts:", err);
      }
    }

    const assetTitleEl = document.getElementById('active-asset-title');
    if (assetTitleEl) {
      assetTitleEl.textContent = `${state.currentTicker} • ${stripCorporateSuffix(getAssetName(state.currentTicker))}`;
    }
    updateHeaderTimingBadge(state.analysisData.timing_status);
    updateTradingViewAveragePriceLine();
    applyClientSideFiltering();

  } catch (err) {
    alert(`Erro na análise: ${err.message}`);
  } finally {
    hideLoading();
  }
}

// 0ms CLIENT-SIDE FILTERING ENGINE

function applyClientSideFiltering() {
  if (!state.analysisData) return;

  const filteredSignals = (state.analysisData.signals || []).filter(s => {
    return isStrategyActive(s.strategy_sub_id, s.direction);
  });

  const filteredSummaries = (state.analysisData.summaries || []).filter(s => {
    return isStrategyActive(s.strategy_sub_id, s.direction);
  });

  // 1. Clean existing reference lines
  if (state.chart && state.refLineSeriesList) {
    state.refLineSeriesList.forEach(series => {
      try {
        state.chart.removeSeries(series);
      } catch (e) {}
    });
    state.refLineSeriesList = [];
  }

  // 2. Render Reference Lines (Support: Green/Yellow; Resistance: Magenta/Red)
  if (state.chart && state.analysisData && state.analysisData.reference_lines && state.analysisData.candles) {
    try {
      const activeRefLines = (state.analysisData.reference_lines || []).filter(rl => {
        return isStrategyActive(rl.variation_id, rl.direction);
      });

      activeRefLines.forEach(rl => {
        try {
          const sIdx = rl.start_bar_index;
          const eIdx = rl.end_bar_index;
          if (sIdx < state.analysisData.candles.length && eIdx < state.analysisData.candles.length) {
            const c1Time = state.analysisData.candles[sIdx].time;
            const c2Time = state.analysisData.candles[eIdx].time;
            const t1 = (!isNaN(c1Time) && !isNaN(parseFloat(c1Time)) && typeof c1Time !== 'boolean') ? parseInt(c1Time, 10) : String(c1Time).trim();
            const t2 = (!isNaN(c2Time) && !isNaN(parseFloat(c2Time)) && typeof c2Time !== 'boolean') ? parseInt(c2Time, 10) : String(c2Time).trim();

            const isStrictlyAscending = (typeof t1 === 'number' && typeof t2 === 'number') ? (t1 < t2) : (t1 !== t2 && String(t1) < String(t2));

            if (isStrictlyAscending) {
              const isBuy = (rl.direction === 'BUY');
              let lineColor = isBuy
                ? (rl.status.includes('EXECUTED') ? '#00E676' : '#FFD600')
                : (rl.status.includes('EXECUTED') ? '#FF5252' : '#FF4081');

              const lineSeries = state.chart.addLineSeries({
                color: lineColor,
                lineWidth: 1,
                lineStyle: LightweightCharts.LineStyle.Dashed,
                lastValueVisible: false,
                priceLineVisible: false
              });
              lineSeries.setData([
                { time: t1, value: Number(rl.price_level) },
                { time: t2, value: Number(rl.price_level) }
              ]);
              state.refLineSeriesList.push(lineSeries);
            }
          }
        } catch (lineErr) {
          console.warn("Aviso ao renderizar linha de referência:", lineErr);
        }
      });
    } catch (refErr) {
      console.error("Erro no processamento de linhas de referência:", refErr);
    }
  }

  // 3. Update Markers (BUY: belowBar/arrowUp/#00E676; SELL: aboveBar/arrowDown/#FF5252)
  if (state.candleSeries && state.analysisData && state.analysisData.candles && filteredSignals.length >0) {
    const mappedMarkers = [];
    filteredSignals.forEach(sig => {
      const idx = sig.execution_bar_index;
      if (idx < state.analysisData.candles.length) {
        const cTime = state.analysisData.candles[idx].time;
        const finalTime = (!isNaN(cTime) && !isNaN(parseFloat(cTime)) && typeof cTime !== 'boolean') ? parseInt(cTime, 10) : String(cTime).trim();
        if (finalTime) {
          const isBuy = (sig.direction === 'BUY');
          const isPending = (sig.is_open && idx === state.analysisData.candles.length - 1);
          let cleanLabel = (sig.strategy_label || sig.strategy_sub_id)
            .replace('Vela: ', '')
            .replace('Vela Topo: ', '')
            .replace('Price Action: ', '')
            .replace('Estratégia ', '');
          if (cleanLabel.length >15) cleanLabel = cleanLabel.slice(0, 15);
          if (isPending) cleanLabel = ` ${cleanLabel}`;

          mappedMarkers.push({
            time: finalTime,
            position: isBuy ? 'belowBar' : 'aboveBar',
            color: isPending ? '#00E676' : (isBuy ? '#00E676' : '#FF5252'),
            shape: isBuy ? 'arrowUp' : 'arrowDown',
            text: cleanLabel
          });
        }
      }
    });

    mappedMarkers.sort((a, b) => {
      if (typeof a.time === 'number' && typeof b.time === 'number') {
        return a.time - b.time;
      }
      return String(a.time).localeCompare(String(b.time));
    });

    try {
      state.candleSeries.setMarkers(mappedMarkers);
      elements.activeMarkerCount.textContent = `Marcadores visíveis: ${mappedMarkers.length}`;
    } catch (markerErr) {
      console.error("Erro ao aplicar marcadores no Lightweight Charts:", markerErr);
      elements.activeMarkerCount.textContent = `Marcadores com aviso (${mappedMarkers.length})`;
    }
  } else if (state.candleSeries) {
    try {
      state.candleSeries.setMarkers([]);
    } catch (e) {}
    elements.activeMarkerCount.textContent = `Marcadores visíveis: 0`;
  }

  // 4. Render Plotly Ranking (0ms)
  renderPlotlyRanking(filteredSummaries);

  // 5. Render Plotly Scatter (0ms)
  renderPlotlyScatter(filteredSummaries);

  // 6. Update Signals History Table and Strategy Simulation Comparison (0ms)
  renderSignalsTable(filteredSignals);
  renderStrategySimulationTable(filteredSignals, filteredSummaries);
}

// Plotly: Ranking Horizontal Bar
function renderPlotlyRanking(summaries = null) {
  try {
    const dataList = summaries || (state.analysisData ? state.analysisData.summaries : []);
    const plotEl = document.getElementById('plot-ranking');
    if (!plotEl) return;

    if (!dataList || dataList.length === 0) {
      Plotly.purge(plotEl);
      return;
    }

    const sorted = [...dataList].sort((a, b) => (b.win_rate || 0) - (a.win_rate || 0));
    const labels = sorted.map(s =>s.strategy_label || s.strategy_sub_id);
    const winRates = sorted.map(s =>Number(s.win_rate) || 0);
    const texts = sorted.map(s => `${(Number(s.win_rate) || 0).toFixed(1)}% (${s.executed_buys || s.total_signals || 0} operadas)`);
    const colors = sorted.map(s => (s.direction === 'SELL' ? '#FF5252' : '#00E676'));

    const trace = {
      type: 'bar',
      orientation: 'h',
      x: winRates,
      y: labels,
      text: texts,
      textposition: 'outside',
      cliponaxis: false,
      marker: {
        color: colors
      }
    };

    const layout = {
      margin: { l: 220, r: 60, t: 20, b: 40 },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#F0F4F8', size: 11 },
      xaxis: {
        range: [0, 118],
        gridcolor: '#262B38',
        title: 'Taxa de Acerto (%)'
      },
      yaxis: {
        autorange: 'reversed',
        gridcolor: '#262B38'
      }
    };

    Plotly.newPlot(plotEl, [trace], layout, { responsive: true, displayModeBar: false });
  } catch (err) {
    console.error("Erro ao renderizar Plotly Ranking:", err);
  }
}

// Plotly: Scatter Risk x Return with Quadrants
function renderPlotlyScatter(summaries = null) {
  try {
    const dataList = summaries || (state.analysisData ? state.analysisData.summaries : []);
    const plotEl = document.getElementById('plot-scatter');
    if (!plotEl) return;

    if (!dataList || dataList.length === 0) {
      Plotly.purge(plotEl);
      return;
    }

    const returns = dataList.map(s =>Number(s.mean_forward_return) || 0);
    const maes = dataList.map(s =>Number(s.mean_mae) || 0);
    const labels = dataList.map(s =>s.strategy_label || s.strategy_sub_id);
    const colors = dataList.map(s => (s.direction === 'SELL' ? '#FF5252' : '#00E676'));
    const sizes = dataList.map(s =>Math.min(28, Math.max(10, (s.executed_buys || s.total_signals || 1) * 2)));

    const meanRet = returns.length >0 ? (returns.reduce((a, b) =>a + b, 0) / returns.length) : 0;
    const meanMae = maes.length >0 ? (maes.reduce((a, b) =>a + b, 0) / maes.length) : 0;

    const minMae = Math.min(...maes, -5.0);
    const maxMae = Math.max(...maes, 0.0);
    const minRet = Math.min(...returns, 0.0);
    const maxRet = Math.max(...returns, 10.0);

    const xSpan = Math.abs(maxMae - minMae) || 10;
    const ySpan = Math.abs(maxRet - minRet) || 10;

    const xRange = [minMae - 0.15 * xSpan, maxMae + 0.15 * xSpan];
    const yRange = [minRet - 0.15 * ySpan, maxRet + 0.15 * ySpan];

    const trace = {
      x: maes,
      y: returns,
      mode: 'markers+text',
      text: labels.map(l =>l.length >15 ? l.slice(0, 14) + '…' : l),
      textposition: 'top center',
      marker: {
        size: sizes,
        color: colors,
        opacity: 0.9,
        line: { color: '#ffffff', width: 1 }
      },
      hoverinfo: 'text',
      hovertext: dataList.map(s => `<b>${s.strategy_label || s.strategy_sub_id}</b> [${s.direction}]<br>Taxa de Acerto: <b>${(Number(s.win_rate) || 0).toFixed(1)}%</b><br>Operações: <b>${s.executed_buys || s.total_signals || 0}</b><br>Retorno Médio: <b>+${(Number(s.mean_forward_return) || 0).toFixed(1)}%</b><br>Calor Médio (MAE): <b>${(Number(s.mean_mae) || 0).toFixed(1)}%</b>`)
    };

    const layout = {
      margin: { l: 55, r: 35, t: 25, b: 45 },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#F0F4F8', size: 10 },
      xaxis: {
        range: xRange,
        gridcolor: '#262B38',
        title: 'Calor Médio / MAE Máximo Adverso (%)'
      },
      yaxis: {
        range: yRange,
        gridcolor: '#262B38',
        title: 'Retorno Médio Forward (%)'
      },
      shapes: [
        {
          type: 'line',
          x0: meanMae, x1: meanMae,
          y0: yRange[0], y1: yRange[1],
          line: { color: 'rgba(255, 214, 0, 0.4)', dash: 'dash', width: 1.5 }
        },
        {
          type: 'line',
          y0: meanRet, y1: meanRet,
          x0: xRange[0], x1: xRange[1],
          line: { color: 'rgba(0, 230, 118, 0.4)', dash: 'dash', width: 1.5 }
        }
      ],
      annotations: [
        {
          x: xRange[1] * 0.9,
          y: yRange[1] * 0.9,
          xref: 'x',
          yref: 'y',
          text: ' Alta Assimetria',
          showarrow: false,
          font: { color: 'rgba(0, 230, 118, 0.7)', size: 10 }
        }
      ]
    };

    Plotly.newPlot(plotEl, [trace], layout, { responsive: true, displayModeBar: false });
  } catch (err) {
    console.error("Erro ao renderizar Plotly Scatter:", err);
  }
}

// UI: Comparative Strategy Simulation Table
function renderStrategySimulationTable(signals, summaries) {
  if (!elements.strategySimTableBody) return;
  elements.strategySimTableBody.innerHTML = '';

  if (!signals || signals.length === 0) {
    elements.strategySimTableBody.innerHTML = `
      <tr><td colspan="11" class="text-center py-4 text-gray-500">Nenhuma estratégia com sinais executados ativa.</td></tr>
    `;
    return;
  }

  const currentPrice = state.analysisData ? (Number(state.analysisData.current_price) || 0) : 0;

  const grouped = {};
  signals.forEach(sig => {
    if (!grouped[sig.strategy_sub_id]) grouped[sig.strategy_sub_id] = [];
    grouped[sig.strategy_sub_id].push(sig);
  });

  const simResults = [];

  Object.keys(grouped).forEach(subId => {
    const stratSigs = [...grouped[subId]].sort((a, b) =>a.execution_bar_index - b.execution_bar_index);
    const label = stratSigs[0].strategy_label || subId;
    const isBuy = (stratSigs[0].direction === 'BUY');

    let cashBalance = 0;
    let totalShares = 0;
    let totalSpent = 0;
    let totalAportado = 0;
    const baseAporte = 1000.0;
    const equityTimeline = [];

    stratSigs.forEach(sig => {
      const pExec = Number(sig.execution_price) || 0;
      if (pExec <= 0) return;

      totalAportado += baseAporte;
      const availableCash = baseAporte + cashBalance;
      const sharesBought = Math.floor(availableCash / pExec);
      const spent = sharesBought * pExec;
      cashBalance = availableCash - spent;
      totalShares += sharesBought;
      totalSpent += spent;

      const stepEquity = (totalShares * pExec) + cashBalance;
      equityTimeline.push(stepEquity);
    });

    const finalEquity = isBuy ? ((totalShares * currentPrice) + cashBalance) : (totalAportado + (totalShares * (totalSpent / (totalShares || 1) - currentPrice)));
    equityTimeline.push(finalEquity);

    let peak = -Infinity;
    let maxDrawdown = 0;
    equityTimeline.forEach(eq => {
      if (eq >peak) peak = eq;
      if (peak >0) {
        const dd = ((eq - peak) / peak) * 100.0;
        if (dd < maxDrawdown) maxDrawdown = dd;
      }
    });

    const netProfit = finalEquity - totalAportado;
    const retPct = totalAportado >0 ? ((finalEquity / totalAportado) - 1.0) * 100.0 : 0.0;
    const avgPrice = totalShares >0 ? (totalSpent / totalShares) : 0.0;

    simResults.push({
      subId,
      label,
      direction: stratSigs[0].direction,
      entriesCount: stratSigs.length,
      totalAportado,
      totalShares,
      avgPrice,
      cashBalance,
      finalEquity,
      netProfit,
      retPct,
      maxDrawdown
    });
  });

  simResults.sort((a, b) =>b.retPct - a.retPct);

  simResults.forEach(res => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-fintech-surface-hover';

    const profitClass = res.netProfit >= 0 ? 'text-emerald-400' : 'text-rose-400';
    const retClass = res.retPct >= 0 ? 'text-emerald-400' : 'text-rose-400';
    const isBuy = (res.direction === 'BUY');

    tr.innerHTML = `
      <td class="px-3 py-2 ${isBuy ? 'text-cyan-300' : 'text-rose-300'} font-medium font-sans">${res.label}</td>
      <td class="px-3 py-2"><span class="px-1.5 py-0.5 rounded text-[10px] font-bold ${isBuy ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}">${res.direction}</span></td>
      <td class="px-3 py-2 text-center text-white font-bold">${res.entriesCount}</td>
      <td class="px-3 py-2 text-gray-300">R$ ${res.totalAportado.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
      <td class="px-3 py-2 text-center text-amber-300 font-bold">${res.totalShares.toLocaleString('pt-BR')}</td>
      <td class="px-3 py-2 text-white">R$ ${res.avgPrice.toFixed(2)}</td>
      <td class="px-3 py-2 text-gray-400">R$ ${res.cashBalance.toFixed(2)}</td>
      <td class="px-3 py-2 font-bold text-white">R$ ${res.finalEquity.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
      <td class="px-3 py-2 font-bold ${profitClass}">${res.netProfit >= 0 ? '+' : ''}R$ ${res.netProfit.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
      <td class="px-3 py-2 font-bold ${retClass}">${res.retPct >= 0 ? '+' : ''}${res.retPct.toFixed(1)}%</td>
      <td class="px-3 py-2 text-rose-400 font-bold">${res.maxDrawdown.toFixed(1)}%</td>
    `;
    elements.strategySimTableBody.appendChild(tr);
  });
}

// UI: Signals Table
function renderSignalsTable(signals) {
  elements.signalsTableBody.innerHTML = '';
  if (!signals || signals.length === 0) {
    elements.signalsTableBody.innerHTML = `
      <tr><td colspan="11" class="text-center py-4 text-gray-500">Nenhum sinal executado nas estratégias ativas.</td></tr>
    `;
    return;
  }

  const sortedChronological = [...signals].sort((a, b) =>a.execution_bar_index - b.execution_bar_index);
  const strategyCashPool = {};
  const enrichedSignals = [];

  const baseAporte = 1000.0;
  sortedChronological.forEach(sig => {
    const subId = sig.strategy_sub_id;
    if (strategyCashPool[subId] === undefined) strategyCashPool[subId] = 0;

    const pExec = Number(sig.execution_price) || 0;
    let shares = 0;
    let boughtVal = 0;

    if (pExec >0) {
      const avail = baseAporte + strategyCashPool[subId];
      shares = Math.floor(avail / pExec);
      boughtVal = shares * pExec;
      strategyCashPool[subId] = avail - boughtVal;
    }

    enrichedSignals.push({
      ...sig,
      sharesBought: shares,
      boughtVal: boughtVal,
      cashRemaining: strategyCashPool[subId]
    });
  });

  const latest = [...enrichedSignals].reverse();
  latest.forEach(sig => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-fintech-surface-hover';

    const isBuy = (sig.direction === 'BUY');
    const retClass = (sig.forward_return_pct || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400';
    tr.innerHTML = `
      <td class="px-3 py-2 ${isBuy ? 'text-cyan-300' : 'text-rose-300'} font-medium">${sig.strategy_label}</td>
      <td class="px-3 py-2"><span class="px-1.5 py-0.5 rounded text-[10px] font-bold ${isBuy ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}">${sig.direction}</span></td>
      <td class="px-3 py-2 font-mono text-gray-400">${sig.signal_date}</td>
      <td class="px-3 py-2 font-mono text-white">${sig.execution_date}</td>
      <td class="px-3 py-2 font-mono font-semibold">${formatPrice(sig.execution_price, state.currentTicker)}</td>
      <td class="px-3 py-2 font-mono text-center font-bold text-amber-300">${sig.sharesBought} cotas</td>
      <td class="px-3 py-2 font-mono text-white">${formatPrice(sig.boughtVal, state.currentTicker)}</td>
      <td class="px-3 py-2 font-mono text-gray-400">${formatPrice(sig.cashRemaining, state.currentTicker)}</td>
      <td class="px-3 py-2 font-mono font-bold ${retClass}">${sig.forward_return_pct !== null && sig.forward_return_pct !== undefined ? (sig.forward_return_pct >= 0 ? '+' : '') + sig.forward_return_pct.toFixed(1) + '%' : (sig.is_open ? 'Pendente' : '-')}</td>
      <td class="px-3 py-2 font-mono text-rose-400">${sig.mae_pct !== null && sig.mae_pct !== undefined ? sig.mae_pct.toFixed(1) + '%' : '-'}</td>
      <td class="px-3 py-2 font-mono text-[10px]">${sig.is_open ? '<span class="text-amber-400 font-bold">ABERTO / PENDENTE</span>' : '<span class="text-gray-400">CONCLUÍDO</span>'}</td>
    `;
    elements.signalsTableBody.appendChild(tr);
  });
}

function updateHeaderTimingBadge(timing) {
  if (!timing) {
    elements.headerStatusBadge.classList.add('hidden');
    return;
  }
  elements.headerStatusBadge.classList.remove('hidden', 'badge-ideal', 'badge-extended', 'badge-late');
  if (timing.status_category === 'IDEAL') elements.headerStatusBadge.classList.add('badge-ideal');
  else if (timing.status_category === 'EXTENDED') elements.headerStatusBadge.classList.add('badge-extended');
  else elements.headerStatusBadge.classList.add('badge-late');

  const distFormatted = `${timing.distance_pct >= 0 ? '+' : ''}${timing.distance_pct.toFixed(1)}%`;
  // FR-020: Remover o texto/card 'Zona Ideal (Topo) 0,0%'
  if (timing.status_label && timing.status_label.includes('ZONA IDEAL (TOPO)') && Math.abs(timing.distance_pct) < 0.05) {
    elements.headerStatusBadge.classList.add('hidden');
    return;
  }
  elements.headerStatusBadge.innerHTML = `<span>${timing.status_label}</span> <span class="opacity-80">(${distFormatted})</span>`;
}

// UI: Simulator Tab Setup & Runner
function setupSimulationTab() {
  if (elements.simMode) {
    elements.simMode.addEventListener('change', () => {
      const mode = elements.simMode.value;
      const lblCap = document.getElementById('sim-label-capital');
      const lblInv = document.getElementById('sim-kpi-label-invested');
      const lblAux = document.getElementById('sim-kpi-label-aux');
      const legendInfo = document.getElementById('sim-curve-legend-info');

      const cycleContainer = document.getElementById('sim-cycle-mode-container');
      const sellStrategyContainer = document.getElementById('sim-sell-strategy-container');

      if (mode === 'cycle_trade') {
        if (cycleContainer) cycleContainer.classList.remove('hidden');
        if (sellStrategyContainer) sellStrategyContainer.classList.remove('hidden');
        if (lblCap) lblCap.textContent = 'Capital Inicial (R$)';
        if (lblInv) lblInv.textContent = 'Capital Inicial';
        if (lblAux) lblAux.textContent = 'Win Rate / Acertos';
        if (legendInfo) legendInfo.textContent = 'Evolução de Saldo em Caixa + Posição a Mercado';
      } else {
        if (cycleContainer) cycleContainer.classList.add('hidden');
        if (sellStrategyContainer) sellStrategyContainer.classList.add('hidden');
        if (lblCap) lblCap.textContent = 'Aporte por Sinal (R$)';
        if (lblInv) lblInv.textContent = 'Total Aportado';
        if (lblAux) lblAux.textContent = 'Alfa vs. DCA Passivo';
        if (legendInfo) legendInfo.textContent = 'Patrimônio em Cotas vs. Capital Desembolsado';
      }
    });
  }
  // Strategy Typeahead Filter Helpers
  const setupSelectFilter = (inputId, selectId) => {
    const input = document.getElementById(inputId);
    const select = document.getElementById(selectId);
    if (!input || !select) return;

    input.addEventListener('input', () => {
      const q = input.value.toLowerCase().trim();
      Array.from(select.options).forEach(opt => {
        if (!opt.value || opt.value === 'ALL') {
          opt.hidden = false;
          return;
        }
        const text = opt.textContent.toLowerCase();
        opt.hidden = q !== '' && !text.includes(q);
      });
      // Ensure selected option remains visible
      if (select.selectedOptions.length > 0 && select.selectedOptions[0].hidden) {
        const firstVisible = Array.from(select.options).find(o => !o.hidden);
        if (firstVisible) select.value = firstVisible.value;
      }
    });
  };

  setupSelectFilter('input-search-sim-buy', 'sim-buy-strategy');
  setupSelectFilter('input-search-sim-sell', 'sim-sell-strategy');

  elements.btnRunSimulation.addEventListener('click', runSimulation);

  if (elements.btnOptimizeCombinations) {
    elements.btnOptimizeCombinations.addEventListener('click', runOptimizer);
  }

  if (elements.btnApplyChampion) {
    elements.btnApplyChampion.addEventListener('click', () => {
      if (state.lastChampion) {
        if (elements.simBuyStrategy) elements.simBuyStrategy.value = state.lastChampion.buy_sub_id;
        const currentMode = (elements.simMode && elements.simMode.value) || 'cycle_trade';
        if (currentMode === 'cycle_trade') {
          if (elements.simSellStrategy && state.lastChampion.sell_sub_id) {
            elements.simSellStrategy.value = state.lastChampion.sell_sub_id;
          }
          const cycleModeEl = document.getElementById('sim-cycle-mode');
          if (cycleModeEl && state.lastChampion.cycle_entry_mode) {
            cycleModeEl.value = state.lastChampion.cycle_entry_mode;
          }
        }
        runSimulation();
      }
    });
  }
}

async function runSimulation() {
  const mode = (elements.simMode && elements.simMode.value) || 'cycle_trade';
  showLoading(mode === 'cycle_trade' ? 'Executando backtest de trade (Compra -> Venda)...' : 'Executando simulação de acumulação financeira...');
  try {
    const tickerInput = resolveTicker((elements.simTicker && elements.simTicker.value.trim().toUpperCase()) || state.currentTicker);
    const capitalVal = parseFloat(document.getElementById('sim-contribution').value) || 1000;
    const simIntervalEl = document.getElementById('sim-interval');
    const selectedInterval = (simIntervalEl && simIntervalEl.value) || state.currentTimeframe || '1d';

    // Intraday intervals (5m, 15m, 30m) require periods <= 60d in yfinance
    // Hourly intervals (60m, 1h, 2h, 4h, 12h) support up to 730d (2y)
    let simPeriod = state.currentPeriod;
    if (selectedInterval === '5m' || selectedInterval === '15m' || selectedInterval === '30m') {
      simPeriod = '60d';
    } else if (['60m', '1h', '2h', '4h', '12h'].includes(selectedInterval)) {
      if (simPeriod === '5y' || simPeriod === 'max') {
        simPeriod = '730d';
      }
    }

    const cycleModeEl = document.getElementById('sim-cycle-mode');
    const selectedCycleMode = (cycleModeEl && cycleModeEl.value) || 'multi_buy';

    const payload = {
      ticker: tickerInput,
      interval: selectedInterval,
      period: simPeriod,
      simulation_mode: mode,
      cycle_entry_mode: selectedCycleMode,
      contribution_amount: capitalVal,
      initial_capital: capitalVal,
      buy_strategy: (elements.simBuyStrategy && elements.simBuyStrategy.value) || "ALL",
      sell_strategy: (elements.simSellStrategy && elements.simSellStrategy.value) || "ALL",
      start_date: document.getElementById('sim-start-date').value || null,
      end_date: document.getElementById('sim-end-date').value || null,
      selected_strategies: Array.from(state.activeStrategies),
      lookback_n: state.lookbackN,
      retest_m: state.retestM,
      retest_tol: 0.005
    };

    const res = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const m = data.metrics;
    const isCycle = (mode === 'cycle_trade');

    // 1. Capital Investido & Patrimônio Final
    document.getElementById('sim-kpi-invested').textContent = `R$ ${m.total_invested.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    document.getElementById('sim-kpi-final').textContent = `R$ ${m.final_portfolio_value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

    // 2. Retorno Estratégia vs Buy & Hold
    const retEl = document.getElementById('sim-kpi-return');
    if (retEl) {
      retEl.textContent = `${m.total_return_pct >= 0 ? '+' : ''}${m.total_return_pct.toFixed(1)}%`;
      retEl.className = `text-base sm:text-lg font-bold font-mono ${m.total_return_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`;
    }
    const bnhSub = document.getElementById('sim-kpi-bnh-sub');
    if (bnhSub) {
      const bnh = m.buy_and_hold_return_pct != null ? m.buy_and_hold_return_pct.toFixed(1) : '0.0';
      const bnhDiff = (m.total_return_pct - (m.buy_and_hold_return_pct || 0)).toFixed(1);
      bnhSub.textContent = `B&H: ${bnh}% (Alpha: ${bnhDiff >= 0 ? '+' : ''}${bnhDiff}%)`;
    }

    // 3. Fator de Lucro & Lucro Líquido
    const pfEl = document.getElementById('sim-kpi-profit-factor');
    if (pfEl) {
      const pf = m.profit_factor != null ? (m.profit_factor >= 999 ? '∞' : m.profit_factor.toFixed(2)) : '0.00';
      pfEl.textContent = pf;
      pfEl.className = `text-base sm:text-lg font-bold font-mono ${parseFloat(pf) >= 1.5 || pf === '∞' ? 'text-amber-400' : (parseFloat(pf) >= 1.0 ? 'text-gray-200' : 'text-rose-400')}`;
    }
    const profitSub = document.getElementById('sim-kpi-profit-sub');
    if (profitSub) {
      profitSub.textContent = `PnL: ${m.total_profit_loss >= 0 ? '+' : ''}R$ ${m.total_profit_loss.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    }

    // 4. Win Rate / Acertos
    const auxEl = document.getElementById('sim-kpi-winrate');
    const tradesSub = document.getElementById('sim-kpi-trades-sub');
    if (auxEl) {
      if (isCycle) {
        const wr = (m.win_rate_pct != null) ? m.win_rate_pct.toFixed(1) : '0.0';
        const wins = m.winning_trades_count || 0;
        const total = (m.winning_trades_count || 0) + (m.losing_trades_count || 0);
        auxEl.textContent = `${wr}%`;
        auxEl.className = `text-base sm:text-lg font-bold font-mono ${parseFloat(wr) >= 50 ? 'text-emerald-400' : 'text-amber-400'}`;
        if (tradesSub) tradesSub.textContent = `${wins}W / ${m.losing_trades_count || 0}L (${m.total_trades_count || 0} ciclos)`;
      } else {
        auxEl.textContent = `${m.alpha_vs_dca_pct >= 0 ? '+' : ''}${m.alpha_vs_dca_pct.toFixed(1)}%`;
        auxEl.className = `text-base sm:text-lg font-bold font-mono ${m.alpha_vs_dca_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`;
        if (tradesSub) tradesSub.textContent = `Aportes: ${m.total_trades_count || 0}`;
      }
    }

    // 5. Drawdown Máximo & Média de Compras
    const ddEl = document.getElementById('sim-kpi-drawdown');
    if (ddEl) {
      ddEl.textContent = `${(m.max_drawdown_pct || 0).toFixed(1)}%`;
    }
    const avgEntriesSub = document.getElementById('sim-kpi-avg-entries-sub');
    if (avgEntriesSub) {
      if (isCycle && m.avg_entries_per_cycle != null) {
        avgEntriesSub.textContent = `Média compras/ciclo: ${m.avg_entries_per_cycle.toFixed(1)}`;
      } else {
        avgEntriesSub.textContent = `Duração média: ${(m.avg_trade_bars || 0).toFixed(0)}b`;
      }
    }

    renderSimulationCurve(data.curve);
    renderSimulationTradesTable(data.trades, mode);

  } catch (err) {
    alert(`Erro na simulação: ${err.message}`);
  } finally {
    hideLoading();
  }
}

async function runOptimizer() {
  const currentMode = (elements.simMode && elements.simMode.value) || 'cycle_trade';
  const isDca = (currentMode === 'accumulation');
  showLoading(isDca ? 'Varrendo estratégias de compra para encontrar a mais lucrativa em DCA...' : 'Varrendo centenas de combinações para encontrar a mais lucrativa...');
  try {
    const tickerInput = resolveTicker((elements.simTicker && elements.simTicker.value.trim().toUpperCase()) || state.currentTicker);
    const capitalVal = parseFloat(document.getElementById('sim-contribution').value) || 1000;
    const simIntervalEl = document.getElementById('sim-interval');
    const selectedInterval = (simIntervalEl && simIntervalEl.value) || state.currentTimeframe || '1d';

    let simPeriod = state.currentPeriod;
    if (selectedInterval === '5m' || selectedInterval === '15m' || selectedInterval === '30m') {
      simPeriod = '60d';
    } else if (['60m', '1h', '2h', '4h', '12h'].includes(selectedInterval)) {
      if (simPeriod === '5y' || simPeriod === 'max') {
        simPeriod = '730d';
      }
    }

    const cycleModeEl = document.getElementById('sim-cycle-mode');
    const selectedCycleMode = (cycleModeEl && cycleModeEl.value) || 'multi_buy';

    const payload = {
      ticker: tickerInput,
      interval: selectedInterval,
      period: simPeriod,
      simulation_mode: currentMode,
      cycle_entry_mode: selectedCycleMode,
      contribution_amount: capitalVal,
      initial_capital: capitalVal,
      min_trades: isDca ? 1 : 2,
      start_date: document.getElementById('sim-start-date').value || null,
      end_date: document.getElementById('sim-end-date').value || null,
      lookback_n: state.lookbackN,
      retest_m: state.retestM,
      retest_tol: 0.005
    };

    const res = await fetch('/api/simulate/optimize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    state.lastChampion = data.champion;

    if (data.champion) {
      const c = data.champion;
      const countEl = document.getElementById('opt-champ-tested-count');
      if (countEl) {
        countEl.textContent = isDca
          ? `${data.total_combinations_tested} estratégias de compra avaliadas`
          : `${data.total_combinations_tested} combinações válidas rankeadas`;
      }

      const modeBadge = document.getElementById('opt-champ-mode-badge');
      if (modeBadge) {
        if (isDca) {
          modeBadge.textContent = 'Acumulação DCA (Fundos)';
        } else {
          modeBadge.textContent = c.cycle_entry_mode === 'single_buy' ? 'Compra Única (1x)' : 'Multi-Buy (Nx)';
        }
      }

      const titleContainer = document.getElementById('opt-champ-title-container') || (document.getElementById('opt-champ-buy-label') && document.getElementById('opt-champ-buy-label').parentElement);
      if (titleContainer) {
        if (isDca) {
          titleContainer.innerHTML = '<span class="text-emerald-400 font-semibold" id="opt-champ-buy-label">' + c.buy_label + '</span> <span class="text-gray-400 font-normal text-xs">(Aportes Periódicos em Fundos)</span>';
        } else {
          titleContainer.innerHTML = '<span class="text-emerald-400 font-semibold" id="opt-champ-buy-label">' + c.buy_label + '</span> <span class="text-gray-400" id="opt-champ-arrow">-&gt;</span> <span class="text-rose-400 font-semibold" id="opt-champ-sell-label">' + (c.sell_label || '-') + '</span>';
        }
      }

      document.getElementById('opt-champ-ret').textContent = `${c.total_return_pct >= 0 ? '+' : ''}${c.total_return_pct.toFixed(1)}%`;
      document.getElementById('opt-champ-pnl').textContent = `${c.net_profit >= 0 ? '+' : ''}R$ ${c.net_profit.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

      const winRateEl = document.getElementById('opt-champ-winrate');
      if (winRateEl) {
        if (isDca) {
          const avgP = c.average_buy_price != null ? `R$ ${c.average_buy_price.toFixed(2)}` : '-';
          winRateEl.textContent = avgP;
          winRateEl.previousElementSibling.textContent = 'Preço Médio de Compra';
        } else {
          winRateEl.textContent = `${c.win_rate_pct.toFixed(1)}% (${c.winning_trades}/${c.closed_trades})`;
          winRateEl.previousElementSibling.textContent = 'Taxa de Acerto (Win Rate)';
        }
      }

      const tradesEl = document.getElementById('opt-champ-trades');
      if (tradesEl) {
        if (isDca) {
          tradesEl.textContent = `${c.closed_trades} aportes`;
          tradesEl.previousElementSibling.textContent = 'Total de Aportes';
        } else {
          tradesEl.textContent = `${c.closed_trades} trades`;
          tradesEl.previousElementSibling.textContent = 'Total de Trades';
        }
      }

      const ddEl = document.getElementById('opt-champ-drawdown');
      if (ddEl) {
        if (isDca && c.total_invested != null) {
          ddEl.textContent = `R$ ${c.total_invested.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
          ddEl.previousElementSibling.textContent = 'Total Aportado';
        } else {
          ddEl.textContent = `${c.max_drawdown_pct.toFixed(1)}%`;
          ddEl.previousElementSibling.textContent = 'Max Drawdown';
        }
      }
    }

    renderTopCombinationsTable(data.top_combinations || [], isDca);

    if (elements.simOptimizerContainer) {
      elements.simOptimizerContainer.classList.remove('hidden');
      elements.simOptimizerContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

  } catch (err) {
    alert(`Erro na otimização: ${err.message}`);
  } finally {
    hideLoading();
  }
}

function renderTopCombinationsTable(combos, isDca = false) {
  if (!elements.simTopCombosTableBody) return;
  elements.simTopCombosTableBody.innerHTML = '';

  const tableHeader = elements.simTopCombosTableBody.closest('table').querySelector('thead tr');
  if (tableHeader) {
    if (isDca) {
      tableHeader.innerHTML = `
        <th class="px-2.5 py-2 text-center">Rank</th>
        <th class="px-2.5 py-2">Estratégia de Compra (Fundo)</th>
        <th class="px-2.5 py-2 text-center">Aportes</th>
        <th class="px-2.5 py-2 font-mono">Total Aportado</th>
        <th class="px-2.5 py-2 font-mono">Preço Médio</th>
        <th class="px-2.5 py-2 font-mono">Retorno (%)</th>
        <th class="px-2.5 py-2 font-mono">Patrimônio Final</th>
        <th class="px-2.5 py-2 font-mono">Lucro Líquido</th>
        <th class="px-2.5 py-2 text-center">Ação</th>
      `;
    } else {
      tableHeader.innerHTML = `
        <th class="px-2.5 py-2 text-center">Rank</th>
        <th class="px-2.5 py-2">Estratégia de Compra (Entrada)</th>
        <th class="px-2.5 py-2">Estratégia de Venda (Saída)</th>
        <th class="px-2.5 py-2 text-center">Trades</th>
        <th class="px-2.5 py-2 text-center font-mono">Win Rate</th>
        <th class="px-2.5 py-2 font-mono">Retorno (%)</th>
        <th class="px-2.5 py-2 font-mono">Lucro Líquido</th>
        <th class="px-2.5 py-2 font-mono text-center">Max Drawdown</th>
        <th class="px-2.5 py-2 text-center">Ação</th>
      `;
    }
  }

  if (!combos || combos.length === 0) {
    elements.simTopCombosTableBody.innerHTML = `<tr><td colspan="9" class="text-center py-4 text-gray-500">${isDca ? 'Nenhuma estratégia com aportes encontrada no período.' : 'Nenhuma combinação com no mínimo 2 trades encontrada no período.'}</td></tr>`;
    return;
  }

  combos.forEach(item => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-fintech-surface-hover';

    const rankBadge = item.rank === 1 ? ' 1º' : (item.rank === 2 ? ' 2º' : (item.rank === 3 ? ' 3º' : `#${item.rank}`));
    const retClass = item.total_return_pct >= 0 ? 'text-emerald-400' : 'text-rose-400';
    const pnlClass = item.net_profit >= 0 ? 'text-emerald-400' : 'text-rose-400';

    if (isDca) {
      tr.innerHTML = `
        <td class="px-2.5 py-2 text-center font-bold text-amber-400">${rankBadge}</td>
        <td class="px-2.5 py-2 text-emerald-300 font-medium font-sans">${item.buy_label}</td>
        <td class="px-2.5 py-2 text-center text-white font-bold">${item.closed_trades}</td>
        <td class="px-2.5 py-2 font-mono text-gray-300">R$ ${(item.total_invested || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
        <td class="px-2.5 py-2 font-mono text-amber-300">R$ ${(item.average_buy_price || 0).toFixed(2)}</td>
        <td class="px-2.5 py-2 font-bold ${retClass}">${item.total_return_pct >= 0 ? '+' : ''}${item.total_return_pct.toFixed(1)}%</td>
        <td class="px-2.5 py-2 font-bold text-cyan-300 font-mono">R$ ${(item.final_equity || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
        <td class="px-2.5 py-2 font-bold ${pnlClass}">R$ ${item.net_profit.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
        <td class="px-2.5 py-2 text-center">
          <button class="btn-test-combo bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-[10px] px-2.5 py-1 rounded transition shadow"
            data-buy="${item.buy_sub_id}" data-sell="${item.sell_sub_id || ''}">
             Testar
          </button>
        </td>
      `;
    } else {
      tr.innerHTML = `
        <td class="px-2.5 py-2 text-center font-bold text-amber-400">${rankBadge}</td>
        <td class="px-2.5 py-2 text-emerald-300 font-medium font-sans">${item.buy_label}</td>
        <td class="px-2.5 py-2 text-rose-300 font-medium font-sans">${item.sell_label}</td>
        <td class="px-2.5 py-2 text-center text-white font-bold">${item.closed_trades}</td>
        <td class="px-2.5 py-2 text-center text-gray-200">${item.win_rate_pct.toFixed(1)}%</td>
        <td class="px-2.5 py-2 font-bold ${retClass}">${item.total_return_pct >= 0 ? '+' : ''}${item.total_return_pct.toFixed(1)}%</td>
        <td class="px-2.5 py-2 font-bold ${pnlClass}">R$ ${item.net_profit.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
        <td class="px-2.5 py-2 text-center text-rose-400">${item.max_drawdown_pct.toFixed(1)}%</td>
        <td class="px-2.5 py-2 text-center">
          <button class="btn-test-combo bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-[10px] px-2.5 py-1 rounded transition shadow"
            data-buy="${item.buy_sub_id}" data-sell="${item.sell_sub_id}">
             Testar
          </button>
        </td>
      `;
    }
    elements.simTopCombosTableBody.appendChild(tr);
  });

  // Attach click listeners to " Testar" buttons
  elements.simTopCombosTableBody.querySelectorAll('.btn-test-combo').forEach(btn => {
    btn.addEventListener('click', () => {
      const buyId = btn.getAttribute('data-buy');
      const sellId = btn.getAttribute('data-sell');
      if (elements.simBuyStrategy) elements.simBuyStrategy.value = buyId;
      if (elements.simSellStrategy && sellId) elements.simSellStrategy.value = sellId;
      runSimulation();
    });
  });
}

function renderSimulationTradesTable(trades, mode) {
  const tbody = document.getElementById('sim-trades-table-body');
  const countBadge = document.getElementById('sim-trades-count-badge');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (!trades || trades.length === 0) {
    tbody.innerHTML = `<tr><td colspan="11" class="text-center py-4 text-gray-500">Nenhum trade realizado com as estratégias selecionadas no período.</td></tr>`;
    if (countBadge) countBadge.textContent = '0 trades';
    return;
  }

  if (countBadge) countBadge.textContent = `${trades.length} trades`;

  trades.forEach(t => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-fintech-surface-hover';

    if (mode === 'cycle_trade') {
      const isWin = (t.return_pct || 0) > 0;
      const isLoss = (t.return_pct || 0) < 0;
      const retClass = isWin ? 'text-emerald-400' : (isLoss ? 'text-rose-400' : 'text-gray-300');
      const pnlClass = (t.profit_loss || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400';
      const isOpen = (t.status === 'ABERTO');
      const numBuys = t.num_entries || (t.buy_entries ? t.buy_entries.length : 1);
      const avgPrice = t.average_buy_price || t.buy_price || 0;

      let statusBadge = '';
      if (isOpen) {
        statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40">EM ABERTO</span>';
      } else if (isWin) {
        statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">LUCRO</span>';
      } else {
        statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40">PREJUÍZO</span>';
      }

      tr.innerHTML = `
        <td class="px-2.5 py-2 text-center text-gray-400 font-bold">${t.trade_id || '-'}</td>
        <td class="px-2.5 py-2 text-cyan-300 font-medium font-sans">${t.buy_strategy || '-'}</td>
        <td class="px-2.5 py-2 text-center font-bold ${numBuys > 1 ? 'text-amber-400' : 'text-gray-300'}">
          <span class="px-1.5 py-0.5 rounded ${numBuys > 1 ? 'bg-amber-500/20 border border-amber-500/40' : 'bg-gray-800'} text-[10px]">
            ${numBuys}x
          </span>
        </td>
        <td class="px-2.5 py-2 text-gray-300">${t.buy_date || '-'}</td>
        <td class="px-2.5 py-2 text-white font-semibold">R$ ${avgPrice.toFixed(2)}</td>
        <td class="px-2.5 py-2 text-rose-300 font-medium font-sans">${t.sell_strategy || '-'}</td>
        <td class="px-2.5 py-2 text-gray-300">${t.sell_date || '-'}</td>
        <td class="px-2.5 py-2 text-white font-semibold">${t.sell_price ? 'R$ ' + t.sell_price.toFixed(2) : '-'}</td>
        <td class="px-2.5 py-2 text-center text-gray-300">${t.duration_bars != null ? t.duration_bars + 'b' : '-'}</td>
        <td class="px-2.5 py-2 font-bold ${retClass}">${(t.return_pct || 0) >= 0 ? '+' : ''}${(t.return_pct || 0).toFixed(1)}%</td>
        <td class="px-2.5 py-2 font-bold ${pnlClass}">${(t.profit_loss || 0) >= 0 ? '+' : ''}R$ ${(t.profit_loss || 0).toFixed(2)}</td>
        <td class="px-2.5 py-2 text-center">${statusBadge}</td>
      `;
    } else {
      tr.innerHTML = `
        <td class="px-2.5 py-2 text-center text-gray-400">-</td>
        <td class="px-2.5 py-2 text-cyan-300 font-medium font-sans">${t.strategy || '-'}</td>
        <td class="px-2.5 py-2 text-center text-gray-300 font-bold">1x</td>
        <td class="px-2.5 py-2 text-gray-300">${t.date || '-'}</td>
        <td class="px-2.5 py-2 text-white font-semibold">R$ ${(t.execution_price || 0).toFixed(2)}</td>
        <td class="px-2.5 py-2 text-gray-500">-</td>
        <td class="px-2.5 py-2 text-gray-500">-</td>
        <td class="px-2.5 py-2 text-gray-500">-</td>
        <td class="px-2.5 py-2 text-center text-gray-400">1b</td>
        <td class="px-2.5 py-2 text-gray-300">-</td>
        <td class="px-2.5 py-2 text-white">R$ ${(t.amount_invested || 0).toFixed(2)}</td>
        <td class="px-2.5 py-2 text-center"><span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400">APORTE</span></td>
      `;
    }

    tbody.appendChild(tr);

    // If multi-buy entries exist, append collapsible/informative sub-row
    if (mode === 'cycle_trade' && t.buy_entries && t.buy_entries.length > 1) {
      const subTr = document.createElement('tr');
      subTr.className = 'bg-fintech-surface/40 text-[10px] text-gray-400';
      const entriesDetail = t.buy_entries.map(be => `
        <span class="inline-flex items-center gap-1 bg-fintech-bg px-2 py-0.5 rounded border border-fintech-border/60">
          <span class="text-cyan-400 font-bold">#${be.entry_id}</span>
          <span>${be.date}: R$ ${be.price.toFixed(2)} (${be.shares.toFixed(1)} cotas)</span>
        </span>
      `).join(' ');

      subTr.innerHTML = `
        <td colspan="12" class="px-4 py-1.5 font-mono">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-amber-400 font-semibold font-sans">↳ Sub-entradas acumuladas:</span>
            ${entriesDetail}
          </div>
        </td>
      `;
      tbody.appendChild(subTr);
    }
  });
}

function renderSimulationCurve(curve) {
  if (!curve || curve.length === 0) return;

  const dates = curve.map(c =>c.date);
  const invested = curve.map(c =>c.total_invested);
  const portfolio = curve.map(c =>c.portfolio_value);

  const tracePortfolio = {
    x: dates,
    y: portfolio,
    mode: 'lines',
    name: 'Valor Patrimonial (Estratégia)',
    line: { color: '#00F0FF', width: 2.5 }
  };

  const traceInvested = {
    x: dates,
    y: invested,
    mode: 'lines',
    name: 'Capital Base / Investido',
    line: { color: 'rgba(255, 255, 255, 0.4)', dash: 'dash', width: 1.5 }
  };

  const layout = {
    margin: { l: 60, r: 30, t: 20, b: 40 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#F0F4F8', size: 11 },
    xaxis: { gridcolor: '#262B38' },
    yaxis: { gridcolor: '#262B38', title: 'Valor (R$)' },
    legend: { x: 0.05, y: 0.95, bgcolor: 'rgba(21, 25, 36, 0.8)' }
  };

  Plotly.newPlot('plot-simulation-curve', [tracePortfolio, traceInvested], layout, { responsive: true, displayModeBar: false });
}

// Helpers
function showLoading(msg = 'Carregando...') {
  elements.loadingText.textContent = msg;
  elements.loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
  elements.loadingOverlay.classList.add('hidden');
}

// UI: Radar Strategy Multi-Select Dropdown Filter

// UI: Setup Radar Table Column Sorting
function setupRadarTableSorting() {
  const thN = document.getElementById('th-sort-n');
  const thWin = document.getElementById('th-sort-winrate');
  const iconN = document.getElementById('sort-icon-n');
  const iconWin = document.getElementById('sort-icon-winrate');

  function updateIcons() {
    if (iconN) iconN.textContent = state.radarSortField === 'historical_n' ? (state.radarSortOrder === 'asc' ? '▲' : '▼') : '↕';
    if (iconWin) iconWin.textContent = state.radarSortField === 'historical_win_rate' ? (state.radarSortOrder === 'asc' ? '▲' : '▼') : '↕';
    if (iconN) iconN.className = state.radarSortField === 'historical_n' ? 'text-[10px] text-cyan-400 font-bold' : 'text-[10px] text-gray-500';
    if (iconWin) iconWin.className = state.radarSortField === 'historical_win_rate' ? 'text-[10px] text-cyan-400 font-bold' : 'text-[10px] text-gray-500';
  }

  if (thN) {
    thN.addEventListener('click', () => {
      if (state.radarSortField === 'historical_n') {
        state.radarSortOrder = state.radarSortOrder === 'desc' ? 'asc' : 'desc';
      } else {
        state.radarSortField = 'historical_n';
        state.radarSortOrder = 'desc';
      }
      updateIcons();
      if (state.lastRadarPage) {
        renderRadarTable(state.lastRadarPage);
      }
    });
  }

  if (thWin) {
    thWin.addEventListener('click', () => {
      if (state.radarSortField === 'historical_win_rate') {
        state.radarSortOrder = state.radarSortOrder === 'desc' ? 'asc' : 'desc';
      } else {
        state.radarSortField = 'historical_win_rate';
        state.radarSortOrder = 'desc';
      }
      updateIcons();
      if (state.lastRadarPage) {
        renderRadarTable(state.lastRadarPage);
      }
    });
  }
}

async function setupRadarStrategyFilter() {
  const toggleBtn = document.getElementById('btn-radar-strat-toggle');
  const menu = document.getElementById('radar-strat-menu');
  const container = document.getElementById('radar-strat-checkbox-container');
  const badge = document.getElementById('radar-strat-badge');
  const clearBtn = document.getElementById('btn-clear-radar-strat');
  if (!toggleBtn || !menu || !container) return;

  toggleBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    menu.classList.toggle('hidden');
  });

  document.addEventListener('click', (e) => {
    if (!menu.contains(e.target) && !toggleBtn.contains(e.target)) {
      menu.classList.add('hidden');
    }
  });

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      state.radarStrategies.clear();
      updateRadarStratCheckboxes();
      state.radarPage = 1;
      loadRadarData(false, state.radarActiveCategory);
    });
  }

  // Fetch strategy catalog from server
  try {
    const res = await fetch('/api/strategies');
    if (!res.ok) return;
    const catData = await res.json();
    window._strategyCatalog = catData;
    renderRadarStratMenu();
  } catch (err) {
    console.error('Error fetching strategies catalog for radar filter:', err);
  }
}

function renderRadarStratMenu() {
  const container = document.getElementById('radar-strat-checkbox-container');
  if (!container || !window._strategyCatalog) return;
  container.innerHTML = '';

  const activeDir = state.activeDirection || 'BUY';

  // Flatten strategies matching direction
  const strats = [];
  Object.values(window._strategyCatalog).forEach(grp => {
    if (activeDir !== 'BOTH' && grp.direction !== activeDir) return;
    (grp.strategies || []).forEach(st => {
      strats.push(st);
    });
  });

  if (strats.length === 0) {
    container.innerHTML = '<div class="text-gray-500 py-1">Nenhuma estratégia disponível.</div>';
    return;
  }

  strats.forEach(st => {
    const label = document.createElement('label');
    label.className = 'flex items-center space-x-2 cursor-pointer hover:text-white text-gray-300 py-0.5';
    const isChecked = state.radarStrategies.has(st.id);
    label.innerHTML = `
      <input type="checkbox" class="radar-strat-cb rounded bg-fintech-bg border-fintech-border text-fintech-cyan" data-id="${st.id}" ${isChecked ? 'checked' : ''}>
      <span class="truncate">${st.label}</span>
    `;
    const cb = label.querySelector('input');
    cb.addEventListener('change', () => {
      if (cb.checked) {
        state.radarStrategies.add(st.id);
      } else {
        state.radarStrategies.delete(st.id);
      }
      updateRadarStratBadge();
      state.radarPage = 1;
      loadRadarData(false, state.radarActiveCategory);
    });
    container.appendChild(label);
  });
  updateRadarStratBadge();
}

function updateRadarStratBadge() {
  const badge = document.getElementById('radar-strat-badge');
  if (!badge) return;
  const count = state.radarStrategies.size;
  if (count > 0) {
    badge.textContent = count;
    badge.classList.remove('hidden');
  } else {
    badge.classList.add('hidden');
  }
}

function updateRadarStratCheckboxes() {
  document.querySelectorAll('.radar-strat-cb').forEach(cb => {
    const id = cb.getAttribute('data-id');
    cb.checked = state.radarStrategies.has(id);
  });
  updateRadarStratBadge();
}


// =========================================================
// TAB 5: GESTOR E SIMULADOR MULTIATIVOS DE CARTEIRA (016)
// =========================================================
const PORTFOLIO_STORAGE_KEY = 'market_engine_portfolio_v1';

state.portfolioState = {
  availableCash: 10000.0,
  holdings: [],
  universeCategory: 'featured',
  customTickers: '',
  interval: '1d',
  period: '2y',
  maxWeightPct: 25.0,
  lastAdviseResponse: null,
  lastSimulateResponse: null,
  previousBackup: null,
  b3TotalIncome: 0,
  b3MonthlyIncome: [],
  b3Filename: null,
};

function loadPortfolioStorage() {
  try {
    const raw = localStorage.getItem(PORTFOLIO_STORAGE_KEY);
    if (!raw) return;
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === 'object') {
      if (parsed.availableCash !== undefined) state.portfolioState.availableCash = Number(parsed.availableCash) || 0;
      if (Array.isArray(parsed.holdings)) state.portfolioState.holdings = parsed.holdings;
      if (parsed.universeCategory) state.portfolioState.universeCategory = parsed.universeCategory;
      if (parsed.customTickers !== undefined) state.portfolioState.customTickers = String(parsed.customTickers);
      if (parsed.interval) state.portfolioState.interval = parsed.interval;
      if (parsed.period) state.portfolioState.period = parsed.period;
      if (parsed.maxWeightPct !== undefined) state.portfolioState.maxWeightPct = Number(parsed.maxWeightPct) || 25;
      if (parsed.previousBackup && typeof parsed.previousBackup === 'object') state.portfolioState.previousBackup = parsed.previousBackup;
      if (parsed.b3TotalIncome !== undefined) state.portfolioState.b3TotalIncome = Number(parsed.b3TotalIncome) || 0;
      if (Array.isArray(parsed.b3MonthlyIncome)) state.portfolioState.b3MonthlyIncome = parsed.b3MonthlyIncome;
      if (parsed.b3Filename !== undefined) state.portfolioState.b3Filename = parsed.b3Filename;
    }
  } catch (err) {
    console.warn('Erro ao carregar carteira do localStorage:', err);
  }
}

function savePortfolioStorage() {
  try {
    const payload = {
      availableCash: state.portfolioState.availableCash,
      holdings: state.portfolioState.holdings,
      universeCategory: state.portfolioState.universeCategory,
      customTickers: state.portfolioState.customTickers,
      interval: state.portfolioState.interval,
      period: state.portfolioState.period,
      maxWeightPct: state.portfolioState.maxWeightPct,
      previousBackup: state.portfolioState.previousBackup,
      b3TotalIncome: state.portfolioState.b3TotalIncome || 0,
      b3MonthlyIncome: state.portfolioState.b3MonthlyIncome || [],
      b3Filename: state.portfolioState.b3Filename || null,
    };
    localStorage.setItem(PORTFOLIO_STORAGE_KEY, JSON.stringify(payload));
  } catch (err) {
    console.warn('Erro ao salvar carteira no localStorage:', err);
  }
}

function syncPortfolioInputsFromState() {
  const cashEl = document.getElementById('portfolio-cash-input');
  const maxWEl = document.getElementById('portfolio-max-weight-input');
  const univEl = document.getElementById('portfolio-universe-select');
  const customWrap = document.getElementById('portfolio-custom-tickers-wrapper');
  const customEl = document.getElementById('portfolio-custom-tickers-input');
  const intEl = document.getElementById('portfolio-interval-select');
  const perEl = document.getElementById('portfolio-period-select');

  if (cashEl) cashEl.value = state.portfolioState.availableCash;
  if (maxWEl) maxWEl.value = state.portfolioState.maxWeightPct;
  if (univEl) univEl.value = state.portfolioState.universeCategory;
  if (customEl) customEl.value = state.portfolioState.customTickers;
  if (intEl) intEl.value = state.portfolioState.interval;
  if (perEl) perEl.value = state.portfolioState.period;
  if (customWrap) {
    if (state.portfolioState.universeCategory === 'custom') customWrap.classList.remove('hidden');
    else customWrap.classList.add('hidden');
  }
}

function readPortfolioInputsToState() {
  const cashEl = document.getElementById('portfolio-cash-input');
  const maxWEl = document.getElementById('portfolio-max-weight-input');
  const univEl = document.getElementById('portfolio-universe-select');
  const customEl = document.getElementById('portfolio-custom-tickers-input');
  const intEl = document.getElementById('portfolio-interval-select');
  const perEl = document.getElementById('portfolio-period-select');

  if (cashEl) state.portfolioState.availableCash = Math.max(0, Number(cashEl.value) || 0);
  if (maxWEl) state.portfolioState.maxWeightPct = Math.min(100, Math.max(5, Number(maxWEl.value) || 25));
  if (univEl) state.portfolioState.universeCategory = univEl.value || 'featured';
  if (customEl) state.portfolioState.customTickers = customEl.value || '';
  if (intEl) state.portfolioState.interval = intEl.value || '1d';
  if (perEl) state.portfolioState.period = perEl.value || '2y';

  savePortfolioStorage();
}

function renderPortfolioHoldingsEditor() {
  const tbody = document.getElementById('portfolio-holdings-list');
  if (!tbody) return;
  tbody.innerHTML = '';

  const holdings = state.portfolioState.holdings || [];
  if (holdings.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="px-3 py-3 text-center text-gray-500 font-sans text-[11px]">
          Nenhuma posição cadastrada (100% em Caixa). Adicione ativos acima se já possuir carteira montada.
        </td>
      </tr>
    `;
    return;
  }

  holdings.forEach((h, idx) => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-fintech-surface-hover';
    const cost = (Number(h.shares) || 0) * (Number(h.average_buy_price) || 0);
    const name = stripCorporateSuffix(getAssetName(h.ticker));
    tr.innerHTML = `
      <td class="px-2.5 py-1.5 font-bold text-white">
        ${name} <span class="text-[10px] text-gray-400">(${h.ticker})</span>
      </td>
      <td class="px-2.5 py-1.5 text-amber-300 font-bold">${Number(h.shares).toLocaleString('pt-BR')}</td>
      <td class="px-2.5 py-1.5 text-gray-200">R$ ${Number(h.average_buy_price).toFixed(2)}</td>
      <td class="px-2.5 py-1.5 text-cyan-300">R$ ${cost.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
      <td class="px-2.5 py-1.5 text-right">
        <button class="btn-remove-holding text-rose-400 hover:text-rose-300 text-xs font-bold px-1.5 cursor-pointer" data-idx="${idx}" title="Remover ativo">✕</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll('.btn-remove-holding').forEach(btn => {
    btn.addEventListener('click', () => {
      const i = parseInt(btn.getAttribute('data-idx'), 10);
      if (!isNaN(i) && state.portfolioState.holdings[i]) {
        const item = state.portfolioState.holdings[i];
        if (confirm(`Deseja realmente remover o ativo ${item.ticker} da sua carteira?`)) {
          // Backup for undo
          state.portfolioState.previousBackup = {
            holdings: JSON.parse(JSON.stringify(state.portfolioState.holdings || [])),
            availableCash: state.portfolioState.availableCash,
          };
          state.portfolioState.holdings.splice(i, 1);
          savePortfolioStorage();
          renderPortfolioHoldingsEditor();
          updateUndoButtonVisibility();
          showToastNotification(`Ativo ${item.ticker} removido.`, true, undoAppliedPortfolioOrders);
        }
      }
    });
  });
}

function setupPortfolioTab() {
  loadPortfolioStorage();
  syncPortfolioInputsFromState();
  renderPortfolioHoldingsEditor();

  const univEl = document.getElementById('portfolio-universe-select');
  if (univEl) {
    univEl.addEventListener('change', () => {
      readPortfolioInputsToState();
      syncPortfolioInputsFromState();
    });
  }

  ['portfolio-cash-input', 'portfolio-max-weight-input', 'portfolio-custom-tickers-input', 'portfolio-interval-select', 'portfolio-period-select'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('change', () => readPortfolioInputsToState());
    }
  });

  const btnAdd = document.getElementById('btn-portfolio-add-holding');
  if (btnAdd) {
    btnAdd.addEventListener('click', () => {
      const tEl = document.getElementById('portfolio-add-ticker');
      const sEl = document.getElementById('portfolio-add-shares');
      const pEl = document.getElementById('portfolio-add-avgprice');
      const ticker = resolveTicker((tEl ? tEl.value : '').trim().toUpperCase());
      const shares = Number(sEl ? sEl.value : 0);
      const avgPrice = Number(pEl ? pEl.value : 0);
      if (!ticker || shares <= 0 || avgPrice <= 0) return;

      const existingIdx = state.portfolioState.holdings.findIndex(x => x.ticker.toUpperCase() === ticker);
      if (existingIdx >= 0) {
        const prev = state.portfolioState.holdings[existingIdx];
        const totShares = Number(prev.shares) + shares;
        const newAvg = ((Number(prev.shares) * Number(prev.average_buy_price)) + (shares * avgPrice)) / totShares;
        state.portfolioState.holdings[existingIdx] = {
          ticker,
          shares: Number(totShares.toFixed(4)),
          average_buy_price: Number(newAvg.toFixed(4)),
        };
      } else {
        state.portfolioState.holdings.push({
          ticker,
          shares: Number(shares.toFixed(4)),
          average_buy_price: Number(avgPrice.toFixed(4)),
        });
      }
      if (tEl) tEl.value = '';
      if (sEl) sEl.value = '';
      if (pEl) pEl.value = '';
      savePortfolioStorage();
      renderPortfolioHoldingsEditor();
    });
  }

  const btnClear = document.getElementById('btn-portfolio-clear-holdings');
  if (btnClear) {
    btnClear.addEventListener('click', () => {
      state.portfolioState.holdings = [];
      savePortfolioStorage();
      renderPortfolioHoldingsEditor();
    });
  }

  const btnRun = document.getElementById('btn-run-portfolio');
  if (btnRun) {
    btnRun.addEventListener('click', () => {
      runPortfolioAdviseAndSimulate();
    });
  }

  const btnApplyOrders = document.getElementById('btn-apply-portfolio-orders');
  if (btnApplyOrders) {
    btnApplyOrders.addEventListener('click', () => {
      openPreFlightOrderModal();
    });
  }

  // Pre-flight confirmation modal listeners
  const btnModalClose = document.getElementById('btn-modal-close');
  const btnModalCancel = document.getElementById('btn-modal-cancel');
  const btnModalConfirm = document.getElementById('btn-modal-confirm');
  if (btnModalClose) btnModalClose.addEventListener('click', closePreFlightOrderModal);
  if (btnModalCancel) btnModalCancel.addEventListener('click', closePreFlightOrderModal);
  if (btnModalConfirm) btnModalConfirm.addEventListener('click', applyRecommendedPortfolioOrders);

  // Undo Apply Orders Button
  const btnUndo = document.getElementById('btn-portfolio-undo-apply');
  if (btnUndo) {
    btnUndo.addEventListener('click', () => {
      undoAppliedPortfolioOrders();
    });
  }
  updateUndoButtonVisibility();

  // CSV / B3 Import Button and Multi-File Input
  const btnImportCsv = document.getElementById('btn-portfolio-import-csv');
  const fileInputCsv = document.getElementById('portfolio-csv-file-input');

  if (btnImportCsv && fileInputCsv) {
    btnImportCsv.addEventListener('click', () => {
      fileInputCsv.value = '';
      fileInputCsv.click();
    });

    fileInputCsv.addEventListener('change', async (e) => {
      const files = Array.from(e.target.files || []);
      if (files.length === 0) return;

      const hasExcel = files.some(f => f.name.endsWith('.xlsx') || f.name.endsWith('.xls'));
      if (hasExcel || files.length > 1) {
        await uploadMultipleB3Spreadsheets(files);
      } else {
        importPortfolioHoldingsFromCsv(files[0]);
      }
    });
  }
}

async function uploadMultipleB3Spreadsheets(files) {
  const count = files.length;
  showLoading(`Processando ${count} ${count === 1 ? 'planilha da B3' : 'planilhas da B3 combinadas'}...`);
  try {
    const formData = new FormData();
    files.forEach(f => {
      formData.append('files', f);
    });

    const res = await fetch('/api/b3/parse', {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      alert(errData.detail || 'Erro ao processar planilhas da B3.');
      return;
    }

    const data = await res.json();
    applyB3ParsedResult(data);
    showToastNotification(`${count} ${count === 1 ? 'planilha processada' : 'planilhas combinadas'} com sucesso! (${data.holdings.length} ativos em custódia)`, false);
  } catch (err) {
    console.error('Erro ao enviar planilhas B3:', err);
    alert('Erro ao processar arquivos da B3.');
  } finally {
    hideLoading();
  }
}

function applyB3ParsedResult(data) {
  if (!data || !Array.isArray(data.holdings)) return;

  // Backup current state for undo
  state.portfolioState.previousBackup = {
    holdings: JSON.parse(JSON.stringify(state.portfolioState.holdings || [])),
    availableCash: state.portfolioState.availableCash,
  };

  const importedHoldings = data.holdings.map(h => ({
    ticker: h.ticker,
    shares: Number(h.shares),
    average_buy_price: Number(h.average_buy_price),
  }));

  state.portfolioState.holdings = importedHoldings;
  state.portfolioState.b3TotalIncome = Number(data.total_income) || 0;
  state.portfolioState.b3MonthlyIncome = Array.isArray(data.monthly_income) ? data.monthly_income : [];
  state.portfolioState.b3Filename = data.filename || null;

  savePortfolioStorage();
  renderPortfolioHoldingsEditor();
  updateUndoButtonVisibility();
  runPortfolioAdviseAndSimulate();

  // If on overview, update dashboard
  if (typeof renderOverviewDashboard === 'function') {
    renderOverviewDashboard();
  }

  // Update chart price line if current ticker is in holdings
  updateTradingViewAveragePriceLine();
}

function updateUndoButtonVisibility() {
  const btnUndo = document.getElementById('btn-portfolio-undo-apply');
  if (!btnUndo) return;
  if (state.portfolioState.previousBackup) {
    btnUndo.classList.remove('hidden');
  } else {
    btnUndo.classList.add('hidden');
  }
}

function undoAppliedPortfolioOrders() {
  const backup = state.portfolioState.previousBackup;
  if (!backup) return;

  state.portfolioState.holdings = Array.isArray(backup.holdings) ? JSON.parse(JSON.stringify(backup.holdings)) : [];
  state.portfolioState.availableCash = Number(backup.availableCash) || 0;
  state.portfolioState.previousBackup = null;

  syncPortfolioInputsFromState();
  savePortfolioStorage();
  renderPortfolioHoldingsEditor();
  updateUndoButtonVisibility();
  runPortfolioAdviseAndSimulate();
}

function importPortfolioHoldingsFromCsv(file) {
  const reader = new FileReader();
  reader.onload = function(evt) {
    try {
      const text = evt.target.result;
      const lines = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
      if (lines.length === 0) return;

      const delimiter = lines[0].includes(';') ? ';' : ',';
      let startIndex = 0;
      const firstLineLower = lines[0].toLowerCase();
      if (firstLineLower.includes('ticker') || firstLineLower.includes('ativo') || firstLineLower.includes('código') || firstLineLower.includes('codigo') || firstLineLower.includes('papel') || firstLineLower.includes('symbol')) {
        startIndex = 1;
      }

      // Backup current state for undo before importing
      state.portfolioState.previousBackup = {
        holdings: JSON.parse(JSON.stringify(state.portfolioState.holdings || [])),
        availableCash: state.portfolioState.availableCash,
      };

      const importedHoldings = [];
      for (let i = startIndex; i < lines.length; i++) {
        const rawCols = lines[i].split(delimiter).map(c => c.trim().replace(/^["']|["']$/g, ''));
        if (rawCols.length < 2) continue;

        let rawTicker = rawCols[0].toUpperCase();
        let rawShares = 0;
        let rawPrice = 0;

        if (rawCols.length >= 3) {
          rawShares = Number(rawCols[1].replace(',', '.')) || 0;
          rawPrice = Number(rawCols[2].replace(',', '.')) || 0;
        } else {
          rawShares = Number(rawCols[1].replace(',', '.')) || 0;
        }

        const resolved = resolveTicker(rawTicker);
        if (resolved && rawShares > 0) {
          importedHoldings.push({
            ticker: resolved,
            shares: Number(rawShares.toFixed(4)),
            average_buy_price: Number(Math.max(0.01, rawPrice).toFixed(4)),
          });
        }
      }

      if (importedHoldings.length > 0) {
        state.portfolioState.holdings = importedHoldings;
        savePortfolioStorage();
        renderPortfolioHoldingsEditor();
        updateUndoButtonVisibility();
        runPortfolioAdviseAndSimulate();
      } else {
        alert('Nenhum ativo válido encontrado no CSV. Formato esperado: Ticker, Quantidade, Preço Médio (Ex: PETR4.SA, 100, 35.50)');
      }
    } catch (err) {
      console.error('Erro ao processar CSV de carteira:', err);
      alert('Erro ao processar arquivo CSV.');
    }
  };
  reader.readAsText(file);
}

function getActionBadgeHtml(actionType, actionLabel) {
  if (actionType === 'BUY') {
    return `<span class="px-2 py-0.5 rounded text-[10px] font-extrabold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">🟢 ${actionLabel}</span>`;
  }
  if (actionType === 'SELL_FULL') {
    return `<span class="px-2 py-0.5 rounded text-[10px] font-extrabold bg-rose-500/20 text-rose-400 border border-rose-500/40">🔴 ${actionLabel}</span>`;
  }
  if (actionType === 'SELL_PARTIAL_REBALANCE') {
    return `<span class="px-2 py-0.5 rounded text-[10px] font-extrabold bg-amber-500/20 text-amber-400 border border-amber-500/40">⚖️ ${actionLabel}</span>`;
  }
  if (actionType === 'ROTATE_OUT' || actionType === 'ROTATE_IN') {
    return `<span class="px-2 py-0.5 rounded text-[10px] font-extrabold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">🔄 ${actionLabel}</span>`;
  }
  return `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-700/50 text-gray-300 border border-gray-600">⏸️ ${actionLabel}</span>`;
}

function renderPortfolioAdviseSection(data) {
  state.portfolioState.lastAdviseResponse = data;
  const eqEl = document.getElementById('advise-total-equity');
  const cashTransEl = document.getElementById('advise-cash-transition');
  const btnApply = document.getElementById('btn-apply-portfolio-orders');
  const tbody = document.getElementById('portfolio-recommendations-tbody');

  if (eqEl) {
    eqEl.textContent = `R$ ${(Number(data.total_portfolio_equity) || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
  if (cashTransEl) {
    const cBefore = (Number(data.current_cash) || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const cAfter = (Number(data.projected_cash_after) || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    cashTransEl.textContent = `R$ ${cBefore} → R$ ${cAfter}`;
  }

  if (!tbody) return;
  tbody.innerHTML = '';

  const recs = data.recommendations || [];
  const hasExecutableOrders = recs.some(r => r.action_type !== 'HOLD' && Math.abs(Number(r.recommended_shares_delta) || 0) > 0);
  if (btnApply) {
    if (hasExecutableOrders) btnApply.classList.remove('hidden');
    else btnApply.classList.add('hidden');
  }

  if (recs.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="10" class="px-4 py-6 text-center text-gray-400 font-mono">
          Nenhuma oportunidade ativa em zona de compra no momento. Recomendação: manter saldo em Caixa aguardando novo fundo estatístico.
        </td>
      </tr>
    `;
    return;
  }

  recs.forEach(r => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-fintech-surface-hover';

    const delta = Number(r.recommended_shares_delta) || 0;
    const deltaSign = delta > 0 ? '+' : '';
    const deltaColor = delta > 0 ? 'text-emerald-400' : (delta < 0 ? 'text-rose-400' : 'text-gray-400');
    const score = Number(r.potential_score) || 0;
    const scoreBarColor = score >= 75 ? 'bg-emerald-400' : (score >= 55 ? 'bg-cyan-400' : 'bg-amber-400');

    let timingDot = '<span class="inline-block w-2.5 h-2.5 rounded-full bg-rose-400" title="Atrasado"></span>';
    if (r.timing_category === 'IDEAL') {
      timingDot = '<span class="inline-block w-2.5 h-2.5 rounded-full bg-emerald-400 ring-2 ring-emerald-500/30" title="Timing Ideal"></span>';
    } else if (r.timing_category === 'EXTENDED') {
      timingDot = '<span class="inline-block w-2.5 h-2.5 rounded-full bg-amber-400 ring-2 ring-amber-500/30" title="Timing Estendido"></span>';
    }

    tr.innerHTML = `
      <td class="px-3 py-2.5">${getActionBadgeHtml(r.action_type, r.action_label)}</td>
      <td class="px-3 py-2.5">
        <div class="font-bold text-white">${stripCorporateSuffix(r.asset_name || r.ticker)}</div>
        <div class="text-[10px] text-gray-400 font-mono">${r.ticker}</div>
      </td>
      <td class="px-3 py-2.5 text-cyan-300 font-medium">${r.strategy_label}</td>
      <td class="px-3 py-2.5 text-center font-mono">
        <div class="font-bold text-white">${score.toFixed(1)}</div>
        <div class="w-16 h-1.5 bg-gray-800 rounded overflow-hidden mx-auto mt-0.5">
          <div class="h-full ${scoreBarColor}" style="width: ${Math.min(100, Math.max(0, score))}%"></div>
        </div>
      </td>
      <td class="px-3 py-2.5 text-center">${timingDot} <span class="text-[10px] text-gray-300 ml-1">${r.timing_category}</span></td>
      <td class="px-3 py-2.5 font-mono text-white">R$ ${(Number(r.current_price) || 0).toFixed(2)}</td>
      <td class="px-3 py-2.5 font-mono font-bold ${deltaColor}">
        ${delta !== 0 ? `${deltaSign}${delta.toLocaleString('pt-BR')} cotas` : '0 (Manter)'}
        <div class="text-[10px] text-gray-400 font-normal">Final: ${(Number(r.target_shares) || 0).toLocaleString('pt-BR')} cotas</div>
      </td>
      <td class="px-3 py-2.5 font-mono font-bold text-white">
        ${r.order_value > 0 ? `R$ ${Number(r.order_value).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '-'}
      </td>
      <td class="px-3 py-2.5 font-mono text-center">
        <span class="text-gray-400">${(Number(r.current_weight_pct) || 0).toFixed(1)}%</span>
        <span class="text-gray-500 mx-1">→</span>
        <span class="font-bold text-cyan-300">${(Number(r.target_weight_pct) || 0).toFixed(1)}%</span>
      </td>
      <td class="px-3 py-2.5 text-gray-300 text-[11px] max-w-xs truncate" title="${r.reason_text}">${r.reason_text}</td>
    `;
    tbody.appendChild(tr);
  });
}

function openPreFlightOrderModal() {
  const adviseData = state.portfolioState.lastAdviseResponse;
  if (!adviseData || !Array.isArray(adviseData.recommendations)) return;

  const recs = adviseData.recommendations.filter(r => r.action_type !== 'HOLD' && Math.abs(Number(r.recommended_shares_delta) || 0) > 0);
  if (recs.length === 0) {
    alert('Nenhuma ordem de compra ou venda a ser executada.');
    return;
  }

  const modal = document.getElementById('modal-apply-orders');
  const countEl = document.getElementById('modal-orders-count');
  const cashEl = document.getElementById('modal-cash-transition');
  const tbody = document.getElementById('modal-orders-tbody');
  if (!modal || !tbody) return;

  if (countEl) countEl.textContent = `${recs.length} ${recs.length === 1 ? 'ordem' : 'ordens'}`;
  if (cashEl) {
    const cBefore = (Number(adviseData.current_cash) || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const cAfter = (Number(adviseData.projected_cash_after) || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    cashEl.textContent = `R$ ${cBefore} → R$ ${cAfter}`;
  }

  tbody.innerHTML = '';
  recs.forEach(r => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-fintech-surface-hover';
    const delta = Number(r.recommended_shares_delta) || 0;
    const isBuy = delta > 0;
    const actionColor = isBuy ? 'text-emerald-400' : 'text-rose-400';
    const actionLabel = isBuy ? 'COMPRA' : 'VENDA';

    tr.innerHTML = `
      <td class="px-2.5 py-1.5 font-bold text-white">${r.ticker}</td>
      <td class="px-2.5 py-1.5 font-bold ${actionColor}">${actionLabel}</td>
      <td class="px-2.5 py-1.5 text-right text-gray-200">${Math.abs(delta).toLocaleString('pt-BR')} cotas</td>
      <td class="px-2.5 py-1.5 text-right font-bold text-white">R$ ${(Number(r.order_value) || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
    `;
    tbody.appendChild(tr);
  });

  modal.classList.remove('hidden');
}

function closePreFlightOrderModal() {
  const modal = document.getElementById('modal-apply-orders');
  if (modal) modal.classList.add('hidden');
}

function applyRecommendedPortfolioOrders() {
  const adviseData = state.portfolioState.lastAdviseResponse;
  if (!adviseData || !Array.isArray(adviseData.recommendations)) return;

  // Save backup before applying orders so user can undo
  state.portfolioState.previousBackup = {
    holdings: JSON.parse(JSON.stringify(state.portfolioState.holdings || [])),
    availableCash: state.portfolioState.availableCash,
  };

  const newHoldings = [];
  adviseData.recommendations.forEach(r => {
    const targetSh = Number(r.target_shares) || 0;
    if (targetSh > 0) {
      const existing = state.portfolioState.holdings.find(h => h.ticker.toUpperCase() === r.ticker.toUpperCase());
      let avgP = Number(r.current_price) || 0;
      if (existing && Number(r.recommended_shares_delta) > 0) {
        const oldSh = Number(existing.shares) || 0;
        const oldAvg = Number(existing.average_buy_price) || avgP;
        const addSh = Number(r.recommended_shares_delta) || 0;
        avgP = ((oldSh * oldAvg) + (addSh * Number(r.current_price))) / (oldSh + addSh);
      } else if (existing) {
        avgP = Number(existing.average_buy_price) || avgP;
      }
      newHoldings.push({
        ticker: r.ticker,
        shares: Number(targetSh.toFixed(4)),
        average_buy_price: Number(avgP.toFixed(4)),
      });
    }
  });

  state.portfolioState.holdings = newHoldings;
  state.portfolioState.availableCash = Number((Number(adviseData.projected_cash_after) || 0).toFixed(2));
  syncPortfolioInputsFromState();
  savePortfolioStorage();
  renderPortfolioHoldingsEditor();
  updateUndoButtonVisibility();
  closePreFlightOrderModal();
  showToastNotification('Ordens aplicadas com sucesso à sua carteira!', true, undoLastPortfolioApply);
  runPortfolioAdviseAndSimulate();
}

async function runPortfolioAdviseAndSimulate() {
  readPortfolioInputsToState();
  const customList = (state.portfolioState.customTickers || '')
    .split(',')
    .map(s => resolveTicker(s.trim().toUpperCase()))
    .filter(Boolean);

  showLoading('Otimizando estratégias campeãs por ativo e calculando rebalanceamento da carteira...');
  try {
    const advisePayload = {
      available_cash: state.portfolioState.availableCash,
      holdings: state.portfolioState.holdings,
      universe_category: state.portfolioState.universeCategory,
      custom_tickers: customList,
      interval: state.portfolioState.interval,
      period: state.portfolioState.period,
      max_weight_pct: state.portfolioState.maxWeightPct,
      rebalance_band_pct: 5.0,
      min_rotation_score_delta: 15.0,
    };

    const resAdvise = await fetch('/api/portfolio/advise', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(advisePayload),
    });

    if (resAdvise.ok) {
      const adviseData = await resAdvise.json();
      renderPortfolioAdviseSection(adviseData);
      if (typeof renderPortfolioOpportunityRanking === 'function') {
        renderPortfolioOpportunityRanking(adviseData.opportunity_ranking || []);
      }
      if (typeof renderPortfolioAllocationChart === 'function') {
        renderPortfolioAllocationChart(adviseData);
      }
    }

    if (typeof runPortfolioHistoricalSimulation === 'function') {
      await runPortfolioHistoricalSimulation(customList);
    }
  } catch (err) {
    console.error('Erro ao processar carteira:', err);
  } finally {
    hideLoading();
  }
}


async function runPortfolioHistoricalSimulation(customList = []) {
  const initialCap = Math.max(100, Number(state.portfolioState.availableCash) || 10000);
  const simPayload = {
    initial_capital: initialCap,
    universe_category: state.portfolioState.universeCategory,
    custom_tickers: customList,
    interval: state.portfolioState.interval,
    period: state.portfolioState.period,
    max_weight_pct: state.portfolioState.maxWeightPct,
    rebalance_band_pct: 5.0,
    min_rotation_score_delta: 15.0,
  };

  const resSim = await fetch('/api/portfolio/simulate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(simPayload),
  });

  if (!resSim.ok) return;
  const simData = await resSim.json();
  state.portfolioState.lastSimulateResponse = simData;

  renderPortfolioSimulationKPIs(simData.metrics || {});
  renderPortfolioLedgerTable(simData.ledger_events || []);
  if (typeof renderPortfolioEquityChart === 'function') {
    renderPortfolioEquityChart(simData.curve || []);
  }
}

function renderPortfolioSimulationKPIs(m) {
  const elInit = document.getElementById('port-kpi-initial');
  const elCashSub = document.getElementById('port-kpi-cash-sub');
  const elFinal = document.getElementById('port-kpi-final');
  const elProfitSub = document.getElementById('port-kpi-profit-sub');
  const elRet = document.getElementById('port-kpi-return');
  const elBenchSub = document.getElementById('port-kpi-bench-sub');
  const elWin = document.getElementById('port-kpi-winrate');
  const elExitsSub = document.getElementById('port-kpi-exits-sub');
  const elPf = document.getElementById('port-kpi-pf');
  const elRotSub = document.getElementById('port-kpi-rotations-sub');
  const elDd = document.getElementById('port-kpi-dd');
  const elEvSub = document.getElementById('port-kpi-events-sub');

  const initCap = Number(m.initial_capital) || 0;
  const finalEq = Number(m.final_equity) || 0;
  const finalCash = Number(m.final_cash) || 0;
  const netProfit = Number(m.net_profit) || 0;
  const totRet = Number(m.total_return_pct) || 0;
  const benchRet = Number(m.benchmark_return_pct) || 0;
  const alpha = Number(m.alpha_vs_benchmark_pct) || 0;
  const winRate = Number(m.win_rate_pct) || 0;
  const pf = Number(m.profit_factor) || 0;
  const dd = Number(m.max_drawdown_pct) || 0;

  if (elInit) elInit.textContent = `R$ ${initCap.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (elCashSub) elCashSub.textContent = `Caixa final: R$ ${finalCash.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (elFinal) {
    elFinal.textContent = `R$ ${finalEq.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    elFinal.className = `text-base sm:text-lg font-bold font-mono ${netProfit >= 0 ? 'text-fintech-green' : 'text-rose-400'}`;
  }
  if (elProfitSub) {
    elProfitSub.textContent = `Lucro: ${netProfit >= 0 ? '+' : ''}R$ ${netProfit.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
  if (elRet) {
    elRet.textContent = `${totRet >= 0 ? '+' : ''}${totRet.toFixed(1)}%`;
    elRet.className = `text-base sm:text-lg font-bold font-mono ${totRet >= 0 ? 'text-fintech-cyan' : 'text-rose-400'}`;
  }
  if (elBenchSub) {
    elBenchSub.textContent = `B&H Cesta: ${benchRet >= 0 ? '+' : ''}${benchRet.toFixed(1)}% (Alfa: ${alpha >= 0 ? '+' : ''}${alpha.toFixed(1)}%)`;
  }
  if (elWin) elWin.textContent = `${winRate.toFixed(1)}%`;
  if (elExitsSub) elExitsSub.textContent = `${m.winning_exits_count || 0}W / ${m.losing_exits_count || 0}L (${m.closed_exits_count || 0} saídas)`;
  if (elPf) elPf.textContent = pf.toFixed(2);
  if (elRotSub) elRotSub.textContent = `${m.rebalance_rotations_count || 0} rebalanceamentos/rotações`;
  if (elDd) elDd.textContent = `${dd.toFixed(1)}%`;
  if (elEvSub) elEvSub.textContent = `${m.total_events_count || 0} ordens executadas`;
}

function renderPortfolioLedgerTable(events) {
  const tbody = document.getElementById('portfolio-ledger-tbody');
  const countBadge = document.getElementById('portfolio-ledger-count-badge');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (countBadge) countBadge.textContent = `${events.length} eventos`;

  if (!events || events.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="13" class="px-4 py-6 text-center text-gray-500">
          Nenhuma operação executada no período selecionado.
        </td>
      </tr>
    `;
    return;
  }

  events.forEach(ev => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-fintech-surface-hover';

    const delta = Number(ev.shares_delta) || 0;
    const deltaSign = delta > 0 ? '+' : '';
    const deltaColor = delta > 0 ? 'text-emerald-400' : 'text-rose-400';

    let pnlHtml = '<span class="text-gray-500">-</span>';
    if (ev.realized_pnl_value !== null && ev.realized_pnl_value !== undefined) {
      const pVal = Number(ev.realized_pnl_value) || 0;
      const pPct = Number(ev.realized_pnl_pct) || 0;
      const pClass = pVal >= 0 ? 'text-emerald-400' : 'text-rose-400';
      const pSign = pVal >= 0 ? '+' : '';
      pnlHtml = `<span class="font-bold ${pClass}">${pSign}R$ ${pVal.toFixed(2)} (${pSign}${pPct.toFixed(1)}%)</span>`;
    }

    tr.innerHTML = `
      <td class="px-2.5 py-2 text-center text-gray-400 font-bold">${ev.event_id}</td>
      <td class="px-2.5 py-2 text-gray-300">${ev.date}</td>
      <td class="px-2.5 py-2">${getActionBadgeHtml(ev.event_type, ev.event_label)}</td>
      <td class="px-2.5 py-2 font-bold text-white">${ev.ticker}</td>
      <td class="px-2.5 py-2 text-cyan-300 font-sans">${ev.strategy_label}</td>
      <td class="px-2.5 py-2 text-center text-amber-300 font-bold">${(Number(ev.potential_score) || 0).toFixed(1)}</td>
      <td class="px-2.5 py-2 text-white">R$ ${(Number(ev.execution_price) || 0).toFixed(2)}</td>
      <td class="px-2.5 py-2 font-bold ${deltaColor}">${deltaSign}${delta.toLocaleString('pt-BR')}</td>
      <td class="px-2.5 py-2 text-white">R$ ${(Number(ev.trade_value) || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
      <td class="px-2.5 py-2">${pnlHtml}</td>
      <td class="px-2.5 py-2 text-center text-gray-300">${(Number(ev.weight_before_pct) || 0).toFixed(1)}% → ${(Number(ev.weight_after_pct) || 0).toFixed(1)}%</td>
      <td class="px-2.5 py-2 text-gray-300">R$ ${(Number(ev.cash_after) || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
      <td class="px-2.5 py-2 font-bold text-white">R$ ${(Number(ev.portfolio_equity_after) || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
    `;
    tbody.appendChild(tr);
  });
}


function renderPortfolioEquityChart(curve) {
  const container = document.getElementById('portfolio-equity-chart');
  if (!container || !window.Plotly) return;

  if (!curve || curve.length === 0) {
    Plotly.purge(container);
    container.innerHTML = '<div class="flex items-center justify-center h-full text-xs text-gray-500 font-mono">Execute a análise/simulação para gerar a curva patrimonial.</div>';
    return;
  }
  container.innerHTML = '';

  const isLight = (document.documentElement.getAttribute('data-theme') || 'dark') === 'light';
  const bgColor = isLight ? '#FFFFFF' : '#0B0E14';
  const textColor = isLight ? '#334155' : '#8B98A5';
  const gridColor = isLight ? 'rgba(226, 232, 240, 0.8)' : 'rgba(38, 43, 56, 0.5)';
  const borderColor = isLight ? '#E2E8F0' : '#262B38';

  const dates = curve.map(c => c.date);
  const eqValues = curve.map(c => Number(c.portfolio_equity) || 0);
  const benchValues = curve.map(c => Number(c.benchmark_equity) || 0);
  const cashValues = curve.map(c => Number(c.cash_balance) || 0);

  const traces = [
    {
      x: dates,
      y: eqValues,
      type: 'scatter',
      mode: 'lines',
      name: 'Carteira Gerenciada',
      line: { color: '#00E676', width: 2.5 },
      fill: 'tozeroy',
      fillcolor: 'rgba(0, 230, 118, 0.08)',
      hovertemplate: '<b>%{x}</b><br>Patrimônio Carteira: R$ %{y:,.2f}<extra></extra>',
    },
    {
      x: dates,
      y: benchValues,
      type: 'scatter',
      mode: 'lines',
      name: 'Buy & Hold Equal-Weight',
      line: { color: '#00E5FF', width: 1.8, dash: 'dot' },
      hovertemplate: '<b>%{x}</b><br>Benchmark Cesta: R$ %{y:,.2f}<extra></extra>',
    },
    {
      x: dates,
      y: cashValues,
      type: 'scatter',
      mode: 'lines',
      name: 'Caixa Livre',
      line: { color: '#F59E0B', width: 1.2, dash: 'dash' },
      hovertemplate: '<b>%{x}</b><br>Caixa Livre: R$ %{y:,.2f}<extra></extra>',
    },
  ];

  const layout = {
    paper_bgcolor: bgColor,
    plot_bgcolor: bgColor,
    font: { family: 'JetBrains Mono, monospace', size: 11, color: textColor },
    margin: { t: 25, r: 20, b: 35, l: 65 },
    legend: { orientation: 'h', y: 1.12, x: 0, font: { size: 10 } },
    xaxis: {
      gridcolor: gridColor,
      linecolor: borderColor,
      tickfont: { size: 10 },
    },
    yaxis: {
      gridcolor: gridColor,
      linecolor: borderColor,
      tickprefix: 'R$ ',
      tickfont: { size: 10 },
    },
    hovermode: 'x unified',
  };

  Plotly.newPlot(container, traces, layout, { responsive: true, displayModeBar: false });
}

function renderPortfolioAllocationChart(adviseData) {
  const container = document.getElementById('portfolio-allocation-chart');
  if (!container || !window.Plotly) return;

  if (!adviseData) {
    Plotly.purge(container);
    container.innerHTML = '<div class="flex items-center justify-center h-full text-xs text-gray-500 font-mono">Execute a análise para visualizar os pesos por ativo.</div>';
    return;
  }
  container.innerHTML = '';

  const isLight = (document.documentElement.getAttribute('data-theme') || 'dark') === 'light';
  const bgColor = isLight ? '#FFFFFF' : '#0B0E14';
  const textColor = isLight ? '#334155' : '#8B98A5';
  const gridColor = isLight ? 'rgba(226, 232, 240, 0.8)' : 'rgba(38, 43, 56, 0.5)';
  const borderColor = isLight ? '#E2E8F0' : '#262B38';

  const recs = (adviseData.recommendations || []).filter(r => (Number(r.current_weight_pct) > 0 || Number(r.target_weight_pct) > 0));
  const totalEq = Math.max(1, Number(adviseData.total_portfolio_equity) || 1);
  const currCashPct = Number(((Number(adviseData.current_cash) || 0) / totalEq * 100).toFixed(2));
  const projCashPct = Number(((Number(adviseData.projected_cash_after) || 0) / totalEq * 100).toFixed(2));

  const labels = recs.map(r => r.ticker).concat(['CAIXA']);
  const currentWeights = recs.map(r => Number(r.current_weight_pct) || 0).concat([currCashPct]);
  const targetWeights = recs.map(r => Number(r.target_weight_pct) || 0).concat([projCashPct]);

  const traces = [
    {
      x: labels,
      y: currentWeights,
      name: 'Peso Atual (%)',
      type: 'bar',
      marker: { color: '#64748B' },
      hovertemplate: '<b>%{x}</b><br>Peso Atual: %{y:.1f}%<extra></extra>',
    },
    {
      x: labels,
      y: targetWeights,
      name: 'Peso Alvo Recomendado (%)',
      type: 'bar',
      marker: { color: '#00E5FF' },
      hovertemplate: '<b>%{x}</b><br>Peso Alvo: %{y:.1f}%<extra></extra>',
    },
  ];

  const layout = {
    barmode: 'group',
    paper_bgcolor: bgColor,
    plot_bgcolor: bgColor,
    font: { family: 'JetBrains Mono, monospace', size: 11, color: textColor },
    margin: { t: 25, r: 15, b: 40, l: 45 },
    legend: { orientation: 'h', y: 1.12, x: 0, font: { size: 10 } },
    xaxis: {
      gridcolor: gridColor,
      linecolor: borderColor,
      tickfont: { size: 10 },
    },
    yaxis: {
      gridcolor: gridColor,
      linecolor: borderColor,
      ticksuffix: '%',
      range: [0, 105],
      tickfont: { size: 10 },
    },
  };

  Plotly.newPlot(container, traces, layout, { responsive: true, displayModeBar: false });
}

function renderPortfolioOpportunityRanking(ranking) {
  const tbody = document.getElementById('portfolio-ranking-tbody');
  const countBadge = document.getElementById('portfolio-ranking-count-badge');
  if (!tbody) return;
  tbody.innerHTML = '';

  const list = ranking || [];
  if (countBadge) countBadge.textContent = `${list.length} ativos avaliados`;

  if (list.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="10" class="px-4 py-6 text-center text-gray-500">
          Nenhum ativo avaliado no universo selecionado.
        </td>
      </tr>
    `;
    return;
  }

  list.forEach((p, idx) => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-fintech-surface-hover';

    const score = Number(p.potential_score) || 0;
    const scoreBarColor = score >= 75 ? 'bg-emerald-400' : (score >= 55 ? 'bg-cyan-400' : 'bg-amber-400');

    let sigBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-700/50 text-gray-400">NEUTRO</span>';
    if (p.active_direction === 'BUY') {
      sigBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-extrabold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">🟢 ZONA DE COMPRA</span>';
    } else if (p.active_direction === 'SELL') {
      sigBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-extrabold bg-rose-500/20 text-rose-400 border border-rose-500/40">🔴 ZONA DE VENDA</span>';
    }

    const retPct = Number(p.historical_return_pct) || 0;
    const retColor = retPct >= 0 ? 'text-emerald-400' : 'text-rose-400';

    tr.innerHTML = `
      <td class="px-3 py-2 text-center font-bold text-gray-400">#${idx + 1}</td>
      <td class="px-3 py-2">
        <span class="font-bold text-white">${stripCorporateSuffix(p.asset_name || p.ticker)}</span>
        <span class="text-[10px] text-gray-400 ml-1">(${p.ticker})</span>
      </td>
      <td class="px-3 py-2 text-cyan-300 font-sans">${p.champion_buy_label}</td>
      <td class="px-3 py-2 text-amber-300 font-sans">${p.champion_sell_label}</td>
      <td class="px-3 py-2 text-center">
        <div class="font-bold text-white">${score.toFixed(1)}</div>
        <div class="w-16 h-1.5 bg-gray-800 rounded overflow-hidden mx-auto mt-0.5">
          <div class="h-full ${scoreBarColor}" style="width: ${Math.min(100, Math.max(0, score))}%"></div>
        </div>
      </td>
      <td class="px-3 py-2 text-center">${sigBadge}</td>
      <td class="px-3 py-2 text-center text-gray-300">${p.timing_label || p.timing_category} (${(Number(p.distance_pct) || 0).toFixed(1)}%)</td>
      <td class="px-3 py-2 text-center font-bold text-emerald-400">${(Number(p.win_rate_pct) || 0).toFixed(1)}%</td>
      <td class="px-3 py-2 text-center font-bold ${retColor}">${retPct >= 0 ? '+' : ''}${retPct.toFixed(1)}%</td>
      <td class="px-3 py-2 text-center text-rose-400">${(Number(p.max_drawdown_pct) || 0).toFixed(1)}%</td>
    `;
    tbody.appendChild(tr);
  });
}


function setupOverviewSubNav() {
  const subBtns = document.querySelectorAll('#overview-sub-nav .overview-sub-btn');
  if (subBtns.length === 0) return;

  subBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetSub = btn.getAttribute('data-sub');
      switchOverviewSubTab(targetSub);
    });
  });
}

function switchOverviewSubTab(subId) {
  const subBtns = document.querySelectorAll('#overview-sub-nav .overview-sub-btn');
  subBtns.forEach(b => {
    if (b.getAttribute('data-sub') === subId) {
      b.className = 'overview-sub-btn active px-3 py-1.5 rounded-md text-xs font-bold text-white bg-fintech-surface border border-fintech-border shadow-sm';
    } else {
      b.className = 'overview-sub-btn px-3 py-1.5 rounded-md text-xs font-semibold text-gray-400 hover:text-white hover:bg-fintech-surface/60 transition';
    }
  });

  const kpis = document.getElementById('overview-section-kpis');
  const charts = document.getElementById('overview-section-charts');
  const posicoes = document.getElementById('overview-section-posicoes');
  const metas = document.getElementById('overview-section-metas');

  if (subId === 'resumo') {
    // Shows everything in integrated dashboard
    if (kpis) kpis.classList.remove('hidden');
    if (charts) charts.classList.remove('hidden');
    if (posicoes) posicoes.classList.remove('hidden');
    if (metas) metas.classList.remove('hidden');
  } else if (subId === 'posicoes') {
    if (kpis) kpis.classList.add('hidden');
    if (charts) charts.classList.add('hidden');
    if (posicoes) posicoes.classList.remove('hidden');
    if (metas) metas.classList.add('hidden');
  } else if (subId === 'patrimonio') {
    if (kpis) kpis.classList.remove('hidden');
    if (charts) charts.classList.remove('hidden');
    if (posicoes) posicoes.classList.add('hidden');
    if (metas) metas.classList.add('hidden');
  } else if (subId === 'metas') {
    if (kpis) kpis.classList.add('hidden');
    if (charts) charts.classList.add('hidden');
    if (posicoes) posicoes.classList.add('hidden');
    if (metas) metas.classList.remove('hidden');
  }

  // Trigger chart resize if charts are visible
  setTimeout(() => {
    ['overview-stacked-bar-chart', 'overview-donut-chart'].forEach(cid => {
      const cEl = document.getElementById(cid);
      if (cEl && cEl.data && window.Plotly) Plotly.Plots.resize(cEl);
    });
  }, 60);
}


let tvAveragePriceLine = null;

function updateTradingViewAveragePriceLine() {
  if (!state.candleSeries) return;
  const currentTicker = (state.currentTicker || '').toUpperCase();
  const holdings = state.portfolioState.holdings || [];
  const found = holdings.find(h => {
    const t = (h.ticker || '').toUpperCase();
    return t === currentTicker || t.replace('.SA', '') === currentTicker.replace('.SA', '');
  });

  if (tvAveragePriceLine) {
    try {
      state.candleSeries.removePriceLine(tvAveragePriceLine);
    } catch (e) {}
    tvAveragePriceLine = null;
  }

  if (found && found.average_buy_price > 0) {
    try {
      tvAveragePriceLine = state.candleSeries.createPriceLine({
        price: Number(found.average_buy_price),
        color: '#f59e0b',
        lineWidth: 2,
        lineStyle: 2, // Dashed
        axisLabelVisible: true,
        title: 'PM B3: R$ ' + found.average_buy_price.toFixed(2),
      });
    } catch (e) {
      console.warn('Erro ao criar linha de Preço Médio no gráfico:', e);
    }
  }
}
