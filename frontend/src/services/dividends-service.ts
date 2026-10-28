import type { B3MonthlyIncomeItem } from "@/types/portfolio";
import { formatMonthYearShort } from "@/lib/formatters";

export interface NormalizedMonthlyIncome {
  rawMonthYear: string;
  sortKey: string;
  shortLabel: string;
  year: string;
  dividendos: number;
  jcp: number;
  rendimentos: number;
  total: number;
}

export function parseMonthYearSortKey(raw: string): {
  sortKey: string;
  year: string;
  shortLabel: string;
} {
  const trimmed = (raw || "").trim();
  const isoMatch = trimmed.match(/^(\d{4})-(\d{2})/);
  if (isoMatch) {
    return {
      sortKey: `${isoMatch[1]}-${isoMatch[2]}`,
      year: isoMatch[1],
      shortLabel: formatMonthYearShort(trimmed),
    };
  }
  const brMatch = trimmed.match(/^(\d{2})\/(\d{4})$/);
  if (brMatch) {
    return {
      sortKey: `${brMatch[2]}-${brMatch[1]}`,
      year: brMatch[2],
      shortLabel: `${brMatch[1]}/${brMatch[2].slice(2)}`,
    };
  }
  return {
    sortKey: trimmed,
    year: trimmed.slice(0, 4) || "2026",
    shortLabel: trimmed,
  };
}

export function normalizeMonthlyIncomeSeries(
  items: B3MonthlyIncomeItem[]
): NormalizedMonthlyIncome[] {
  return (items || [])
    .map((item) => {
      const parsed = parseMonthYearSortKey(item.month_year);
      const dividendos = Number(item.dividendos) || 0;
      const jcp = Number(item.jcp) || 0;
      const rendimentos = Number(item.rendimentos) || 0;
      const total =
        Number(item.total) || dividendos + jcp + rendimentos;
      return {
        rawMonthYear: item.month_year,
        sortKey: parsed.sortKey,
        shortLabel: parsed.shortLabel,
        year: parsed.year,
        dividendos,
        jcp,
        rendimentos,
        total,
      };
    })
    .sort((a, b) => a.sortKey.localeCompare(b.sortKey));
}

export function aggregateAnnualIncomeSeries(
  normalized: NormalizedMonthlyIncome[]
): Array<{
  year: string;
  dividendos: number;
  jcp: number;
  rendimentos: number;
  total: number;
}> {
  const byYear = new Map<
    string,
    { year: string; dividendos: number; jcp: number; rendimentos: number; total: number }
  >();
  for (const item of normalized) {
    const existing = byYear.get(item.year) || {
      year: item.year,
      dividendos: 0,
      jcp: 0,
      rendimentos: 0,
      total: 0,
    };
    existing.dividendos += item.dividendos;
    existing.jcp += item.jcp;
    existing.rendimentos += item.rendimentos;
    existing.total += item.total;
    byYear.set(item.year, existing);
  }
  return Array.from(byYear.values()).sort((a, b) => a.year.localeCompare(b.year));
}
