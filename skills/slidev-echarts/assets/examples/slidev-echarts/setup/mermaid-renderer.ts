import { defineMermaidRendererSetup } from '@slidev/types'
import mermaid from 'mermaid/dist/mermaid.esm.mjs'
import { createColorsetRenderer } from '../../../templates/slidev-diagram-style/diagram-style.mjs'
import setupMermaid from './mermaid'

export default defineMermaidRendererSetup(() => createColorsetRenderer(mermaid, setupMermaid))
