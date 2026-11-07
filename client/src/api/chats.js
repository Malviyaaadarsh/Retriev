import { apiClient } from "./client";

function chatsPath(workspaceId) {
  return `/workspaces/${encodeURIComponent(workspaceId)}/chats`;
}

export async function getChats(workspaceId) {
  const { data } = await apiClient.get(chatsPath(workspaceId));
  return data;
}

export async function createChat(workspaceId, payload) {
  const { data } = await apiClient.post(chatsPath(workspaceId), payload);
  return data;
}

export async function deleteChat(workspaceId, chatId) {
  const { data } = await apiClient.delete(`${chatsPath(workspaceId)}/${encodeURIComponent(chatId)}`);
  return data;
}

export async function appendChatMessage(workspaceId, chatId, message) {
  const { data } = await apiClient.post(
    `${chatsPath(workspaceId)}/${encodeURIComponent(chatId)}/messages`,
    message,
  );
  return data;
}
