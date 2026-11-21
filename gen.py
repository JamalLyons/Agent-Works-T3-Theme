#!/usr/bin/env python3
"""Generates the 'Agent Works' pixel factory theme for T3 Code.

Usage: python3 gen.py OUT_DIR [--no-id]

Importing this module builds everything in memory and writes nothing; tests import it.
`main()` writes OUT_DIR/{agent-works.json, factory.svg, lights.svg, anchors.json}.
--no-id leaves "id" out of the theme JSON (themes-folder installs take the id from the file name).
"""
import base64, json, os, re, sys
import fx

# ---------- palette: old B&W CRT grays ----------
G = ['#0c0d0e', '#141517', '#1c1e20', '#25272a', '#2f3235', '#3b3e42',
     '#4a4d51', '#5c5f63', '#717478', '#888b8e', '#a3a5a7', '#c1c3c3',
     '#dcdddb', '#f0f0ec']
K = G[0]
A1, A2, AD = '#ffb547', '#ff9a2e', '#5a4122'   # amber accents (lit, deep, unlit)


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
    'J': ['001', '001', '001', '101', '010'], 'M': ['10001', '11011', '10101', '10001', '10001'],
    'L': ['100', '100', '100', '100', '111'], 'Y': ['101', '101', '010', '010', '010'],
    'C': ['011', '100', '100', '100', '011'], '.': ['000', '000', '000', '000', '010'],
    'Z': ['111', '001', '010', '100', '111'],
}


def text(s, x, y, c):
    out = []
    for ch in s:
        for j, row in enumerate(FONT[ch]):
            for i, b in enumerate(row):
                if b == '1':
                    out.append((c, x + i, y + j, 1, 1))
        x += len(FONT[ch][0]) + 1
    return out

def text_w(s):
    return sum(len(FONT[ch][0]) + 1 for ch in s) - 1


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
    s += g([(G[10], 5, 9, 2, 1), (G[10], 9, 9, 2, 1)], cls='se')   # closed eyes, shown only in the sleep frame
    s += g([(G[13], 6, -2, 3, 2)], cls='an')
    return f"<g class='hd'>{s}</g>"


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
# 480x320 scene. Chat column covers roughly x 133..347 at a 1.4:1 window, so the
# working stations sit in the side zones and only a fast belt span crosses the middle.
W, H = 480, 320
FY = 282            # floor line
DY = 150            # line layer offset (line art is drawn in the old 180-high coords)
S = (36, 92, 220, 348, 404)   # box rest x: chute, inspector, (transit), press, tape
parts = []
defs = []

# wall
defs.append("<pattern id='br' width='16' height='8' patternUnits='userSpaceOnUse'>"
            f"<path fill='{G[3]}' d='M0 0h16v8H0z'/>"
            f"<path fill='{G[2]}' d='M0 3h16v1H0zM0 7h16v1H0zM7 0h1v3H7zM15 4h1v3h-1z'/>"
            f"<path fill='{G[4]}' d='M1 0h5v1H1zM9 4h5v1H9z'/></pattern>")
parts.append(f"<path fill='url(%23br)' d='M0 0h{W}v{FY}H0z'/>")
defs.append("<radialGradient id='wl' cx='50%' cy='45%' r='70%'>"
            f"<stop offset='0' stop-color='{G[9]}' stop-opacity='.08'/>"
            f"<stop offset='1' stop-color='{K}' stop-opacity='.35'/></radialGradient>")
parts.append(f"<path fill='url(%23wl)' d='M0 0h{W}v{FY}H0z'/>")

# windows with sky, clouds, distant chimneys
defs.append("<linearGradient id='sk' x1='0' y1='0' x2='0' y2='1'>"
            f"<stop offset='0' stop-color='{G[8]}'/><stop offset='1' stop-color='{G[10]}'/></linearGradient>")
defs.append("<pattern id='cl' width='60' height='30' patternUnits='userSpaceOnUse'>"
            f"<path fill='{G[11]}' d='M6 6h10v1h3v2H3V7h3zM34 15h8v1h3v2H30v-2h4zM48 3h6v1h2v1h-9V4h1z'/>"
            f"<path fill='{G[9]}' d='M3 9h16v1H3zM30 18h15v1H30z'/></pattern>")
WINS = ((142, 96), (296, 96))
assert len({wy for _, wy in WINS}) == 1, 'render/fx.js assumes every window has the same glass y'
GLASS_Y = (20 + WINS[0][1] - 17, 46 + WINS[0][1] - 17)   # glass top/bottom in scene space (99, 125)
for wx, wy in WINS:
    o = wy - 17
    cid = f'w{wx}'
    defs.append(f"<clipPath id='{cid}'><path d='{R(wx + 2, 20 + o, 40, 26)}'/></clipPath>")
    parts.append(g([(K, wx - 1, 17 + o, 46, 33), (G[6], wx, 18 + o, 44, 30)]))
    inner = f"<path fill='url(%23sk)' d='{R(wx + 2, 20 + o, 40, 26)}'/>"
    inner += f"<g class='cld'><path fill='url(%23cl)' opacity='.8' d='M{wx - 58} {20 + o}h160v26h-160z'/></g>"
    inner += g([(G[7], wx + 2, 38 + o, 40, 8), (G[7], wx + 8, 30 + o, 4, 8), (G[7], wx + 26, 26 + o, 4, 12),
                (G[6], wx + 2, 42 + o, 40, 4), (G[7], wx + 14, 34 + o, 8, 4)])
    for i, (sx_, sy_) in enumerate(((wx + 10, 28 + o), (wx + 28, 24 + o))):
        inner += f"<g class='smk s{i}'><path fill='{G[11]}' d='{R(sx_ - 1, sy_ - 2, 3, 2)}'/></g>"
    parts.append(f"<g clip-path='url(%23{cid})'>{inner}</g>")
    parts.append(g([(G[6], wx + 21, 20 + o, 2, 26), (G[6], wx + 2, 32 + o, 40, 2),
                    (G[8], wx, 18 + o, 44, 1), (G[4], wx, 47 + o, 44, 1), (G[9], wx - 2, 48 + o, 48, 2),
                    (K, wx - 2, 50 + o, 48, 1)]))
    parts.append(f"<path class='sh' fill='{G[12]}' d='M{wx + 2} {46 + o}L{wx + 42} {46 + o}"
                 f"L{wx + 62} {FY}L{wx + 22} {FY}Z' opacity='.03'/>")

