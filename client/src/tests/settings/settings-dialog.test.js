import { describe, expect, it } from "vitest";
import { DEFAULT_SETTINGS } from "../../context/SettingsContext";

describe("settings dialog values", () => {
  it("starts with valid retrieval settings", () => {
    expect(DEFAULT_SETTINGS.chunkSize).toBeGreaterThan(0);
    expect(DEFAULT_SETTINGS.chunkOverlap).toBeGreaterThanOrEqual(0);
    expect(DEFAULT_SETTINGS.topK).toBeGreaterThanOrEqual(1);
    expect(DEFAULT_SETTINGS.embeddingModel).toBe("all-MiniLM-L6-v2");
  });
});
