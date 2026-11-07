import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { createWorkspace, deleteWorkspace, getWorkspaces } from "../api/workspaces";
import { waitForBackendReady } from "../api/health";
import { toast } from "sonner";

export function mapWorkspaceResponse(workspace) {
  return {
    ...workspace,
    id: workspace.workspace_id,
    description: "",
    chatCount: 0,
    documentCount: 0,
    createdAt: workspace.created_at,
  };
}

export function useWorkspaces() {
  const queryClient = useQueryClient();
  const workspaces = useQuery({
    queryKey: ["workspaces"],
    queryFn: async () => {
      await waitForBackendReady();
      const response = await getWorkspaces();
      return response.map(mapWorkspaceResponse);
    },
    retry: 2,
    retryDelay: () => 1000,
    refetchOnReconnect: true,
  });

  useEffect(() => {
    if (workspaces.isError) {
      toast.error("Unable to load workspaces");
    }
  }, [workspaces.isError]);

  const create = useMutation({
    mutationFn: async (data) => mapWorkspaceResponse(await createWorkspace(data)),
    onSuccess: (workspace) => {
      queryClient.setQueryData(["workspaces"], (current = []) => [workspace, ...current]);
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
      toast.success("Workspace Created");
    },
    onError: (error) => toast.error(error.message || "Workspace creation failed"),
  });

  const remove = useMutation({
    mutationFn: deleteWorkspace,
    onSuccess: (_, workspaceId) => {
      queryClient.setQueryData(["workspaces"], (current = []) =>
        current.filter((workspace) => workspace.id !== workspaceId),
      );
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
      toast.success("Workspace Deleted");
    },
    onError: (error) => toast.error(error.message || "Workspace deletion failed"),
  });

  return { ...workspaces, createWorkspace: create.mutateAsync, deleteWorkspace: remove.mutateAsync };
}
