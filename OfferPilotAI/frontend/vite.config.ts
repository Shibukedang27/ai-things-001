import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");
  const apiProxyTarget = env.VITE_API_PROXY_TARGET ?? "http://localhost:8000";

  return {
    plugins: [react()],
    build: {
      chunkSizeWarningLimit: 650,
      rollupOptions: {
        output: {
          manualChunks: {
            "charts-vendor": ["recharts"],
            "editor-vendor": [
              "@uiw/react-codemirror",
              "@codemirror/lang-python",
              "@codemirror/lang-java",
              "@codemirror/lang-sql",
            ],
            "icons-vendor": ["lucide-react"],
          },
        },
      },
    },
    server: {
      port: 5173,
      proxy: {
        "/api": apiProxyTarget,
      },
    },
  };
});
