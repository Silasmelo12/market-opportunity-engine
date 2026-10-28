import * as React from "react";
import { useAppContext } from "@/state/app-context";
import { formatCurrencyBRL } from "@/lib/formatters";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { AppIcon } from "@/components/layout/SvgSprite";

export function NewTransactionDialog() {
  const {
    isNewTradeModalOpen,
    setIsNewTradeModalOpen,
    isMetasModalOpen,
    setIsMetasModalOpen,
    addOrUpdateManualHolding,
    portfolio,
    updatePortfolio,
    showToast,
  } = useAppContext();

  const [operation, setOperation] = React.useState<"BUY" | "SELL">("BUY");
  const [assetClass, setAssetClass] = React.useState<string>("acao_br");
  const [ticker, setTicker] = React.useState<string>("");
  const [shares, setShares] = React.useState<string>("");
  const [price, setPrice] = React.useState<string>("");
  const [tradeDate, setTradeDate] = React.useState<string>("2026-10-28");

  React.useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsNewTradeModalOpen(false);
        setIsMetasModalOpen(false);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [setIsNewTradeModalOpen, setIsMetasModalOpen]);

  const numericShares = Number(shares.replace(",", ".")) || 0;
  const numericPrice = Number(price.replace(",", ".")) || 0;
  const totalPreview = numericShares * numericPrice;

  const handleSaveTrade = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticker.trim() || numericShares <= 0) {
      showToast("Preencha o ticker e uma quantidade maior que zero.", "warning");
      return;
    }
    addOrUpdateManualHolding({
      ticker: ticker.trim(),
      shares: numericShares,
      average_buy_price: numericPrice,
      asset_class: assetClass,
      operation,
    });
    setTicker("");
    setShares("");
    setPrice("");
    setIsNewTradeModalOpen(false);
    showToast("Lançamento registrado na custódia com sucesso!", "success");
  };

  return (
    <>
      {/* Modal 10: Novo Lançamento Manual */}
      <div
        id="modal-new-trade"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-new-trade-title"
        className={`fixed inset-0 z-50 flex items-center justify-center bg-canvas/75 p-4 backdrop-blur-sm ${
          isNewTradeModalOpen ? "" : "hidden"
        }`}
      >
        <form
          onSubmit={handleSaveTrade}
          className="card-surface w-full max-w-xl space-y-4 rounded-xl border border-border bg-surface p-6 shadow-lg"
        >
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div>
              <h2
                id="modal-new-trade-title"
                className="font-sans text-base font-bold text-foreground"
              >
                Novo Lançamento Manual na Carteira
              </h2>
              <p className="text-xs text-muted-foreground">
                Registre compras ou vendas para atualizar automaticamente seu preço médio e custódia
              </p>
            </div>
            <button
              type="button"
              aria-label="Fechar modal de novo lançamento"
              onClick={() => setIsNewTradeModalOpen(false)}
              className="btn-icon h-8 w-8 rounded-md"
            >
              <AppIcon name="icon-x" className="h-4 w-4" />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              aria-pressed={operation === "BUY"}
              onClick={() => setOperation("BUY")}
              className={`modal-trade-type-btn rounded-md border py-2 font-sans text-xs font-bold transition-all ${
                operation === "BUY"
                  ? "bg-success-soft text-success border-success-border"
                  : "bg-surface text-muted-foreground border-border"
              }`}
            >
              ▲ Compra / Aporte
            </button>
            <button
              type="button"
              aria-pressed={operation === "SELL"}
              onClick={() => setOperation("SELL")}
              className={`modal-trade-type-btn rounded-md border py-2 font-sans text-xs font-bold transition-all ${
                operation === "SELL"
                  ? "bg-danger-soft text-danger border-danger-border"
                  : "bg-surface text-muted-foreground border-border"
              }`}
            >
              ▼ Venda / Baixa
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <Label htmlFor="modal-trade-ticker">Ticker do Ativo</Label>
              <Input
                id="modal-trade-ticker"
                placeholder="Ex: ITUB4.SA"
                mono
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
              />
            </div>

            <div>
              <Label htmlFor="modal-trade-class">Classe do Ativo</Label>
              <Select
                id="modal-trade-class"
                value={assetClass}
                onChange={(e) => setAssetClass(e.target.value)}
              >
                <option value="acao_br">Ações Brasil</option>
                <option value="fii">Fundos Imobiliários (FIIs)</option>
                <option value="bdr">BDRs & Exterior</option>
                <option value="etf">ETFs</option>
                <option value="cripto">Criptoativos</option>
              </Select>
            </div>

            <div>
              <Label htmlFor="modal-trade-shares">Quantidade</Label>
              <Input
                id="modal-trade-shares"
                type="number"
                step="any"
                placeholder="50"
                mono
                value={shares}
                onChange={(e) => setShares(e.target.value)}
              />
            </div>

            <div>
              <Label htmlFor="modal-trade-price">Preço Unitário (R$)</Label>
              <Input
                id="modal-trade-price"
                type="number"
                step="0.01"
                placeholder="40.00"
                mono
                value={price}
                onChange={(e) => setPrice(e.target.value)}
              />
            </div>

            <div className="sm:col-span-2">
              <Label htmlFor="modal-trade-date">Data da Operação</Label>
              <Input
                id="modal-trade-date"
                type="date"
                mono
                value={tradeDate}
                onChange={(e) => setTradeDate(e.target.value)}
              />
            </div>
          </div>

          <div className="flex items-center justify-between rounded-md bg-surface-subtle p-3">
            <span className="text-xs font-semibold text-muted-foreground">
              Valor Financeiro Estimado:
            </span>
            <span
              id="modal-trade-total-preview"
              className="font-mono text-base font-extrabold text-foreground"
            >
              {formatCurrencyBRL(totalPreview)}
            </span>
          </div>

          <div className="flex items-center justify-end gap-2 border-t border-border pt-3">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setIsNewTradeModalOpen(false)}
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              id="btn-modal-trade-save"
              variant="primary"
              size="sm"
            >
              Salvar Lançamento
            </Button>
          </div>
        </form>
      </div>

      {/* Modal 3: Metas de Alocação por Classe */}
      <div
        id="modal-allocation-goals"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-goals-title"
        className={`fixed inset-0 z-50 flex items-center justify-center bg-canvas/75 p-4 backdrop-blur-sm ${
          isMetasModalOpen ? "" : "hidden"
        }`}
      >
        <div className="card-surface w-full max-w-md space-y-4 rounded-xl border border-border bg-surface p-6 shadow-lg">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <h2
              id="modal-goals-title"
              className="font-sans text-base font-bold text-foreground"
            >
              Metas de Alocação por Classe (%)
            </h2>
            <button
              type="button"
              aria-label="Fechar modal de metas"
              onClick={() => setIsMetasModalOpen(false)}
              className="btn-icon h-8 w-8 rounded-md"
            >
              <AppIcon name="icon-x" className="h-4 w-4" />
            </button>
          </div>
          <p className="text-xs text-muted-foreground">
            Defina os percentuais-alvo para orientar o rebalanceamento da carteira.
          </p>
          <div className="flex justify-end gap-2 border-t border-border pt-3">
            <Button
              type="button"
              variant="primary"
              size="sm"
              onClick={() => {
                updatePortfolio((prev) => ({ ...prev }));
                setIsMetasModalOpen(false);
              }}
            >
              Concluir
            </Button>
          </div>
        </div>
      </div>

      {/* Modal 4: Confirmação de Ordens (Pre-flight) */}
      <div
        id="modal-order-preflight"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-preflight-title"
        className="fixed inset-0 z-50 hidden items-center justify-center bg-canvas/75 p-4 backdrop-blur-sm"
      >
        <div className="card-surface w-full max-w-md rounded-xl border border-border bg-surface p-6 shadow-lg">
          <h2
            id="modal-preflight-title"
            className="font-sans text-base font-bold text-foreground"
          >
            Revisão de Ordens Sugeridas
          </h2>
        </div>
      </div>
    </>
  );
}
