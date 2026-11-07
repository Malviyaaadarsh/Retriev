import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  deleteDocument,
  getDocumentPreview,
  getDocuments,
  importDocuments,
  uploadDocument,
} from "../api/documents";
import { toast } from "sonner";

export function mapDocumentResponse(document) {
  const extension = document.file_type.toLowerCase();
  return {
    id: document.file_name,
    fileName: document.file_name,
    title: document.file_name,
    fileType: extension === "md" ? "markdown" : extension,
    sizeBytes: document.size_bytes,
    size: `${(document.size_bytes / 1024).toFixed(1)} KB`,
    chunkCount: null,
    status: document.status === "indexed" ? "Indexed" : "Uploaded",
    isIndexed: document.status === "indexed",
    uploadedAt: "Uploaded",
  };
}

export function useDocuments(workspaceId) {
  const queryClient = useQueryClient();
  const queryKey = ["documents", workspaceId];
  const documents = useQuery({
    queryKey,
    queryFn: async () => {
      const response = await getDocuments(workspaceId);
      return response.map(mapDocumentResponse);
    },
    enabled: Boolean(workspaceId),
    retry: 10,
    retryDelay: () => 1000,
    refetchOnReconnect: true,
  });

  const upload = useMutation({
    mutationFn: (file) => uploadDocument(workspaceId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
      toast.success("Document Uploaded");
    },
    onError: (error) => toast.error(error.message || "Upload Failed"),
  });

  const nativeImport = useMutation({
    mutationFn: (paths) => importDocuments(workspaceId, paths),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey });
      toast.success(`${result.imported} document${result.imported === 1 ? "" : "s"} imported`);
    },
    onError: (error) => toast.error(error.message || "Native import failed"),
  });

  const remove = useMutation({
    mutationFn: (fileName) => deleteDocument(workspaceId, fileName),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
      toast.success("Document Deleted");
    },
    onError: (error) => toast.error(error.message || "Document deletion failed"),
  });

  const preview = useMutation({
    mutationFn: (fileName) => getDocumentPreview(workspaceId, fileName),
    onError: (error) => toast.error(error.message || "Preview Failed"),
  });

  return {
    ...documents,
    uploadDocument: upload.mutateAsync,
    importDocuments: nativeImport.mutateAsync,
    deleteDocument: remove.mutateAsync,
    getDocumentPreview: preview.mutateAsync,
    isUploading: upload.isPending,
    isImporting: nativeImport.isPending,
    isDeleting: remove.isPending,
    isPreviewing: preview.isPending,
  };
}
