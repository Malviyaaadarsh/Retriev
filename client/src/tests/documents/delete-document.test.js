import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../../api/client";
import { deleteDocument } from "../../api/documents";

describe("document deletion", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("deletes the selected document by encoded file name", async () => {
    vi.spyOn(apiClient, "delete").mockResolvedValue({
      data: { success: true },
    });

    await expect(deleteDocument("workspace-1", "project notes.txt")).resolves.toEqual({
      success: true,
    });
    expect(apiClient.delete).toHaveBeenCalledWith(
      "/workspaces/workspace-1/documents/project%20notes.txt",
    );
  });
});
