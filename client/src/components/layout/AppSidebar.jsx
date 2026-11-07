import { useWorkspace } from "../../context/WorkspaceContext";
import { confirm } from "@tauri-apps/plugin-dialog";
import darkModeLogo from "@/assets/logo.png";
import lightModeLogo from "@/assets/logo-white.png";
import {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarMenuBadge,
  SidebarFooter,
  SidebarRail,
} from "@/components/ui/sidebar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuGroup,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import {
  Plus,
  MessageSquare,
  Files,
  Search,
  Sliders,
  ChevronDown,
  Check,
  Trash2,
} from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export function AppSidebar() {
  const {
    workspaces,
    activeWorkspace,
    switchWorkspace,
    setIsCreateWorkspaceOpen,
    activeView,
    setActiveView,
    activeDocuments,
    activeConversations,
    activeChatId,
    setActiveChatId,
    createNewChat,
    setIsSearchOpen,
    setIsSettingsOpen,
    isWorkspacesLoading,
    isWorkspacesError,
    deleteWorkspace,
  } = useWorkspace();

  const handleDeleteWorkspace = async () => {
    if (!activeWorkspace) return;
    const message = `Delete "${activeWorkspace.name}"?\n\nThis action cannot be undone.`;
    const confirmed = window.__TAURI_INTERNALS__
      ? await confirm(message, {
        title: "Delete workspace",
        kind: "warning",
      })
      : window.confirm(message);
    if (confirmed) {
      await deleteWorkspace(activeWorkspace.id);
    }
  };

  return (
    <Sidebar collapsible="icon" className="border-r border-sidebar-border bg-sidebar select-none">
      {/* 1. Workspace Header Section */}
      <SidebarHeader className="p-3 border-b border-sidebar-border/60">

        <div className="flex items-center justify-between mb-2 px-1">
          {/* Expanded mode: text logo */}
          <span className="font-bold text-lg tracking-tight text-sidebar-foreground group-data-[collapsible=icon]:hidden">
            Retriev
          </span>

          {/* Collapsed mode: theme-aware image logo */}
          <div className="hidden w-full items-center justify-center group-data-[collapsible=icon]:flex">
            <img
              src={darkModeLogo}
              alt="Retriev"
              className="hidden size-10 object-contain dark:block rounded-3xl"
            />

            <img
              src={lightModeLogo}
              alt="Retriev"
              className="block size-10 object-contain dark:hidden rounded-3xl"
            />
          </div>
        </div>


        {/* Workspace Switcher Button */}
        <div className="group-data-[collapsible=icon]:hidden">
          <DropdownMenu>
            <DropdownMenuTrigger
              className="w-full flex items-center justify-between gap-2 rounded-lg border border-sidebar-border bg-sidebar-accent/50 p-2 text-xs font-medium text-sidebar-foreground transition-colors hover:bg-sidebar-accent focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-sidebar-ring"
            >
              <div className="flex items-center gap-2 truncate text-left">
                <div className="truncate min-w-0 group-data-[collapsible=icon]:hidden">
                  <p className="truncate font-medium">{activeWorkspace?.name || "Workspace"}</p>
                  <p className="text-[10px] text-muted-foreground truncate">
                    {activeDocuments.length} docs • {activeConversations.length} chats
                  </p>
                </div>
              </div>
              <ChevronDown className="size-3.5 text-muted-foreground shrink-0" />
            </DropdownMenuTrigger>

            <DropdownMenuContent align="start" className="w-64 p-1 shadow-xl">
              <DropdownMenuGroup>
                <DropdownMenuLabel className="px-2 py-1 text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                  Switch Workspace
                </DropdownMenuLabel>
                {isWorkspacesLoading ? (
                  <div className="space-y-2 px-2 py-2">
                    <Skeleton className="h-7 w-full" />
                    <Skeleton className="h-7 w-5/6" />
                  </div>
                ) : workspaces.length === 0 ? (
                  <div className="px-2 py-3 text-center text-xs text-muted-foreground">
                    <p>No workspaces yet.</p>
                    <p className="mt-1">Create your first workspace to begin building your local knowledge base.</p>
                  </div>
                ) : (
                  workspaces.map((ws) => (
                    <DropdownMenuItem
                      key={ws.id}
                      onClick={() => switchWorkspace(ws.id)}
                      className={`flex items-center justify-between gap-2 rounded-md px-2 py-2 text-xs cursor-pointer ${ws.id === activeWorkspace?.id
                        ? "bg-accent font-medium text-accent-foreground"
                        : "text-foreground hover:bg-muted"
                        }`}
                    >
                      <div className="flex items-center gap-2 truncate">
                        <span className="truncate">{ws.name}</span>
                      </div>
                      {ws.id === activeWorkspace?.id && <Check className="size-3.5 text-primary shrink-0" />}
                    </DropdownMenuItem>
                  ))
                )}
              </DropdownMenuGroup>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => setIsCreateWorkspaceOpen(true)}
                className="flex items-center gap-2 text-xs text-primary font-medium cursor-pointer"
              >
                <Plus className="size-3.5" />
                <span>Create Workspace</span>
              </DropdownMenuItem>
              {activeWorkspace && (
                <DropdownMenuItem
                  onClick={handleDeleteWorkspace}
                  className="flex items-center gap-2 text-xs text-destructive cursor-pointer"
                >
                  <Trash2 className="size-3.5" />
                  <span>Delete Current Workspace</span>
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </SidebarHeader>

      <SidebarContent className="p-2 gap-3">
        {/* 2, 3, 4: Primary Actions Group (New Chat, Documents, Search) */}
        <SidebarGroup className="p-0">
          <SidebarMenu>
            {/* New Chat */}
            <SidebarMenuItem>
              <SidebarMenuButton
                onClick={createNewChat}
                isActive={activeView === "chat" && activeChatId === null}
                className="font-medium text-xs text-sidebar-foreground hover:bg-sidebar-accent"
                tooltip="Start a new chat in this workspace"
              >
                <Plus className="size-4 text-primary" />
                <span>New Chat</span>
              </SidebarMenuButton>
            </SidebarMenuItem>

            {/* Documents Library */}
            <SidebarMenuItem>
              <SidebarMenuButton
                onClick={() => setActiveView("documents")}
                isActive={activeView === "documents"}
                className="font-medium text-xs text-sidebar-foreground hover:bg-sidebar-accent"
                tooltip="Open workspace document library"
              >
                <Files className="size-4 text-sidebar-foreground/80" />
                <span>Documents</span>
              </SidebarMenuButton>
              <SidebarMenuBadge className="text-[10px] px-1.5 py-0 h-4 bg-sidebar-accent">
                {activeDocuments.length}
              </SidebarMenuBadge>
            </SidebarMenuItem>

            {/* Search */}
            <SidebarMenuItem>
              <SidebarMenuButton
                onClick={() => setIsSearchOpen(true)}
                className="font-medium text-xs text-sidebar-foreground hover:bg-sidebar-accent"
                tooltip="Search chats & documents (Ctrl+K)"
              >
                <Search className="size-4 text-sidebar-foreground/80" />
                <span>Search</span>
              </SidebarMenuButton>
              <SidebarMenuBadge className="text-[10px] text-muted-foreground font-mono">
                ⌘K
              </SidebarMenuBadge>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>

        {/* 5. Recent Conversations in Active Workspace */}
        <SidebarGroup className="p-0 flex-1">
          <div className="flex items-center justify-between px-2 py-1">
            <SidebarGroupLabel className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider p-0 h-auto">
              Conversations
            </SidebarGroupLabel>
          </div>

          <SidebarMenu className="mt-1 space-y-0.5">
            {activeConversations.length === 0 ? (
              <div className="px-2 py-3 text-center group-data-[collapsible=icon]:hidden">
                <p className="text-xs text-muted-foreground">No chats yet</p>
                <Button
                  variant="ghost"
                  size="xs"
                  onClick={createNewChat}
                  className="mt-1.5 text-[11px] text-primary"
                >
                  Start first chat
                </Button>
              </div>
            ) : (
              activeConversations.map((conv) => {
                const isSelected = activeView === "chat" && activeChatId === conv.id;
                return (
                  <SidebarMenuItem key={conv.id}>
                    <SidebarMenuButton
                      onClick={() => {
                        setActiveChatId(conv.id);
                        setActiveView("chat");
                      }}
                      isActive={isSelected}
                      className={`text-xs group/chat justify-start truncate ${isSelected
                        ? "bg-sidebar-accent font-medium text-sidebar-accent-foreground"
                        : "text-muted-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent/50"
                        }`}
                      tooltip={conv.title}
                    >
                      <MessageSquare className="size-3.5 shrink-0 opacity-70" />
                      <span className="truncate">{conv.title}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })
            )}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>

      {/* 6. Settings & Local Storage Footer Section */}
      <SidebarFooter className="p-3 border-t border-sidebar-border/60 gap-2">
        {/* Settings Button */}
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              onClick={() => setIsSettingsOpen(true)}
              className="text-xs text-sidebar-foreground font-medium hover:bg-sidebar-accent"
              tooltip="Open application settings"
            >
              <Sliders className="size-4 text-sidebar-foreground/80" />
              <span>Settings</span>
            </SidebarMenuButton>
            <SidebarMenuBadge className="text-[10px] text-muted-foreground font-mono group-data-[collapsible=icon]:hidden">
              ⌘,
            </SidebarMenuBadge>
          </SidebarMenuItem>
        </SidebarMenu>

      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  );
}
