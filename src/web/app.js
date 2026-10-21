
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
  setupAccordions();
  setupMobileStrategiesToggle();
  setupTimeframeButtons();
  setupRadarTimeframeButtons();
  setupRadarCategoryPills();
  setupRadarStrategyFilter();
  setupGranularStrategyCheckboxes();
  initTradingViewChart();
  setupSimulationTab();

  // Initial load
  loadRadarData();

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

  // Update Plotly charts if present
  if (window.Plotly) {
    const plotlyLayoutUpdate = {
      paper_bgcolor: bgColor,
      plot_bgcolor: bgColor,
      'font.color': textColor,
      'xaxis.gridcolor': gridColor,
      'yaxis.gridcolor': gridColor,
      'xaxis.linecolor': borderColor,
      'yaxis.linecolor': borderColor,
    };
    ['plot-ranking', 'plot-scatter', 'plot-simulation-curve'].forEach(id => {
      const el = document.getElementById(id);
      if (el && el.data) {
        Plotly.relayout(el, plotlyLayoutUpdate).catch(() => {});
      }
    });
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

function switchTab(tabId) {
  state.activeTab = tabId;
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

  if (tabId === 'tab-terminal') {
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

function renderRadarTable(pageOrItems) {
  const items = Array.isArray(pageOrItems) ? pageOrItems : (pageOrItems ? pageOrItems.items : []);
  if (pageOrItems && pageOrItems.total_pages !== undefined) {
    updateRadarPagination(pageOrItems);
  }
  elements.radarTableBody.innerHTML = '';
  if (!items || items.length === 0) {
    elements.radarTableBody.innerHTML = `
      <tr>
        <td colspan="11" class="text-center py-8 text-gray-500">
          Nenhuma oportunidade com sinal ativo ou reteste pendente no momento.
        </td>
      </tr>
    `;
    return;
  }

  // Filter radar items by active direction and category
  const filtered = items.filter(it => {
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
        <td colspan="11" class="text-center py-8 text-gray-500">
          Nenhuma oportunidade encontrada para a direção selecionada (${state.activeDirection}).
        </td>
      </tr>
    `;
    return;
  }

  filtered.forEach(item => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-fintech-surface-hover transition';

    let badgeClass = 'badge-ideal';
    if (item.timing_category === 'EXTENDED') badgeClass = 'badge-extended';
    if (item.timing_category === 'LATE') badgeClass = 'badge-late';

    const isBuy = (item.direction === 'BUY');
    const dirBadge = isBuy
      ? '<span class="text-xs px-2 py-0.5 rounded font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">COMPRA</span>'
      : '<span class="text-xs px-2 py-0.5 rounded font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">VENDA</span>';

    const friendlyName = stripCorporateSuffix(item.asset_name || getAssetName(item.ticker));

    tr.innerHTML = `
      <td class="px-4 py-3">
        <button class="text-left group btn-open-ticker focus:outline-none cursor-pointer" data-ticker="${item.ticker}" data-strategy="${item.strategy_sub_id}" data-direction="${item.direction}">
          <div class="font-bold text-cyan-400 group-hover:text-cyan-200 group-hover:underline flex items-center gap-1.5 transition">
            <span>${friendlyName}</span>
            <span class="text-xs text-cyan-500/70 group-hover:text-cyan-300"></span>
          </div>
          <div class="text-[11px] text-gray-500 font-mono tracking-wide">${item.ticker}</div>
        </button>
      </td>
      <td class="px-4 py-3 text-gray-400">${item.category}</td>
      <td class="px-4 py-3">${dirBadge}</td>
      <td class="px-4 py-3 font-mono font-semibold">${formatPrice(item.current_price, item.ticker, item.category)}</td>
      <td class="px-4 py-3 ${isBuy ? 'text-emerald-300' : 'text-rose-300'} font-medium">${item.strategy_label}</td>
      <td class="px-4 py-3 font-mono text-gray-300">${item.status_signal}</td>
      <td class="px-4 py-3">
        <span class="px-2 py-0.5 rounded text-[11px] font-semibold ${badgeClass}">
          ${item.timing_label}
        </span>
      </td>
      <td class="px-4 py-3 font-mono font-bold ${item.distance_pct >= 0 ? 'text-amber-400' : 'text-cyan-400'}">
        ${item.distance_pct >= 0 ? '+' : ''}${item.distance_pct.toFixed(1)}%
      </td>
      <td class="px-4 py-3 font-mono text-gray-400">${formatPrice(item.recommended_price, item.ticker, item.category)}</td>
      <td class="px-4 py-3 font-mono text-gray-400">${item.historical_n} entradas (${item.historical_win_rate.toFixed(1)}%)</td>
      <td class="px-4 py-3 text-right">
        <button class="bg-cyan-600/30 hover:bg-cyan-600 text-cyan-300 hover:text-white px-2.5 py-1 rounded text-xs font-semibold transition btn-open-ticker cursor-pointer" data-ticker="${item.ticker}" data-strategy="${item.strategy_sub_id}" data-direction="${item.direction}">
          Abrir Gráfico →
        </button>
      </td>
    `;
    elements.radarTableBody.appendChild(tr);
  });

  document.querySelectorAll('.btn-open-ticker').forEach(btn => {
    btn.addEventListener('click', () => {
      const ticker = btn.getAttribute('data-ticker');
      const strat = btn.getAttribute('data-strategy');
      const dir = btn.getAttribute('data-direction');

      const resolved = resolveTicker(ticker);
      state.currentTicker = resolved;
      elements.inputTicker.value = resolved;
      if (elements.simTicker) elements.simTicker.value = resolved;

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
        if (dir && (dir === 'BUY' || dir === 'SELL') && state.activeDirection !== dir) {
          state.activeDirection = dir;
          document.querySelectorAll('.direction-btn').forEach(b => {
            const bDir = b.getAttribute('data-direction');
            if (bDir === 'BOTH') {
              b.classList.add('active', 'border-fintech-cyan', 'text-fintech-cyan');
            } else {
              b.classList.remove('active', 'border-fintech-cyan', 'text-fintech-cyan');
            }
          });
        }
        state.activeStrategies.add(strat);
        const aliases = STRATEGY_ALIASES[strat] || [];
        aliases.forEach(a =>state.activeStrategies.add(a));
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
    applyClientSideFiltering();

  } catch (err) {
    alert(`Erro na análise: ${err.message}`);
  } finally {
    hideLoading();
  }
}

// 0ms CLIENT-SIDE FILTERING ENGINE (Direction & Strategy Selective)
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

      if (mode === 'cycle_trade') {
        if (cycleContainer) cycleContainer.classList.remove('hidden');
        if (lblCap) lblCap.textContent = 'Capital Inicial (R$)';
        if (lblInv) lblInv.textContent = 'Capital Inicial';
        if (lblAux) lblAux.textContent = 'Win Rate / Acertos';
        if (legendInfo) legendInfo.textContent = 'Evolução de Saldo em Caixa + Posição a Mercado';
      } else {
        if (cycleContainer) cycleContainer.classList.add('hidden');
        if (lblCap) lblCap.textContent = 'Aporte por Sinal (R$)';
        if (lblInv) lblInv.textContent = 'Total Aportado';
        if (lblAux) lblAux.textContent = 'Alfa vs. DCA Passivo';
        if (legendInfo) legendInfo.textContent = 'Patrimônio em Cotas vs. Capital Desembolsado';
      }
    });
  }
  elements.btnRunSimulation.addEventListener('click', runSimulation);

  if (elements.btnOptimizeCombinations) {
    elements.btnOptimizeCombinations.addEventListener('click', runOptimizer);
  }

  if (elements.btnApplyChampion) {
    elements.btnApplyChampion.addEventListener('click', () => {
      if (state.lastChampion) {
        if (elements.simBuyStrategy) elements.simBuyStrategy.value = state.lastChampion.buy_sub_id;
        if (elements.simSellStrategy) elements.simSellStrategy.value = state.lastChampion.sell_sub_id;
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

    // Intraday intervals (5m, 15m) in yfinance require periods <= 60d
    let simPeriod = state.currentPeriod;
    if (selectedInterval === '5m') {
      simPeriod = '60d';
    } else if (selectedInterval === '15m' || selectedInterval === '60m') {
      simPeriod = '60d';
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
  showLoading('Varrendo centenas de combinações para encontrar a mais lucrativa...');
  try {
    const tickerInput = resolveTicker((elements.simTicker && elements.simTicker.value.trim().toUpperCase()) || state.currentTicker);
    const capitalVal = parseFloat(document.getElementById('sim-contribution').value) || 1000;
    const payload = {
      ticker: tickerInput,
      interval: state.currentTimeframe,
      period: state.currentPeriod,
      initial_capital: capitalVal,
      min_trades: 2,
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
      if (countEl) countEl.textContent = `${data.total_combinations_tested} combinações válidas rankeadas`;
      document.getElementById('opt-champ-buy-label').textContent = c.buy_label;
      document.getElementById('opt-champ-sell-label').textContent = c.sell_label;
      document.getElementById('opt-champ-ret').textContent = `${c.total_return_pct >= 0 ? '+' : ''}${c.total_return_pct.toFixed(1)}%`;
      document.getElementById('opt-champ-pnl').textContent = `${c.net_profit >= 0 ? '+' : ''}R$ ${c.net_profit.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
      document.getElementById('opt-champ-winrate').textContent = `${c.win_rate_pct.toFixed(1)}% (${c.winning_trades}/${c.closed_trades})`;
      document.getElementById('opt-champ-trades').textContent = `${c.closed_trades} trades`;
      document.getElementById('opt-champ-drawdown').textContent = `${c.max_drawdown_pct.toFixed(1)}%`;
    }

    renderTopCombinationsTable(data.top_combinations || []);

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

function renderTopCombinationsTable(combos) {
  if (!elements.simTopCombosTableBody) return;
  elements.simTopCombosTableBody.innerHTML = '';

  if (!combos || combos.length === 0) {
    elements.simTopCombosTableBody.innerHTML = `<tr><td colspan="9" class="text-center py-4 text-gray-500">Nenhuma combinação com no mínimo 2 trades encontrada no período.</td></tr>`;
    return;
  }

  combos.forEach(item => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-fintech-surface-hover';

    const rankBadge = item.rank === 1 ? ' 1º' : (item.rank === 2 ? ' 2º' : (item.rank === 3 ? ' 3º' : `#${item.rank}`));
    const retClass = item.total_return_pct >= 0 ? 'text-emerald-400' : 'text-rose-400';
    const pnlClass = item.net_profit >= 0 ? 'text-emerald-400' : 'text-rose-400';

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
    elements.simTopCombosTableBody.appendChild(tr);
  });

  // Attach click listeners to " Testar" buttons
  elements.simTopCombosTableBody.querySelectorAll('.btn-test-combo').forEach(btn => {
    btn.addEventListener('click', () => {
      const buyId = btn.getAttribute('data-buy');
      const sellId = btn.getAttribute('data-sell');
      if (elements.simBuyStrategy) elements.simBuyStrategy.value = buyId;
      if (elements.simSellStrategy) elements.simSellStrategy.value = sellId;
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
