import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../../api/client";
import {
  createWorkspace,
  deleteWorkspace,
  getWorkspace,
  getWorkspaces,
} from "../../api/workspaces";

describe("workspace API", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("lists, gets, creates, and deletes workspaces", async () => {
    vi.spyOn(apiClient, "get")
      .mockResolvedValueOnce({ data: [{ workspace_id: "ws-1" }] })
      .mockResolvedValueOnce({ data: { workspace_id: "ws-1" } });
    vi.spyOn(apiClient, "post").mockResolvedValue({ data: { workspace_id: "ws-2" } });
    vi.spyOn(apiClient, "delete").mockResolvedValue({ data: { success: true } });

    await expect(getWorkspaces()).resolves.toEqual([{ workspace_id: "ws-1" }]);
    await expect(getWorkspace("ws/1")).resolves.toEqual({ workspace_id: "ws-1" });
    await expect(createWorkspace({ name: "Research" })).resolves.toEqual({
      workspace_id: "ws-2",
    });
    await expect(deleteWorkspace("ws-1")).resolves.toEqual({ success: true });

    expect(apiClient.get).toHaveBeenNthCalledWith(2, "/workspaces/ws%2F1");
    expect(apiClient.post).toHaveBeenCalledWith("/workspaces", { name: "Research" });
    expect(apiClient.delete).toHaveBeenCalledWith("/workspaces/ws-1");
  });
});
