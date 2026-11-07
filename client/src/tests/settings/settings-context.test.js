import { describe, expect, it } from "vitest";
import { DEFAULT_SETTINGS, loadSettings, SETTINGS_KEY } from "../../context/SettingsContext";

describe("settings context defaults", () => {
  it("loads persisted settings over backend-aligned defaults", () => {
    const storage = {
      getItem: (key) => key === SETTINGS_KEY
        ? JSON.stringify({ provider: "ollama", model: "mistral", topK: 8 })
        : null,
    };
    globalThis.localStorage = storage;

    expect(loadSettings()).toMatchObject({
      ...DEFAULT_SETTINGS,
      provider: "ollama",
      model: "mistral",
      topK: 8,
    });
  });
});