# ceiling beam + truss
parts.append(g([(G[1], 0, 0, W, 6), (G[4], 0, 5, W, 1), (G[2], 0, 6, W, 1)] +
               [(G[6], x, 2, 1, 1) for x in range(6, W, 16)]))

# sign: AGENT WORKS (hung on long cables)
sx = 240 - 22
SY = 56
parts.append(g([(K, sx - 4, SY, 51, 11), (G[2], sx - 3, SY + 1, 49, 9), (G[5], sx - 3, SY + 1, 49, 1),
                (K, sx + 4, 6, 1, SY - 6), (K, sx + 38, 6, 1, SY - 6)]))
parts.append(g(text('AGENT WORKS', sx, SY + 3, G[6])))

# clock (between the windows)
cx, cy = 240, 112
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

# pipes: left wall run + control panel, right wall run with steam vent
pipes = [(G[5], 0, 196, 30, 4), (G[7], 0, 196, 30, 1), (G[3], 0, 199, 30, 1), (G[6], 18, 194, 3, 8),
         (G[5], 10, 7, 4, 189), (G[7], 10, 7, 1, 189), (G[6], 8, 60, 8, 3), (G[6], 8, 130, 8, 3),
         # control panel
         (K, 2, 214, 22, 30), (G[5], 3, 215, 20, 28), (G[7], 3, 215, 20, 1), (K, 6, 219, 14, 8), (G[2], 7, 220, 12, 6),
         (G[3], 6, 231, 4, 4), (G[3], 12, 231, 4, 4), (G[7], 7, 237, 12, 1),
         # right run
         (G[5], 440, 186, 40, 4), (G[7], 440, 186, 40, 1), (G[3], 440, 189, 40, 1),
         (G[5], 466, 186, 4, 96), (G[7], 466, 186, 1, 96), (G[6], 464, 214, 8, 3), (G[6], 464, 248, 8, 3),
         (G[6], 446, 182, 6, 4), (K, 447, 181, 4, 1),
         # gauge
         (K, 470, 196, 9, 9), (G[11], 471, 197, 7, 7), (K, 474, 199, 1, 3)]
parts.append(g(pipes))
parts.append(''.join(g([(A1, x, 239, 2, 2)], cls=f'ld d{i}') for i, x in enumerate((5, 9, 13, 17))))
# welding torch on the left wall pipe (arc centre WELD; sparks fall to the 196 pipe)
WELD = (14, 160)
parts.append(g([(K, 15, 158, 7, 2), (G[5], 21, 157, 3, 4), (G[6], 8, 162, 8, 2)]))
parts.append("<g class='wo'>" + g([(G[13], WELD[0] - 1, WELD[1] - 1, 2, 2), (A1, WELD[0] - 2, WELD[1] - 2, 1, 1), (A1, WELD[0] + 1, WELD[1] + 1, 1, 1)], cls='wa') +
             ''.join(g([(A1, x, 161, 1, 1), (G[13], x + 2, 163, 1, 1)], cls=f'wf f{i}') for i, x in enumerate((11, 14, 16))) + '</g>')
PANEL_LEDS = [(8, 221), (12, 221)]
parts.append(g([(A1, 8, 221, 2, 2)], cls='pl a') + g([(G[11], 12, 221, 2, 2)], cls='pl c') +
             g([(G[9], 8, 224, 9, 1)], cls='pw'))
for i in range(3):
    parts.append(f"<g transform='translate(140 120)'><g class='stm t{i}'><path fill='{G[11]}' d='M308 57h3v1h1v2h-5v-2h1z'/></g></g>")
# shelf with spare parts on the far right
parts.append(g([(K, 446, 120, 34, 3), (G[6], 447, 120, 33, 1), (K, 450, 123, 2, 6), (K, 474, 123, 2, 6)] +
               box_sprite(452, 106) + [(K, 470, 110, 8, 10), (G[7], 471, 111, 6, 8)]))

# maker's plate: the author credit, bolted to the wall above the tape station.
# Kept right of the chat column and low enough to survive the bottom-anchored cover crop; text is one
# shade off the plate so it reads as set dressing, not a watermark.
CREDIT = 'JAMALLYONS.COM'
CREDIT_XY = (382, 200)   # text origin; plate is 3 px larger on every side
cw = text_w(CREDIT)
px_, py_ = CREDIT_XY[0] - 3, CREDIT_XY[1] - 3
parts.append(g([(K, px_, py_, cw + 6, 11), (G[2], px_ + 1, py_ + 1, cw + 4, 9), (G[4], px_ + 1, py_ + 1, cw + 4, 1),
                (G[5], px_ + 1, py_ + 1, 1, 1), (G[5], px_ + cw + 4, py_ + 1, 1, 1),
                (G[5], px_ + 1, py_ + 9, 1, 1), (G[5], px_ + cw + 4, py_ + 9, 1, 1)]))
parts.append(g(text(CREDIT, *CREDIT_XY, G[5])))

# hanging lamps above the side stations + light cones
LAMPS = (100, 382)   # cord x; the unlit bulb is the 3x1 rect at (lx-1, BULB_Y)
BULB_Y = 177
for lx in LAMPS:
    parts.append(g([(K, lx, 6, 1, 166), (K, lx - 4, 172, 9, 5), (G[6], lx - 3, 172, 7, 1), (G[4], lx - 3, 173, 7, 3),
                    (AD, lx - 1, BULB_Y, 3, 1)]))

# ---------- line layer (old coords, shifted down by DY) ----------
PX = S[3] + 8 - 160          # press x offset from the old 160-centered drawing
def sh(rects, dx):
    return [(c, x + dx, y, w, h) for c, x, y, w, h in rects]

