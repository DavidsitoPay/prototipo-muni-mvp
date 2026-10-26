import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
export default defineConfig({
    plugins: [react()],
    server: {
        host: true,
        port: 3000,
    },
    test: {
        environment: "jsdom",
        setupFiles: ["./vitest.setup.ts"],
        css: true,
    },
});
