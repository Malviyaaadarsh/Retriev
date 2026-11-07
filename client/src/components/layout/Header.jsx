import { Badge } from "@/components/ui/badge";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { CircleCheck, CircleX, LoaderCircle } from "lucide-react";
import { useHealth } from "../../hooks/useHealth";
import { useWorkspace } from "../../context/WorkspaceContext";

export function Header() {
  const { activeWorkspace, settings } = useWorkspace();
  const health = useHealth();
  const provider = settings.provider === "gemini" ? "Gemini" : "Ollama";

  const isOnline =
    health.isSuccess && health.data?.status === "ready";

  const statusLabel = health.isPending
    ? "Connecting..."
    : isOnline
      ? "Operational"
      : "Retriev is Offline";

  return (
    <header className="sticky top-0 z-30 flex h-14 w-full items-center justify-between border-b border-border/80 bg-background/85 px-4 backdrop-blur-md">
      <div className="flex items-center gap-2.5">
        <SidebarTrigger className="-ml-1" />
        <div>
          <p className="text-xs font-semibold text-foreground">
            {activeWorkspace?.name || "Select Workspace"}
          </p>
          <p className="text-[10px] text-muted-foreground">
            Current workspace
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Badge variant="outline" className="text-[10px]">
          Model Using : {provider} - {settings.model}
        </Badge>

        <Badge variant="outline" className="gap-1 text-[10px]">
          {health.isPending ? (
            <LoaderCircle className="size-3 animate-spin" />
          ) : isOnline ? (
            <CircleCheck className="size-3 text-emerald-500" />
          ) : (
            <CircleX className="size-3 text-destructive" />
          )}
          {statusLabel}
        </Badge>
      </div>
    </header>
  );
}
