import { defineConfig } from 'vite'

export default defineConfig({
  base: './',
  build: {
    chunkSizeWarningLimit: 700,
  },
  server: {
    host: '127.0.0.1',
    port: 4180,
  },
  preview: {
    host: '127.0.0.1',
    port: 4180,
  },
})
