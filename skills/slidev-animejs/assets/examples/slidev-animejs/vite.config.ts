import { defineConfig } from 'vite'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  publicDir: fileURLToPath(new URL('../../templates/slidev-hyperframes/public', import.meta.url)),
  optimizeDeps: {
    include: ['@fix-webm-duration/fix'],
  },
  resolve: {
    dedupe: ['animejs', 'vue', '@hyperframes/player'],
  },
})
