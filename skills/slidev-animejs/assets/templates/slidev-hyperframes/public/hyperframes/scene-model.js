/** Pure seconds-first state, shared by the live composition and file fallback. */
export const SCENE_DURATION = 12
export function sceneState(seconds) {
  const time = Math.max(0, Math.min(SCENE_DURATION, Number.isFinite(seconds) ? seconds : 0))
  const progress = Math.max(0, Math.min(1, (time - 2) / 8))
  return { time, valveOpen: time >= 2 && time < 10, level: progress * 80, parcelProgress: progress }
}

export function sceneMarkup(seconds, palette, compact = false, prefix = '') {
  const state = sceneState(seconds)
  const width = compact ? 420 : 720, height = compact ? 260 : 400
  const p = palette.roles, fluid = p.secondary || p.primary
  const ink = '#000000', tankX = compact ? 280 : 492, tankY = compact ? 94 : 145
  const tankWidth = compact ? 100 : 154, tankHeight = compact ? 112 : 168
  const inletX = compact ? 36 : 64, valveX = compact ? 130 : 218
  const routeY = tankY + tankHeight * .45
  const parcelX = valveX + (tankX - valveX) * state.parcelProgress
  const fillHeight = tankHeight * state.level / 100
  const font = compact ? 24 : 22
  const markup = `<svg xmlns="http://www.w3.org/2000/svg" data-scene-svg viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="scene-title scene-description">
    <title id="scene-title">Valve-controlled transport</title><desc id="scene-description">At ${state.time.toFixed(2)} seconds the valve is ${state.valveOpen ? 'open' : 'closed'} and the tank is ${Math.round(state.level)} percent full.</desc>
    <rect width="${width}" height="${height}" fill="${p.surface}"/>
    <g font-family="Open Sans, sans-serif" font-size="${font}" fill="${ink}" font-weight="600">
      <text x="${inletX}" y="${compact ? 48 : 88}">Inlet</text><text x="${valveX}" y="${compact ? 48 : 88}" text-anchor="middle">Valve</text><text x="${tankX + tankWidth / 2}" y="${compact ? 48 : 88}" text-anchor="middle">Tank</text>
    </g>
    <path id="transport" d="M${inletX} ${routeY} H${tankX}" stroke="${p.primary}" stroke-width="${compact ? 10 : 14}" fill="none"/>
    <rect id="inlet" x="${inletX - 12}" y="${routeY - 24}" width="24" height="48" rx="3" fill="${p.primary}"/>
    <circle id="valve" cx="${valveX}" cy="${routeY}" r="${compact ? 20 : 28}" fill="${p.primary}"/>
    <path d="M${valveX - 12} ${routeY + (state.valveOpen ? 0 : -12)} L${valveX + 12} ${routeY + (state.valveOpen ? 0 : 12)}" stroke="#ffffff" stroke-width="5"/>
    <rect id="tank" x="${tankX}" y="${tankY}" width="${tankWidth}" height="${tankHeight}" fill="${p.quiet}"/>
    <rect id="tank-fill" x="${tankX}" y="${tankY + tankHeight - fillHeight}" width="${tankWidth}" height="${fillHeight}" fill="${fluid}"/>
    <circle id="parcel" cx="${parcelX}" cy="${routeY}" r="${compact ? 8 : 11}" fill="#ffffff" stroke="${p.primary}" stroke-width="3" visibility="${state.valveOpen ? 'visible' : 'hidden'}"/>
    <g font-family="Open Sans, sans-serif" font-size="${font}" fill="${ink}"><text id="valve-readout" x="${valveX}" y="${compact ? 232 : 349}" text-anchor="middle">${state.valveOpen ? 'Open' : 'Closed'}</text><text id="level-readout" x="${tankX + tankWidth / 2}" y="${compact ? 232 : 349}" text-anchor="middle">${Math.round(state.level)}%</text></g>
  </svg>`
  return markup.replace(/\bid="([^"]+)"/g, (_, id) => `id="${prefix}${id}" data-scene-mark="${id}"`)
    .replace('aria-labelledby="scene-title scene-description"', `aria-labelledby="${prefix}scene-title ${prefix}scene-description"`)
}
