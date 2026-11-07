import { useState, useRef } from "react";
import { confirm, open } from "@tauri-apps/plugin-dialog";
import { useWorkspace } from "../../context/WorkspaceContext";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import {
  Files,
  FileText,
  UploadCloud,
  Trash2,
  Eye,
  FolderKanban,
  CheckCircle2,
  HardDrive,
  Layers,
  Search,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button as DialogButton } from "@/components/ui/button";

export function DocumentsView() {
  const {
    activeWorkspace,
    activeDocuments,
    isDocumentsLoading,
    isDocumentsError,
    uploadDocument,
    importDocuments,
    deleteDocument,
    getDocumentPreview,
    isUploading,
    isImporting,
    isDeleting,
    isPreviewing,
    runIngestion,
    isIngesting,
    setPreviewDocument,
  } = useWorkspace();

  const [searchFilter, setSearchFilter] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [ingestionResult, setIngestionResult] = useState(null);
  const fileInputRef = useRef(null);

  // Filter documents by title
  const filteredDocs = activeDocuments.filter((doc) =>
    doc.fileName.toLowerCase().includes(searchFilter.toLowerCase())
  );

  // Total stats
  const totalChunks = activeDocuments.filter((document) => document.isIndexed).length > 0
    ? "Indexed"
    : "—";
  const totalSize = activeDocuments.reduce((acc, d) => acc + (d.sizeBytes || 0), 0);
  const formattedTotalSize = `${(totalSize / (1024 * 1024)).toFixed(2)} MB`;

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const handleFiles = async (files) => {
    for (const file of files) {
      try {
        await uploadDocument(file);
      } catch {
        // The API hook displays the normalized error toast.
      }
    }
  };

  const handleNativeImport = async (directory) => {
    try {
      const selected = await open({
        multiple: true,
        directory,
        title: directory ? "Select folders to import" : "Select documents to import",
      });
      if (!selected) return;
      await importDocuments(Array.isArray(selected) ? selected : [selected]);
    } catch {
      // The mutation displays the normalized import error.
    }
  };

  const handlePreview = async (document) => {
    try {
      const preview = await getDocumentPreview(document.fileName);
      setPreviewDocument({
        ...document,
        fileType: preview.file_type,
        excerpt: preview.preview,
      });
    } catch {
      // The API hook displays the normalized error toast.
    }
  };

  const handleDelete = async (document) => {
    const message = `Delete "${document.fileName}"?\n\nThis action cannot be undone.`;
    const confirmed = window.__TAURI_INTERNALS__
      ? await confirm(message, {
        title: "Delete document",
        kind: "warning",
      })
      : window.confirm(message);
    if (!confirmed) {
      return;
    }
    try {
      await deleteDocument(document.fileName);
    } catch {
      // The API hook displays the normalized error toast.
    }
  };

  const handleIngestion = async () => {
    try {
      setIngestionResult(await runIngestion());
    } catch {
      // The API hook displays the normalized error toast.
    }
  };

  const getFileIcon = (fileType) => {
    switch (fileType) {
      case "pdf":
        return <FileText className="size-5 text-rose-500" />;
      case "markdown":
      case "md":
        return <FileText className="size-5 text-blue-500" />;
      case "csv":
        return <FileText className="size-5 text-amber-500" />;
      case "docx":
        return <FileText className="size-5 text-violet-500" />;
      default:
        return <FileText className="size-5 text-emerald-500" />;
    }
  };

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col overflow-y-auto bg-background p-4 sm:p-6 lg:p-8">
      <div className="mx-auto w-full max-w-5xl space-y-6">
        {/* Workspace Title & Stats Banner */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <FolderKanban className="size-4" />
              </span>
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
                {activeWorkspace?.name || "Workspace"} Documents
              </h1>
            </div>
            <p className="mt-1 text-xs sm:text-sm text-muted-foreground">
              Knowledge base files scoped exclusively to this workspace.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="default"
              size="sm"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="gap-1.5 text-xs shadow-xs"
            >
              <UploadCloud className="size-3.5" />
              <span>Upload Document</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleNativeImport(false)}
              disabled={isImporting}
              className="gap-1.5 text-xs"
            >
              <HardDrive className="size-3.5" />
              <span>{isImporting ? "Importing..." : "Import from Disk"}</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleNativeImport(true)}
              disabled={isImporting}
              className="gap-1.5 text-xs"
            >
              <FolderKanban className="size-3.5" />
              <span>Import Folder</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleIngestion}
              disabled={isIngesting || activeDocuments.length === 0}
              className="gap-1.5 text-xs"
            >
              {isIngesting && <Loader2 className="size-3.5 animate-spin" />}
              <span>{isIngesting ? "Indexing Workspace..." : "Ingest my Docs"}</span>
            </Button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileInputChange}
              className="hidden"
              multiple
              accept=".pdf,.txt,.md,.csv,.docx"
            />
          </div>
        </div>

        {/* Quick Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Card className="p-3 bg-card/60">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Files className="size-3.5 text-primary" />
              <span className="text-xs font-medium">Total Documents</span>
            </div>
            <p className="mt-1.5 text-xl font-bold text-foreground">
              {activeDocuments.length}
            </p>
          </Card>

          <Card className="p-3 bg-card/60">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Layers className="size-3.5 text-emerald-500" />
              <span className="text-xs font-medium">Indexed Chunks</span>
            </div>
            <p className="mt-1.5 text-xl font-bold text-foreground">
              {totalChunks}
            </p>
          </Card>

          <Card className="p-3 bg-card/60">
            <div className="flex items-center gap-2 text-muted-foreground">
              <HardDrive className="size-3.5 text-sky-500" />
              <span className="text-xs font-medium">Storage Volume</span>
            </div>
            <p className="mt-1.5 text-xl font-bold text-foreground">
              {formattedTotalSize}
            </p>
          </Card>

          <Card className="p-3 bg-card/60">
            <div className="flex items-center gap-2 text-muted-foreground">
              <CheckCircle2 className="size-3.5 text-amber-500" />
              <span className="text-xs font-medium">Formats Supported</span>
            </div>
            <p className="mt-1.5 text-xs font-semibold text-foreground font-mono">
                .pdf, .txt, .md, .csv, .docx
            </p>
          </Card>
        </div>

        {/* Upload Dropzone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative cursor-pointer rounded-2xl border-2 border-dashed p-6 sm:p-8 text-center transition-all ${
            isDragging
              ? "border-primary bg-primary/5 scale-[1.005]"
              : "border-border/80 bg-card/40 hover:border-primary/40 hover:bg-muted/30"
          }`}
        >
          <div className="mx-auto flex size-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <UploadCloud className="size-6" />
          </div>
          <h3 className="mt-3 text-sm font-semibold text-foreground">
            Drop files here or click to browse
          </h3>
          <p className="mt-1 text-xs text-muted-foreground">
            Supports .pdf, .md, .csv, .docx, .txt files
          </p>
          
        </div>

        {/* Documents Table / List Section */}
        <div className="space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
              <span>Indexed Files</span>
              <Badge variant="secondary" className="text-[10px] px-1.5 py-0 h-4">
                {filteredDocs.length} of {activeDocuments.length}
              </Badge>
            </h2>

            {/* Filter Input */}
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 size-3.5 text-muted-foreground" />
              <input
                type="text"
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                placeholder="Filter files..."
                className="w-full rounded-lg border border-border bg-card/60 pl-8 pr-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          </div>

          {isDocumentsLoading ? (
            <Card className="p-6 space-y-3">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </Card>
          ) : isDocumentsError ? (
            <Card className="p-8 text-center bg-card/40">
              <AlertCircle className="mx-auto size-10 text-destructive/70" />
              <p className="mt-2 text-sm font-medium text-foreground">Unable to load documents</p>
              <p className="mt-1 text-xs text-muted-foreground">Unable to connect to Retriev backend.</p>
            </Card>
          ) : activeDocuments.length === 0 ? (
            <Card className="p-8 text-center bg-card/40">
              <Files className="mx-auto size-10 text-muted-foreground/50" />
              <p className="mt-2 text-sm font-medium text-foreground">No documents in this workspace</p>
              <p className="mt-1 text-xs text-muted-foreground">
              Upload files to start building your knowledge base.
              </p>
            </Card>
          ) : filteredDocs.length === 0 ? (
            <Card className="p-6 text-center bg-card/40">
              <p className="text-xs text-muted-foreground">
                No documents match "{searchFilter}".
              </p>
            </Card>
          ) : (
            <div className="divide-y divide-border/60 rounded-xl border border-border/80 bg-card overflow-hidden shadow-xs">
              {filteredDocs.map((doc) => (
                <div
                  key={doc.id}
                  className="group flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 transition-colors hover:bg-muted/40"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-background ring-1 ring-foreground/10">
                      {getFileIcon(doc.fileType)}
                    </div>
                    <div className="min-w-0 truncate">
                      <p className="text-xs sm:text-sm font-medium text-foreground truncate">
                        {doc.fileName}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5 text-[11px] text-muted-foreground">
                        <span className="uppercase font-mono text-[10px] font-semibold">
                          {doc.fileType}
                        </span>
                        <span>•</span>
                        <span>{doc.size}</span>
                        <span>•</span>
                        <span>{doc.isIndexed ? "Indexed" : "Awaiting ingestion"}</span>
                        <span>•</span>
                        <span>{doc.uploadedAt}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0 self-end sm:self-center">
                    <Badge
                      variant="secondary"
                      className="text-[10px] uppercase font-semibold tracking-wider text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
                    >
                      {doc.isIndexed ? "Indexed" : "Uploaded"}
                    </Badge>

                    <Button
                      variant="outline"
                      size="xs"
                      onClick={() => handlePreview(doc)}
                      disabled={isPreviewing}
                      className="h-7 gap-1 text-xs border-border/80 hover:bg-muted"
                      title="Inspect document excerpt"
                    >
                      <Eye className="size-3" />
                      <span>Preview</span>
                    </Button>

                    <Button
                      variant="ghost"
                      size="icon-xs"
                      onClick={() => handleDelete(doc)}
                      disabled={isDeleting}
                      className="size-7 text-muted-foreground hover:text-destructive"
                      title="Remove document from workspace"
                    >
                      <Trash2 className="size-3.5" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      <Dialog open={Boolean(ingestionResult)} onOpenChange={(open) => !open && setIngestionResult(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Workspace Indexed Successfully</DialogTitle>
            <DialogDescription>Documents have been processed and stored for retrieval.</DialogDescription>
          </DialogHeader>
          {ingestionResult && (
            <div className="grid grid-cols-2 gap-3 text-sm">
              <span>Files Processed</span><strong>{ingestionResult.files_processed}</strong>
              <span>Chunks Generated</span><strong>{ingestionResult.chunks_generated}</strong>
              <span>Embeddings Generated</span><strong>{ingestionResult.embeddings_generated}</strong>
              <span>Vectors Stored</span><strong>{ingestionResult.vectors_stored}</strong>
              <span>Execution Time</span><strong>{ingestionResult.total_time_seconds.toFixed(2)}s</strong>
            </div>
          )}
          <DialogFooter>
            <DialogButton onClick={() => setIngestionResult(null)}>Close</DialogButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
