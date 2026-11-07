import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../../api/client";
import {
  deleteDocument,
  getDocumentPreview,
  getDocuments,
  uploadDocument,
} from "../../api/documents";

describe("documents API", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("lists, uploads, deletes, and previews documents", async () => {
    vi.spyOn(apiClient, "get")
      .mockResolvedValueOnce({ data: [{ file_name: "notes.txt" }] })
      .mockResolvedValueOnce({ data: { preview: "content" } });
    vi.spyOn(apiClient, "post").mockResolvedValue({ data: { file_name: "notes.txt" } });
    vi.spyOn(apiClient, "delete").mockResolvedValue({ data: { success: true } });
    const file = new File(["content"], "notes.txt", { type: "text/plain" });

    await expect(getDocuments("ws-1")).resolves.toEqual([{ file_name: "notes.txt" }]);
    await expect(uploadDocument("ws-1", file)).resolves.toEqual({
      file_name: "notes.txt",
    });
    await expect(deleteDocument("ws-1", "notes notes.txt")).resolves.toEqual({
      success: true,
    });
    await expect(getDocumentPreview("ws-1", "notes.txt")).resolves.toEqual({
      preview: "content",
    });

    expect(apiClient.post).toHaveBeenCalledWith(
      "/workspaces/ws-1/documents",
      expect.any(FormData),
    );
    expect(apiClient.delete).toHaveBeenCalledWith(
      "/workspaces/ws-1/documents/notes%20notes.txt",
    );
  });
});
