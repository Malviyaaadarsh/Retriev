import { useWorkspace } from "../../context/WorkspaceContext";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  FileText,
  Layers,
  CheckCircle2,
  BookOpen,
} from "lucide-react";

export function DocumentPreviewDialog() {
  const { previewDocument, setPreviewDocument } = useWorkspace();

  if (!previewDocument) return null;

  return (
    <Dialog open={!!previewDocument} onOpenChange={(open) => !open && setPreviewDocument(null)}>
      <DialogContent className="sm:max-w-xl p-0 overflow-hidden rounded-2xl border-border bg-card">
        <DialogHeader className="p-4 sm:p-5 border-b border-border/80 bg-muted/30">
          <div className="flex items-start gap-3">
            <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary mt-0.5">
              <FileText className="size-5" />
            </div>
            <div className="min-w-0">
              <DialogTitle className="text-sm sm:text-base font-semibold text-foreground truncate">
                {previewDocument.fileName || previewDocument.title}
              </DialogTitle>
              <DialogDescription className="text-xs text-muted-foreground flex items-center gap-2 mt-1">
                <span className="uppercase font-mono text-[10px] font-semibold">{previewDocument.fileType}</span>
                {previewDocument.size && <><span>{previewDocument.size}</span><span>•</span></>}
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="p-4 sm:p-5 space-y-4">
          {/* Metadata badges */}
          <div className="flex flex-wrap items-center gap-2">
            <Badge
              variant="secondary"
              className="text-[10px] uppercase font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
            >
              <CheckCircle2 className="size-3 mr-1" />
              Status: {previewDocument.status || "Uploaded"}
            </Badge>

            <Badge variant="outline" className="text-[10px] text-muted-foreground">
              <Layers className="size-3 mr-1" />
              {previewDocument.isIndexed ? "Indexed" : "Awaiting ingestion"}
            </Badge>
            {previewDocument.page && (
              <Badge variant="outline" className="text-[10px] text-muted-foreground">
                Page {previewDocument.page}
              </Badge>
            )}

          </div>

          {/* Excerpt preview */}
          <div>
            <label className="text-xs font-semibold text-foreground block mb-2 flex items-center gap-1.5">
              <BookOpen className="size-3.5 text-primary" />
              <span>Extracted Passage</span>
            </label>
            <div className="max-h-56 overflow-y-auto rounded-xl border border-border/80 bg-muted/30 p-3.5 font-mono text-xs leading-relaxed text-foreground select-text whitespace-pre-wrap">
              {previewDocument.excerpt || "No preview text available for this item."}
            </div>
          </div>

          <p className="text-[11px] text-muted-foreground">
            Preview content is provided by the backend extraction service and limited to 3000 characters.
          </p>
        </div>

        <DialogFooter className="p-4 border-t border-border/80 bg-muted/20">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPreviewDocument(null)}
            className="text-xs"
          >
            Close Preview
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
