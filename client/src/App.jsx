import React from "react";
import { WorkspaceProvider } from "./context/WorkspaceContext";
import { SettingsProvider } from "./context/SettingsContext";
import { AppLayout } from "./components/layout/AppLayout";

function App() {
  return (
    <SettingsProvider>
      <WorkspaceProvider>
        <AppLayout />
      </WorkspaceProvider>
    </SettingsProvider>
  );
}

export default App;
