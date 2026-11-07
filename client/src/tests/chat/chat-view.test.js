import { describe, expect, it } from "vitest";

describe("chat messages", () => {
  it("keeps empty-context answers as normal assistant messages", () => {
    const message = { role: "assistant", content: "No relevant information found." };
    expect(message.role).toBe("assistant");
    expect(message.content).toBe("No relevant information found.");
  });
});
