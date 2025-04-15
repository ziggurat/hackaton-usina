import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
// import basicSsl from "@vitejs/plugin-basic-ssl";

// https://vite.dev/config/
export default defineConfig({
  logLevel: "debug",
  plugins: [react()],
  root: "./",
  build: {
    outDir: "dist",
  },
  server: {
    port: 3000,
  },
});
