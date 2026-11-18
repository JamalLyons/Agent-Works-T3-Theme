#!/usr/bin/env python3
"""Generates the 'Agent Works' pixel factory theme for T3 Code."""
import json, sys, urllib.parse

# ---------- palette: old B&W CRT grays ----------
G = ['#0c0d0e', '#141517', '#1c1e20', '#25272a', '#2f3235', '#3b3e42',
     '#4a4d51', '#5c5f63', '#717478', '#888b8e', '#a3a5a7', '#c1c3c3',
     '#dcdddb', '#f0f0ec']
K = G[0]


def R(x, y, w, h):
    return f'M{x} {y}h{w}v{h}h{-w}z'


def g(rects, cls=None, tr=None, extra=''):
    """rects: list of (color, x, y, w, h). Merges into one path per color."""
    by = {}
    for c, x, y, w, h in rects:
        by.setdefault(c, []).append(R(x, y, w, h))
    a = ''
    if cls:
        a += f" class='{cls}'"
    if tr:
        a += f" transform='{tr}'"
    a += extra
    body = ''.join(f"<path fill='{c}' d='{''.join(d)}'/>" for c, d in by.items())
    return f'<g{a}>{body}</g>'


def sprite(rows, pal, ox=0, oy=0):
    """ASCII map -> rects (horizontal runs)."""
    out = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            ch = row[x]
            if ch in pal:
                s = x
                while x < len(row) and row[x] == ch:
                    x += 1
                out.append((pal[ch], ox + s, oy + y, x - s, 1))
            else:
                x += 1
    return out


FONT = {
    'A': ['010', '101', '111', '101', '101'], 'G': ['011', '100', '101', '101', '011'],
    'E': ['111', '100', '110', '100', '111'], 'N': ['101', '111', '111', '111', '101'],
    'T': ['111', '010', '010', '010', '010'], 'W': ['101', '101', '101', '111', '101'],
    'O': ['010', '101', '101', '101', '010'], 'R': ['110', '101', '110', '101', '101'],
    'K': ['101', '101', '110', '101', '101'], 'S': ['011', '100', '010', '001', '110'],
    ' ': ['000'] * 5, '3': ['110', '001', '010', '001', '110'], 'N': ['110', '101', '101', '101', '101'],
}


def text(s, x, y, c):
    out = []
    for ch in s:
        for j, row in enumerate(FONT[ch]):
            for i, b in enumerate(row):
                if b == '1':
                    out.append((c, x + i, y + j, 1, 1))
        x += 4
    return out


# ---------- sprites ----------
def robot_head(eye_cls='ey'):
    """TV-headed agent. 17 wide. head rows 3..13. returns svg string (no transform)."""
    r = [
        (K, 7, 0, 1, 3),                      # antenna stalk
        (K, 2, 3, 13, 11), (G[10], 3, 4, 11, 9),  # head shell
        (G[12], 3, 4, 11, 1),                  # top highlight
        (G[8], 3, 12, 11, 1),                  # bottom shade
        (K, 4, 5, 7, 7), (G[4], 5, 6, 5, 5),     # screen bezel + glass
        (G[6], 5, 6, 2, 1),                    # glass glint
        (G[7], 12, 6, 1, 1), (K, 12, 8, 1, 1), (K, 12, 10, 1, 1),  # knobs
        (G[7], 7, 10, 1, 1),                   # mouth
    ]
    s = g(r)
    s += g([(G[13], 6, 8, 1, 2), (G[13], 9, 8, 1, 2)], cls=eye_cls)
    s += g([(G[13], 6, -2, 3, 2)], cls='an')
    return s


def robot_body(arm_cls=None, legs=False):
    r = [
        (K, 7, 14, 3, 1),                     # neck
        (K, 3, 15, 11, 9), (G[8], 4, 16, 9, 7), (G[10], 4, 16, 9, 1),
        (G[6], 4, 22, 9, 1),
        (K, 6, 18, 5, 2), (G[5], 7, 18, 3, 1),  # chest plate
    ]
    s = g(r)
    s += g([(G[13], 7, 19, 1, 1)], cls='la') + g([(G[11], 9, 19, 1, 1)], cls='lb')
    arms = [(K, 0, 16, 3, 6), (G[7], 1, 17, 1, 4), (G[11], 0, 21, 3, 2),
            (K, 14, 16, 3, 6), (G[7], 15, 17, 1, 4), (G[11], 14, 21, 3, 2)]
    s += g(arms, cls=arm_cls)
    return s


