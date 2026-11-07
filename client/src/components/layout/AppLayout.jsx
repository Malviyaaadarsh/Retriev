import React from "react";
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";
import { AppSidebar } from "./AppSidebar";
import { Header } from "./Header";
import { ChatView } from "../chat/ChatView";
import { DocumentsView } from "../documents/DocumentsView";
import { SettingsDialog } from "../settings/SettingsDialog";
import { SearchDialog } from "../search/SearchDialog";
import { CreateWorkspaceDialog } from "../workspace/CreateWorkspaceDialog";
import { DocumentPreviewDialog } from "../documents/DocumentPreviewDialog";
import { useWorkspace } from "../../context/WorkspaceContext";

export function AppLayout() {
  const { activeView, isWorkspacesLoading } = useWorkspace();

  return (
    <SidebarProvider defaultOpen={true}>
      <div className="flex h-screen w-full overflow-hidden bg-background">
        {/* Sidebar */}
        <AppSidebar />

        {/* Main Content Area */}
        <SidebarInset className="flex flex-1 flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-hidden">
            {activeView === "chat" ? <ChatView /> : <DocumentsView />}
          </main>
        </SidebarInset>
      </div>
      {isWorkspacesLoading && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
          <div
            className="h-8 w-8 animate-spin rounded-full border-2 border-muted-foreground/30 border-t-primary"
            aria-label="Loading Retriev"
          />
        </div>
      )}

      {/* Floating Modals & Command Palettes */}
      <SettingsDialog />
      <SearchDialog />
      <CreateWorkspaceDialog />
      <DocumentPreviewDialog />
    </SidebarProvider>
  );
}
