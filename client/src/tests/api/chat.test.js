import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../../api/client";
import { askQuestion } from "../../api/chat";

describe("chat API", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("returns an answer with citations", async () => {
    const payload = {
      query: "What is RAG?",
      workspace_id: "ws-1",
      provider_name: "ollama",
      model_name: "llama3.2",
    };
    const response = {
      answer: "A grounded answer.",
      citations: [{ file_name: "notes.txt", excerpt: "evidence" }],
    };
    vi.spyOn(apiClient, "post").mockResolvedValue({ data: response });

    await expect(askQuestion(payload)).resolves.toEqual(response);
    expect(apiClient.post).toHaveBeenCalledWith("/chat", payload, { timeout: 300000 });
  });
});