stamper_housing = g(sh([(K, 157, -150, 6, 176), (G[4], 158, -150, 4, 176),
                        (K, 145, 26, 30, 50), (G[6], 146, 27, 28, 48), (G[8], 146, 27, 28, 2), (G[4], 146, 73, 28, 2),
                        (K, 150, 33, 20, 12), (G[3], 151, 34, 18, 10),
                        (G[3], 149, 52, 22, 1), (G[3], 149, 56, 22, 1), (G[3], 149, 60, 22, 1),
                        (K, 148, 76, 24, 3), (G[4], 156, 76, 8, 3)], PX), cls='pk')
PRESS_LEDS = [(x, y + DY) for _, x, y, _, _ in sh([(0, 153, 37, 2, 2), (0, 158, 37, 2, 2), (0, 163, 37, 2, 2)], PX)]
stamper_lights = (g(sh([(A1, 153, 37, 2, 2)], PX), cls='pl a') + g(sh([(G[11], 158, 37, 2, 2)], PX), cls='pl b') +
                  g(sh([(A2, 163, 37, 2, 2)], PX), cls='pl c') + g(sh([(G[9], 153, 41, 13, 1)], PX), cls='pw'))
# head: ram 157..163, plate 145..175 x 82..91, die 150..170 x 91..93. Rest -4px, hit +6px (die bottom on box top 98, +1 squash)
stamper_head = g(sh([(K, 157, 56, 6, 26), (G[9], 158, 56, 4, 26), (G[11], 158, 56, 1, 26),
                     (K, 145, 82, 30, 9), (G[8], 146, 83, 28, 7), (G[11], 146, 83, 28, 1), (G[5], 146, 89, 28, 1),
                     (G[4], 148, 85, 2, 2), (G[4], 170, 85, 2, 2), (K, 150, 91, 20, 2), (G[6], 151, 91, 18, 1)], PX), cls='pr')
# impact: flash line + sparks kicking sideways (right side is the mirror about x=356)
spk = g([(G[13], 346, 97, 20, 1)], cls='fl')
for side in ('', " transform='translate(712 0) scale(-1 1)'"):
    spk += (f"<g{side}>" + g([(G[13], 345, 96, 2, 1), (A1, 343, 94, 1, 1), (A1, 341, 97, 1, 1), (G[13], 344, 93, 1, 1)], cls='spa') +
            g([(A1, 346, 95, 1, 1), (A2, 342, 95, 2, 1), (G[13], 340, 96, 1, 1), (A1, 344, 91, 1, 1)], cls='spb') + '</g>')

# ---------- belt: three spans (left, fast middle, right) joined by drive gears ----------
BX0, BX1 = S[0] - 14, S[4] + 16
J1, J2 = 138, 334
belt_back = g([(G[1], BX0 - 2, 110, BX1 - BX0 + 4, 2)])
belt_top = g([(G[7], BX0, 112, BX1 - BX0, 4), (G[9], BX0, 112, BX1 - BX0, 1)])
for i, (a, b, d) in enumerate(((BX0, J1, 56), (J1, J2, 128), (J2, BX1, 56))):
    defs.append(f"<clipPath id='b{i}'><path d='{R(a, 112, b - a, 4)}'/></clipPath>")
    stripes = [(G[4], x, 113, 3, 2) for x in range(a - d - 8, b, 8)]
    belt_top += f"<g clip-path='url(%23b{i})'>{g(stripes, cls=f'bt b{d}')}</g>"
belt_top += g([(K, J1 - 1, 112, 2, 4), (K, J2 - 1, 112, 2, 4)])
belt_side = [(K, BX0 - 2, 116, BX1 - BX0 + 4, 6), (G[3], BX0 - 1, 117, BX1 - BX0 + 2, 4), (G[5], BX0 - 1, 117, BX1 - BX0 + 2, 1)]
for x in range(BX0 + 10, BX1 - 4, 16):
    belt_side += [(G[6], x, 118, 2, 2)]
legs = []
for x in (BX0 + 6, 104, 182, 260, 316, BX1 - 22):
    legs += [(K, x, 122, 5, 18), (G[4], x + 1, 122, 3, 17), (G[6], x + 1, 122, 1, 17), (K, x - 1, 139, 7, 2)]
belt_front = g(belt_side) + g(legs)
gears = ''
for gx in (BX0 + 4, J1, J2, BX1 - 4):
    gears += g([(K, gx - 4, 115, 9, 9), (G[8], gx - 3, 116, 7, 7), (G[5], gx - 1, 118, 3, 3)])
    gears += g([(K, gx, 116, 1, 2), (K, gx, 121, 1, 2), (K, gx - 3, 119, 2, 1), (K, gx + 2, 119, 2, 1)], cls='gr')

# ---------- boxes (5 on a 20s loop) ----------
boxes = ''
for i in range(5):
    b = g(box_sprite(0, 0))
    d = f" style='animation-delay:-{i * 4}s'"
    b += g([(G[3], 3, 6, 6, 4), (G[11], 4, 7, 4, 2), (G[3], 5, 7, 1, 1), (G[3], 7, 8, 1, 1)], cls='lab', extra=d)
    b += g([(G[12], 7, 0, 2, 14), (G[13], 7, 0, 1, 14)], cls='tap', extra=d)
    boxes += f"<g class='bx'{d}><g transform='translate(0 98)'><g class='sq'{d}>{b}</g></g></g>"

# ---------- chute (runs up to the ceiling) ----------
CX = S[0] - 4
chute = g(sh([(K, 20, -150, 24, 232), (G[5], 21, -150, 22, 231), (G[7], 21, -150, 3, 231), (G[3], 40, -150, 3, 231),
              (K, 17, 78, 30, 8), (G[6], 18, 79, 28, 6), (G[8], 18, 79, 28, 1), (G[3], 20, 85, 24, 1)] +
             [r for y in (-110, -60, -10, 30, 54) for r in ((G[3], 21, y, 22, 2), (G[8], 22, y + 1, 1, 1))], CX - 20))
lever = (g([(K, CX + 26, 70, 4, 8), (G[6], CX + 27, 71, 2, 6)]) +
         f"<g class='lv'>{g([(K, CX + 28, 62, 1, 12), (G[12], CX + 27, 60, 3, 3)])}</g>")

