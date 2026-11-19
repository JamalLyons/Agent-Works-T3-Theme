"""Reactive layer for Agent Works: everything that responds to app state.

gen.py calls overlay() and css() with its ANCHORS and pixel helpers after it builds the scene. The overlay SVG uses the
same viewBox and `center bottom / cover` sizing as the scene, so its pixels line
up with the scene's pixels at any window size without measuring anything.
"""

A = '#ffb547'     # amber phosphor
A1 = '#ff9a2e'    # deep amber
A2 = '#ffe2a8'    # hot filament

CONV = '[data-workspace-area="conversation"]'
LIVE = '[data-timeline-row-kind="working"],[data-timeline-row-kind="work-live"]'
ON = f'{CONV}:has({LIVE})'
SB = '[data-slot="sidebar-inner"]'
ROW = '[data-sidebar-row]'
CUR = f'{ROW}[aria-current="page"]'
SHELF = '[data-testid="sidebar-working-header"]'      # the sidebar's "Working" shelf; present while any thread runs
BUSY = (f'body:has({LIVE})', f'body:has({SHELF})')     # an agent is working somewhere

def busy(sel):
    """`sel` scoped to 'an agent is working', for both signals."""
    return ','.join(f'{b} {sel}' for b in BUSY)


def overlay(an, g, text, R):
    """Lights-on layer: lamp cones and pools, lit sign, chase lights, LEDs.

    an: gen.ANCHORS (all positions). g, text, R: gen.py's pixel helpers.
    """
    BX0, BX1 = an['belt']['x0'], an['belt']['x1']
    sx, SY = an['sign']['x'], an['sign']['y']
    by = an['bulbY']
    defs = (
        f"<linearGradient id='c' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{A}' stop-opacity='.42'/>"
        f"<stop offset='1' stop-color='{A1}' stop-opacity='0'/></linearGradient>"
        f"<radialGradient id='p'><stop offset='0' stop-color='{A}' stop-opacity='.38'/>"
        f"<stop offset='1' stop-color='{A1}' stop-opacity='0'/></radialGradient>"
        f"<radialGradient id='b'><stop offset='0' stop-color='{A2}' stop-opacity='.9'/>"
        f"<stop offset='.25' stop-color='{A}' stop-opacity='.45'/><stop offset='1' stop-color='{A1}' stop-opacity='0'/></radialGradient>"
    )
    s = ''
    for lx in an['lamps']:
        s += (f"<path fill='url(#c)' d='M{lx - 4} {by + 1}L{lx + 5} {by + 1}L{lx + 34} 270L{lx - 33} 270Z'/>"
              f"<ellipse fill='url(#p)' cx='{lx + .5}' cy='268' rx='46' ry='9'/>"
              f"<circle fill='url(#b)' cx='{lx + .5}' cy='{by + 1}' r='16'/>"
              f"<path fill='{A2}' d='{R(lx - 1, by, 3, 1)}'/>"
              )
    # sign: warm glow behind, amber letters on top
    s += f"<ellipse fill='url(#p)' cx='240' cy='{SY + 5}' rx='44' ry='14'/>"
    s += g(text('AGENT WORKS', sx, SY + 3, A2), cls='sg')
    # chase lights along the belt skirt, running with the belt
    y = an['belt']['skirtY']
    s += f"<path class='ch' stroke='{A}' stroke-width='2' stroke-dasharray='2 14' d='M{BX0 + 10} {y}H{BX1 - 4}'/>"
    # control panel and press LEDs
    (p0, p1), (q0, q1, q2) = an['panelLeds'], an['pressLeds']
    s += g([(A, *p0, 2, 2)], cls='ld') + g([(A1, *p1, 2, 2)], cls='ld d')
    s += g([(A, *q0, 2, 2), (A2, *q1, 2, 2), (A1, *q2, 2, 2)], cls='ld d')
    st = (".ch{animation:k .625s linear infinite}@keyframes k{to{stroke-dashoffset:-16}}"
          ".ld{animation:l .8s steps(1) infinite}.d{animation-delay:-.4s}@keyframes l{50%{opacity:.2}}"
          ".sg{animation:sg 5s steps(1) infinite}@keyframes sg{0%,100%{opacity:1}71%{opacity:.4}72%{opacity:1}}"
          "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 480 320' preserveAspectRatio='xMidYMax slice' "
            f"shape-rendering='crispEdges'><style>{st}</style><defs>{defs}</defs>{s}</svg>")


