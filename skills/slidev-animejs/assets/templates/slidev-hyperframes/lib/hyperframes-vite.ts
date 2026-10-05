// Imported by the deck's vite.config.ts; requires its declared Vite and single-file plugin.
import type { Plugin } from 'vite'
import { viteSingleFile } from 'vite-plugin-singlefile'

export function hyperframesBuildPlugins(): Plugin[] {
  if (process.env.SLIDEV_SINGLE_FILE !== '1') return []
  return [viteSingleFile({ removeViteModuleLoader: true }), {
    name: 'slidev-hyperframes-single-file', enforce: 'post',
    configResolved(config) {
      // Slidev's manual chunks conflict with the single-file plugin's codeSplitting=false.
      for (const options of [config.build.rollupOptions, config.build.rolldownOptions]) {
        const output = options?.output
        for (const item of Array.isArray(output) ? output : output ? [output] : []) delete item.manualChunks
      }
    },
  }]
}