# ---------- workers ----------
def worker(x, y, arm_cls, eye_cls, bob_delay):
    return (f"<g transform='translate({x} {y})'><g class='bob' style='animation-delay:{bob_delay}s'>"
            f"{robot_body(arm_cls)}{robot_head(eye_cls)}</g></g>")


w_lever = worker(CX + 30, 87, 'arL', 'ey e1', -0.3)
w_scan = worker(S[1] + 22, 87, 'arS', 'ey e2 lk', -1.1)
w_tape = worker(S[4] - 20, 87, 'arT', 'ey e3', -0.7)
bub = sprite(['kkkkkkkkk', 'kwwwwwwwk', 'kwwwwwkwk', 'kwkwwkwwk', 'kwwkkwwwk', 'kwwwwwwwk', 'kkkkkkkkk', '...kk....', '...k.....'],
             {'k': K, 'w': G[12]}, S[1] + 34, 72)
beam = g(bub, cls='bm')

# ---------- bin ----------
BN = S[4] + 4
bin_back = g([(K, BN + 2, 116, 32, 4), (G[2], BN + 3, 117, 30, 3)])
bin_front = g([(K, BN, 120, 36, 22), (G[6], BN + 1, 121, 34, 20), (G[8], BN + 1, 121, 34, 1), (G[4], BN + 1, 139, 34, 2),
               (G[4], BN + 5, 126, 26, 1), (G[4], BN + 5, 130, 26, 1), (G[4], BN + 5, 134, 26, 1),
               (K, BN + 2, 141, 4, 3), (K, BN + 30, 141, 4, 3)])

# ---------- floor ----------
floor = [(G[1], 0, FY, W, 4), (G[4], 0, FY, W, 1), (G[2], 0, FY + 4, W, H - FY - 4)]
for y in (FY + 9, FY + 17, FY + 28):
    floor.append((G[3], 0, y, W, 1))
floor_lines = ''.join(f"<path stroke='{G[3]}' stroke-width='1' d='M{240 + (x - 240) * .55:g} {FY + 4}L{x} {H}'/>"
                      for x in range(-160, 680, 40))
haz = [(G[6], x, FY + 13, 4, 2) for x in range(0, W, 8)]

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
], {'l': G[8], 'k': K, 'p': G[5]}, 4, FY + 20)
stack = []
for bx, by in ((448, FY + 22), (454, FY + 8), (462, FY + 22)):
    stack += box_sprite(bx, by)

# ---------- walkers ----------
walker_body = robot_body(None) + robot_head('ey e4')
legsA = g([(K, 5, 24, 3, 4), (K, 10, 24, 3, 3), (G[6], 4, 27, 4, 1), (G[6], 10, 26, 4, 1)], cls='la1')
legsB = g([(K, 5, 24, 3, 3), (K, 10, 24, 3, 4), (G[6], 4, 26, 4, 1), (G[6], 10, 27, 4, 1)], cls='la2')
carry = g(box_sprite(1, 12) + [(K, 0, 17, 2, 4), (K, 15, 17, 2, 4), (G[11], 0, 20, 2, 2), (G[11], 15, 20, 2, 2)])
walker = (f"<g class='wk'><g transform='translate(0 {FY + 6})'>"
          f"<g class='wb'>{walker_body}{carry}</g>{legsA}{legsB}</g></g>")
broom = g([(K, -2, 10, 1, 14), (G[8], -4, 24, 5, 3), (G[6], -4, 26, 5, 1)])
walker2 = (f"<g class='wk2'><g transform='translate(0 {FY + 8}) scale(.82)'>"
           f"<g class='wb'>{robot_body(None)}{robot_head('ey e2')}{broom}</g>{legsA}{legsB}</g></g>")

# ---------- foreground (near-black, nearer than the line, moves faster) ----------
FG = '#070708'
FG2 = '#18191b'
FR = '#3b3e42'   # cool rim light from the windows
defs.append(f"<pattern id='cn' width='8' height='8' patternUnits='userSpaceOnUse'><path fill='{FG}' d='M0 0h4v6H0zM1 6h2v2H1z'/>"
            f"<path fill='{FG2}' d='M1 1h2v4H1z'/></pattern>")
# drawn at half size, shown at 2x: block y 236..256, hook tip ~(482,284), bowl bottom ~y 310
hook = [(FG, -7, 118, 14, 5), (FG2, -6, 118, 12, 1), (FG, -9, 120, 18, 2),   # block
        (FG, -2, 123, 4, 3), (FG, -5, 126, 10, 2),                         # shank + collar
        (FG, -1, 128, 3, 8), (FG, -3, 136, 5, 3), (FG, -2, 139, 7, 2),
        (FG, 4, 133, 3, 7), (FG, 5, 130, 2, 3),                            # curl, tip at local (6,130)
        (FG2, 0, 129, 1, 6), (FR, -7, 118, 1, 4), (FR, -9, 120, 1, 2), (FR, -5, 126, 1, 2), (FR, -1, 128, 1, 8),
        (FR, -3, 136, 1, 3), (FR, 4, 133, 1, 5), (FR, 5, 130, 1, 3)]
fg_hook = (f"<g class='hk'><g transform='translate(464 0) scale(2)'><g class='hs'><path fill='url(%23cn)' transform='translate(-2 0)' d='M0 -20h4v138H0z'/>{g(hook)}</g></g></g>")
fg_chain = (f"<g transform='translate(74 0)'><g class='ch'><path fill='url(%23cn)' d='M0 0h4v64H0z'/>"
            f"{g([(FG, -2, 64, 8, 3), (FG, -1, 67, 6, 2)])}</g></g>")
fg_pipe = g([(FG, 0, 300, 96, 14), (FG2, 0, 301, 96, 1), (FG, 92, 296, 8, 22), (FG2, 93, 297, 1, 20),
             (FG, 40, 296, 6, 22), (FG2, 41, 297, 1, 20), (FG, 0, 314, 120, 6)])
fg = f"<g class='fg'>{fg_chain}{fg_pipe}{fg_hook}</g>"

