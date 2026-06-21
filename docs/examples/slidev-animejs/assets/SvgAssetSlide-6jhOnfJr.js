import{F as e,L as t,N as n,Y as r,_ as i,b as a,g as o,lt as s,vt as c,xt as l,z as u}from"./modules/shiki-D7SYso3p.js";import{nt as d}from"./index-WvVKIWHE.js";import{d as f,i as p,l as m,n as h,o as g,r as _,t as v}from"./morphto-DjH7y8zl.js";var y={"drawable-circuit":`<svg class="anime-svg-asset anime-svg-drawable-circuit" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img" aria-labelledby="drawable-circuit-title drawable-circuit-desc">
  <title id="drawable-circuit-title">Drawable circuit asset</title>
  <desc id="drawable-circuit-desc">A circuit-style SVG with independent path and node hooks for Anime.js draw-on and stagger animations.</desc>
  <rect class="svg-backdrop" width="960" height="540" rx="42" fill="#f8fafc"/>
  <g class="circuit-panels" data-anime-group="panels">
    <rect class="circuit-panel" x="78" y="96" width="164" height="112" rx="18" fill="#ffffff" stroke="#cbd5e1" stroke-width="4"/>
    <rect class="circuit-panel" x="716" y="92" width="168" height="122" rx="18" fill="#ffffff" stroke="#cbd5e1" stroke-width="4"/>
    <rect class="circuit-panel" x="376" y="334" width="206" height="98" rx="18" fill="#ffffff" stroke="#cbd5e1" stroke-width="4"/>
  </g>
  <g data-anime-group="drawables" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <path id="circuit-main-a" class="svg-drawable circuit-line primary" d="M158 208 C158 284 262 292 318 238 S454 142 524 212 S690 304 798 214" stroke="#2563eb" stroke-width="13"/>
    <path id="circuit-main-b" class="svg-drawable circuit-line accent" d="M242 152 C330 120 384 158 430 236 C476 314 542 338 646 306 C712 286 752 310 800 374" stroke="#0f766e" stroke-width="10"/>
    <path id="circuit-main-c" class="svg-drawable circuit-line warm" d="M112 374 C198 314 282 388 358 350 C454 302 484 406 594 372 C694 342 760 408 850 328" stroke="#f59e0b" stroke-width="9"/>
    <path id="circuit-spark" class="svg-drawable circuit-line rose" d="M480 94 L514 132 L486 166 L526 206" stroke="#db2777" stroke-width="8"/>
  </g>
  <g data-anime-group="nodes">
    <circle class="svg-node node-primary" cx="158" cy="208" r="18" fill="#2563eb"/>
    <circle class="svg-node node-primary" cx="318" cy="238" r="14" fill="#2563eb"/>
    <circle class="svg-node node-primary" cx="524" cy="212" r="16" fill="#2563eb"/>
    <circle class="svg-node node-primary" cx="798" cy="214" r="18" fill="#2563eb"/>
    <circle class="svg-node node-accent" cx="242" cy="152" r="13" fill="#0f766e"/>
    <circle class="svg-node node-accent" cx="646" cy="306" r="15" fill="#0f766e"/>
    <circle class="svg-node node-warm" cx="112" cy="374" r="13" fill="#f59e0b"/>
    <circle class="svg-node node-warm" cx="850" cy="328" r="15" fill="#f59e0b"/>
    <circle class="svg-node node-rose" cx="526" cy="206" r="13" fill="#db2777"/>
  </g>
  <g class="circuit-labels" fill="#475569" font-family="Inter, Arial, sans-serif" font-size="24" font-weight="700">
    <text x="112" y="160">input</text>
    <text x="742" y="166">signal</text>
    <text x="418" y="392">output</text>
  </g>
</svg>
`,"motion-orbit":`<svg class="anime-svg-asset anime-svg-motion-orbit" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img" aria-labelledby="motion-orbit-title motion-orbit-desc">
  <title id="motion-orbit-title">Motion orbit asset</title>
  <desc id="motion-orbit-desc">A path-following SVG with an orbit route, traveler group, pulses, and rings for Anime.js motion path animation.</desc>
  <rect class="svg-backdrop" width="960" height="540" rx="42" fill="#f8fafc"/>
  <g class="orbit-field" transform="translate(480 270)">
    <ellipse class="orbit-ring ring-blue" cx="0" cy="0" rx="318" ry="120" fill="none" stroke="#bfdbfe" stroke-width="5"/>
    <ellipse class="orbit-ring ring-green" cx="0" cy="0" rx="250" ry="170" fill="none" stroke="#bbf7d0" stroke-width="5" transform="rotate(-28)"/>
    <ellipse class="orbit-ring ring-amber" cx="0" cy="0" rx="190" ry="88" fill="none" stroke="#fde68a" stroke-width="5" transform="rotate(42)"/>
  </g>
  <path id="orbit-path" class="svg-drawable orbit-path" d="M126 292 C194 88 388 92 470 250 S700 452 826 176" fill="none" stroke="#64748b" stroke-width="10" stroke-linecap="round"/>
  <g class="orbit-pulses" data-anime-group="pulses">
    <circle class="orbit-pulse" cx="190" cy="164" r="24" fill="#dbeafe"/>
    <circle class="orbit-pulse" cx="484" cy="264" r="30" fill="#dcfce7"/>
    <circle class="orbit-pulse" cx="754" cy="264" r="26" fill="#fef3c7"/>
  </g>
  <g id="orbit-traveler" class="svg-traveler orbit-traveler" data-anime-target="traveler">
    <circle cx="0" cy="0" r="26" fill="#db2777"/>
    <path d="M-10 -10 L16 0 L-10 10 Z" fill="#ffffff"/>
    <circle cx="-2" cy="0" r="6" fill="#be123c"/>
  </g>
  <g class="orbit-labels" fill="#334155" font-family="Inter, Arial, sans-serif" font-size="24" font-weight="750">
    <text x="112" y="420">route draw</text>
    <text x="684" y="420">path follower</text>
  </g>
</svg>
`,"morphing-badge":`<svg class="anime-svg-asset anime-svg-morphing-badge" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img" aria-labelledby="morphing-badge-title morphing-badge-desc">
  <title id="morphing-badge-title">Morphing badge asset</title>
  <desc id="morphing-badge-desc">A central path with hidden target paths that can be morphed with Anime.js svg.morphTo.</desc>
  <rect class="svg-backdrop" width="960" height="540" rx="42" fill="#f8fafc"/>
  <g class="badge-rays" data-anime-group="rays" stroke-linecap="round">
    <path class="badge-spark" d="M480 76 L480 120" stroke="#2563eb" stroke-width="10"/>
    <path class="badge-spark" d="M638 118 L610 154" stroke="#0f766e" stroke-width="10"/>
    <path class="badge-spark" d="M716 270 L666 270" stroke="#f59e0b" stroke-width="10"/>
    <path class="badge-spark" d="M638 422 L610 386" stroke="#db2777" stroke-width="10"/>
    <path class="badge-spark" d="M480 464 L480 420" stroke="#2563eb" stroke-width="10"/>
    <path class="badge-spark" d="M322 422 L350 386" stroke="#0f766e" stroke-width="10"/>
    <path class="badge-spark" d="M244 270 L294 270" stroke="#f59e0b" stroke-width="10"/>
    <path class="badge-spark" d="M322 118 L350 154" stroke="#db2777" stroke-width="10"/>
  </g>
  <path id="badge-source" class="badge-source" data-anime-target="morph-source" d="M480 118 C562 118 632 188 632 270 C632 352 562 422 480 422 C398 422 328 352 328 270 C328 188 398 118 480 118 Z" fill="#0f766e" stroke="#0f172a" stroke-width="8"/>
  <path id="badge-target-star" class="badge-target" data-anime-target="morph-target" d="M480 104 C508 184 580 178 644 166 C596 226 638 286 688 338 C606 328 568 392 548 464 C506 394 432 404 362 438 C382 358 326 314 258 270 C334 236 352 164 356 88 C416 136 448 144 480 104 Z" fill="none" opacity="0"/>
  <path id="badge-target-wave" class="badge-target" data-anime-target="morph-target" d="M288 278 C312 170 400 142 470 182 C544 224 606 128 674 198 C746 274 664 392 548 378 C462 366 438 444 358 402 C302 372 266 334 288 278 Z" fill="none" opacity="0"/>
  <path id="badge-target-diamond" class="badge-target" data-anime-target="morph-target" d="M480 86 C526 152 598 180 686 270 C600 354 526 388 480 454 C432 388 360 354 274 270 C360 180 432 152 480 86 Z" fill="none" opacity="0"/>
  <g class="badge-center-mark" fill="#ffffff" font-family="Inter, Arial, sans-serif" text-anchor="middle">
    <text x="480" y="258" font-size="42" font-weight="850">SVG</text>
    <text x="480" y="298" font-size="22" font-weight="750">morph hooks</text>
  </g>
</svg>
`,"stagger-dashboard":`<svg class="anime-svg-asset anime-svg-stagger-dashboard" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img" aria-labelledby="stagger-dashboard-title stagger-dashboard-desc">
  <title id="stagger-dashboard-title">Stagger dashboard asset</title>
  <desc id="stagger-dashboard-desc">A dashboard SVG with repeated cards, bars, and dots designed for Anime.js stagger sequences.</desc>
  <rect class="svg-backdrop" width="960" height="540" rx="42" fill="#f8fafc"/>
  <g class="dashboard-shell">
    <rect x="92" y="72" width="776" height="396" rx="28" fill="#ffffff" stroke="#cbd5e1" stroke-width="4"/>
    <rect x="92" y="72" width="776" height="72" rx="28" fill="#eff6ff"/>
    <circle class="dashboard-dot" cx="134" cy="108" r="12" fill="#db2777"/>
    <circle class="dashboard-dot" cx="174" cy="108" r="12" fill="#f59e0b"/>
    <circle class="dashboard-dot" cx="214" cy="108" r="12" fill="#0f766e"/>
  </g>
  <g class="dashboard-cards" data-anime-group="cards">
    <rect class="dashboard-card" x="134" y="184" width="180" height="218" rx="18" fill="#dbeafe" stroke="#93c5fd" stroke-width="4"/>
    <rect class="dashboard-card" x="390" y="184" width="180" height="218" rx="18" fill="#dcfce7" stroke="#86efac" stroke-width="4"/>
    <rect class="dashboard-card" x="646" y="184" width="180" height="218" rx="18" fill="#fef3c7" stroke="#fcd34d" stroke-width="4"/>
  </g>
  <g class="dashboard-bars" data-anime-group="bars" stroke-linecap="round">
    <path class="dashboard-bar bar-blue" d="M168 246 H278" stroke="#2563eb" stroke-width="18"/>
    <path class="dashboard-bar bar-blue" d="M168 292 H250" stroke="#2563eb" stroke-width="18"/>
    <path class="dashboard-bar bar-blue" d="M168 338 H292" stroke="#2563eb" stroke-width="18"/>
    <path class="dashboard-bar bar-green" d="M424 246 H548" stroke="#0f766e" stroke-width="18"/>
    <path class="dashboard-bar bar-green" d="M424 292 H512" stroke="#0f766e" stroke-width="18"/>
    <path class="dashboard-bar bar-green" d="M424 338 H532" stroke="#0f766e" stroke-width="18"/>
    <path class="dashboard-bar bar-amber" d="M680 246 H792" stroke="#f59e0b" stroke-width="18"/>
    <path class="dashboard-bar bar-amber" d="M680 292 H760" stroke="#f59e0b" stroke-width="18"/>
    <path class="dashboard-bar bar-amber" d="M680 338 H806" stroke="#f59e0b" stroke-width="18"/>
  </g>
  <g class="dashboard-labels" fill="#334155" font-family="Inter, Arial, sans-serif" font-size="24" font-weight="750">
    <text x="134" y="444">stagger cards</text>
    <text x="390" y="444">scale bars</text>
    <text x="646" y="444">pulse dots</text>
  </g>
</svg>
`,"timeline-machine":`<svg class="anime-svg-asset anime-svg-timeline-machine" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img" aria-labelledby="timeline-machine-title timeline-machine-desc">
  <title id="timeline-machine-title">Timeline machine asset</title>
  <desc id="timeline-machine-desc">A machine-themed SVG with cable paths, gears, a conveyor block, and signals for Anime.js timeline sequencing.</desc>
  <rect class="svg-backdrop" width="960" height="540" rx="42" fill="#f8fafc"/>
  <g class="machine-rails" fill="none" stroke-linecap="round">
    <path class="machine-cable machine-cable-main" d="M126 178 C246 116 342 126 420 204 S596 318 800 184" stroke="#2563eb" stroke-width="12"/>
    <path class="machine-cable machine-cable-secondary" d="M126 346 C244 292 350 318 452 366 S664 410 808 312" stroke="#0f766e" stroke-width="10"/>
  </g>
  <g class="machine-stations" data-anime-group="stations">
    <rect x="96" y="132" width="112" height="92" rx="18" fill="#ffffff" stroke="#cbd5e1" stroke-width="4"/>
    <rect x="756" y="140" width="112" height="92" rx="18" fill="#ffffff" stroke="#cbd5e1" stroke-width="4"/>
    <rect x="96" y="300" width="112" height="92" rx="18" fill="#ffffff" stroke="#cbd5e1" stroke-width="4"/>
    <rect x="756" y="276" width="112" height="92" rx="18" fill="#ffffff" stroke="#cbd5e1" stroke-width="4"/>
  </g>
  <g class="machine-gears" transform="translate(480 270)">
    <path class="machine-gear gear-blue" d="M0 -62 L14 -38 L42 -44 L38 -16 L62 0 L38 16 L42 44 L14 38 L0 62 L-14 38 L-42 44 L-38 16 L-62 0 L-38 -16 L-42 -44 L-14 -38 Z" fill="#dbeafe" stroke="#2563eb" stroke-width="6"/>
    <circle cx="0" cy="0" r="22" fill="#2563eb"/>
  </g>
  <g class="machine-conveyor" data-anime-group="conveyor">
    <path d="M268 438 H692" stroke="#94a3b8" stroke-width="12" stroke-linecap="round"/>
    <rect class="machine-block" x="294" y="402" width="86" height="64" rx="14" fill="#fef3c7" stroke="#f59e0b" stroke-width="5"/>
  </g>
  <g class="machine-signals" data-anime-group="signals">
    <circle class="machine-signal" cx="152" cy="178" r="18" fill="#db2777"/>
    <circle class="machine-signal" cx="812" cy="186" r="18" fill="#2563eb"/>
    <circle class="machine-signal" cx="152" cy="346" r="18" fill="#0f766e"/>
    <circle class="machine-signal" cx="812" cy="322" r="18" fill="#f59e0b"/>
  </g>
</svg>
`,"interactive-hotspots":`<svg class="anime-svg-asset anime-svg-interactive-hotspots" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img" aria-labelledby="interactive-hotspots-title interactive-hotspots-desc">
  <title id="interactive-hotspots-title">Interactive hotspots asset</title>
  <desc id="interactive-hotspots-desc">A map-like SVG with route, hotspot, and callout hooks for Anime.js stagger, draw, and click-state animations.</desc>
  <rect class="svg-backdrop" width="960" height="540" rx="42" fill="#f8fafc"/>
  <path class="map-region region-blue" d="M112 158 C214 78 330 124 366 220 C394 294 328 370 206 358 C122 350 58 244 112 158 Z" fill="#dbeafe" stroke="#93c5fd" stroke-width="5"/>
  <path class="map-region region-green" d="M412 118 C526 72 650 124 676 234 C704 348 604 438 474 394 C376 360 314 184 412 118 Z" fill="#dcfce7" stroke="#86efac" stroke-width="5"/>
  <path class="map-region region-amber" d="M668 186 C746 116 872 146 898 250 C926 362 826 432 724 398 C634 368 594 252 668 186 Z" fill="#fef3c7" stroke="#fcd34d" stroke-width="5"/>
  <path class="map-route" d="M184 272 C292 186 366 298 470 246 S650 168 768 292" fill="none" stroke="#334155" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
  <g class="map-hotspots" data-anime-group="hotspots">
    <g class="map-hotspot" data-region="west" transform="translate(184 272)">
      <circle r="28" fill="#2563eb"/>
      <circle r="10" fill="#ffffff"/>
    </g>
    <g class="map-hotspot" data-region="center" transform="translate(470 246)">
      <circle r="28" fill="#0f766e"/>
      <circle r="10" fill="#ffffff"/>
    </g>
    <g class="map-hotspot" data-region="east" transform="translate(768 292)">
      <circle r="28" fill="#f59e0b"/>
      <circle r="10" fill="#ffffff"/>
    </g>
  </g>
  <g class="map-callouts" fill="#ffffff" stroke="#cbd5e1" stroke-width="4" data-anime-group="callouts">
    <rect class="map-callout" x="98" y="390" width="174" height="64" rx="14"/>
    <rect class="map-callout" x="384" y="58" width="174" height="64" rx="14"/>
    <rect class="map-callout" x="682" y="390" width="174" height="64" rx="14"/>
  </g>
  <g class="map-labels" fill="#334155" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="750">
    <text x="132" y="430">hotspot A</text>
    <text x="418" y="98">hotspot B</text>
    <text x="716" y="430">hotspot C</text>
  </g>
</svg>
`},b={"drawable-circuit":{title:`Drawable Circuit`,summary:`Independent circuit paths and nodes for path draw-on, node pulse, and staggered signal sequencing.`,file:`examples/slidev-animejs/assets/animated-svg/drawable-circuit.svg`,api:[`svg.createDrawable`,`animate`,`stagger`],selectors:[`.svg-drawable`,`.svg-node`,`[data-anime-group="drawables"]`],clickStory:`Click steps change the draw origin and node emphasis while the SVG structure stays stable.`},"motion-orbit":{title:`Motion Orbit`,summary:`A routed orbit path with a traveler group, pulses, and rings for path-following motion.`,file:`examples/slidev-animejs/assets/animated-svg/motion-orbit.svg`,api:[`svg.createMotionPath`,`svg.createDrawable`,`animate`],selectors:[`#orbit-path`,`#orbit-traveler`,`.orbit-ring`,`.orbit-pulse`],clickStory:`Click steps change ring direction and route timing without touching path geometry.`},"morphing-badge":{title:`Morphing Badge`,summary:`One visible source path plus hidden compatible target paths for controlled shape morphing.`,file:`examples/slidev-animejs/assets/animated-svg/morphing-badge.svg`,api:[`svg.morphTo`,`animate`,`stagger`],selectors:[`#badge-source`,`#badge-target-star`,`#badge-target-wave`,`#badge-target-diamond`,`.badge-spark`],clickStory:`Click steps pick diamond, star, or wave targets through the same source path.`},"stagger-dashboard":{title:`Stagger Dashboard`,summary:`Repeated cards, bars, and status dots sized for staggered entrance and metric animation.`,file:`examples/slidev-animejs/assets/animated-svg/stagger-dashboard.svg`,api:[`animate`,`stagger`],selectors:[`.dashboard-card`,`.dashboard-bar`,`.dashboard-dot`],clickStory:`Click steps change stagger origin and bar reach while preserving dashboard layout.`},"timeline-machine":{title:`Timeline Machine`,summary:`Cable paths, gear, conveyor block, and signal lamps for label-based timeline choreography.`,file:`examples/slidev-animejs/assets/animated-svg/timeline-machine.svg`,api:[`createTimeline`,`svg.createDrawable`,`animate`],selectors:[`.machine-cable`,`.machine-gear`,`.machine-block`,`.machine-signal`],clickStory:`Click steps vary conveyor distance and signal overlap inside one repeatable timeline.`},"interactive-hotspots":{title:`Interactive Hotspots`,summary:`Map regions, a route, hotspots, and callouts for pointer or click-driven state animation.`,file:`examples/slidev-animejs/assets/animated-svg/interactive-hotspots.svg`,api:[`svg.createDrawable`,`animate`,`stagger`],selectors:[`.map-route`,`.map-hotspot`,`.map-callout`,`[data-region]`],clickStory:`Click steps rotate the active hotspot emphasis from west to center to east.`}};function x(e){return{slug:e,...b[e]}}var S=[`data-asset`],C={class:`svg-asset-header`},w={class:`svg-asset-body`},T=[`innerHTML`],E={class:`svg-asset-notes`},D={__name:`SvgAssetSlide`,props:{asset:{type:String,required:!0},step:{type:Number,default:0}},setup(b){let{$slidev:D,$nav:O,$clicksContext:k,$clicks:A,$page:j,$renderContext:M,$frontmatter:N}=d(),P=b,F=s(null),I=o(()=>x(P.asset)),L=o(()=>y[P.asset]||``),R=o(()=>Math.min(Math.max(Number(P.step)||0,0),2)),z=null;function B(){z&&=(z.revert(),null)}function V(e){return F.value.querySelector(e)}function H(e){return Array.from(F.value.querySelectorAll(e))}function U(e){return H(e).flatMap(e=>h(e))}function W(){f(U(`.svg-drawable`),{draw:[`0 0`,`0 1`],delay:p(120,{from:R.value===0?`first`:R.value===1?`center`:`last`}),duration:1800,ease:`inOutQuad`,loop:!0,loopDelay:280}),f(`.svg-node`,{scale:[.82,1.18],opacity:[.62,1],transformOrigin:`center`,delay:p(80,{from:R.value===2?`last`:`first`}),duration:760,ease:`outBack(2)`,loop:!0,alternate:!0})}function G(){let e=V(`#orbit-path`);f(V(`#orbit-traveler`),{..._(e),duration:R.value>1?2200:3e3,ease:`linear`,loop:!0}),f(h(e),{draw:[`0 0`,`0 1`],duration:R.value>0?2200:3e3,ease:`linear`,loop:!0}),f(`.orbit-ring`,{rotate:R.value===1?`-1turn`:`1turn`,transformOrigin:`center`,delay:p(90),duration:3600,ease:`linear`,loop:!0}),f(`.orbit-pulse`,{scale:[.7,1.22],opacity:[.42,.9],transformOrigin:`center`,delay:p(140),duration:860,ease:`inOutSine`,loop:!0,alternate:!0})}function K(){f(`#badge-source`,{d:v([`#badge-target-diamond`,`#badge-target-star`,`#badge-target-wave`][R.value],.65),fill:[`#0f766e`,`#2563eb`,`#db2777`][R.value],duration:1500,ease:`inOutExpo`,loop:!0,alternate:!0}),f(`.badge-spark`,{scale:[.82,1.22],opacity:[.56,1],transformOrigin:`center`,delay:p(70,{from:`center`}),duration:680,ease:`outBack(2)`,loop:!0,alternate:!0})}function q(){f(`.dashboard-card`,{y:[12,0],opacity:[.58,1],delay:p(120,{from:R.value===0?`first`:R.value===1?`center`:`last`}),duration:900,ease:`outExpo`,loop:!0,alternate:!0}),f(`.dashboard-bar`,{scaleX:[.18,R.value>1?1.08:.92],transformOrigin:`left center`,delay:p(70),duration:980,ease:`inOutQuad`,loop:!0,alternate:!0}),f(`.dashboard-dot`,{scale:[.78,1.18],transformOrigin:`center`,delay:p(90),duration:680,ease:`outBack(2)`,loop:!0,alternate:!0})}function J(){f(U(`.machine-cable`),{draw:[`0 0`,`0 1`],delay:p(160),duration:1700,ease:`inOutQuad`,loop:!0}),m({defaults:{duration:900,ease:`outExpo`},loop:!0,alternate:!0}).label(`start`).add(`.machine-gear`,{rotate:`1turn`,transformOrigin:`center`,duration:1900,ease:`linear`},`start`).add(`.machine-block`,{x:R.value>1?286:214},`start+=120`).add(`.machine-signal`,{scale:[.72,1.2],opacity:[.4,1],transformOrigin:`center`,delay:p(110)},`start+=240`)}function Y(){f(h(V(`.map-route`)),{draw:[`0 0`,`0 1`],duration:1800,ease:`inOutQuad`,loop:!0}),f(`.map-hotspot`,{scale:[.82,1.22],opacity:[.72,1],transformOrigin:`center`,delay:p(120,{from:R.value===0?`first`:R.value===1?`center`:`last`}),duration:760,ease:`outBack(2)`,loop:!0,alternate:!0}),f(`.map-callout`,{y:[10,0],opacity:[.58,1],delay:p(130),duration:860,ease:`outExpo`,loop:!0,alternate:!0})}let X={"drawable-circuit":W,"motion-orbit":G,"morphing-badge":K,"stagger-dashboard":q,"timeline-machine":J,"interactive-hotspots":Y};async function Z(){F.value&&(B(),await n(),z=g({root:F.value,defaults:{duration:900,ease:`outExpo`}}),z.add(()=>{X[I.value.slug]()}))}return t(Z),e(B),r(()=>[P.asset,R.value],Z,{flush:`post`}),(e,t)=>(u(),a(`section`,{ref_key:`root`,ref:F,class:`svg-asset-slide`,"data-asset":I.value.slug},[i(`div`,C,[i(`div`,null,[t[0]||=i(`p`,{class:`eyebrow`},`generated svg asset`,-1),i(`h2`,null,l(I.value.title),1)]),i(`p`,null,l(I.value.summary),1)]),i(`div`,w,[i(`div`,{class:c([`svg-asset-stage`,`stage-${I.value.slug}`]),innerHTML:L.value},null,10,T),i(`aside`,E,[i(`div`,null,[t[1]||=i(`h3`,null,`Source File`,-1),i(`p`,null,l(I.value.file),1)]),i(`div`,null,[t[2]||=i(`h3`,null,`Anime.js APIs`,-1),i(`p`,null,l(I.value.api.join(`, `)),1)]),i(`div`,null,[t[3]||=i(`h3`,null,`Animation Hooks`,-1),i(`p`,null,l(I.value.selectors.join(`, `)),1)]),i(`div`,null,[t[4]||=i(`h3`,null,`Click Story`,-1),i(`p`,null,l(I.value.clickStory),1)])])])],8,S))}};export{D as t};
