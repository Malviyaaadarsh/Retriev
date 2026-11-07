import { apiClient } from "./client";

export async function runIngestion(workspaceId) {
  const { data } = await apiClient.post(
    `/workspaces/${encodeURIComponent(workspaceId)}/ingest`,
  );
  return data;
}
