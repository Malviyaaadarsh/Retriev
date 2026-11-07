import { describe, expect, it } from "vitest";
import { mapWorkspaceResponse } from "../../hooks/useWorkspaces";

describe("workspace response mapping", () => {
  it("maps backend workspace fields to the UI workspace shape", () => {
    expect(
      mapWorkspaceResponse({
        workspace_id: "workspace-1",
        name: "Research",
        path: "C:/workspaces/workspace-1",
        created_at: "2026-10-20T12:00:00Z",
        updated_at: "2026-10-20T12:00:00Z",
      }),
    ).toMatchObject({
      id: "workspace-1",
      name: "Research",
      description: "",
      chatCount: 0,
      documentCount: 0,
      createdAt: "2026-10-20T12:00:00Z",
    });
  });
});
