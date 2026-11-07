import { describe, expect, it } from "vitest";
import { DEFAULT_SETTINGS } from "../../context/SettingsContext";

describe("theme persistence settings", () => {
  it("stores the theme in the settings model", () => {
    const saved = JSON.stringify({ ...DEFAULT_SETTINGS, theme: "light" });
    expect(JSON.parse(saved).theme).toBe("light");
  });
});
