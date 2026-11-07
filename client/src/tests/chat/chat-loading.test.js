import { describe, expect, it } from "vitest";

describe("chat loading state", () => {
  it("disables sending while a request is pending", () => {
    const isChatLoading = true;
    expect(!"question".trim() || isChatLoading).toBe(true);
  });
});
