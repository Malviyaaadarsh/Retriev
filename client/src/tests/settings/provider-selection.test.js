import { describe, expect, it } from "vitest";
import { MODEL_OPTIONS } from "../../config/settings";

describe("provider model selection", () => {
  it("exposes only supported Gemini and Ollama models", () => {
    expect(Object.keys(MODEL_OPTIONS)).toEqual(["gemini", "ollama"]);
    expect(MODEL_OPTIONS.gemini).toEqual(["gemini-3.6-flash", "gemini-3.8-pro"]);
    expect(MODEL_OPTIONS.ollama).toEqual(["qwen2.5:3b", "llama3.2:3b", "gemma3:4b"]);
  });
});
