// Slidev loads this hook automatically; run the deck with `npx slidev`.
import { defineMermaidRendererSetup } from '@slidev/types'
import mermaid from 'mermaid/dist/mermaid.esm.mjs'
import { createColorsetRenderer } from '../diagram-style.mjs'
import setupMermaid from './mermaid'

export default defineMermaidRendererSetup(() => createColorsetRenderer(mermaid, setupMermaid))
