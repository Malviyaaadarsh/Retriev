import axios from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
  timeout: 30000,
});

export function normalizeApiError(error) {
  if (error?.response) {
    const detail = error.response.data?.detail;
    return {
      success: false,
      message:
        typeof detail === "string"
          ? detail
          : `Request failed with status ${error.response.status}.`,
      status: error.response.status,
    };
  }

  if (error?.code === "ECONNABORTED" || error?.code === "ETIMEDOUT") {
    return { success: false, message: "The request timed out." };
  }

  return { success: false, message: "Unable to connect to server." };
}

apiClient.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(normalizeApiError(error)),
);
