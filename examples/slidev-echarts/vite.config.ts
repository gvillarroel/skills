import { defineConfig } from 'vite'
import { viteSingleFile } from 'vite-plugin-singlefile'

const singleFileBuild = process.env.SLIDEV_SINGLE_FILE === '1'

function dropManualChunksForSingleFile() {
  return {
    name: 'slidev-echarts-single-file-drop-manual-chunks',
    enforce: 'post' as const,
    configResolved(config: any) {
      const output = config.build?.rollupOptions?.output
      const outputs = Array.isArray(output) ? output : output ? [output] : []

      for (const item of outputs) {
        delete item.manualChunks
      }
    },
  }
}

export default defineConfig({
  plugins: singleFileBuild
    ? [
        viteSingleFile({
          removeViteModuleLoader: true,
        }),
        dropManualChunksForSingleFile(),
      ]
    : [],
  optimizeDeps: {
    include: ['@fix-webm-duration/fix'],
  },
})
