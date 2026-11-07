import { apiClient } from "./client";

export async function getHealth() {
  const { data } = await apiClient.get("/health");
  return data;
}

export async function getReadiness() {
  const { data } = await apiClient.get("/ready");
  return data;
}

export async function waitForBackendReady({
  timeoutMs = 120000,
  intervalMs = 1000,
} = {}) {
  const deadline = Date.now() + timeoutMs;

  while (Date.now() < deadline) {
    try {
      const readiness = await getReadiness();
      if (readiness.status === "ready") {
        return readiness;
      }
    } catch {
      // The packaged backend may still be starting its local model.
    }

    await new Promise((resolve) => window.setTimeout(resolve, intervalMs));
  }

  throw new Error("Retriev backend did not become ready before the timeout.");
}
