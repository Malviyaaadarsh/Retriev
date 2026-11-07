import { apiClient } from "./client";

export async function getWorkspaces() {
  const { data } = await apiClient.get("/workspaces");
  return data;
}

export async function getWorkspace(id) {
  const { data } = await apiClient.get(`/workspaces/${encodeURIComponent(id)}`);
  return data;
}

export async function createWorkspace(data) {
  const response = await apiClient.post("/workspaces", data);
  return response.data;
}

export async function deleteWorkspace(id) {
  const { data } = await apiClient.delete(`/workspaces/${encodeURIComponent(id)}`);
  return data;
}
