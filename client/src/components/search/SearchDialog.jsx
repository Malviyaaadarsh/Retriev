import React from "react";
import { useWorkspace } from "../../context/WorkspaceContext";
import {
  CommandDialog,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandSeparator,
} from "@/components/ui/command";
import {
  Search,
  FileText,
  MessageSquare,
  Plus,
  Files,
  Sliders,
  Info,
  ExternalLink,
} from "lucide-react";

export function SearchDialog() {
  const {
    isSearchOpen,
    setIsSearchOpen,
    activeWorkspace,
    activeDocuments,
    activeConversations,
    setPreviewDocument,
    setActiveChatId,
    setActiveView,
    createNewChat,
    setIsSettingsOpen,
  } = useWorkspace();

  const handleSelectDoc = (doc) => {
    setIsSearchOpen(false);
    setPreviewDocument(doc);
  };

  const handleSelectChat = (chatId) => {
    setIsSearchOpen(false);
    setActiveChatId(chatId);
    setActiveView("chat");
  };

  return (
    <CommandDialog
      open={isSearchOpen}
      onOpenChange={setIsSearchOpen}
      title="Search Workspace"
      description="Quickly navigate documents and conversations in this workspace"
    >
      <CommandInput placeholder={`Search in ${activeWorkspace?.name || "workspace"}...`} />
      <CommandList className="max-h-80 p-1">
        <CommandEmpty>No matching documents or chats found.</CommandEmpty>

        {/* Documents Group */}
        {activeDocuments.length > 0 && (
          <CommandGroup heading={`Documents in ${activeWorkspace?.name || "Workspace"}`}>
            {activeDocuments.map((doc) => (
              <CommandItem
                key={doc.id}
                onSelect={() => handleSelectDoc(doc)}
                className="flex items-center justify-between gap-2 py-2 cursor-pointer"
              >
                <div className="flex items-center gap-2 truncate">
                  <FileText className="size-3.5 text-primary shrink-0" />
                  <span className="truncate text-xs">{doc.fileName}</span>
                </div>
                <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground shrink-0">
                  <span>{doc.size}</span>
                  <span>•</span>
                  <span>{doc.chunkCount} chunks</span>
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
        )}

        <CommandSeparator />

        {/* Conversations Group */}
        {activeConversations.length > 0 && (
          <CommandGroup heading="Recent Conversations">
            {activeConversations.map((chat) => (
              <CommandItem
                key={chat.id}
                onSelect={() => handleSelectChat(chat.id)}
                className="flex items-center justify-between gap-2 py-2 cursor-pointer"
              >
                <div className="flex items-center gap-2 truncate">
                  <MessageSquare className="size-3.5 text-muted-foreground shrink-0" />
                  <span className="truncate text-xs">{chat.title}</span>
                </div>
                <span className="text-[10px] text-muted-foreground shrink-0">
                  {chat.updatedAt}
                </span>
              </CommandItem>
            ))}
          </CommandGroup>
        )}

        <CommandSeparator />

        {/* Quick Actions */}
        <CommandGroup heading="Actions">
          <CommandItem
            onSelect={() => {
              setIsSearchOpen(false);
              createNewChat();
            }}
            className="flex items-center gap-2 py-2 cursor-pointer"
          >
            <Plus className="size-3.5 text-primary" />
            <span className="text-xs">Start New Chat</span>
          </CommandItem>

          <CommandItem
            onSelect={() => {
              setIsSearchOpen(false);
              setActiveView("documents");
            }}
            className="flex items-center gap-2 py-2 cursor-pointer"
          >
            <Files className="size-3.5" />
            <span className="text-xs">Open Document Library</span>
          </CommandItem>

          <CommandItem
            onSelect={() => {
              setIsSearchOpen(false);
              setIsSettingsOpen(true);
            }}
            className="flex items-center gap-2 py-2 cursor-pointer"
          >
            <Sliders className="size-3.5" />
            <span className="text-xs">Open Settings</span>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
