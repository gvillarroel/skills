// Slidev loads this client setup automatically; run the deck with `npx slidev`.
import { defineMermaidSetup } from '@slidev/types'
import { mermaidColorsetConfig } from '../diagram-style.mjs'

// Select colorset2 here only for an explicit extended-color request.
export default defineMermaidSetup(() => mermaidColorsetConfig('colorset1'))
