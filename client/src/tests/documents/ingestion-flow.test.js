import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../../api/client";
import { runIngestion } from "../../api/ingestion";

describe("document ingestion", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("calls ingestion and exposes the backend result metrics", async () => {
    const result = {
      workspace_id: "workspace-1",
      success: true,
      files_processed: 2,
      files_failed: 0,
      chunks_generated: 8,
      embeddings_generated: 8,
      vectors_stored: 8,
      total_time_seconds: 1.25,
    };
    vi.spyOn(apiClient, "post").mockResolvedValue({ data: result });

    await expect(runIngestion("workspace-1")).resolves.toEqual(result);
    expect(apiClient.post).toHaveBeenCalledWith("/workspaces/workspace-1/ingest");
  });
});
