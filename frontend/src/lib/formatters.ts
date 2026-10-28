export type AssetCategoryKey =
  | "fii"
  | "acao_br"
  | "bdr"
  | "cripto"
  | "etf"
  | "commodities"
  | "fx"
  | "us_equities";

const KNOWN_FIIS = new Set([
  "MXRF11", "HGLG11", "KNRI11", "XPML11", "VISC11", "BTLG11",
  "KNCR11", "KNIP11", "XPLG11", "IRDM11", "CPTS11", "HGRU11",
  "TGAR11", "BRCO11", "HSML11", "PVBI11", "RBRR11", "VGIR11",
  "RECR11", "BCFF11", "HGBS11", "LVBI11", "TRXF11", "ALZR11",
  "VILG11", "GGRC11", "JSRE11", "KNHY11", "RZTR11", "URPR11",
]);

const KNOWN_ETFS = new Set([
  "BOVA11", "IVVB11", "SMAL11", "HASH11", "NASD11", "SPXI11",
  "XINA11", "GOLD11", "DIVO11", "PIBB11", "MATB11", "FIND11",
]);

export function formatCurrencyBRL(value: number | null | undefined): string {
  const num = Number(value);
  if (!Number.isFinite(num)) return "R$ 0,00";
  return num
    .toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
    .replace(/\u00A0/g, " ");
}

export function formatSignedCurrencyBRL(value: number | null | undefined): string {
  const num = Number(value);
  if (!Number.isFinite(num)) return "R$ 0,00";
  const absFormatted = Math.abs(num)
    .toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
    .replace(/\u00A0/g, " ");
  if (num > 0.0001) return `+${absFormatted}`;
  if (num < -0.0001) return `-${absFormatted}`;
  return absFormatted;
}

export function formatPercentPtBr(
  value: number | null | undefined,
  decimals = 2,
  signed = false
): string {
  const num = Number(value);
  if (!Number.isFinite(num)) return "0,00%";
  const formatted = Math.abs(num).toLocaleString("pt-BR", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  if (signed) {
    if (num > 0.0001) return `+${formatted}%`;
    if (num < -0.0001) return `-${formatted}%`;
  } else if (num < -0.0001) {
    return `-${formatted}%`;
  }
  return `${formatted}%`;
}

export function formatQuantityPtBr(value: number | null | undefined): string {
  const num = Number(value);
  if (!Number.isFinite(num)) return "0";
  const isInt = Math.abs(num - Math.round(num)) < 1e-6;
  return num.toLocaleString("pt-BR", {
    minimumFractionDigits: isInt ? 0 : 2,
    maximumFractionDigits: isInt ? 0 : 4,
  });
}

export function sanitizeTickerQueryParam(raw: string | null | undefined): string | null {
  if (!raw || typeof raw !== "string") return null;
  let decoded = raw.trim();
  try {
    decoded = decodeURIComponent(decoded).trim();
  } catch {
    // Keep raw trimmed string if already decoded
  }
  const upper = decoded.toUpperCase();
  if (!upper || upper.length > 18) return null;
  if (!/^[A-Z0-9.^=-]{1,18}$/.test(upper)) return null;
  if (upper.includes("SCRIPT") || upper.includes("HTTP")) return null;
  return upper;
}

export function classifyAssetCategory(ticker: string): {
  key: AssetCategoryKey;
  label: string;
  shortBadge: string;
} {
  const clean = (ticker || "").toUpperCase().replace(/\.SA$/, "").trim();
  if (clean.endsWith("-USD") || clean === "BTC" || clean === "ETH" || clean === "SOL") {
    return { key: "cripto", label: "Criptoativos", shortBadge: "Cripto" };
  }
  if (clean.endsWith("=F")) {
    return { key: "commodities", label: "Commodities", shortBadge: "Comm" };
  }
  if (clean.endsWith("=X")) {
    return { key: "fx", label: "Moedas & FX", shortBadge: "FX" };
  }
  if (KNOWN_ETFS.has(clean)) {
    return { key: "etf", label: "ETFs", shortBadge: "ETF" };
  }
  if (KNOWN_FIIS.has(clean) || /^[A-Z]{4}11B?$/.test(clean)) {
    return { key: "fii", label: "Fundos Imobiliários (FIIs)", shortBadge: "FII" };
  }
  if (/^[A-Z]{4}(31|32|33|34|35|39)$/.test(clean)) {
    return { key: "bdr", label: "BDRs & Internacionais", shortBadge: "BDR" };
  }
  if (/^[A-Z]{4}[345678]$/.test(clean) || ticker.toUpperCase().endsWith(".SA")) {
    return { key: "acao_br", label: "Ações Brasil", shortBadge: "Ação" };
  }
  return { key: "us_equities", label: "Exterior & Global", shortBadge: "Global" };
}

export function formatMonthYearShort(monthYear: string): string {
  const raw = (monthYear || "").trim();
  const matchIso = raw.match(/^(\d{4})-(\d{2})/);
  if (matchIso) {
    return `${matchIso[2]}/${matchIso[1].slice(2)}`;
  }
  const matchBr = raw.match(/^(\d{2})\/(\d{4})$/);
  if (matchBr) {
    return `${matchBr[1]}/${matchBr[2].slice(2)}`;
  }
  return raw;
}
