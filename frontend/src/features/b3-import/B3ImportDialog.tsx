import * as React from "react";
import { useAppContext } from "@/state/app-context";
import { syncLocalB3Folder, uploadB3Files } from "@/services/portfolio-service";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AppIcon } from "@/components/layout/SvgSprite";

export function B3ImportDialog() {
  const {
    isB3ModalOpen,
    setIsB3ModalOpen,
    updatePortfolio,
    showToast,
    setLoadingText,
  } = useAppContext();

  const [selectedFiles, setSelectedFiles] = React.useState<File[]>([]);
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);

  React.useEffect(() => {
    if (!isB3ModalOpen) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsB3ModalOpen(false);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [isB3ModalOpen, setIsB3ModalOpen]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setSelectedFiles((prev) => [...prev, ...files]);
  };

  const handleProcessFiles = async () => {
    if (!selectedFiles.length) {
      showToast("Selecione ao menos um arquivo B3 (.xlsx ou .csv).", "warning");
      return;
    }
    setLoadingText("Conciliando extratos B3...");
    try {
      const resp = await uploadB3Files(selectedFiles);
      updatePortfolio((prev) => ({
        ...prev,
        holdings: resp.holdings || prev.holdings,
        b3TotalIncome: resp.total_income ?? prev.b3TotalIncome,
        b3MonthlyIncome: resp.monthly_income || prev.b3MonthlyIncome,
        b3Timeline: resp.timeline || prev.b3Timeline,
      }));
      showToast("Importação e conciliação B3 concluídas!", "success");
      setSelectedFiles([]);
      setIsB3ModalOpen(false);
    } catch (err) {
      showToast(
        err instanceof Error ? err.message : "Erro ao processar arquivos B3",
        "error"
      );
    } finally {
      setLoadingText(null);
    }
  };

  const handleSyncLocalFolder = async () => {
    setLoadingText("Sincronizando diretório local B3/...");
    try {
      const resp = await syncLocalB3Folder();
      updatePortfolio((prev) => ({
        ...prev,
        holdings: resp.holdings || prev.holdings,
        b3TotalIncome: resp.total_income ?? prev.b3TotalIncome,
        b3MonthlyIncome: resp.monthly_income || prev.b3MonthlyIncome,
        b3Timeline: resp.timeline || prev.b3Timeline,
      }));
      showToast("Diretório local B3 sincronizado com sucesso!", "success");
      setIsB3ModalOpen(false);
    } catch (err) {
      showToast(
        err instanceof Error ? err.message : "Erro ao sincronizar pasta B3",
        "error"
      );
    } finally {
      setLoadingText(null);
    }
  };

  return (
    <div
      id="modal-b3-import"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-b3-title"
      className={`fixed inset-0 z-50 flex items-center justify-center bg-canvas/75 p-4 backdrop-blur-sm ${
        isB3ModalOpen ? "" : "hidden"
      }`}
    >
      <div className="card-surface w-full max-w-2xl space-y-4 rounded-xl border border-border bg-surface p-6 shadow-lg">
        <div className="flex items-center justify-between border-b border-border pb-3">
          <div>
            <h2
              id="modal-b3-title"
              className="font-sans text-base font-bold text-foreground"
            >
              Importação e Conciliação de Extratos B3
            </h2>
            <p className="text-xs text-muted-foreground">
              Envie arquivos de Negociação, Movimentação ou Posição (.xlsx, .csv) com desduplicação automática
            </p>
          </div>
          <button
            type="button"
            aria-label="Fechar modal de importação B3"
            onClick={() => setIsB3ModalOpen(false)}
            className="btn-icon h-8 w-8 rounded-md"
          >
            <AppIcon name="icon-x" className="h-4 w-4" />
          </button>
        </div>

        <div
          id="modal-b3-dropzone"
          onClick={() => fileInputRef.current?.click()}
          className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-border-strong bg-surface-subtle p-6 text-center transition-colors hover:bg-surface-hover"
        >
          <AppIcon name="icon-import" className="h-6 w-6 text-primary" />
          <p className="font-sans text-xs font-bold text-foreground">
            Clique para selecionar ou arraste seus relatórios oficiais da B3
          </p>
          <p className="text-[11px] text-muted-foreground">
            Suporta múltiplos arquivos simultâneos (Negociação, Movimentação de Proventos e Custódia)
          </p>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".xlsx,.xls,.csv"
            className="hidden"
            aria-label="Selecionar arquivos B3 para conciliação"
            onChange={handleFileChange}
          />
        </div>

        <div id="modal-b3-files-list" className="space-y-1.5 text-xs">
          {selectedFiles.length === 0 ? (
            <p className="text-muted-foreground">
              Nenhum arquivo na fila de processamento.
            </p>
          ) : (
            selectedFiles.map((f, idx) => (
              <div
                key={`${f.name}-${idx}`}
                className="flex items-center justify-between rounded-md bg-surface-subtle px-3 py-1.5"
              >
                <span className="font-mono font-semibold text-foreground">
                  {f.name}
                </span>
                <Badge intent="primary">Pronto</Badge>
              </div>
            ))
          )}
        </div>

        <div className="flex flex-wrap items-center justify-between gap-2 border-t border-border pt-3">
          <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={handleSyncLocalFolder}
          >
            Sincronizar Pasta Local B3/
          </Button>
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setIsB3ModalOpen(false)}
            >
              Cancelar
            </Button>
            <Button
              type="button"
              id="btn-modal-b3-process"
              variant="primary"
              size="sm"
              onClick={handleProcessFiles}
            >
              Processar e Conciliar
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
