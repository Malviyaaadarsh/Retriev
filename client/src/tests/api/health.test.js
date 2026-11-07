import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../../api/client";
import { getHealth, getReadiness } from "../../api/health";

describe("health API", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("returns the health response", async () => {
    vi.spyOn(apiClient, "get").mockResolvedValue({ data: { status: "healthy" } });

    await expect(getHealth()).resolves.toEqual({ status: "healthy" });
    expect(apiClient.get).toHaveBeenCalledWith("/health");
  });

  it("normalizes server failures", async () => {
    vi.spyOn(apiClient, "get").mockRejectedValue({
      success: false,
      message: "Server offline",
    });

    await expect(getHealth()).rejects.toEqual({
      success: false,
      message: "Server offline",
    });
  });

  it("returns readiness after storage and model checks", async () => {
    vi.spyOn(apiClient, "get").mockResolvedValue({
      data: { status: "ready", embedding_model: true },
    });

    await expect(getReadiness()).resolves.toEqual({
      status: "ready",
      embedding_model: true,
    });
    expect(apiClient.get).toHaveBeenCalledWith("/ready");
  });
});
