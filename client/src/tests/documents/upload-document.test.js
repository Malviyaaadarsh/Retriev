import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../../api/client";
import { uploadDocument } from "../../api/documents";

describe("document upload", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("uploads a document using the multipart file contract", async () => {
    vi.spyOn(apiClient, "post").mockResolvedValue({
      data: { file_name: "notes.txt", file_type: "txt", size_bytes: 12 },
    });
    const file = new File(["hello world!"], "notes.txt", { type: "text/plain" });

    await expect(uploadDocument("workspace-1", file)).resolves.toMatchObject({
      file_name: "notes.txt",
    });
    expect(apiClient.post).toHaveBeenCalledWith(
      "/workspaces/workspace-1/documents",
      expect.any(FormData),
    );
  });
});
