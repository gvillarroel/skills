import { defineConfig } from 'vite'

export default defineConfig({
  optimizeDeps: {
    include: ['@fix-webm-duration/fix'],
  },
})
