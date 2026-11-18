"""Reactive layer for Agent Works: everything that responds to app state.

gen.py calls css(globals()) after it builds the scene. The overlay SVG uses the
same viewBox and `center bottom / cover` sizing as the scene, so its pixels line
up with the scene's pixels at any window size without measuring anything.
"""

A = '#ffb547'     # amber phosphor
A1 = '#ff9a2e'    # deep amber
A2 = '#ffe2a8'    # hot filament

CONV = '[data-workspace-area="conversation"]'
LIVE = '[data-timeline-row-kind="working"],[data-timeline-row-kind="work-live"]'
ON = f'{CONV}:has({LIVE})'


def overlay(ns):
    """Lights-on layer: lamp cones and pools, lit sign, chase lights, LEDs."""
    g, text, R = ns['g'], ns['text'], ns['R']
    BX0, BX1, DY = ns['BX0'], ns['BX1'], ns['DY']
    sx, SY = ns['sx'], ns['SY']
    defs = (
        f"<linearGradient id='c' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{A}' stop-opacity='.42'/>"
        f"<stop offset='1' stop-color='{A1}' stop-opacity='0'/></linearGradient>"
        f"<radialGradient id='p'><stop offset='0' stop-color='{A}' stop-opacity='.38'/>"
        f"<stop offset='1' stop-color='{A1}' stop-opacity='0'/></radialGradient>"
        f"<radialGradient id='b'><stop offset='0' stop-color='{A2}' stop-opacity='.9'/>"
        f"<stop offset='.25' stop-color='{A}' stop-opacity='.45'/><stop offset='1' stop-color='{A1}' stop-opacity='0'/></radialGradient>"
    )
    s = ''
    for lx in ns.get('LAMPS', (100, 382)):
        s += (f"<path fill='url(#c)' d='M{lx - 4} 178L{lx + 5} 178L{lx + 34} 270L{lx - 33} 270Z'/>"
              f"<ellipse fill='url(#p)' cx='{lx + .5}' cy='268' rx='46' ry='9'/>"
              f"<circle fill='url(#b)' cx='{lx + .5}' cy='178' r='16'/>"
              f"<path fill='{A2}' d='{R(lx - 1, 177, 3, 1)}'/>"
              )
    # sign: warm glow behind, amber letters on top
    s += f"<ellipse fill='url(#p)' cx='240' cy='{SY + 5}' rx='44' ry='14'/>"
    s += g(text('AGENT WORKS', sx, SY + 3, A2), cls='sg')
    # chase lights along the belt skirt, running with the belt
    y = 119 + DY
    s += f"<path class='ch' stroke='{A}' stroke-width='2' stroke-dasharray='2 14' d='M{BX0 + 10} {y}H{BX1 - 4}'/>"
    # control panel and press LEDs
    s += g([(A, 8, 221, 2, 2)], cls='ld') + g([(A1, 12, 221, 2, 2)], cls='ld d')
    s += g([(A, 341, 187, 2, 2), (A2, 346, 187, 2, 2), (A1, 351, 187, 2, 2)], cls='ld d')
    st = (".ch{animation:k .6s linear infinite}@keyframes k{to{stroke-dashoffset:-16}}"
          ".ld{animation:l .8s steps(1) infinite}.d{animation-delay:-.4s}@keyframes l{50%{opacity:.2}}"
          ".sg{animation:sg 6s steps(1) infinite}@keyframes sg{0%,100%{opacity:1}71%{opacity:.4}72%{opacity:1}}"
          "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 480 320' preserveAspectRatio='xMidYMax slice' "
            f"shape-rendering='crispEdges'><style>{st}</style><defs>{defs}</defs>{s}</svg>")


def css(ns):
    enc = ns['enc']
    over = 'data:image/svg+xml,' + enc(overlay(ns))
    
    rm = '@media (prefers-reduced-motion:reduce)'
    out = f"""
{CONV}{{position:relative;isolation:isolate;animation:aw-on .7s cubic-bezier(.2,.7,.2,1) both}}
@keyframes aw-on{{0%{{clip-path:inset(50% 0 50% 0);filter:brightness(4) contrast(2)}}
18%{{clip-path:inset(49.6% 8% 49.6% 8%);filter:brightness(5)}}
45%{{clip-path:inset(0 0 0 0);filter:brightness(1.8)}}100%{{clip-path:inset(0 0 0 0);filter:none}}}}
{CONV}::before{{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;mix-blend-mode:screen;opacity:0;
background:url("{over}") center bottom/cover no-repeat;transition:opacity 1.2s ease}}
{CONV}::after{{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;opacity:.35;transition:opacity 1.2s ease;
background:radial-gradient(ellipse 70% 60% at 50% 40%,transparent,rgba(0,0,0,.6))}}
{ON}::before{{opacity:1;animation:aw-flick 1.1s steps(1) both}}
{ON}::after{{opacity:0}}
@keyframes aw-flick{{0%{{opacity:0}}6%{{opacity:.9}}10%{{opacity:.1}}16%{{opacity:1}}22%{{opacity:.3}}30%,100%{{opacity:1}}}}
{','.join(f'[data-timeline-row-kind="{k}"]>*' for k in ('work-live', 'working'))}{{position:relative;
box-shadow:0 -2px {A1},0 2px {A1},-2px 0 {A1},2px 0 {A1},0 0 18px rgba(255,154,46,.28),4px 4px 0 2px rgba(0,0,0,.4)!important}}
{','.join(f'[data-timeline-row-kind="{k}"]>*::after' for k in ('work-live', 'working'))}{{content:"";position:absolute;left:0;right:0;bottom:-2px;height:2px;
background:repeating-linear-gradient(90deg,{A2} 0 6px,transparent 6px 12px);background-size:24px 2px;animation:aw-belt .5s linear infinite;pointer-events:none}}
@keyframes aw-belt{{to{{background-position:24px 0}}}}
[data-streaming="true"]>:last-child::after{{content:"";display:inline-block;width:.55em;height:1.05em;margin-left:2px;vertical-align:-.15em;
background:{A};box-shadow:0 0 8px {A1};animation:aw-cur 1s steps(1) infinite}}
@keyframes aw-cur{{50%{{opacity:0}}}}
[data-slot="composer-host"]:focus-within{{background-image:linear-gradient(90deg,transparent,rgba(255,181,71,.0) 40%,rgba(255,181,71,.55) 50%,rgba(255,181,71,0) 60%,transparent)!important;
background-size:300% 2px!important;background-repeat:no-repeat!important;background-position:120% 0;animation:aw-sweep .9s ease-out both}}
@keyframes aw-sweep{{from{{background-position:120% 0}}to{{background-position:-20% 0}}}}
body:has({LIVE}) [data-slot="composer-host"]{{box-shadow:0 -2px {A1},0 2px {A1},-2px 0 {A1},2px 0 {A1},0 0 22px rgba(255,154,46,.22),5px 5px 0 2px rgba(0,0,0,.5)!important}}
{rm}{{{CONV},{CONV}::before,[data-slot="composer-host"],[data-timeline-row-kind]>*::after,[data-streaming]>*::after{{animation:none!important}}}}
"""
    return ''.join(l.strip() for l in out.strip().splitlines())
