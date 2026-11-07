import { useMutation, useQueryClient } from "@tanstack/react-query";
import { runIngestion } from "../api/ingestion";
import { toast } from "sonner";

export function useIngestion(workspaceId) {
  const queryClient = useQueryClient();
  const ingestion = useMutation({
    mutationFn: () => runIngestion(workspaceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", workspaceId] });
      toast.success("Ingestion Complete");
    },
    onError: (error) => toast.error(error.message || "Ingestion Failed"),
  });

  return {
    ...ingestion,
    runIngestion: ingestion.mutateAsync,
    isLoading: ingestion.isPending,
  };
}