def box_sprite(x, y):
    r = [(K, x, y, 16, 14), (G[9], x + 1, y + 1, 14, 12), (G[11], x + 1, y + 1, 14, 1),
         (G[7], x + 1, y + 12, 14, 1), (G[7], x + 1, y + 4, 14, 1), (G[8], x + 7, y + 1, 2, 3)]
    return r


# ---------- scene ----------
parts = []
defs = []

# wall
defs.append("<pattern id='br' width='16' height='8' patternUnits='userSpaceOnUse'>"
            f"<path fill='{G[3]}' d='M0 0h16v8H0z'/>"
            f"<path fill='{G[2]}' d='M0 3h16v1H0zM0 7h16v1H0zM7 0h1v3H7zM15 4h1v3h-1z'/>"
            f"<path fill='{G[4]}' d='M1 0h5v1H1zM9 4h5v1H9z'/></pattern>")
parts.append(f"<path fill='url(%23br)' d='M0 0h320v132H0z'/>")
# soft light falloff on wall
defs.append("<radialGradient id='wl' cx='50%' cy='40%' r='65%'>"
            f"<stop offset='0' stop-color='{G[9]}' stop-opacity='.10'/>"
            f"<stop offset='1' stop-color='{K}' stop-opacity='.35'/></radialGradient>")
parts.append("<path fill='url(%23wl)' d='M0 0h320v132H0z'/>")

# windows with sky, clouds, distant chimneys
defs.append("<linearGradient id='sk' x1='0' y1='0' x2='0' y2='1'>"
            f"<stop offset='0' stop-color='{G[8]}'/><stop offset='1' stop-color='{G[10]}'/></linearGradient>")
defs.append("<pattern id='cl' width='60' height='30' patternUnits='userSpaceOnUse'>"
            f"<path fill='{G[11]}' d='M6 6h10v1h3v2H3V7h3zM34 15h8v1h3v2H30v-2h4zM48 3h6v1h2v1h-9V4h1z'/>"
            f"<path fill='{G[9]}' d='M3 9h16v1H3zM30 18h15v1H30z'/></pattern>")
for wx in (36, 240):
    cid = f'w{wx}'
    defs.append(f"<clipPath id='{cid}'><path d='{R(wx + 2, 20, 40, 26)}'/></clipPath>")
    parts.append(g([(K, wx - 1, 17, 46, 33), (G[6], wx, 18, 44, 30)]))
    inner = f"<path fill='url(%23sk)' d='{R(wx + 2, 20, 40, 26)}'/>"
    inner += f"<g class='cld'><path fill='url(%23cl)' opacity='.8' d='M{wx - 58} 20h160v26h-160z'/></g>"
    # distant factory silhouette
    inner += g([(G[7], wx + 2, 38, 40, 8), (G[7], wx + 8, 30, 4, 8), (G[7], wx + 26, 26, 4, 12),
                (G[6], wx + 2, 42, 40, 4), (G[7], wx + 14, 34, 8, 4)])
    for i, (sx, sy) in enumerate(((wx + 10, 28), (wx + 28, 24))):
        inner += f"<g class='smk s{i}'><path fill='{G[11]}' d='{R(sx - 1, sy - 2, 3, 2)}'/></g>"
    parts.append(f"<g clip-path='url(%23{cid})'>{inner}</g>")
    parts.append(g([(G[6], wx + 21, 20, 2, 26), (G[6], wx + 2, 32, 40, 2),
                    (G[8], wx, 18, 44, 1), (G[4], wx, 47, 44, 1), (G[9], wx - 2, 48, 48, 2), (K, wx - 2, 50, 48, 1)]))

# light shafts from windows
for wx in (36, 240):
    parts.append(f"<path class='sh' fill='{G[12]}' d='M{wx + 2} 46L{wx + 42} 46L{wx + 70} 132L{wx + 22} 132Z' opacity='.035'/>")

# ceiling beam + truss
parts.append(g([(G[1], 0, 0, 320, 6), (G[4], 0, 5, 320, 1), (G[2], 0, 6, 320, 1)] +
               [(G[6], x, 2, 1, 1) for x in range(6, 320, 16)]))

# sign: AGENT WORKS
sx = 160 - 22
parts.append(g([(K, sx - 4, 9, 51, 11), (G[2], sx - 3, 10, 49, 9), (G[5], sx - 3, 10, 49, 1),
                (K, sx + 4, 6, 1, 3), (K, sx + 38, 6, 1, 3)]))
parts.append(g(text('AGENT WORKS', sx, 12, G[11]), cls='sg'))