# ---------- CRT roll band ----------
defs.append("<linearGradient id='rb' x1='0' y1='0' x2='0' y2='1'>"
            f"<stop offset='0' stop-color='{G[13]}' stop-opacity='0'/>"
            f"<stop offset='.5' stop-color='{G[13]}' stop-opacity='.05'/>"
            f"<stop offset='1' stop-color='{G[13]}' stop-opacity='0'/></linearGradient>")
roll = f"<g class='rl'><path fill='url(%23rb)' d='M0 -40h{W}v40H0z'/></g>"

# ---------- order ----------
LT = f"<g transform='translate(0 {DY})'>"
scene = ''.join(parts)
scene += LT + stamper_head + stamper_housing + stamper_lights
scene += w_scan + w_tape + w_lever + belt_back
scene += bin_back + boxes + spk + beam + belt_top + gears + chute + lever + '</g>'
scene += g(floor) + floor_lines + g(haz) + LT + belt_front + bin_front + '</g>'
scene += g(stack) + g(plant) + walker2 + walker + fg + roll

# ---------- animation css (inside svg) ----------
# Cycle = 4s: 0-37.5% belt paused (workers act), 37.5-100% belt moves 64px.
css = """
*{animation-timing-function:ease-in-out}
.bx{animation:bx 20s infinite}
@keyframes bx{
0%{transform:translate(36px,-36px);opacity:1;animation-timing-function:ease-in}
3%{transform:translateX(36px)}3.8%{transform:translate(36px,-3px)}4.6%{transform:translateX(36px)}
7.5%{transform:translateX(36px)}20%{transform:translateX(92px)}
27.5%{transform:translateX(92px)}40%{transform:translateX(220px)}
47.5%{transform:translateX(220px)}60%{transform:translateX(348px)}
67.5%{transform:translateX(348px)}80%{transform:translateX(404px)}
87.5%{transform:translateX(404px)}89.5%{transform:translateX(406px);animation-timing-function:ease-in}
93%{transform:translate(416px,30px);opacity:1}93.5%,100%{transform:translate(416px,30px);opacity:0}}
.lab,.tap{opacity:0;animation:lab 20s step-end infinite}
.tap{animation-name:tap}
@keyframes lab{0%,61.8%{opacity:0}61.9%,99.9%{opacity:1}}
@keyframes tap{0%,83.4%{opacity:0}83.5%,99.9%{opacity:1}}
.sq{transform-box:fill-box;transform-origin:50% 100%;animation:sq 20s infinite}
@keyframes sq{0%,61.85%{transform:none}61.9%,62.6%{transform:scale(1.07,.93)}63.6%,100%{transform:none}}
.bt{animation:bt 4s infinite}.b128{animation-name:bu}
@keyframes bt{0%,37.5%{transform:translateX(0)}100%{transform:translateX(56px)}}
@keyframes bu{0%,37.5%{transform:translateX(0)}100%{transform:translateX(128px)}}
.gr,.lv{transform-box:fill-box;transform-origin:center}.lv{transform-origin:50% 100%}
.gr{animation:gr 4s infinite}
@keyframes gr{0%,37.5%{transform:rotate(0)}100%{transform:rotate(360deg)}}
.pr{animation:pr 4s infinite}
@keyframes pr{0%{transform:translateY(-4px)}5%{transform:translateY(-8px);animation-timing-function:cubic-bezier(.7,0,1,1)}
9.5%,14%{transform:translateY(6px);animation-timing-function:ease-out}15.5%{transform:translateY(5px)}32%,100%{transform:translateY(-4px)}}
.pk{animation:pk 4s infinite}
@keyframes pk{0%,9.4%,14%,100%{transform:none}9.5%{transform:translateY(-1px)}11%{transform:translateY(1px)}}
.fl{opacity:0;animation:fl 4s steps(1) infinite}@keyframes fl{9.5%{opacity:1}11.5%{opacity:0}}
.spa,.spb{opacity:0;animation:sp 4s linear infinite}.spb{animation-name:sp2}
@keyframes sp{0%,9.4%{opacity:0;transform:none}9.5%{opacity:1;transform:none}
13%{opacity:1;transform:translate(-9px,-3px)}18%{opacity:0;transform:translate(-16px,4px)}100%{opacity:0}}
@keyframes sp2{0%,9.9%{opacity:0;transform:none}10%{opacity:1;transform:translateX(-1px)}
14%{opacity:1;transform:translate(-13px,-6px)}21%{opacity:0;transform:translate(-22px,3px)}100%{opacity:0}}
.pl{animation:pl 2s steps(1) infinite}.pl.b{animation-delay:-.5s}.pl.c{animation-delay:-1.25s}
@keyframes pl{50%{opacity:.25}}
.pw{animation:pw 4s steps(1) infinite}@keyframes pw{0%,30%{opacity:1}31%{opacity:.2}}
.ld{animation:pl 1s steps(1) infinite}.d1{animation-duration:2.5s}.d2{animation-duration:.5s;animation-delay:-.25s}.d3{animation-duration:4s;animation-delay:-1s}
.wo{animation:wo 5s steps(1) infinite}@keyframes wo{0%{opacity:1}44%{opacity:0}}
.wa{animation:wa .2s steps(1) infinite}@keyframes wa{50%{opacity:.35}}
.wf{animation:wf .5s linear infinite}.f1{animation-delay:-.2s}.f2{animation-delay:-.35s}
@keyframes wf{0%{transform:translate(0,0);opacity:1}100%{transform:translate(-3px,30px);opacity:0}}
.lv{animation:lv 4s infinite}
@keyframes lv{0%{transform:rotate(-35deg)}4%{transform:rotate(30deg)}30%,100%{transform:rotate(-35deg)}}
.arL{animation:arL 4s infinite}@keyframes arL{0%{transform:translateY(-3px)}6%,100%{transform:translateY(0)}}
.arT{animation:arT 4s infinite}
@keyframes arT{0%,5%{transform:translate(0,0)}9%{transform:translate(-2px,-3px)}13%{transform:translate(0,0)}
17%{transform:translate(-2px,-3px)}22%,100%{transform:translate(0,0)}}
.arS{animation:arS 4s infinite}@keyframes arS{0%,4%,32%,100%{transform:none}8%,28%{transform:translateY(-2px)}}
.bm{animation:bm 4s steps(1) infinite}
@keyframes bm{0%,10%{opacity:0}11%,30%{opacity:1}31%,100%{opacity:0}}
.ey{transform-box:fill-box;transform-origin:center;animation:bl 4s infinite step-end}
.e1{animation-duration:5s}.e3{animation-duration:20s;animation-name:bl3}.e4{animation-duration:2.5s}
.se{opacity:0}
.lk{animation:lk 4s infinite,bl 5s infinite step-end -2s}
@keyframes lk{0%,4%,30%,100%{transform:none}8%,26%{transform:translate(-2px,1px)}}
@keyframes bl{0%,93%{transform:scaleY(1)}94%{transform:scaleY(.2)}97%{transform:scaleY(1)}}
@keyframes bl3{0%,30%,33%,63%,66%,100%{transform:scaleY(1)}31%,64%{transform:scaleY(.2)}}
.an{animation:an 2.5s steps(1) infinite}@keyframes an{60%{opacity:.3}}
.la{animation:pl 1.25s steps(1) infinite}.lb{animation:pl 1.25s steps(1) infinite -.625s}
.bob{animation:bob 2s steps(1) infinite}@keyframes bob{50%{transform:translateY(1px)}}
.wk{animation:wk 20s linear infinite}@keyframes wk{from{transform:translateX(-30px)}to{transform:translateX(500px)}}
.wk2{animation:wk2 20s linear infinite -7s}
@keyframes wk2{from{transform:translateX(510px) scaleX(-1)}to{transform:translateX(-40px) scaleX(-1)}}
.wb{animation:bob .4s steps(1) infinite}
.la1{animation:la1 .4s steps(1) infinite}.la2{animation:la1 .4s steps(1) infinite -.2s}
@keyframes la1{50%{opacity:0}}
.cld{animation:cld 20s linear infinite}@keyframes cld{to{transform:translateX(60px)}}
.smk{animation:smk 5s linear infinite}.s1{animation-delay:-2.5s}
@keyframes smk{0%{transform:translate(0,0) scale(1);opacity:.8}100%{transform:translate(6px,-14px) scale(2.4);opacity:0}}
.smk,.stm{transform-box:fill-box;transform-origin:center}
.stm{animation:stm 4s ease-out infinite}.t1{animation-delay:-1.333s}.t2{animation-delay:-2.667s}
@keyframes stm{0%{transform:translate(0,0) scale(.6);opacity:.7}100%{transform:translate(-4px,-20px) scale(2.6);opacity:0}}
.mh{transform-origin:240.5px 112.5px;animation:rot 20s steps(20) infinite}
@keyframes rot{to{transform:rotate(360deg)}}
.hk{animation:hk 20s infinite}
@keyframes hk{0%,8%{transform:translateX(44px)}30%,62%{transform:translateX(-8px)}88%,100%{transform:translateX(44px)}}
.hs{transform-origin:0 -20px;animation:hs 10s infinite}
@keyframes hs{0%,100%{transform:rotate(1.6deg)}50%{transform:rotate(-1.6deg)}}
.ch{transform-origin:1px 0;animation:hs 5s infinite}
.rl{animation:rl 10s linear infinite}@keyframes rl{to{transform:translateY(360px)}}
@media (prefers-reduced-motion:reduce){*{animation-play-state:paused!important}}
"""
css = ''.join(l.strip() for l in css.strip().splitlines())
css = re.sub(r'\s*([{}:;,])\s*', r'\1', css).replace(';}', '}')

