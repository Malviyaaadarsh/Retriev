import { apiClient } from "./client";

function workspaceDocumentsPath(workspaceId) {
  return `/workspaces/${encodeURIComponent(workspaceId)}/documents`;
}

export async function getDocuments(workspaceId) {
  const { data } = await apiClient.get(workspaceDocumentsPath(workspaceId));
  return data;
}

export async function uploadDocument(workspaceId, file) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post(workspaceDocumentsPath(workspaceId), formData);
  return data;
}

export async function importDocuments(workspaceId, paths) {
  const { data } = await apiClient.post(
    `${workspaceDocumentsPath(workspaceId)}/import`,
    { paths },
  );
  return data;
}

export async function deleteDocument(workspaceId, fileName) {
  const { data } = await apiClient.delete(
    `${workspaceDocumentsPath(workspaceId)}/${encodeURIComponent(fileName)}`,
  );
  return data;
}

export async function getDocumentPreview(workspaceId, fileName) {
  const { data } = await apiClient.get(
    `${workspaceDocumentsPath(workspaceId)}/${encodeURIComponent(fileName)}/content`,
  );
  return data;
}
