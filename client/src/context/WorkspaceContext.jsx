/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect } from "react";
import {
  SUGGESTED_PROMPTS,
} from "../data/mockData";
import { useSettings } from "./SettingsContext";
import { useWorkspaces } from "../hooks/useWorkspaces";
import { useDocuments } from "../hooks/useDocuments";
import { useIngestion } from "../hooks/useIngestion";
import { useChat } from "../hooks/useChat";
import { useChats } from "../hooks/useChats";

const WorkspaceContext = createContext(null);

export function WorkspaceProvider({ children }) {
  const { settings, updateSettings, toggleTheme } = useSettings();
  const chat = useChat();

  const {
    data: workspaces = [],
    isLoading: isWorkspacesLoading,
    isError: isWorkspacesError,
    createWorkspace: createRemoteWorkspace,
    deleteWorkspace: deleteRemoteWorkspace,
  } = useWorkspaces();
  const [storedWorkspaceId, setStoredWorkspaceId] = useState(
    () => localStorage.getItem("retriev_active_workspace") || ""
  );

  // Active workspace object
  const activeWorkspaceId =
    workspaces.find((workspace) => workspace.id === storedWorkspaceId)?.id ||
    workspaces[0]?.id ||
    "";
  const activeWorkspace = workspaces.find((w) => w.id === activeWorkspaceId) || null;

  useEffect(() => {
    if (activeWorkspaceId) {
      localStorage.setItem("retriev_active_workspace", activeWorkspaceId);
    } else {
      localStorage.removeItem("retriev_active_workspace");
    }
  }, [activeWorkspaceId]);

  // Active view: 'chat' | 'documents'
  const [activeView, setActiveView] = useState("chat");

  const {
    data: activeDocuments = [],
    isLoading: isDocumentsLoading,
    isError: isDocumentsError,
    uploadDocument,
    importDocuments,
    deleteDocument,
    getDocumentPreview,
    isUploading,
    isImporting,
    isDeleting,
    isPreviewing,
  } = useDocuments(activeWorkspaceId);
  const ingestion = useIngestion(activeWorkspaceId);

  const handleUploadDocument = async (file) => {
    return uploadDocument(file);
  };

  const handleDeleteDocument = async (fileName) => {
    return deleteDocument(fileName);
  };

  // Conversations state keyed by workspaceId
  const chats = useChats(activeWorkspaceId);
  const [conversationsMap, setConversationsMap] = useState({});
  useEffect(() => {
    if (chats.data) {
      // Synchronize the sidebar with the persisted workspace chats.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setConversationsMap((previous) => ({
        ...previous,
        [activeWorkspaceId]: chats.data,
      }));
    }
  }, [activeWorkspaceId, chats.data]);

  // Active chat ID within current workspace (null means empty new chat)
  const [activeChatId, setActiveChatId] = useState(
    null
  );

  // Modals & Panels
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isCreateWorkspaceOpen, setIsCreateWorkspaceOpen] = useState(false);
  const [previewDocument, setPreviewDocument] = useState(null);

  // Switch workspace and update active chat to first chat in that workspace (or null)
  const switchWorkspace = (workspaceId) => {
    setStoredWorkspaceId(workspaceId);
    setPreviewDocument(null);
    setActiveChatId(null);
  };

  const createWorkspace = async (name) => {
    const workspace = await createRemoteWorkspace({ name });
    setStoredWorkspaceId(workspace.id);
    setActiveChatId(null);
    setActiveView("chat");
    return workspace;
  };

  const deleteWorkspace = async (workspaceId) => {
    await deleteRemoteWorkspace(workspaceId);
    if (workspaceId === activeWorkspaceId) {
      setStoredWorkspaceId("");
      setActiveChatId(null);
    }
  };

  // Current workspace conversations
  const activeConversations = conversationsMap[activeWorkspaceId] || [];

  // Active conversation object
  const activeConversation =
    activeConversations.find((c) => c.id === activeChatId) || null;

  // Start new empty chat
  const createNewChat = () => {
    setActiveChatId(null);
    setActiveView("chat");
  };

  const sendMessage = async (userPrompt) => {
    const trimmed = userPrompt?.trim();
    if (!trimmed || !activeWorkspaceId || chat.isPending) return;

    const userMsg = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: trimmed,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    const conversationId = activeChatId || `conv-${Date.now()}`;
    const conversation = {
      id: conversationId,
      workspaceId: activeWorkspaceId,
      title: trimmed.length > 38 ? `${trimmed.substring(0, 38)}...` : trimmed,
      updatedAt: "Just now",
      messages: [userMsg],
    };
    setConversationsMap((previous) => {
      const current = previous[activeWorkspaceId] || [];
      const existing = current.find((item) => item.id === conversationId);
      return {
        ...previous,
        [activeWorkspaceId]: existing
          ? current.map((item) => item.id === conversationId
            ? { ...item, updatedAt: "Just now", messages: [...item.messages, userMsg] }
            : item)
          : [conversation, ...current],
      };
    });
    setActiveChatId(conversationId);

    if (activeChatId) {
      await chats.appendChatMessage({
        chatId: activeChatId,
        message: { role: "user", content: userMsg.content },
      });
    }

    let response;
    try {
      response = await chat.askQuestion({
        query: trimmed,
        workspace_id: activeWorkspaceId,
        provider_name: settings.provider,
        model_name: settings.model,
        api_key: settings.provider === "gemini" ? settings.apiKey || null : null,
      });
    } catch {
      return;
    }
    const assistantMsg = {
      id: `msg-${Date.now()}`,
      role: "assistant",
      content: response.answer,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      citations: response.citations.map((citation, index) => ({
        sourceNumber: index + 1,
        fileName: citation.file_name,
        page: citation.page,
        chunkId: citation.chunk_id,
        excerpt: citation.excerpt,
      })),
      metadata: {
        retrievedChunks: response.retrieved_chunks,
        executionTimeMs: response.execution_time_ms,
        provider: response.provider_name,
        model: response.model_name,
      },
    };
    setConversationsMap((previous) => ({
      ...previous,
      [activeWorkspaceId]: (previous[activeWorkspaceId] || []).map((item) =>
        item.id === conversationId
          ? { ...item, messages: [...item.messages, assistantMsg] }
          : item
      ),
    }));
    if (!activeChatId) {
      const persisted = await chats.createChat({
        title: conversation.title,
        messages: [userMsg, assistantMsg],
      });
      setConversationsMap((previous) => ({
        ...previous,
        [activeWorkspaceId]: (previous[activeWorkspaceId] || []).map((item) =>
          item.id === conversationId ? { ...item, id: persisted.chat_id } : item
        ),
      }));
      setActiveChatId(persisted.chat_id);
    } else {
      await chats.appendChatMessage({
        chatId: activeChatId,
        message: { role: "assistant", content: assistantMsg.content },
      });
    }
  };

  // Keyboard shortcut listener for Ctrl+K / Cmd+K (Search) and Ctrl+B / Cmd+B
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsSearchOpen((prev) => !prev);
      }
      if ((e.metaKey || e.ctrlKey) && e.key === ",") {
        e.preventDefault();
        setIsSettingsOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const suggestedPrompts = SUGGESTED_PROMPTS[activeWorkspaceId] || [
    "What are the key concepts documented in this workspace?",
    "Summarize the main documents in this collection.",
    "Show me the most important takeaways from recent files.",
  ];

  return (
    <WorkspaceContext.Provider
      value={{
        theme: settings.theme,
        toggleTheme,
        workspaces,
        isWorkspacesLoading,
        isWorkspacesError,
        activeWorkspaceId,
        activeWorkspace,
        switchWorkspace,
        createWorkspace,
        deleteWorkspace,
        activeView,
        setActiveView,
        activeDocuments,
        isDocumentsLoading,
        isDocumentsError,
        uploadDocument: handleUploadDocument,
        importDocuments,
        deleteDocument: handleDeleteDocument,
        getDocumentPreview,
        isUploading,
        isImporting,
        isDeleting,
        isPreviewing,
        runIngestion: async () => {
          return ingestion.runIngestion();
        },
        isIngesting: ingestion.isLoading,
        activeConversations,
        activeChatId,
        setActiveChatId,
        activeConversation,
        createNewChat,
        sendMessage,
        isSearchOpen,
        setIsSearchOpen,
        isSettingsOpen,
        setIsSettingsOpen,
        isCreateWorkspaceOpen,
        setIsCreateWorkspaceOpen,
        previewDocument,
        setPreviewDocument,
        settings,
        updateSettings,
        suggestedPrompts,
        isChatLoading: chat.isLoading,
        isChatError: chat.isError,
        isChatsLoading: chats.isLoading,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error("useWorkspace must be used within a WorkspaceProvider");
  }
  return context;
}