# ---------- scene anchors ----------
# The one place the reactive overlay (fx.py) and the render effects (render/fx.js) learn where
# things are drawn. Both layers must read positions from here, never retype them.
PRESS_HIT_PCT, PRESS_PERIOD = 9.5, 4      # .pr keyframe: die lands at 9.5% of the 4 s cycle
WELD_OFF_PCT, WELD_PERIOD = 44, 5         # .wo keyframe: arc on until 44% of 5 s
assert f'{PRESS_HIT_PCT:g}%,14%{{transform:translateY(6px)' in css, 'press hit keyframe moved; update PRESS_HIT_PCT'
assert f'.wo{{animation:wo {WELD_PERIOD}s' in css and f'{WELD_OFF_PCT}%{{opacity:0}}' in css, 'weld keyframe moved'
ANCHORS = {
    'loop': 20, 'floorY': FY,
    'lamps': list(LAMPS), 'bulbY': BULB_Y,
    'windows': [wx for wx, _ in WINS], 'glassY': list(GLASS_Y),
    'sign': {'x': sx, 'y': SY},
    'belt': {'x0': BX0, 'x1': BX1, 'skirtY': 119 + DY},
    'pressLeds': PRESS_LEDS, 'panelLeds': PANEL_LEDS,
    'pressHit': {'x': 160 + PX, 'y': 97 + DY, 't': round(PRESS_HIT_PCT / 100 * PRESS_PERIOD, 4), 'period': PRESS_PERIOD},
    'weld': {'x': WELD[0], 'y': WELD[1], 'on': round(WELD_OFF_PCT / 100 * WELD_PERIOD, 4), 'period': WELD_PERIOD},
}

svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 480 320' preserveAspectRatio='xMidYMax slice' "
       f"shape-rendering='crispEdges'><style>{css}</style><defs>{''.join(defs)}</defs>"
       f"<path fill='{G[3]}' d='M0 0h480v320H0z'/>{scene}</svg>")


