import { defineConfig } from 'vite'
import { hyperframesBuildPlugins } from './lib/hyperframes-vite'
export default defineConfig({ plugins: [...hyperframesBuildPlugins()] })