# clock
cx, cy = 204, 40
clock = sprite([
    '...kkkkk...',
    '..kwwwwwk..',
    '.kwwwwwwwk.',
    'kwwwwwwwwwk',
    'kwwwwwwwwwk',
    'kwwwwwwwwwk',
    'kwwwwwwwwwk',
    'kwwwwwwwwwk',
    '.kwwwwwwwk.',
    '..kwwwwwk..',
    '...kkkkk...',
], {'k': K, 'w': G[11]}, cx - 5, cy - 5)
clock += [(G[7], cx, cy - 4, 1, 1), (G[7], cx + 4, cy, 1, 1), (G[7], cx, cy + 4, 1, 1), (G[7], cx - 4, cy, 1, 1)]
parts.append(g(clock))
parts.append(f"<g class='mh'><path fill='{K}' d='{R(cx, cy - 4, 1, 4)}'/></g>")
parts.append(f"<g class='hh'><path fill='{G[5]}' d='{R(cx, cy, 3, 1)}'/></g>")
parts.append(g([(K, cx, cy, 1, 1)]))

# pipes + steam vent
parts.append(g([(G[5], 0, 60, 24, 4), (G[7], 0, 60, 24, 1), (G[3], 0, 63, 24, 1),
                (G[5], 292, 66, 28, 4), (G[7], 292, 66, 28, 1), (G[3], 292, 69, 28, 1),
                (G[5], 292, 66, 4, 66), (G[7], 292, 66, 1, 66), (G[6], 290, 90, 8, 3), (G[6], 290, 112, 8, 3),
                (G[6], 306, 62, 6, 4), (K, 307, 61, 4, 1)]))
for i in range(3):
    parts.append(f"<g class='stm t{i}'><path fill='{G[11]}' d='M308 57h3v1h1v2h-5v-2h1z'/></g>")

# hanging lamps above workers + light cones
for lx in (118, 244):
    parts.append(f"<path class='lc' fill='{G[13]}' d='M{lx - 4} 28L{lx + 5} 28L{lx + 26} 112L{lx - 25} 112Z' opacity='.05'/>")
    parts.append(g([(K, lx, 6, 1, 16), (K, lx - 4, 22, 9, 5), (G[6], lx - 3, 22, 7, 1), (G[4], lx - 3, 23, 7, 3),
                    (G[13], lx - 1, 27, 3, 1)]))

# chute (drawn after boxes, see below) ; stamper housing
stamper_housing = g([(G[2], 158, 20, 4, 6),
                     (K, 145, 26, 30, 50), (G[6], 146, 27, 28, 48), (G[8], 146, 27, 28, 2), (G[4], 146, 73, 28, 2),
                     (K, 150, 33, 20, 12), (G[3], 151, 34, 18, 10),
                     (G[3], 149, 52, 22, 1), (G[3], 149, 56, 22, 1), (G[3], 149, 60, 22, 1),
                     (K, 148, 76, 24, 3), (G[4], 157, 76, 6, 6)])
stamper_lights = (g([(G[13], 153, 37, 2, 2)], cls='pl a') + g([(G[11], 158, 37, 2, 2)], cls='pl b') +
                  g([(G[12], 163, 37, 2, 2)], cls='pl c') + g([(G[9], 153, 41, 13, 1)], cls='pw'))
stamper_head = g([(G[9], 158, 78, 4, 6), (G[11], 158, 78, 1, 6), (K, 148, 84, 24, 6), (G[9], 149, 85, 22, 4),
                  (G[11], 149, 85, 22, 1), (G[6], 150, 89, 20, 1)], cls='pr')

# ---------- belt ----------
belt_back = g([(G[1], 14, 110, 282, 2)])
defs.append(f"<clipPath id='bc'><path d='{R(16, 112, 276, 4)}'/></clipPath>")
stripes = [(G[4], x, 113, 3, 2) for x in range(-48, 300, 8)]
belt_top = (g([(G[7], 16, 112, 276, 4), (G[9], 16, 112, 276, 1)]) +
            f"<g clip-path='url(%23bc)'>{g(stripes, cls='bt')}</g>")
belt_side = [(K, 14, 116, 282, 6), (G[3], 15, 117, 280, 4), (G[5], 15, 117, 280, 1)]
for x in range(24, 292, 16):
    belt_side += [(G[6], x, 118, 2, 2)]
legs = []
for x in (28, 92, 156, 220, 280):
    legs += [(K, x, 122, 5, 18), (G[4], x + 1, 122, 3, 17), (G[6], x + 1, 122, 1, 17), (K, x - 1, 139, 7, 2)]
belt_front = g(belt_side) + g(legs)
gears = ''
for gx in (20, 288):
    gears += g([(K, gx - 4, 115, 9, 9), (G[8], gx - 3, 116, 7, 7), (G[5], gx - 1, 118, 3, 3)])
    gears += g([(K, gx, 116, 1, 2), (K, gx, 121, 1, 2), (K, gx - 3, 119, 2, 1), (K, gx + 2, 119, 2, 1)],
               cls='gr', extra=f" style='transform-origin:{gx + .5}px {119.5}px'")