SEL = 'rgba(220,221,219,.1)'   # selection: neutral steel, readable on any monogram color
SEL_SH = 'inset 0 0 0 1px rgba(220,221,219,.14),0 0 14px rgba(0,0,0,.35)'
WAIT = '[data-approval-detail],[data-pending-user-input-toggle]'   # approval or question pending: the line is on hold
WAITS = tuple(f'body:has({w})' for w in WAIT.split(','))

def wait_css(HZ):
    """Hold state, plus the static control-panel surfaces (palette, menus, toasts, drop dock, plan, terminal, settings)."""
    hold = ','.join(f'{w} {CONV}::before' for w in WAITS)
    rail = ','.join(f'{w} [data-slot="sidebar-inner"]::after' for w in WAITS)
    comp = ','.join(f'{w} [data-slot="composer-host"]' for w in WAITS)
    glow = ','.join(f'{w} [data-slot="composer-host"]::before' for w in WAITS)   # blink only the glow; opacity on the host would fade the whole question card
    item = ','.join(f'[data-slot="{k}"][data-highlighted]' for k in ('menu-item', 'command-item', 'select-item', 'combobox-item'))
    out = f"""
{hold}{{opacity:1;animation:aw-hold 1.6s steps(1) infinite}}
@keyframes aw-hold{{50%{{opacity:.3}}}}
{rail}{{opacity:1;animation:none;background:{HZ} right 0 top 0/3px 100% no-repeat,linear-gradient(270deg,rgba(255,154,46,.28),transparent)}}
{comp}{{box-shadow:0 -2px {A},0 2px {A},-2px 0 {A},2px 0 {A},5px 5px 0 2px rgba(0,0,0,.5)!important}}
{glow}{{content:"";position:absolute;inset:0;pointer-events:none;box-shadow:0 0 26px rgba(255,154,46,.45);animation:aw-hold 1.6s steps(1) infinite}}
[data-timeline-row-kind]>:has([data-approval-detail]){{position:relative;box-shadow:0 0 22px rgba(255,154,46,.3),4px 4px 0 2px rgba(0,0,0,.4)!important}}
[data-timeline-row-kind]>:has([data-approval-detail])::before{{content:"";position:absolute;inset:-3px;padding:3px;pointer-events:none;background:{HZ};background-size:17px 17px;
mask:linear-gradient(#000 0 0) content-box exclude,linear-gradient(#000 0 0);animation:aw-tape 1.2s linear infinite}}
@keyframes aw-tape{{to{{background-position:17px 0}}}}
[data-command-palette]{{border-radius:0!important;background-image:repeating-linear-gradient(0deg,rgba(0,0,0,.18) 0 1px,transparent 1px 3px)!important;
box-shadow:0 -3px {A1},0 0 0 2px #5c5f63,8px 8px 0 rgba(0,0,0,.55),0 0 40px rgba(255,154,46,.12)!important}}
[data-command-palette] input,.composer-tiptap{{caret-color:{A}}}
{item}{{background:{SEL}!important;box-shadow:{SEL_SH}!important;border-radius:0!important}}
[data-slot="toast-popup"]{{border-radius:0!important;box-shadow:inset 3px 0 {A1},0 0 0 2px #4a4d51,5px 5px 0 rgba(0,0,0,.5)!important}}
[data-chat-workspace-drop-overlay="true"]{{border-radius:0!important;background:repeating-linear-gradient(-45deg,rgba(255,181,71,.12) 0 14px,rgba(12,13,14,.55) 14px 28px)!important;
box-shadow:inset 0 0 0 3px {A},inset 0 0 60px rgba(255,154,46,.25)!important;color:{A2}!important}}
[data-timeline-row-kind="proposed-plan"]>*{{background:linear-gradient(rgba(255,181,71,.06) 1px,transparent 1px) 0 0/16px 16px,
linear-gradient(90deg,rgba(255,181,71,.06) 1px,transparent 1px) 0 0/16px 16px,rgba(20,21,23,.94)!important;box-shadow:0 -2px {A1},0 2px #5c5f63,-2px 0 #5c5f63,2px 0 #5c5f63,4px 4px 0 2px rgba(0,0,0,.45)!important}}
[data-model-picker-selected-indicator="true"]{{color:{A}!important;filter:drop-shadow(0 0 3px {A1})}}
[data-thread-terminal-drawer]{{border-top:2px solid #4a4d51!important;box-shadow:0 -2px 0 #0c0d0e,0 -8px 18px rgba(0,0,0,.35)!important}}
[data-slot="skeleton"]{{border-radius:0!important;background:#2f3235!important}}
[data-settings-page-scroll]{{background:linear-gradient(rgba(20,21,23,.9),rgba(20,21,23,.97)),var(--theme-background-image) center bottom/cover no-repeat!important}}
[data-slot="settings-group"]{{border-radius:0!important}}
"""
    return ''.join(l.strip() for l in out.strip().splitlines())

