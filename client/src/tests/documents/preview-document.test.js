import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../../api/client";
import { getDocumentPreview } from "../../api/documents";

describe("document preview", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("returns the backend extracted preview", async () => {
    vi.spyOn(apiClient, "get").mockResolvedValue({
      data: {
        file_name: "notes.txt",
        file_type: "txt",
        preview: "Extracted document text",
      },
    });

    await expect(getDocumentPreview("workspace-1", "notes.txt")).resolves.toEqual({
      file_name: "notes.txt",
      file_type: "txt",
      preview: "Extracted document text",
    });
    expect(apiClient.get).toHaveBeenCalledWith(
      "/workspaces/workspace-1/documents/notes.txt/content",
    );
  });
});
