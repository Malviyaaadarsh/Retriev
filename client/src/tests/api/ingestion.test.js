import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../../api/client";
import { runIngestion } from "../../api/ingestion";

describe("ingestion API", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("returns the ingestion result", async () => {
    vi.spyOn(apiClient, "post").mockResolvedValue({
      data: { success: true, files_processed: 2, vectors_stored: 8 },
    });

    await expect(runIngestion("ws-1")).resolves.toEqual({
      success: true,
      files_processed: 2,
      vectors_stored: 8,
    });
    expect(apiClient.post).toHaveBeenCalledWith("/workspaces/ws-1/ingest");
  });
});