# ---------- boxes (5 on a 20s loop, stations 64px apart) ----------
boxes = ''
for i in range(5):
    b = g(box_sprite(0, 0))
    d = f" style='animation-delay:-{i * 4}s'"
    b += g([(G[3], 3, 6, 6, 4), (G[11], 4, 7, 4, 2), (G[3], 5, 7, 1, 1), (G[3], 7, 8, 1, 1)], cls='lab', extra=d)
    b += g([(G[12], 7, 0, 2, 14), (G[13], 7, 0, 1, 14)], cls='tap', extra=d)
    boxes += f"<g class='bx' style='animation-delay:-{i * 4}s'><g transform='translate(0 98)'>{b}</g></g>"

# ---------- chute ----------
chute = g([(K, 20, 0, 24, 82), (G[5], 21, 0, 22, 81), (G[7], 21, 0, 3, 81), (G[3], 40, 0, 3, 81),
           (K, 17, 78, 30, 8), (G[6], 18, 79, 28, 6), (G[8], 18, 79, 28, 1), (G[3], 20, 85, 24, 1),
           (G[3], 21, 30, 22, 2), (G[3], 21, 54, 22, 2), (G[8], 22, 31, 1, 1), (G[8], 22, 55, 1, 1)])
lever = (g([(K, 46, 70, 4, 8), (G[6], 47, 71, 2, 6)]) +
         f"<g class='lv' style='transform-origin:48px 74px'>{g([(K, 48, 62, 1, 12), (G[12], 47, 60, 3, 3)])}</g>")

# ---------- workers ----------
def worker(x, y, arm_cls, eye_cls, bob_delay):
    return (f"<g transform='translate({x} {y})'><g class='bob' style='animation-delay:{bob_delay}s'>"
            f"{robot_body(arm_cls)}{robot_head(eye_cls)}</g></g>")


w_lever = worker(50, 87, 'arL', 'ey e1', -0.3)
w_scan = worker(110, 87, 'arS', 'ey e2 lk', -1.1)
w_tape = worker(236, 87, 'arT', 'ey e3', -0.7)
# inspector pops a little check-mark bubble
bub = sprite(['kkkkkkkkk', 'kwwwwwwwk', 'kwwwwwkwk', 'kwkwwkwwk', 'kwwkkwwwk', 'kwwwwwwwk', 'kkkkkkkkk', '...kk....', '...k.....'],
             {'k': K, 'w': G[12]}, 122, 72)
beam = g(bub, cls='bm')

# ---------- bin ----------
bin_back = g([(K, 286, 116, 32, 4), (G[2], 287, 117, 30, 3)])
bin_front = g([(K, 284, 120, 36, 22), (G[6], 285, 121, 34, 20), (G[8], 285, 121, 34, 1), (G[4], 285, 139, 34, 2),
               (G[4], 289, 126, 26, 1), (G[4], 289, 130, 26, 1), (G[4], 289, 134, 26, 1),
               (K, 286, 141, 4, 3), (K, 314, 141, 4, 3)])

# ---------- floor ----------
floor = [(G[1], 0, 132, 320, 4), (G[4], 0, 132, 320, 1), (G[2], 0, 136, 320, 44)]
for y in (141, 149, 160, 175):
    floor.append((G[3], 0, y, 320, 1))
floor_lines = ''.join(f"<path stroke='{G[3]}' stroke-width='1' d='M{160 + (x - 160) * .55} 136L{x} 180'/>"
                      for x in range(-120, 460, 40))
# hazard stripes along floor walkway
haz = []
for x in range(0, 320, 8):
    haz += [(G[6], x, 145, 4, 2)]

# props: plant + stacked boxes
plant = sprite([
    '...l..l....',
    '.l.ll.l.l..',
    '.ll.lll.ll.',
    '..llllll...',
    'l..llll..l.',
    '.ll.ll.ll..',
    '..lllll....',
    '....l......',
    '..kkkkkk...',
    '..kppppk...',
    '..kppppk...',
    '...kppk....',
    '...kkkk....',
], {'l': G[8], 'k': K, 'p': G[5]}, 6, 152)
stack = []
for bx, by in ((294, 160), (300, 146), (276, 164)):
    stack += box_sprite(bx, by)

