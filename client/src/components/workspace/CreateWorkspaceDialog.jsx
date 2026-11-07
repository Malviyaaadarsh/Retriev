import React, { useState } from "react";
import { useWorkspace } from "../../context/WorkspaceContext";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FolderKanban, Plus } from "lucide-react";

export function CreateWorkspaceDialog() {
  const { isCreateWorkspaceOpen, setIsCreateWorkspaceOpen, createWorkspace } = useWorkspace();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      await createWorkspace(name.trim(), description.trim());
      setName("");
      setDescription("");
      setIsCreateWorkspaceOpen(false);
    } catch {
      // The hook displays the normalized backend error.
    }
  };

  return (
    <Dialog open={isCreateWorkspaceOpen} onOpenChange={setIsCreateWorkspaceOpen}>
      <DialogContent className="sm:max-w-md p-5 rounded-2xl border-border bg-card">
        <DialogHeader className="space-y-1.5 pb-2">
          <div className="flex items-center gap-2">
            <span className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <FolderKanban className="size-4" />
            </span>
            <DialogTitle className="text-base font-semibold text-foreground">
              Create New Workspace
            </DialogTitle>
          </div>
          <DialogDescription className="text-xs text-muted-foreground">
            A workspace creates an isolated boundary for your documents, vector indexes, and chat sessions.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-3.5 pt-1">
          <div>
            <label className="text-xs font-semibold text-foreground block mb-1">
              Workspace Name *
            </label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Legal Contracts 2026, ML Research"
              required
              autoFocus
              className="text-xs h-9"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-foreground block mb-1">
              Description (Optional)
            </label>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of the documents stored here"
              className="text-xs h-9"
            />
          </div>

          <div className="rounded-lg bg-muted/40 p-2.5 text-[11px] text-muted-foreground border border-border/50">
            Every query and ingestion action in Retriev strictly filters by workspace ID, ensuring full multi-tenant isolation.
          </div>

          <DialogFooter className="pt-2 flex items-center justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setIsCreateWorkspaceOpen(false)}
              className="text-xs"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="default"
              size="sm"
              disabled={!name.trim()}
              className="text-xs gap-1"
            >
              <Plus className="size-3.5" />
              <span>Create Workspace</span>
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
