import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../../api/client";
import { getDocuments } from "../../api/documents";
import { mapDocumentResponse } from "../../hooks/useDocuments";

describe("documents list", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("loads and maps backend document metadata", async () => {
    vi.spyOn(apiClient, "get").mockResolvedValue({
      data: [{ file_name: "guide.md", file_type: "md", size_bytes: 2048 }],
    });

    const response = await getDocuments("workspace-1");

    expect(response).toEqual([
      { file_name: "guide.md", file_type: "md", size_bytes: 2048 },
    ]);
    expect(mapDocumentResponse(response[0])).toMatchObject({
      id: "guide.md",
      fileName: "guide.md",
      fileType: "markdown",
      sizeBytes: 2048,
      status: "Uploaded",
    });
  });
});
