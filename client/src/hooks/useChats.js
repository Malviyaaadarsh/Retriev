import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { appendChatMessage, createChat, deleteChat, getChats } from "../api/chats";

function mapChat(chat) {
  return {
    id: chat.chat_id,
    workspaceId: chat.workspace_id,
    title: chat.title || "Conversation",
    updatedAt: chat.updated_at,
    messages: chat.messages.map((message) => ({
      id: message.message_id,
      role: message.role,
      content: message.content,
      timestamp: new Date(message.timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    })),
  };
}

export function useChats(workspaceId) {
  const queryClient = useQueryClient();
  const queryKey = ["chats", workspaceId];
  const chats = useQuery({
    queryKey,
    queryFn: async () => (await getChats(workspaceId)).map(mapChat),
    enabled: Boolean(workspaceId),
    retry: 10,
    retryDelay: () => 1000,
    refetchOnReconnect: true,
  });
  const create = useMutation({
    mutationFn: (payload) => createChat(workspaceId, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey }),
  });
  const remove = useMutation({
    mutationFn: (chatId) => deleteChat(workspaceId, chatId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey }),
  });
  const append = useMutation({
    mutationFn: ({ chatId, message }) => appendChatMessage(workspaceId, chatId, message),
    onSuccess: () => queryClient.invalidateQueries({ queryKey }),
  });
  return {
    ...chats,
    createChat: create.mutateAsync,
    deleteChat: remove.mutateAsync,
    appendChatMessage: append.mutateAsync,
  };
}