# ---------- walker carrying a box ----------
walker_body = robot_body(None) + robot_head('ey e4')
legsA = g([(K, 5, 24, 3, 4), (K, 10, 24, 3, 3), (G[6], 4, 27, 4, 1), (G[6], 10, 26, 4, 1)], cls='la1')
legsB = g([(K, 5, 24, 3, 3), (K, 10, 24, 3, 4), (G[6], 4, 26, 4, 1), (G[6], 10, 27, 4, 1)], cls='la2')
carry = g(box_sprite(1, 12) + [(K, 0, 17, 2, 4), (K, 15, 17, 2, 4), (G[11], 0, 20, 2, 2), (G[11], 15, 20, 2, 2)])
walker = (f"<g class='wk'><g transform='translate(0 148)'>"
          f"<g class='wb'>{walker_body}{carry}</g>{legsA}{legsB}</g></g>")
# second little walker going the other way, no box (sweeping)
broom = g([(K, -2, 10, 1, 14), (G[8], -4, 24, 5, 3), (G[6], -4, 26, 5, 1)])
walker2 = (f"<g class='wk2'><g transform='translate(0 150) scale(.82)'>"
           f"<g class='wb'>{robot_body(None)}{robot_head('ey e2')}{broom}</g>{legsA}{legsB}</g></g>")

# ---------- CRT roll band ----------
defs.append("<linearGradient id='rb' x1='0' y1='0' x2='0' y2='1'>"
            f"<stop offset='0' stop-color='{G[13]}' stop-opacity='0'/>"
            f"<stop offset='.5' stop-color='{G[13]}' stop-opacity='.05'/>"
            f"<stop offset='1' stop-color='{G[13]}' stop-opacity='0'/></linearGradient>")
roll = "<g class='rl'><path fill='url(%23rb)' d='M0 -40h320v40H0z'/></g>"

# ---------- order ----------
scene = ''.join(parts)
scene += stamper_housing + stamper_lights
scene += w_scan + w_tape + w_lever + belt_back
scene += stamper_head
scene += bin_back + boxes + beam + belt_top + gears + chute + lever
scene += g(floor) + floor_lines + g(haz) + belt_front + bin_front
scene += g(stack) + g(plant) + walker2 + walker + roll