PANEL = '[data-workspace-area="panel"]'   # the right panel (browser, terminal, files, diff, PRs, ...)
CARD = '[data-thread-details-card]'   # the thread details card (branch, PR, changes), inline or as a popover

def details_css():
    """Right panel as a lit control wall, and the thread details card as a steel control panel; an amber chase on its top edge while an agent works."""
    out = f"""
{CARD}{{position:relative;border-radius:0!important;border:0!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important;
background:repeating-linear-gradient(0deg,rgba(0,0,0,.18) 0 1px,transparent 1px 3px),linear-gradient(#1f2123,#17181a)!important;
box-shadow:0 -2px #6a6d71,0 0 0 2px #4a4d51,inset 0 1px rgba(220,221,219,.06),6px 6px 0 rgba(0,0,0,.5)!important}}
{CARD}::before{{content:"";position:absolute;left:0;right:0;top:-2px;height:2px;z-index:2;pointer-events:none;opacity:0;transition:opacity 1.2s ease;
background:repeating-linear-gradient(90deg,{A2} 0 6px,transparent 6px 16px) 0 0/32px 2px}}
{busy(f'{CARD}::before')}{{opacity:1;animation:aw-flick 1.1s steps(1) both,aw-chase .8s linear 1.1s infinite}}
@keyframes aw-chase{{to{{background-position:32px 0}}}}
{CARD} [data-slot="separator"],{CARD} [role="separator"]{{height:2px!important;border:0!important;background:repeating-linear-gradient(90deg,#55585c 0 2px,transparent 2px 10px),#26282b!important}}
{CARD} [data-slot="button"]{{border-radius:0!important}}
{CARD} :is(a,button,[role="button"],[data-slot="button"]):hover{{background-color:{SEL}!important}}
{CARD} [data-pull-request-action-pending] [data-slot="button"]{{background:#2a2c2f!important;box-shadow:0 0 0 1px #5c5f63,2px 2px 0 rgba(0,0,0,.5)!important;color:#dcdddb!important}}
{CARD} [data-pull-request-action-pending] [data-slot="button"]:hover{{box-shadow:0 0 0 1px {A},0 0 10px rgba(255,154,46,.35),2px 2px 0 rgba(0,0,0,.5)!important;color:{A2}!important}}
{CARD} [data-pull-request-action-pending="true"] [data-slot="button"]{{color:{A}!important;box-shadow:0 0 0 1px {A1},0 0 12px rgba(255,154,46,.4)!important;animation:aw-lamp 1.2s steps(1) infinite}}
{PANEL}{{position:relative;isolation:isolate;border-left:2px solid #0c0d0e!important;box-shadow:inset 2px 0 #3a3d40!important}}
{PANEL}::before{{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;
background:repeating-linear-gradient(0deg,rgba(0,0,0,.22) 0 1px,transparent 1px 3px),linear-gradient(rgba(17,18,20,.86),rgba(17,18,20,.93)),var(--theme-background-image) center bottom/cover no-repeat fixed}}
{PANEL}::after{{content:"";position:absolute;top:-16px;bottom:0;left:0;width:2px;z-index:3;pointer-events:none;opacity:0;transition:opacity 1.2s ease;will-change:transform;
background:repeating-linear-gradient(180deg,{A2} 0 4px,transparent 4px 16px)}}
{busy(f'{PANEL}::after')}{{opacity:1;animation:aw-flick 1.1s steps(1) both,aw-rail .8s linear 1.1s infinite}}
{PANEL} [data-right-panel-tabbar]{{background:repeating-linear-gradient(0deg,rgba(0,0,0,.18) 0 1px,transparent 1px 3px),linear-gradient(#232527,#1a1b1d)!important;
border-bottom:2px solid #0c0d0e!important;box-shadow:0 1px #3a3d40!important}}
{PANEL} [data-surface-subheader]{{background:rgba(20,21,23,.9)!important;border-bottom:2px solid #2a2c2f!important}}
{PANEL} [data-right-panel-surface-content]{{background:transparent!important}}
{PANEL} :is([data-slot="toggle"],[data-slot="toggle-group"],[data-slot="badge"],[data-slot="kbd"],[data-slot="tabs-tab"],[role="tab"],[data-slot="input"],[data-slot="collapsible"]){{border-radius:0!important}}
{PANEL} [role="tab"][aria-selected="true"],{PANEL} [data-slot="toggle"][data-pressed]{{background:{SEL}!important;box-shadow:inset 0 -2px {A}!important}}
{PANEL} :is([data-slot="table-row"],[data-changed-file-row]):hover{{background:rgba(220,221,219,.06)!important}}
"""
    return ''.join(l.strip() for l in out.strip().splitlines())

