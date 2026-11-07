import { apiClient } from "./client";

export async function askQuestion(payload) {
  const { data } = await apiClient.post("/chat", payload, { timeout: 300000 });
  return data;
}
