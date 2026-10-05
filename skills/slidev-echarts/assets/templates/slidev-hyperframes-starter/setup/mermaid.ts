import { defineMermaidSetup } from '@slidev/types'
import { mermaidColorsetConfig } from '../diagram-style.mjs'
import story from '../data/hyperframes-story.json'

export default defineMermaidSetup(() => mermaidColorsetConfig(story.colorset))
