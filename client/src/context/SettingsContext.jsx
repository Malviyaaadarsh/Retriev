/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useEffect, useState } from "react";

export const SETTINGS_KEY = "retriev_settings";

export const DEFAULT_SETTINGS = {
  provider: "gemini",
  model: "gemini-3.6-flash",
  apiKey: "",
  temperature: 0.2,
  embeddingModel: "all-MiniLM-L6-v2",
  chunkSize: 1000,
  chunkOverlap: 200,
  topK: 5,
  theme: "dark",
  storagePath: "",
};

const SettingsContext = createContext(null);

export function loadSettings() {
  try {
    const stored = localStorage.getItem(SETTINGS_KEY);
    if (!stored) return DEFAULT_SETTINGS;
    const parsed = JSON.parse(stored);
    return { ...DEFAULT_SETTINGS, ...parsed };
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export function SettingsProvider({ children }) {
  const [settings, setSettings] = useState(loadSettings);

  useEffect(() => {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
    document.documentElement.classList.toggle("dark", settings.theme === "dark");
  }, [settings]);

  const updateSettings = (updates) => {
    setSettings((previous) => ({ ...previous, ...updates }));
  };

  const toggleTheme = () => {
    updateSettings({ theme: settings.theme === "dark" ? "light" : "dark" });
  };

  return (
    <SettingsContext.Provider value={{ settings, updateSettings, toggleTheme }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error("useSettings must be used within a SettingsProvider");
  }
  return context;
}
