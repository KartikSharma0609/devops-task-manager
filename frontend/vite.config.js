import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev: /api/* is proxied to the local Flask app (prefix stripped),
// matching what Nginx does in production.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:5000",
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