# ---------- sleep frame ----------
# The idle state is one still frame of this same scene with the line shut down: workers slumped with eyes shut,
# belt empty, press parked, every light off but one standby LED. render/sleep.sh renders it from svg_sleep;
# fx.py stacks it over the live WebP while no agent works, with Zzz floating from the SLEEPERS.
SLEEP_T = 0          # frame time: belt paused, press up, lever at rest
WK2_X = 128          # the sweeper dozes left of the chat column, leaning on its broom
sleep_css = (
    '*{animation-play-state:paused!important}'
    '.hd{transform:translateY(2px)!important}.ey{opacity:0!important}.se{opacity:1!important}.an{opacity:.25!important}'
    '.arL,.arS,.arT,.bob,.wb,.lk{transform:none!important}.la,.lb{opacity:.2!important}.la2{opacity:0!important}.la1{opacity:1!important}'
    '.bx,.bm,.fl,.spa,.spb,.wo,.stm,.rl,.wk,.ld{opacity:0!important}.ld.d0{opacity:.5!important}'
    '.pl,.pw{opacity:.15!important}.pl.a{opacity:.7!important}'
    '.pr{transform:translateY(-8px)!important}.pk,.lv{transform:none!important}.lv{transform:rotate(-35deg)!important}'
    f'.wk2{{transform:translateX({WK2_X}px) scaleX(-1)!important}}'
)
svg_sleep = svg.replace('</style>', sleep_css + '</style>', 1)
# top-right corner of each dozing robot's head, in scene space (heads sink 2 px); Zzz rise from here.
# The inspector between them dozes too, without Zzz, so the snoring stays sparse.
SLEEPERS = [(x + 15, 87 + DY + 3 + 2) for x in (CX + 30, S[4] - 20)]
ANCHORS['sleepers'] = SLEEPERS
SLEEP_WEBP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'agent-works-sleep.webp')
with open(SLEEP_WEBP, 'rb') as f:   # made by render/sleep.sh; committed so builds need no browser
    sleep_uri = 'data:image/webp;base64,' + base64.b64encode(f.read()).decode()

def enc(s):
    # < and > are legal inside a quoted CSS url("data:..."); only % and # need escaping
    return s.replace('%', '%25').replace('#', '%23').replace('"', "'")


# re-encode: the scene already uses %23 for url refs; undo double-encoding for those
svg_raw = svg.replace('%23', '#')

# ---------- small composer mascot (sits on top of composer, follows text end) ----------
def mascot():
    """Sprite sheet: idle robot at x 0, typing robot (amber face, fast arms) at x 17."""
    head = robot_head('ey')
    lit = head.replace("fill='%s' d='M6 8h1v2h-1z" % G[13], "fill='#ffb547' d='M6 8h1v2h-1z").replace(
        "fill='%s' d='M6 -2" % G[13], "fill='#ffb547' d='M6 -2")
    st = ("*{animation-timing-function:ease-in-out}"
          ".ey{transform-box:fill-box;transform-origin:center;animation:bl 3.9s infinite step-end}"
          "@keyframes bl{0%,93%{transform:scaleY(1)}94%{transform:scaleY(.2)}97%{transform:scaleY(1)}}"
          ".an{animation:an 2s steps(1) infinite}@keyframes an{50%{opacity:.3}}"
          ".la{animation:p 1s steps(1) infinite}.lb{animation:p 1s steps(1) infinite -.5s}@keyframes p{50%{opacity:.25}}"
          ".bo{animation:bo 2.2s steps(1) infinite}@keyframes bo{50%{transform:translateY(1px)}}"
          ".ty{animation:ty .28s steps(1) infinite}@keyframes ty{50%{transform:translateY(-2px)}}"
          "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 -3 34 27' shape-rendering='crispEdges'>"
            f"<style>{st}</style><g class='bo'>{robot_body('id')}{head}</g>"
            f"<g transform='translate(17 0)'><g class='bo'>{robot_body('ty')}{lit}</g></g></svg>").replace('%23', '#')

m_sheet = 'data:image/svg+xml,' + enc(mascot())

# ---------- theme css ----------
SCAN = "repeating-linear-gradient(0deg,rgba(0,0,0,.22) 0 1px,transparent 1px 3px)"
VIG = "radial-gradient(ellipse 90% 85% at 50% 50%,transparent 55%,rgba(0,0,0,.55) 100%)"
DIM = "linear-gradient(rgba(10,11,12,.18),rgba(10,11,12,.18))"
BAND = ("linear-gradient(90deg,transparent calc(50% - 560px),rgba(12,13,14,.38) calc(50% - 360px),"
        "rgba(12,13,14,.38) calc(50% + 360px),transparent calc(50% + 560px))")