# ---------- animation css (inside svg) ----------
# Cycle = 4s: 0-37.5% belt paused (workers act), 37.5-100% belt moves 64px.
css = """
*{animation-timing-function:ease-in-out}
.bx{animation:bx 20s infinite}
@keyframes bx{
0%{transform:translate(24px,-36px);opacity:1;animation-timing-function:ease-in}
3%{transform:translate(24px,0)}3.8%{transform:translate(24px,-3px)}4.6%{transform:translate(24px,0)}
7.5%{transform:translate(24px,0)}20%{transform:translate(88px,0)}
27.5%{transform:translate(88px,0)}40%{transform:translate(152px,0)}
47.5%{transform:translate(152px,0)}60%{transform:translate(216px,0)}
67.5%{transform:translate(216px,0)}80%{transform:translate(280px,0)}
82%{transform:translate(281px,0);animation-timing-function:ease-in}
86%{transform:translate(292px,30px);opacity:1}86.5%,100%{transform:translate(292px,30px);opacity:0}}
.lab,.tap{opacity:0;animation:lab 20s step-end infinite}
.tap{animation-name:tap}
@keyframes lab{0%,41.6%{opacity:0}41.7%,99.9%{opacity:1}}
@keyframes tap{0%,62%{opacity:0}62.1%,99.9%{opacity:1}}
.bt{animation:bt 4s infinite}
@keyframes bt{0%,37.5%{transform:translateX(0)}100%{transform:translateX(64px)}}
.gr{animation:gr 4s infinite}
@keyframes gr{0%,37.5%{transform:rotate(0)}100%{transform:rotate(360deg)}}
.pr{animation:pr 4s infinite}
@keyframes pr{0%,6%{transform:translateY(0);animation-timing-function:ease-in}
11%,16%{transform:translateY(8px);animation-timing-function:ease-out}30%,100%{transform:translateY(0)}}
.pl{animation:pl 1.6s steps(1) infinite}.pl.b{animation-delay:-.5s}.pl.c{animation-delay:-1.1s}
@keyframes pl{50%{opacity:.25}}
.pw{animation:pw 4s steps(1) infinite}@keyframes pw{0%,30%{opacity:1}31%{opacity:.2}}
.lv{animation:lv 4s infinite}
@keyframes lv{0%{transform:rotate(-35deg)}4%{transform:rotate(30deg)}30%,100%{transform:rotate(-35deg)}}
.arL{animation:arL 4s infinite}@keyframes arL{0%{transform:translateY(-3px)}6%,100%{transform:translateY(0)}}
.arT{animation:arT 4s infinite}
@keyframes arT{0%,5%{transform:translate(0,0)}9%{transform:translate(-2px,-3px)}13%{transform:translate(0,0)}
17%{transform:translate(-2px,-3px)}22%,100%{transform:translate(0,0)}}
.arS{animation:arS 4s infinite}@keyframes arS{0%,4%,32%,100%{transform:none}8%,28%{transform:translateY(-2px)}}
.bm{animation:bm 4s steps(1) infinite}
@keyframes bm{0%,10%{opacity:0}11%,30%{opacity:1}31%,100%{opacity:0}}
.lk{animation:lk 4s infinite}@keyframes lk{0%,4%,30%,100%{transform:none}8%,26%{transform:translate(-2px,1px)}}
.ey{transform-box:fill-box;transform-origin:center;animation:bl 4.3s infinite step-end}
.e1{animation-duration:5.1s}.e3{animation-duration:6.3s;animation-delay:-2s}.e4{animation-duration:3.7s}
.lk{animation:lk 4s infinite,bl 5.7s infinite step-end}
@keyframes bl{0%,93%{transform:scaleY(1)}94%{transform:scaleY(.2)}97%{transform:scaleY(1)}}
.an{animation:an 2.4s steps(1) infinite}@keyframes an{60%{opacity:.3}}
.la{animation:pl 1.2s steps(1) infinite}.lb{animation:pl 1.2s steps(1) infinite -.6s}
.bob{animation:bob 2s steps(1) infinite}@keyframes bob{50%{transform:translateY(1px)}}
.wk{animation:wk 46s linear infinite}@keyframes wk{from{transform:translateX(-30px)}to{transform:translateX(340px)}}
.wk2{animation:wk2 64s linear infinite -20s}
@keyframes wk2{from{transform:translateX(350px) scaleX(-1)}to{transform:translateX(-40px) scaleX(-1)}}
.wb{animation:bob .5s steps(1) infinite}
.la1{animation:la1 .5s steps(1) infinite}.la2{animation:la1 .5s steps(1) infinite -.25s}
@keyframes la1{50%{opacity:0}}
.cld{animation:cld 70s linear infinite}@keyframes cld{to{transform:translateX(60px)}}
.smk{animation:smk 5s linear infinite}.s1{animation-delay:-2.5s}
@keyframes smk{0%{transform:translate(0,0) scale(1);opacity:.8}100%{transform:translate(6px,-14px) scale(2.4);opacity:0}}
.smk,.stm{transform-box:fill-box;transform-origin:center}
.stm{animation:stm 3.6s ease-out infinite}.t1{animation-delay:-1.2s}.t2{animation-delay:-2.4s}
@keyframes stm{0%{transform:translate(0,0) scale(.6);opacity:.7}100%{transform:translate(-4px,-20px) scale(2.6);opacity:0}}
.lc{animation:lc 7s steps(1) infinite}@keyframes lc{0%,100%{opacity:.05}41%{opacity:.035}43%{opacity:.055}}
.mh{transform-origin:204.5px 40.5px;animation:rot 60s steps(60) infinite}
.hh{transform-origin:204.5px 40.5px;animation:rot 720s linear infinite}
@keyframes rot{to{transform:rotate(360deg)}}
.rl{animation:rl 11s linear infinite}@keyframes rl{to{transform:translateY(220px)}}
.sg{animation:sg 9s steps(1) infinite}@keyframes sg{0%,100%{opacity:1}61%{opacity:.55}62%{opacity:1}64%{opacity:.6}65%{opacity:1}}
@media (prefers-reduced-motion:reduce){*{animation-play-state:paused!important}}
"""
css = ' '.join(l.strip() for l in css.strip().splitlines())

svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 320 180' preserveAspectRatio='xMidYMax slice' "
       f"shape-rendering='crispEdges'><style>{css}</style><defs>{''.join(defs)}</defs>"
       f"<path fill='{G[3]}' d='M0 0h320v180H0z'/>{scene}</svg>")


def enc(s):
    return s.replace('%', '%25').replace('#', '%23').replace('<', '%3C').replace('>', '%3E').replace('"', "'")


# re-encode: the scene already uses %23 for url refs; undo double-encoding for those
svg_raw = svg.replace('%23', '#')
data_uri = 'data:image/svg+xml,' + enc(svg_raw)

open(sys.argv[1] + '/factory.svg', 'w').write(svg_raw)