def css(an, g, text, R, enc):
    """Reactive CSS. enc: gen.enc, the data: URI escaper."""
    over = 'data:image/svg+xml,' + enc(overlay(an, g, text, R))

    rm = '@media (prefers-reduced-motion:reduce)'
    HZ = f'repeating-linear-gradient(-45deg,{A} 0 6px,#141517 6px 12px)'   # hazard tape
    WAIT_CSS = wait_css(HZ)
    HOLD_ANIM = f'{",".join(f"{w} {CONV}::before" for w in WAITS)},{",".join(f"{w} [data-slot=composer-host]::before" for w in WAITS)},[data-timeline-row-kind]>:has([data-approval-detail])::before'
    SCAN_SB = 'repeating-linear-gradient(0deg,rgba(0,0,0,.22) 0 1px,transparent 1px 3px)'
    out = f"""
{CONV}{{position:relative;isolation:isolate;animation:aw-on .7s cubic-bezier(.2,.7,.2,1) both}}
@keyframes aw-on{{0%{{clip-path:inset(50% 0 50% 0);filter:brightness(4) contrast(2)}}
18%{{clip-path:inset(49.6% 8% 49.6% 8%);filter:brightness(5)}}
45%{{clip-path:inset(0 0 0 0);filter:brightness(1.8)}}100%{{clip-path:inset(0 0 0 0);filter:none}}}}
{CONV}::before{{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;mix-blend-mode:screen;opacity:0;
background:url("{over}") center bottom/cover no-repeat fixed;transition:opacity 1.2s ease}}
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
{SB}{{position:relative;isolation:isolate}}
{SB}::before{{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;
background:{SCAN_SB},linear-gradient(90deg,rgba(17,18,20,.72),rgba(17,18,20,.5)),var(--theme-background-image) center bottom/cover no-repeat fixed}}
{SB}{{overflow:hidden}}
{SB}::after{{content:"";position:absolute;top:-16px;bottom:0;right:0;width:48px;z-index:-1;pointer-events:none;opacity:0;transition:opacity 1.2s ease;will-change:transform;
background:repeating-linear-gradient(180deg,{A2} 0 4px,transparent 4px 16px) right 0 top 0/2px 16px repeat-y,linear-gradient(270deg,rgba(255,154,46,.2),transparent)}}
{busy(f'{SB}::after')}{{opacity:1;animation:aw-flick 1.1s steps(1) both,aw-rail .8s linear 1.1s infinite}}
@keyframes aw-rail{{to{{transform:translateY(16px)}}}}
[data-testid="sidebar-working-shelf-toggle"]{{color:{A}!important;text-shadow:0 0 6px rgba(255,154,46,.6)}}
[data-testid="sidebar-working-shelf-toggle"]::before{{content:"";flex:none;width:6px;height:6px;background:{A2};box-shadow:0 0 0 1px {A1},0 0 8px {A};animation:aw-lamp 1.6s steps(1) infinite}}
@keyframes aw-lamp{{50%{{opacity:.35}}}}
{ROW}{{border-radius:0!important;transition:background .25s ease}}
{ROW}:hover{{background:rgba(220,221,219,.06)!important}}
{CUR}{{background:{SEL}!important;box-shadow:{SEL_SH}!important}}
{busy(f'{SB} [data-slot="project-monogram"]')}{{outline:1px solid rgba(255,181,71,.7);outline-offset:1px}}
{WAIT_CSS}
{details_css()}
{rm}{{{SB}::after,{PANEL}::after,{CARD}::before,{CARD} [data-pull-request-action-pending] [data-slot=button],[data-testid="sidebar-working-shelf-toggle"]::before,{HOLD_ANIM}{{animation:none!important}}{ROW}{{transition:none!important}}}}
{rm}{{{CONV},{CONV}::before,[data-slot="composer-host"],[data-timeline-row-kind]>*::after,[data-streaming]>*::after{{animation:none!important}}}}
"""
    return ''.join(l.strip() for l in out.strip().splitlines())
