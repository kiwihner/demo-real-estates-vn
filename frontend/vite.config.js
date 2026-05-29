import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  server: {
    port: 5173,
    proxy: {
      // /api/* → FastAPI backend
      // Docker:  target = http://backend:8000  (tên service trong docker-compose)
      // Local:   target = http://localhost:8000
      // Chọn theo env VITE_API_TARGET hoặc mặc định localhost
      "/api": {
        target:       process.env.VITE_API_TARGET || "http://localhost:8000",
        changeOrigin: true,
        rewrite:      (path) => path.replace(/^\/api/, ""),
      },
    },
  },

  build: {
    outDir:   "dist",
    sourcemap: false,
  },
});