# ---------- small composer mascot (sits on top of composer, follows text end) ----------
def mascot(typing):
    head = robot_head('ey')
    body = robot_body('ty' if typing else 'id')
    st = ("*{animation-timing-function:ease-in-out}"
          ".ey{transform-box:fill-box;transform-origin:center;animation:bl 3.9s infinite step-end}"
          "@keyframes bl{0%,93%{transform:scaleY(1)}94%{transform:scaleY(.2)}97%{transform:scaleY(1)}}"
          ".an{animation:an 2s steps(1) infinite}@keyframes an{50%{opacity:.3}}"
          ".la{animation:p 1s steps(1) infinite}.lb{animation:p 1s steps(1) infinite -.5s}@keyframes p{50%{opacity:.25}}"
          ".bo{animation:bo 2.2s steps(1) infinite}@keyframes bo{50%{transform:translateY(1px)}}"
          ".ty{animation:ty .28s steps(1) infinite}@keyframes ty{50%{transform:translateY(-2px)}}"
          "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 -3 17 27' shape-rendering='crispEdges'>"
            f"<style>{st}</style><g class='bo'>{body}{head}</g></svg>").replace('%23', '#')


m_idle = 'data:image/svg+xml,' + enc(mascot(False))
m_type = 'data:image/svg+xml,' + enc(mascot(True))

# ---------- theme css ----------
SCAN = "repeating-linear-gradient(0deg,rgba(0,0,0,.22) 0 1px,transparent 1px 3px)"
VIG = "radial-gradient(ellipse 90% 85% at 50% 50%,transparent 55%,rgba(0,0,0,.55) 100%)"
DIM = "linear-gradient(rgba(10,11,12,.18),rgba(10,11,12,.18))"
theme_css = f"""
[data-workspace-area="conversation"]{{background:{SCAN},{VIG},{DIM},url("{data_uri}") center bottom/cover no-repeat #25272a!important}}
[data-workspace-area="conversation"] .messages-timeline-scroll,[data-workspace-area="conversation"]>div,[data-chat-header]{{background:transparent!important}}
[data-workspace-area="conversation"] *,[data-workspace-area="conversation"] *::before,[data-workspace-area="conversation"] *::after{{backdrop-filter:none!important}}
[data-chat-header]{{border-bottom:2px solid #0c0d0e!important;background:linear-gradient(#1c1e20,#1c1e20cc)!important}}
[data-user-message-bubble]{{background:#2f3235!important;color:#f0f0ec!important;border:0!important;border-radius:0!important;padding:10px 14px!important;box-shadow:0 -2px #a3a5a7,0 2px #a3a5a7,-2px 0 #a3a5a7,2px 0 #a3a5a7,4px 4px 0 2px rgba(0,0,0,.45)!important;margin:2px 4px 6px!important}}
[data-message-role="assistant"] .chat-markdown{{background:rgba(20,21,23,.94)!important;border:0!important;border-radius:0!important;padding:10px 14px!important;box-shadow:0 -2px #5c5f63,0 2px #5c5f63,-2px 0 #5c5f63,2px 0 #5c5f63,4px 4px 0 2px rgba(0,0,0,.45)!important;margin:2px 4px 6px!important}}
[data-timeline-row-kind="work"]>*{{background-color:rgba(20,21,23,.9)!important;border-radius:0!important}}
.chat-markdown-codeblock{{background:#0c0d0e!important;border:1px solid #3b3e42!important;border-radius:0!important}}
.chat-markdown a{{color:#dcdddb!important;text-decoration:underline dotted!important}}
[data-slot="sidebar-inner"]{{background:{SCAN},linear-gradient(#1c1e20,#141517)!important;border-right:2px solid #0c0d0e!important}}
[data-thread-item]{{border-radius:0!important}}
[data-thread-item]:hover{{background:rgba(220,221,219,.07)!important}}
[data-thread-item][data-active=true],[data-thread-item][aria-current]{{box-shadow:inset 3px 0 #c1c3c3!important}}
[data-slot="project-monogram"]{{image-rendering:pixelated;border-radius:0!important}}
[data-slot="composer-host"]{{position:relative;overflow:visible!important;margin-top:30px!important;background:#141517!important;border-radius:0!important;border:0!important;box-shadow:0 -2px #888b8e,0 2px #888b8e,-2px 0 #888b8e,2px 0 #888b8e,5px 5px 0 2px rgba(0,0,0,.5)!important}}
[data-slot="composer-host"]:focus-within{{box-shadow:0 -2px #dcdddb,0 2px #dcdddb,-2px 0 #dcdddb,2px 0 #dcdddb,5px 5px 0 2px rgba(0,0,0,.5)!important}}
[data-slot="composer-shell"]::before{{display:none!important}}
[data-slot="composer-host"] .composer-tiptap{{overflow:visible!important;max-height:none!important}}
[data-slot="composer-host"] .composer-tiptap p:last-child::after{{content:"";position:absolute;top:-33px;width:22px;height:35px;margin-left:2px;pointer-events:none;z-index:5;image-rendering:pixelated;background:url("{m_idle}") 0 0/22px 35px no-repeat}}
[data-slot="composer-host"]:focus-within .composer-tiptap p:last-child::after{{background-image:url("{m_type}")}}
[data-slot="button"],[data-slot="input"],[data-slot="select-trigger"],[data-slot="dialog-popup"],[data-slot="popover-popup"],[data-slot="menu-popup"],[data-slot="tooltip-popup"],[data-thread-details-card]{{border-radius:0!important}}
[data-slot="dialog-popup"],[data-slot="popover-popup"],[data-slot="menu-popup"]{{box-shadow:0 0 0 2px #5c5f63,6px 6px 0 rgba(0,0,0,.5)!important}}
[data-slot="tooltip-popup"]{{background:#0c0d0e!important;color:#f0f0ec!important;box-shadow:0 0 0 1px #888b8e!important}}
[data-slot="switch"]{{border-radius:0!important}}[data-slot="switch"] *{{border-radius:0!important}}
svg.lucide{{stroke-linecap:square;stroke-linejoin:miter}}
::selection{{background:#a3a5a7;color:#0c0d0e}}
::-webkit-scrollbar{{width:10px;height:10px}}::-webkit-scrollbar-track{{background:transparent}}
::-webkit-scrollbar-thumb{{background:#4a4d51;border:2px solid #141517;border-radius:0}}
::-webkit-scrollbar-thumb:hover{{background:#717478}}
[data-slot="scroll-area-thumb"]{{background:#5c5f63!important;border-radius:0!important}}
"""
theme_css = ''.join(l.strip() for l in theme_css.strip().splitlines())

