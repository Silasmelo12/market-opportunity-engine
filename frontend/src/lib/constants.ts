// Catálogo Unificado de Ativos do Sistema
export interface AssetOption {
  symbol: string;
  name: string;
}

export interface AssetCategoryGroup {
  category: string;
  assets: AssetOption[];
}

export const KNOWN_ASSET_NAMES: Record<string, string> = {
  "GC=F": "Gold (Ouro / XAUUSD)",
  "XAUUSD": "Gold (Ouro / XAUUSD)",
  "XAUUSD=X": "Gold (Ouro / XAUUSD)",
  "GOLD": "Gold (Ouro / XAUUSD)",
  "SI=F": "Silver (Prata)",
  "CL=F": "Crude Oil WTI (Petróleo)",
  "BZ=F": "Brent Oil (Petróleo Brent)",
  "HG=F": "Copper (Cobre)",
  "NG=F": "Natural Gas (Gás Natural)",
  "ZC=F": "Corn (Milho)",
  "ZS=F": "Soybeans (Soja)",
  "ZW=F": "Wheat (Trigo)",
  "KC=F": "Coffee (Café Arábica)",
  "CT=F": "Cotton (Algodão)",
  "SB=F": "Sugar (Açúcar)",
  "LE=F": "Live Cattle (Boi Gordo)",
  "HE=F": "Lean Hogs (Suínos)",
  "^BVSP": "Mini Índice / Ibovespa (WIN)",
  "WIN": "Mini Índice (WIN)",
  "USDBRL=X": "Mini Dólar (WDO / USDBRL)",
  "WDO": "Mini Dólar (WDO)",
  "BRL=X": "Mini Dólar (WDO / BRL)",
  "EURUSD=X": "EUR/USD",
  "GBPUSD=X": "GBP/USD",
  "USDJPY=X": "USD/JPY",
  "USDCHF=X": "USD/CHF",
  "AUDUSD=X": "AUD/USD",
  "USDCAD=X": "USD/CAD",
  "NZDUSD=X": "NZD/USD",
  "EURJPY=X": "EUR/JPY",
  "GBPJPY=X": "GBP/JPY",
  "EURCHF=X": "EUR/CHF",
  "BTC-USD": "Bitcoin",
  "ETH-USD": "Ethereum",
  "SOL-USD": "Solana",
  "PETR4.SA": "Petrobras PN",
  "VALE3.SA": "Vale ON",
  "ITUB4.SA": "Itaú Unibanco PN",
  "BBDC4.SA": "Bradesco PN",
  "BBAS3.SA": "Banco do Brasil ON",
  "ABEV3.SA": "Ambev ON",
  "WEGE3.SA": "WEG ON",
  "RENT3.SA": "Localiza ON",
  "EGIE3.SA": "Engie Brasil ON",
  "PRIO3.SA": "PRIO ON",
  "BRSR6.SA": "Banrisul PNB",
  "KLBN4.SA": "Klabin PN",
  "CXSE3.SA": "Caixa Seguridade ON",
  "BMGB4.SA": "Banco BMG PN",
  "BRKM5.SA": "Braskem PNA",
  "TASA4.SA": "Taurus Armas PN",
  "PMAM3.SA": "Paranapanema ON",
  "CMIG4.SA": "Cemig PN",
  "CPFE3.SA": "CPFL Energia ON",
  "POMO4.SA": "Marcopolo PN",
  "TAEE11.SA": "Taesa Unit",
  "BBSE3.SA": "BB Seguridade ON",
  "SUZB3.SA": "Suzano ON",
  "GGBR4.SA": "Gerdau PN",
  "CSNA3.SA": "Siderúrgica Nacional ON",
  "GRND3.SA": "Grendene ON",
  "HGLG11.SA": "CSHG Logística",
  "KNRI11.SA": "Kinea Renda Imob.",
  "MXRF11.SA": "Maxi Renda",
  "VISC11.SA": "Vinci Shopping",
  "BTLG11.SA": "BTG Logística",
  "HGRE11.SA": "CSHG Real Estate",
  "KNIP11.SA": "Kinea Índices",
  "HSML11.SA": "HSI Malls",
  "GGRC11.SA": "GGR Covepi",
  "RBRR11.SA": "RBR Rendimento",
  "RBVA11.SA": "Rio Bravo Renda",
  "SNCI11.SA": "Suno Recebíveis",
  "TRXF11.SA": "TRX Real Estate",
  "XPLG11.SA": "XP Log",
  "CPTS11.SA": "Capitânia Securities",
  "VGIR11.SA": "Valora RE",
  "VRTA11.SA": "Fator Verita",
  "VINO11.SA": "Vinci Offices",
  "RECR11.SA": "REC Renda Imob.",
  "HFOF11.SA": "Hedge FOF",
  "BTAL11.SA": "BTG Agro Logística",
  "NVDC34.SA": "Nvidia BDR",
  "AAPL34.SA": "Apple BDR",
  "MSFT34.SA": "Microsoft BDR",
  "GOGL34.SA": "Alphabet (Google) BDR",
  "AMZO34.SA": "Amazon BDR",
  "M1TA34.SA": "Meta Platforms BDR",
  "TSLA34.SA": "Tesla BDR",
  "AVGO34.SA": "Broadcom BDR",
  "TSMC34.SA": "TSMC BDR",
  "A1MD34.SA": "AMD BDR",
  "TMCO34.SA": "Toyota BDR",
  "BERK34.SA": "Berkshire Hathaway BDR",
  "JPMC34.SA": "JPMorgan Chase BDR",
  "VISA34.SA": "Visa BDR",
  "MSCD34.SA": "Mastercard BDR",
  "BOAC34.SA": "Bank of America BDR",
  "GSGI34.SA": "Goldman Sachs BDR",
  "WALM34.SA": "Walmart BDR",
  "COCA34.SA": "Coca-Cola BDR",
  "PEPB34.SA": "PepsiCo BDR",
  "MCDC34.SA": "McDonald's BDR",
  "DISB34.SA": "Disney BDR",
  "NFLX34.SA": "Netflix BDR",
  "NIKE34.SA": "Nike BDR",
  "COWC34.SA": "Costco BDR",
  "LILY34.SA": "Eli Lilly BDR",
  "N1VO34.SA": "Novo Nordisk BDR",
  "JNJB34.SA": "Johnson & Johnson BDR",
  "UNHH34.SA": "UnitedHealth BDR",
  "PFIZ34.SA": "Pfizer BDR",
  "EXXO34.SA": "Exxon Mobil BDR",
  "CHVX34.SA": "Chevron BDR",
  "CATP34.SA": "Caterpillar BDR",
  "BOEI34.SA": "Boeing BDR",
  "IVVB11.SA": "iShares S&P 500 Fundo de Índice",
  "BIVB39.SA": "iShares Core S&P 500 BDR",
  "NASD11.SA": "Trend ETF Nasdaq 100",
  "BNDA39.SA": "Invesco QQQ Trust BDR",
  "ACWI11.SA": "Trend ETF MSCI ACWI",
  "BACW39.SA": "iShares MSCI ACWI BDR",
  "SPCX34.SA": "SpaceX BDR (Space Exploration)",
  "AAPL": "Apple",
  "MSFT": "Microsoft",
  "GOOGL": "Google (Alphabet)",
  "AMZN": "Amazon",
  "NVDA": "Nvidia",
  "META": "Meta Platforms",
  "TSLA": "Tesla",
  "BRK-B": "Berkshire Hathaway",
  "JPM": "JPMorgan Chase",
  "V": "Visa",
  "JNJ": "Johnson & Johnson",
  "WMT": "Walmart",
  "PG": "Procter & Gamble",
  "MA": "Mastercard",
  "UNH": "UnitedHealth",
  "HD": "Home Depot",
  "DIS": "Disney",
  "ADBE": "Adobe",
  "NFLX": "Netflix",
  "CRM": "Salesforce",
  "KO": "Coca-Cola",
  "AMD": "AMD",
  "INTC": "Intel",
  "CSCO": "Cisco",
  "ABBV": "AbbVie",
  "CVX": "Chevron",
  "XOM": "Exxon Mobil",
  "PFE": "Pfizer",
  "IBM": "IBM",
  "MMM": "3M",
  "VZ": "Verizon",
  "T": "AT&T",
  "BA": "Boeing",
  "CAT": "Caterpillar",
  "GE": "General Electric",
  "GM": "General Motors",
  "F": "Ford",
  "UBER": "Uber",
  "LYFT": "Lyft",
  "TM": "Toyota",
  "SNAP": "Snap",
  "PINS": "Pinterest",
  "PYPL": "PayPal",
  "SHOP": "Shopify",
  "ZM": "Zoom",
  "DOCU": "DocuSign",
  "CRWD": "CrowdStrike",
  "NET": "Cloudflare",
  "O": "Realty Income",
  "SPG": "Simon Property",
  "PLD": "Prologis",
  "AMT": "American Tower",
  "CCI": "Crown Castle",
  "EQIX": "Equinix",
  "PSA": "Public Storage",
  "DLR": "Digital Realty",
  "WELL": "Welltower",
  "AVB": "AvalonBay",
  "EQR": "Equity Residential",
  "BXP": "Boston Properties",
  "VTR": "Ventas",
  "ARE": "Alexandria RE",
  "MAA": "Mid-America Apt.",
  "UDR": "UDR Inc.",
  "KIM": "Kimco Realty",
  "REG": "Regency Centers",
  "HST": "Host Hotels",
  "FRT": "Federal Realty",
  "NNN": "NNN REIT",
  "WPC": "W. P. Carey",
  "GLPI": "Gaming and Leisure"
};

