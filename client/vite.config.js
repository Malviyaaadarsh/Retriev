import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import path from "path"
import process from "process"
const clientRoot = import.meta.dirname;
export default defineConfig({
  plugins: [react(), tailwindcss()],
  root: clientRoot,
  server: {
    watch: {
      ignored: ["**/src-tauri/**"],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },
  base: "./",
  build: {
    outDir: path.resolve(clientRoot, "dist"),
    emptyOutDir: true,
  },
})