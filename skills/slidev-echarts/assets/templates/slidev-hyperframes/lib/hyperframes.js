import palettes from '../public/hyperframes/colorsets.json'
export { sceneState, sceneMarkup, SCENE_DURATION } from '../public/hyperframes/scene-model.js'

export function cueTime(step, cues = [0, 3, 6, 9], duration = Infinity) {
  if (!Array.isArray(cues) || !cues.length || cues.some(time => !Number.isFinite(time) || time < 0)) throw new TypeError('cueTimes must contain finite, nonnegative seconds')
  const index = Math.max(0, Math.min(cues.length - 1, Math.trunc(Number.isFinite(step) ? step : 0)))
  return Math.min(cues[index], duration > 0 ? duration : Infinity)
}
export function assetUrl(src, base, documentUrl) {
  if (!src || typeof src !== 'string') throw new TypeError('src must be a nonempty composition URL')
  if (/^[a-z][a-z\d+.-]*:/i.test(src) || src.startsWith('//') || src.startsWith('/')) return new URL(src, documentUrl).href
  return new URL(src, new URL(base || './', documentUrl)).href
}
export function paletteFor(selected = 'colorset1') {
  if (!palettes.colorsets[selected]) throw new TypeError('colorset must be colorset1 or colorset2')
  return palettes.colorsets[selected]
}
export function starterUrl(src, colorset, base, documentUrl) {
  const resolved = new URL(assetUrl(src, base, documentUrl))
  // Only the bundled starter opts into our palette; caller-owned scenes keep their URL/styles.
  if (resolved.pathname.endsWith('/hyperframes/starter.html')) resolved.searchParams.set('colorset', colorset)
  return resolved.href
}

export function compositionDocument(html, sourceUrl) {
  if (typeof html !== 'string' || !html.trim()) throw new TypeError('Composition HTML must be nonempty')
  const escape = value => value.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;')
  const baseTag = /<base\b[^>]*\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))[^>]*>/i
  const existing = html.match(baseTag)
  if (existing) {
    const value = (existing[1] ?? existing[2] ?? existing[3]).replace(/&amp;/g, '&')
    const resolved = new URL(value, sourceUrl).href
    return html.replace(baseTag, tag => tag.replace(/\bhref\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)/i, `href="${escape(resolved)}"`))
  }
  const escaped = escape(sourceUrl)
  const base = `<base href="${escaped}">`
  if (/<head\b[^>]*>/i.test(html)) return html.replace(/<head\b[^>]*>/i, tag => `${tag}${base}`)
  return `${base}${html}`
}