export const ALL_ASSET_GROUPS: AssetCategoryGroup[] = [
  {
    "category": "Destaques",
    "assets": [
      {
        "symbol": "^BVSP",
        "name": "Mini Índice / Ibovespa (WIN)"
      },
      {
        "symbol": "USDBRL=X",
        "name": "Mini Dólar (WDO / USDBRL)"
      },
      {
        "symbol": "GC=F",
        "name": "Gold (Ouro / XAUUSD)"
      },
      {
        "symbol": "PETR4.SA",
        "name": "Petrobras PN"
      },
      {
        "symbol": "VALE3.SA",
        "name": "Vale ON"
      },
      {
        "symbol": "ITUB4.SA",
        "name": "Itaú Unibanco PN"
      },
      {
        "symbol": "BBAS3.SA",
        "name": "Banco do Brasil ON"
      },
      {
        "symbol": "HGLG11.SA",
        "name": "CSHG Logística"
      },
      {
        "symbol": "MXRF11.SA",
        "name": "Maxi Renda"
      },
      {
        "symbol": "AAPL",
        "name": "Apple"
      },
      {
        "symbol": "NVDA",
        "name": "Nvidia"
      },
      {
        "symbol": "MSFT",
        "name": "Microsoft"
      },
      {
        "symbol": "TSLA",
        "name": "Tesla"
      },
      {
        "symbol": "CL=F",
        "name": "Crude Oil WTI (Petróleo)"
      },
      {
        "symbol": "EURUSD=X",
        "name": "EUR/USD"
      },
      {
        "symbol": "BTC-USD",
        "name": "Bitcoin"
      }
    ]
  },
  {
    "category": "Ações Brasil",
    "assets": [
      {
        "symbol": "^BVSP",
        "name": "Mini Índice / Ibovespa (WIN)"
      },
      {
        "symbol": "PETR4.SA",
        "name": "Petrobras PN"
      },
      {
        "symbol": "VALE3.SA",
        "name": "Vale ON"
      },
      {
        "symbol": "ITUB4.SA",
        "name": "Itaú Unibanco PN"
      },
      {
        "symbol": "BBDC4.SA",
        "name": "Bradesco PN"
      },
      {
        "symbol": "BBAS3.SA",
        "name": "Banco do Brasil ON"
      },
      {
        "symbol": "ABEV3.SA",
        "name": "Ambev ON"
      },
      {
        "symbol": "WEGE3.SA",
        "name": "WEG ON"
      },
      {
        "symbol": "RENT3.SA",
        "name": "Localiza ON"
      },
      {
        "symbol": "EGIE3.SA",
        "name": "Engie Brasil ON"
      },
      {
        "symbol": "PRIO3.SA",
        "name": "PRIO ON"
      },
      {
        "symbol": "BRSR6.SA",
        "name": "Banrisul PNB"
      },
      {
        "symbol": "KLBN4.SA",
        "name": "Klabin PN"
      },
      {
        "symbol": "CXSE3.SA",
        "name": "Caixa Seguridade ON"
      },
      {
        "symbol": "BMGB4.SA",
        "name": "Banco BMG PN"
      },
      {
        "symbol": "BRKM5.SA",
        "name": "Braskem PNA"
      },
      {
        "symbol": "TASA4.SA",
        "name": "Taurus Armas PN"
      },
      {
        "symbol": "PMAM3.SA",
        "name": "Paranapanema ON"
      },
      {
        "symbol": "CMIG4.SA",
        "name": "Cemig PN"
      },
      {
        "symbol": "CPFE3.SA",
        "name": "CPFL Energia ON"
      },
      {
        "symbol": "POMO4.SA",
        "name": "Marcopolo PN"
      },
      {
        "symbol": "TAEE11.SA",
        "name": "Taesa Unit"
      },
      {
        "symbol": "BBSE3.SA",
        "name": "BB Seguridade ON"
      },
      {
        "symbol": "SUZB3.SA",
        "name": "Suzano ON"
      },
      {
        "symbol": "GGBR4.SA",
        "name": "Gerdau PN"
      },
      {
        "symbol": "CSNA3.SA",
        "name": "Siderúrgica Nacional ON"
      },
      {
        "symbol": "USIM5.SA",
        "name": "USIM5.SA"
      },
      {
        "symbol": "VIVT3.SA",
        "name": "VIVT3.SA"
      },
      {
        "symbol": "TIMS3.SA",
        "name": "TIMS3.SA"
      },
      {
        "symbol": "HAPV3.SA",
        "name": "HAPV3.SA"
      },
      {
        "symbol": "LREN3.SA",
        "name": "LREN3.SA"
      },
      {
        "symbol": "GRND3.SA",
        "name": "Grendene ON"
      }
    ]
  },
  {
    "category": "FIIs Brasil",
    "assets": [
      {
        "symbol": "HGLG11.SA",
        "name": "CSHG Logística"
      },
      {
        "symbol": "KNRI11.SA",
        "name": "Kinea Renda Imob."
      },
      {
        "symbol": "MXRF11.SA",
        "name": "Maxi Renda"
      },
      {
        "symbol": "VISC11.SA",
        "name": "Vinci Shopping"
      },
      {
        "symbol": "BTLG11.SA",
        "name": "BTG Logística"
      },
      {
        "symbol": "HGRE11.SA",
        "name": "CSHG Real Estate"
      },
      {
        "symbol": "KNIP11.SA",
        "name": "Kinea Índices"
      },
      {
        "symbol": "HSML11.SA",
        "name": "HSI Malls"
      },
      {
        "symbol": "GGRC11.SA",
        "name": "GGR Covepi"
      },
      {
        "symbol": "RBRR11.SA",
        "name": "RBR Rendimento"
      },
      {
        "symbol": "RBVA11.SA",
        "name": "Rio Bravo Renda"
      },
      {
        "symbol": "SNCI11.SA",
        "name": "Suno Recebíveis"
      },
      {
        "symbol": "TRXF11.SA",
        "name": "TRX Real Estate"
      },
      {
        "symbol": "XPLG11.SA",
        "name": "XP Log"
      },
      {
        "symbol": "CPTS11.SA",
        "name": "Capitânia Securities"
      },
      {
        "symbol": "VGIR11.SA",
        "name": "Valora RE"
      },
      {
        "symbol": "VRTA11.SA",
        "name": "Fator Verita"
      },
      {
        "symbol": "VINO11.SA",
        "name": "Vinci Offices"
      },
      {
        "symbol": "RECR11.SA",
        "name": "REC Renda Imob."
      },
      {
        "symbol": "HFOF11.SA",
        "name": "Hedge FOF"
      },
      {
        "symbol": "BTAL11.SA",
        "name": "BTG Agro Logística"
      },
      {
        "symbol": "TGAR11.SA",
        "name": "TGAR11.SA"
      },
      {
        "symbol": "ALZR11.SA",
        "name": "ALZR11.SA"
      }
    ]
  },
  {
    "category": "BDRs",
    "assets": [
      {
        "symbol": "NVDC34.SA",
        "name": "Nvidia BDR"
      },
      {
        "symbol": "AAPL34.SA",
        "name": "Apple BDR"
      },
      {
        "symbol": "MSFT34.SA",
        "name": "Microsoft BDR"
      },
      {
        "symbol": "GOGL34.SA",
        "name": "Alphabet (Google) BDR"
      },
      {
        "symbol": "AMZO34.SA",
        "name": "Amazon BDR"
      },
      {
        "symbol": "M1TA34.SA",
        "name": "Meta Platforms BDR"
      },
      {
        "symbol": "TSLA34.SA",
        "name": "Tesla BDR"
      },
      {
        "symbol": "AVGO34.SA",
        "name": "Broadcom BDR"
      },
      {
        "symbol": "TSMC34.SA",
        "name": "TSMC BDR"
      },
      {
        "symbol": "A1MD34.SA",
        "name": "AMD BDR"
      },
      {
        "symbol": "TMCO34.SA",
        "name": "Toyota BDR"
      },
      {
        "symbol": "BERK34.SA",
        "name": "Berkshire Hathaway BDR"
      },
      {
        "symbol": "JPMC34.SA",
        "name": "JPMorgan Chase BDR"
      },
      {
        "symbol": "VISA34.SA",
        "name": "Visa BDR"
      },
      {
        "symbol": "MSCD34.SA",
        "name": "Mastercard BDR"
      },
      {
        "symbol": "BOAC34.SA",
        "name": "Bank of America BDR"
      },
      {
        "symbol": "GSGI34.SA",
        "name": "Goldman Sachs BDR"
      },
      {
        "symbol": "WALM34.SA",
        "name": "Walmart BDR"
      },
      {
        "symbol": "COCA34.SA",
        "name": "Coca-Cola BDR"
      },
      {
        "symbol": "PEPB34.SA",
        "name": "PepsiCo BDR"
      },
      {
        "symbol": "MCDC34.SA",
        "name": "McDonald's BDR"
      },
      {
        "symbol": "DISB34.SA",
        "name": "Disney BDR"
      },
      {
        "symbol": "NFLX34.SA",
        "name": "Netflix BDR"
      },
      {
        "symbol": "NIKE34.SA",
        "name": "Nike BDR"
      },
      {
        "symbol": "COWC34.SA",
        "name": "Costco BDR"
      },
      {
        "symbol": "LILY34.SA",
        "name": "Eli Lilly BDR"
      },
      {
        "symbol": "N1VO34.SA",
        "name": "Novo Nordisk BDR"
      },
      {
        "symbol": "JNJB34.SA",
        "name": "Johnson & Johnson BDR"
      },
      {
        "symbol": "UNHH34.SA",
        "name": "UnitedHealth BDR"
      },
      {
        "symbol": "PFIZ34.SA",
        "name": "Pfizer BDR"
      },
      {
        "symbol": "EXXO34.SA",
        "name": "Exxon Mobil BDR"
      },
      {
        "symbol": "CHVX34.SA",
        "name": "Chevron BDR"
      },
      {
        "symbol": "CATP34.SA",
        "name": "Caterpillar BDR"
      },
      {
        "symbol": "BOEI34.SA",
        "name": "Boeing BDR"
      },
      {
        "symbol": "IVVB11.SA",
        "name": "iShares S&P 500 Fundo de Índice"
      },
      {
        "symbol": "BIVB39.SA",
        "name": "iShares Core S&P 500 BDR"
      },
      {
        "symbol": "NASD11.SA",
        "name": "Trend ETF Nasdaq 100"
      },
      {
        "symbol": "BNDA39.SA",
        "name": "Invesco QQQ Trust BDR"
      },
      {
        "symbol": "ACWI11.SA",
        "name": "Trend ETF MSCI ACWI"
      },
      {
        "symbol": "BACW39.SA",
        "name": "iShares MSCI ACWI BDR"
      },
      {
        "symbol": "SPCX34.SA",
        "name": "SpaceX BDR (Space Exploration)"
      }
    ]
  },
  {
    "category": "Ações EUA",
    "assets": [
      {
        "symbol": "AAPL",
        "name": "Apple"
      },
      {
        "symbol": "MSFT",
        "name": "Microsoft"
      },
      {
        "symbol": "GOOGL",
        "name": "Google (Alphabet)"
      },
      {
        "symbol": "AMZN",
        "name": "Amazon"
      },
      {
        "symbol": "NVDA",
        "name": "Nvidia"
      },
      {
        "symbol": "META",
        "name": "Meta Platforms"
      },
      {
        "symbol": "TSLA",
        "name": "Tesla"
      },
      {
        "symbol": "BRK-B",
        "name": "Berkshire Hathaway"
      },
      {
        "symbol": "JPM",
        "name": "JPMorgan Chase"
      },
      {
        "symbol": "V",
        "name": "Visa"
      },
      {
        "symbol": "JNJ",
        "name": "Johnson & Johnson"
      },
      {
        "symbol": "WMT",
        "name": "Walmart"
      },
      {
        "symbol": "PG",
        "name": "Procter & Gamble"
      },
      {
        "symbol": "MA",
        "name": "Mastercard"
      },
      {
        "symbol": "UNH",
        "name": "UnitedHealth"
      },
      {
        "symbol": "HD",
        "name": "Home Depot"
      },
      {
        "symbol": "DIS",
        "name": "Disney"
      },
      {
        "symbol": "ADBE",
        "name": "Adobe"
      },
      {
        "symbol": "NFLX",
        "name": "Netflix"
      },
      {
        "symbol": "CRM",
        "name": "Salesforce"
      },
      {
        "symbol": "KO",
        "name": "Coca-Cola"
      },
      {
        "symbol": "AMD",
        "name": "AMD"
      },
      {
        "symbol": "INTC",
        "name": "Intel"
      },
      {
        "symbol": "CSCO",
        "name": "Cisco"
      },
      {
        "symbol": "ABBV",
        "name": "AbbVie"
      },
      {
        "symbol": "CVX",
        "name": "Chevron"
      },
      {
        "symbol": "XOM",
        "name": "Exxon Mobil"
      },
      {
        "symbol": "PFE",
        "name": "Pfizer"
      },
      {
        "symbol": "IBM",
        "name": "IBM"
      },
      {
        "symbol": "MMM",
        "name": "3M"
      },
      {
        "symbol": "VZ",
        "name": "Verizon"
      },
      {
        "symbol": "T",
        "name": "AT&T"
      },
      {
        "symbol": "BA",
        "name": "Boeing"
      },
      {
        "symbol": "CAT",
        "name": "Caterpillar"
      },
      {
        "symbol": "GE",
        "name": "General Electric"
      },
      {
        "symbol": "GM",
        "name": "General Motors"
      },
      {
        "symbol": "F",
        "name": "Ford"
      },
      {
        "symbol": "UBER",
        "name": "Uber"
      },
      {
        "symbol": "LYFT",
        "name": "Lyft"
      },
      {
        "symbol": "TM",
        "name": "Toyota"
      },
      {
        "symbol": "SNAP",
        "name": "Snap"
      },
      {
        "symbol": "PINS",
        "name": "Pinterest"
      },
      {
        "symbol": "PYPL",
        "name": "PayPal"
      },
      {
        "symbol": "SHOP",
        "name": "Shopify"
      },
      {
        "symbol": "ZM",
        "name": "Zoom"
      },
      {
        "symbol": "DOCU",
        "name": "DocuSign"
      },
      {
        "symbol": "CRWD",
        "name": "CrowdStrike"
      },
      {
        "symbol": "NET",
        "name": "Cloudflare"
      },
      {
        "symbol": "O",
        "name": "Realty Income"
      },
      {
        "symbol": "SPG",
        "name": "Simon Property"
      },
      {
        "symbol": "PLD",
        "name": "Prologis"
      },
      {
        "symbol": "AMT",
        "name": "American Tower"
      },
      {
        "symbol": "CCI",
        "name": "Crown Castle"
      },
      {
        "symbol": "EQIX",
        "name": "Equinix"
      },
      {
        "symbol": "PSA",
        "name": "Public Storage"
      },
      {
        "symbol": "DLR",
        "name": "Digital Realty"
      },
      {
        "symbol": "WELL",
        "name": "Welltower"
      },
      {
        "symbol": "AVB",
        "name": "AvalonBay"
      },
      {
        "symbol": "EQR",
        "name": "Equity Residential"
      },
      {
        "symbol": "BXP",
        "name": "Boston Properties"
      },
      {
        "symbol": "VTR",
        "name": "Ventas"
      },
      {
        "symbol": "ARE",
        "name": "Alexandria RE"
      },
      {
        "symbol": "MAA",
        "name": "Mid-America Apt."
      },
      {
        "symbol": "UDR",
        "name": "UDR Inc."
      },
      {
        "symbol": "KIM",
        "name": "Kimco Realty"
      },
      {
        "symbol": "REG",
        "name": "Regency Centers"
      },
      {
        "symbol": "HST",
        "name": "Host Hotels"
      },
      {
        "symbol": "FRT",
        "name": "Federal Realty"
      },
      {
        "symbol": "NNN",
        "name": "NNN REIT"
      },
      {
        "symbol": "WPC",
        "name": "W. P. Carey"
      },
      {
        "symbol": "GLPI",
        "name": "Gaming and Leisure"
      }
    ]
  },
  {
    "category": "Commodities",
    "assets": [
      {
        "symbol": "GC=F",
        "name": "Gold (Ouro / XAUUSD)"
      },
      {
        "symbol": "SI=F",
        "name": "Silver (Prata)"
      },
      {
        "symbol": "CL=F",
        "name": "Crude Oil WTI (Petróleo)"
      },
      {
        "symbol": "BZ=F",
        "name": "Brent Oil (Petróleo Brent)"
      },
      {
        "symbol": "HG=F",
        "name": "Copper (Cobre)"
      },
      {
        "symbol": "NG=F",
        "name": "Natural Gas (Gás Natural)"
      },
      {
        "symbol": "ZC=F",
        "name": "Corn (Milho)"
      },
      {
        "symbol": "ZS=F",
        "name": "Soybeans (Soja)"
      },
      {
        "symbol": "ZW=F",
        "name": "Wheat (Trigo)"
      },
      {
        "symbol": "KC=F",
        "name": "Coffee (Café Arábica)"
      },
      {
        "symbol": "CT=F",
        "name": "Cotton (Algodão)"
      },
      {
        "symbol": "SB=F",
        "name": "Sugar (Açúcar)"
      },
      {
        "symbol": "LE=F",
        "name": "Live Cattle (Boi Gordo)"
      },
      {
        "symbol": "HE=F",
        "name": "Lean Hogs (Suínos)"
      }
    ]
  },
  {
    "category": "Forex",
    "assets": [
      {
        "symbol": "USDBRL=X",
        "name": "Mini Dólar (WDO / USDBRL)"
      },
      {
        "symbol": "EURUSD=X",
        "name": "EUR/USD"
      },
      {
        "symbol": "GBPUSD=X",
        "name": "GBP/USD"
      },
      {
        "symbol": "USDJPY=X",
        "name": "USD/JPY"
      },
      {
        "symbol": "USDCHF=X",
        "name": "USD/CHF"
      },
      {
        "symbol": "AUDUSD=X",
        "name": "AUD/USD"
      },
      {
        "symbol": "USDCAD=X",
        "name": "USD/CAD"
      },
      {
        "symbol": "NZDUSD=X",
        "name": "NZD/USD"
      },
      {
        "symbol": "EURJPY=X",
        "name": "EUR/JPY"
      },
      {
        "symbol": "GBPJPY=X",
        "name": "GBP/JPY"
      },
      {
        "symbol": "EURCHF=X",
        "name": "EUR/CHF"
      }
    ]
  },
  {
    "category": "Criptomoedas",
    "assets": [
      {
        "symbol": "BTC-USD",
        "name": "Bitcoin"
      },
      {
        "symbol": "ETH-USD",
        "name": "Ethereum"
      },
      {
        "symbol": "SOL-USD",
        "name": "Solana"
      }
    ]
  }
];

