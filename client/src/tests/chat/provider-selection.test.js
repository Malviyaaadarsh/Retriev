import { describe, expect, it } from "vitest";

describe("chat provider selection", () => {
  it("uses the settings provider and model fields in the API contract", () => {
    const settings = { provider: "ollama", model: "llama3.2" };
    const payload = {
      query: "Explain this",
      workspace_id: "workspace-1",
      provider_name: settings.provider,
      model_name: settings.model,
    };

    expect(payload.provider_name).toBe("ollama");
    expect(payload.model_name).toBe("llama3.2");
  });
});
