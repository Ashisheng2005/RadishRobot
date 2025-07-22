import path from "path"
import tailwindcss from "@tailwindcss/vite"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  base: '/static/',
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),

    },
  },
  optimizeDeps: {
    include: ['vis-network'],
  },

  build: {
    rollupOptions: {
      external: [],
    },
    minify: 'esbuild',
    outDir: 'dist',
    sourcemap: false,
  },

  server: {
    fs: {
      allow: ['.'],
    },
    host: '0.0.0.0',
    port: 5173,
    proxy: {
        '/api': {
            target: 'http://192.168.0.106:8000',
            changeOrigin: true,
        },
    },
  },
})