WK = ",".join(f'[data-timeline-row-kind="{k}"]>*' for k in ("work","work-live","work-toggle","thinking","working"))
theme_css = f"""
[data-workspace-area="conversation"]{{background:@@BG@@ center bottom/cover no-repeat #25272a!important;background-attachment:scroll,fixed!important}}
[data-workspace-area="conversation"] .messages-timeline-scroll,[data-workspace-area="conversation"]>div,[data-chat-header]{{background:transparent!important}}
[data-workspace-area="conversation"] *,[data-workspace-area="conversation"] *::before,[data-workspace-area="conversation"] *::after{{backdrop-filter:none!important}}
[data-chat-header]{{border-bottom:2px solid #0c0d0e!important;background:linear-gradient(#1c1e20,#1c1e20cc)!important}}
[data-user-message-bubble]{{background:#2f3235!important;color:#f0f0ec!important;border:0!important;border-radius:0!important;padding:10px 14px!important;box-shadow:0 -2px #a3a5a7,0 2px #a3a5a7,-2px 0 #a3a5a7,2px 0 #a3a5a7,4px 4px 0 2px rgba(0,0,0,.45)!important;margin:2px 4px 6px!important}}
[data-message-role="assistant"] .chat-markdown{{background:rgba(20,21,23,.94)!important;border:0!important;border-radius:0!important;padding:10px 14px!important;box-shadow:0 -2px #5c5f63,0 2px #5c5f63,-2px 0 #5c5f63,2px 0 #5c5f63,4px 4px 0 2px rgba(0,0,0,.45)!important;margin:2px 4px 6px!important}}
{WK}{{background:rgba(20,21,23,.9)!important;border:0!important;border-radius:0!important;padding:5px 12px!important;margin:0 4px 8px!important;box-shadow:0 -2px #4a4d51,0 2px #4a4d51,-2px 0 #4a4d51,2px 0 #4a4d51,4px 4px 0 2px rgba(0,0,0,.4)!important}}
.chat-markdown-codeblock{{background:#0c0d0e!important;border:1px solid #3b3e42!important;border-radius:0!important}}
.chat-markdown a{{color:#dcdddb!important;text-decoration:underline dotted!important}}
[data-slot="sidebar-inner"]{{background:{SCAN},linear-gradient(#1c1e20,#141517)!important;border-right:2px solid #0c0d0e!important}}
[data-thread-item]{{border-radius:0!important}}
[data-slot="project-monogram"]{{image-rendering:pixelated;border-radius:0!important}}
[data-slot="composer-host"]{{position:relative;overflow:visible!important;margin-top:44px!important;background:#141517!important;border-radius:0!important;border:0!important;box-shadow:0 -2px #888b8e,0 2px #888b8e,-2px 0 #888b8e,2px 0 #888b8e,5px 5px 0 2px rgba(0,0,0,.5)!important}}
[data-slot="composer-host"]:focus-within{{box-shadow:0 -2px #dcdddb,0 2px #dcdddb,-2px 0 #dcdddb,2px 0 #dcdddb,5px 5px 0 2px rgba(0,0,0,.5)!important}}
[data-slot="composer-shell"]::before{{display:none!important}}
[data-composer-banner-surface],[data-composer-banner-surface]::before,[data-chat-composer-main-surface],[data-chat-composer-main-surface]::before,[data-chat-composer-main-surface]::after,[data-slot="composer-host"]::after{{border-radius:0!important}}
[data-slot="composer-banner-attachment"]:has([data-chat-composer-top-drawer]){{width:100%!important;margin-bottom:0!important}}
[data-chat-composer-top-drawer]::after{{display:none!important}}
[data-composer-banner-surface]::before{{background:#1a1b1d!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important;border:0!important;box-shadow:none!important;mask:none!important;-webkit-mask:none!important}}
[data-chat-composer-main-surface]{{background:#141517!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important;box-shadow:none!important}}
[data-chat-composer-main-surface]::after{{border:0!important}}
[data-slot="composer-banner-attachment"]:has([data-chat-composer-top-drawer])+*,[data-slot="composer-banner-attachment"]:has([data-chat-composer-top-drawer])~* [data-chat-composer-main-surface]{{border-top:2px dashed #4a4d51!important}}
body:has([data-chat-composer-top-drawer]) .composer-tiptap>:last-child::after{{display:none!important}}
[data-slot="composer-host"] .composer-tiptap,[data-slot="composer-host"] .composer-tiptap>*{{position:static!important}}
[data-slot="composer-host"] .composer-tiptap>:last-child::after{{content:"";position:absolute;top:-50px;width:34px;height:54px;margin-left:2px;pointer-events:none;z-index:5;image-rendering:pixelated;background:url("{m_sheet}") 0 0/68px 54px no-repeat}}
[data-slot="composer-host"]:focus-within .composer-tiptap>:last-child::after{{background-position:-34px 0}}
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
# The scene comes from the rendered animated WebP beside the theme file (var(--theme-background-image)),
# which already carries its own vignette, scanlines and shading; keep only the chat band on top.
# While no agent works, the chat shows the still sleep frame instead, so the WebP isn't drawn or decoded at all.
theme_css = (theme_css.replace('@@BG@@', f'{BAND},var(--aw-sleep)')
             + f"{fx.busy('[data-workspace-area="conversation"]')}{{background-image:{BAND},var(--theme-background-image)!important}}"
             + fx.css(ANCHORS, g, text, R, enc, sleep_uri))
CREDIT_CSS = '/* Agent Works by Jamal Lyons | jamallyons.com | x.com/codingwithjamal */'
theme_css = CREDIT_CSS + theme_css

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
    "terminalBackground": "#111214", "terminalForeground": "#d4d5d2", "terminalCursor": "#ffb547",
    "terminalSelection": "#3b3e42", "terminalScrollbar": "#2f3235", "terminalScrollbarHover": "#4a4d51",
}
TID = 'agent-works'
CSS_MAX = 50000   # THEME_CSS_MAX_LENGTH in T3 Code; not configurable
theme = {"id": TID, "version": 1, "name": "Agent Works", "appearance": "dark", "canvas": "#1c1e20", "accent": "#c1c3c3",
         "colors": colors, "css": theme_css}
lights_svg = fx.overlay(ANCHORS, g, text, R)


def check():
    """Invariants the build must hold. Raises AssertionError; main() and the tests both run it."""
    assert len(theme_css) <= CSS_MAX, f'css is {len(theme_css)} chars, over the {CSS_MAX} limit'
    # every LED the overlay lights must sit exactly on an LED the scene draws
    for x, y in overlay_leds():
        assert (x, y) in PRESS_LEDS + PANEL_LEDS, f'overlay LED at ({x},{y}) has no scene LED under it'


def overlay_leds():
    """Every 2x2 LED rect the overlay draws inside an `ld` group."""
    return [(int(x), int(y)) for grp in re.findall(r"<g class='ld[^']*'>(.*?)</g>", lights_svg)
            for x, y in re.findall(r'M(\d+) (\d+)h2v2h-2z', grp)]


def main(argv):
    args = [a for a in argv if not a.startswith('-')]
    if len(args) != 1 or set(argv) - set(args) - {'--no-id'}:   # a folder named like a flag needs ./-out
        sys.exit('usage: gen.py OUT_DIR [--no-id]')
    out = args[0]
    check()
    os.makedirs(out, exist_ok=True)
    body = {k: v for k, v in theme.items() if k != 'id'} if '--no-id' in argv else theme
    with open(f'{out}/{TID}.json', 'w') as f:
        json.dump(body, f)
    for name, text_ in (('factory.svg', svg_raw), ('lights.svg', lights_svg), ('sleep.svg', svg_sleep.replace('%23', '#'))):
        with open(f'{out}/{name}', 'w') as f:
            f.write(text_)
    with open(f'{out}/anchors.json', 'w') as f:
        json.dump(ANCHORS, f, indent=1)
    print(f'{TID}: css {len(theme_css)} / {CSS_MAX}')


if __name__ == '__main__':
    main(sys.argv[1:])