colors = {
    "canvas": "#1c1e20", "chrome": "#141517", "toolbar": "#1c1e20", "toolbarForeground": "#dcdddb",
    "toolbarBorder": "#0c0d0e", "toolbarControl": "#2f3235", "toolbarControlForeground": "#dcdddb",
    "toolbarControlHover": "#3b3e42", "surface": "#1c1e20", "surfaceRaised": "#25272a", "surfaceOverlay": "#2f3235",
    "text": "#e6e7e4", "textMuted": "#9a9c9e", "border": "#3b3e42", "input": "#4a4d51", "focus": "#c1c3c3",
    "accent": "#c1c3c3", "accentForeground": "#0c0d0e", "secondary": "#2f3235", "secondaryForeground": "#e6e7e4",
    "muted": "#25272a", "mutedForeground": "#8d9093", "placeholder": "#717478", "secondaryLabel": "#888b8e",
    "iconMuted": "#888b8e", "error": "#c98a86", "errorForeground": "#e2b3ae", "errorSurface": "#2b2221",
    "warning": "#cdbf94", "warningForeground": "#e2d8b8", "warningSurface": "#2a2820",
    "update": "#b4bcc4", "updateForeground": "#e6e7e4", "updateSurface": "#2a2d31",
    "accentSurface": "#2f3235", "accentSurfaceForeground": "#f0f0ec", "messageSurface": "#2f3235",
    "messageForeground": "#f0f0ec", "messageAction": "#c1c3c3", "messageActionForeground": "#0c0d0e",
    "messageActionHover": "#dcdddb", "codeBackground": "#0c0d0e", "codeForeground": "#dcdddb",
    "searchMatchBackground": "#4a4d51", "searchMatchForeground": "#f0f0ec", "searchMatchActiveBackground": "#c1c3c3",
    "searchMatchActiveForeground": "#0c0d0e", "sidebar": "#17181a", "sidebarForeground": "#dcdddb",
    "sidebarMutedForeground": "#888b8e", "sidebarControlSurface": "#25272a", "sidebarRowHover": "#25272a",
    "sidebarRowActive": "#2f3235", "sidebarRowSelected": "#3b3e42", "sidebarBorder": "#0c0d0e",
    "terminalBackground": "#111214", "terminalForeground": "#d4d5d2", "terminalCursor": "#f0f0ec",
    "terminalSelection": "#3b3e42", "terminalScrollbar": "#2f3235", "terminalScrollbarHover": "#4a4d51",
}
theme = {"version": 1, "name": "Agent Works", "appearance": "dark", "canvas": "#1c1e20", "accent": "#c1c3c3",
         "colors": colors, "css": theme_css}
json.dump(theme, open(sys.argv[1] + '/agent-works.json', 'w'))
print('css chars:', len(theme_css), 'svg uri:', len(data_uri))
