# Agent notes: how the Agent Works theme is built

These are the facts that took real digging to find. Read this before you change the theme so you don't have to rediscover any of it. The README covers features and install; this file covers the code and the T3 Code internals it depends on.

Verified against T3 Code (Beta) **0.1.10** on macOS, 2026-11. If the app updates, recheck anything in "T3 Code internals" before relying on it.

## Pipeline at a glance

```
gen.py ──► out/factory.svg ──► render/render.sh ──► media/agent-works.webp ─┐
   │                             (Brave + puppeteer,                        │
   │                              render/page.mjs + render/fx.js)           │
   ├─► out/agent-works.json  (colors + CSS; CSS includes fx.py output) ─────┤
   ├─► out/lights.svg        (the "agent working" overlay, for preview.sh)  │
   └─► out/anchors.json      (scene positions; page.mjs hands them to fx.js)│
                                                                            ▼
                         install.sh ──► ~/.t3/userdata/themes/agent-works.{json,webp}
```

- `python3 gen.py out` takes about a second and creates `out/` if needed. It writes `out/agent-works.json`, `out/factory.svg`, `out/lights.svg` and `out/anchors.json`. It asserts that the CSS is at most 50,000 characters (and prints the count, currently about 19.6K), that every overlay LED sits on a scene LED, and that the press and weld keyframes still match the timing in `ANCHORS`. `--no-id` leaves `id` out of the JSON, which is what `install.sh` uses.
- `python3 -m unittest discover -s tests` takes well under a second. It imports `gen` (importing builds the theme in memory and writes nothing) and checks the CSS limit and restrictions, LED and lamp alignment, that every scene animation period divides the 20 s loop, and the CLI outputs. Run it after any change to `gen.py` or `fx.py`.
- `render/render.sh [scale=3] [quality=85]` takes about 6.5 minutes. Run it only when the scene changes in `gen.py`. It writes `media/agent-works.webp` (1440×960, 300 frames, 15 fps, 20 s loop, about 4.6 MB) and `media/agent-works-poster.png`. It runs `npm i` inside `render/` on its first run.
- `render/preview.sh` takes about 30 seconds. It reuses `render/build/frames/` from the last render, composites `out/lights.svg` over them and writes `media/preview.gif` (untracked): 10 s idle, then the lights flicker on. It's a quick scene check only. The README uses `media/demo.gif`, and Twitter uses `media/demo.mp4`; both are screen recordings of the real app window (`screencapture -v -l <windowID>`, cropped and encoded with ffmpeg).
- `./install.sh [-y]` builds the theme JSON with `gen.py out --no-id` (the file name supplies the ID) and copies the JSON and WebP into `~/.t3/userdata/themes/`. Override the folder with `T3_THEMES_DIR`.

**Tools:** Brave at `/Applications/Brave Browser.app` (override with the `BRAVE` env var), plus `img2webp`, `ffmpeg` and Node, all from Homebrew. Python uses only the standard library.

## Files

| File | Role |
|---|---|
| `gen.py` | Builds, top to bottom at import time, the 480×320 pixel scene as an SVG with CSS keyframes inside it, `ANCHORS`, the composer mascot sprite sheet, the UI CSS (adding `fx.css(...)`) and the color roles. `check()` holds the build invariants; `main()` (only when run as a script) writes the files. |
| `fx.py` | The reactive layer: everything that responds to app state. `overlay(an, g, text, R)` builds the amber light SVG, and `css(an, g, text, R, enc)` returns the CSS. `an` is `gen.ANCHORS`, the only source of positions; the rest are `gen.py`'s pixel helpers. |
| `render/page.mjs` | Builds `render/build/page.html`: three inline copies of the SVG (base, bloom, reflection), canvas layers, and a threshold filter for bloom. |
| `render/fx.js` | Draws the canvas effects: shading and ambient occlusion, a calm center band, light shafts, dust motes, backlit steam and CRT structure. Every effect is a pure function of `t` and periodic over 20 s. |
| `render/harness.mjs` | Shared headless-Brave launcher. `seek(t)` pauses every animation at `t` (`document.getAnimations()` → pause, set `currentTime`), calls `AW_drawFx(t)` if the page has it, then waits two animation frames so the screenshot isn't stale. Both capture scripts use it; add any new capture script on top of it. |
| `render/capture.mjs` | Seeks to each frame time and screenshots it. Passing a 4th argument such as `0,1.5,12.4` captures single test frames to `t<sec>.png`. |
| `render/preview.mjs` + `preview.sh` | Builds the README GIF. |
| `tests/test_theme.py` | Standard-library `unittest` checks of the build invariants and the `gen.py` CLI. |
| `install.sh` / `uninstall.sh` | Install or update the theme in T3 Code's themes folder, or remove it. Both ask before changing an existing install. `-y` skips the question. Without `-y`, a non-interactive run (no terminal) exits without changing anything. `uninstall.sh` deletes only `agent-works.{json,webp,png,jpg,jpeg}` and never follows symlinks. |

## Scene coordinates and conventions (gen.py)

- **Scene space:** 480×320 units. Floor line `FY = 282`.
- **Line layer:** stations, belt, boxes and workers are drawn in an older 180-tall coordinate system and shifted down by `DY = 150` through the `LT` group.
- **Box rest positions:** `S = (36, 92, 220, 348, 404)`, for the chute, the inspector, transit, the press and the tape station.
- **Chat column:** it covers about x 133–347, so keep that band calm. Stations sit to the sides, and only a fast belt span crosses the middle.
- **Helpers:**
  - `g(rects)` merges `(color, x, y, w, h)` rects into one path per color.
  - `sprite(rows, pal)` turns an ASCII map into rects.
  - `text()` uses the 3×5 pixel `FONT`.
- **Loop:** every animation period must divide **20 s** (the box cycle), or the WebP jumps when it loops. The station clock is 4 s; the belt pauses from 0% to 37.5% and moves 64 px from 37.5% to 100%.
- **Scene anchors (`ANCHORS` in `gen.py`).** This is the one source of positions for `fx.py` (the overlay) and `render/fx.js` (the canvas effects, through `out/anchors.json` → `window.AW_ANCHORS`). Each anchor comes from the same variable that draws it (`LAMPS`, `BULB_Y`, `WINS`, `WELD`, `PRESS_LEDS`, ...), so moving a station moves its lights too. Never retype a coordinate in `fx.py` or `fx.js`; add it to `ANCHORS` instead. Current values:

| Anchor | Key | Value |
|---|---|---|
| Lamps | `lamps`, `bulbY` | x 100 and 382, bulb y 177 (cone starts at y 178) |
| Windows | `windows`, `glassY` | x 142 and 296, glass y 99–125 |
| Sign | `sign` | text origin x 218, y 56 (letters at y 59) |
| Belt | `belt` | x 22–420, skirt chase line y 269 |
| Press LEDs | `pressLeds` | (349, 187), (354, 187), (359, 187) |
| Panel LEDs | `panelLeds` | (8, 221), (12, 221) |
| Press hit | `pressHit` | (356, 247) at 0.38 s of each 4 s cycle (`.pr` keyframe 9.5%) |
| Weld arc | `weld` | (14, 160), on for the first 2.2 s of 5 s (`.wo` keyframe 44%) |

- **Foreground layer** (`FG`, x 0–120 pipe, chain at x 72–78, crane hook near x 456–508). It uses class `fg`. `page.mjs` blurs it slightly and leaves it out of the bloom and reflection copies.

## How the reactive layer works (fx.py)

- **Agent working:** `[data-workspace-area="conversation"]:has([data-timeline-row-kind="working"],[data-timeline-row-kind="work-live"])`. T3 renders a `working` row (id `working-indicator-row`) while a turn runs, and `work-live` for the active tool group. Both go away when the turn ends.
- **Lights-on layer:** a `::before` pseudo-element on the conversation area.
  - Its background is `lights.svg` as a `data:` URI, sized `center bottom / cover` with the same `viewBox` as the scene and `preserveAspectRatio='xMidYMax slice'`. That's why it lines up pixel for pixel with the WebP at any window size. Keep the two sizing rules identical.
- **One scene for the whole window:** the chat background, the lights overlay and the sidebar wall all use `center bottom / cover` with `background-attachment: fixed`, so they're sized to the window, not to each element. That keeps the belt continuous across the sidebar edge. Don't give any of them their own size or position.
  - It uses `mix-blend-mode: screen` and `z-index: -1` on top of `isolation: isolate`, so it sits above the background and below the messages.
- **`::after`** is a dimming vignette for the idle state. It fades out while work is happening.
- **The composer reacts to app-wide state** through `body:has(...)`. The composer isn't inside the conversation area, so a `[conversation]:has(...) [composer]` selector never matches.
- **Mascot:** one sprite sheet, 34×27 units with two 17-wide poses: idle gray, and typing with an amber face and fast arms. It's applied to `.composer-tiptap>:last-child::after`, and `:focus-within` switches between the poses with `background-position`.
- **Streaming cursor:** `[data-streaming="true"]>:last-child::after`. `data-streaming` is set on the markdown wrapper of the reply that's currently streaming.
- **Sidebar:** `[data-slot="sidebar-inner"]::before` shows `var(--theme-background-image)` (fixed to the window, darkened) and `::after` is the amber chase rail. "Working anywhere" is `body:has(<live row>)` **or** `body:has([data-testid="sidebar-working-header"])`, the sidebar's "Working" shelf, which T3 renders while any thread runs (`busy()` in `fx.py` builds both). The open thread is `[data-sidebar-row][aria-current="page"]`. `aria-current` sits on the inner row div, **not** on `li[data-thread-item]`. A single row's running state is only a Tailwind class (`text-info-foreground`), so the theme doesn't target it.
- **Hold state** (`WAIT` in `fx.py`): `[data-approval-detail]` renders only while an approval request is pending (T3 shows it from `pendingApprovals`), and `[data-pending-user-input-toggle]` is present while a question waits for an answer. Either one sets the lamps to a slow blink, puts hazard tape around the request, makes the sidebar rail a hazard bar and glows the composer.
- **Right panel and details card** (`details_css()` in `fx.py`): the right panel is `[data-workspace-area="panel"]` (tab bar `[data-right-panel-tabbar]`, header `[data-surface-subheader]`, body `[data-right-panel-surface-content]`). Its `::before` is the fixed, darkened scene and its `::after` is an amber chase on the left edge while any agent works. The thread details card (branch, PR, changes) is `[data-thread-details-card]`, normally a `dropdown-glass` popover; the theme drops the blur for a steel frame. Its PR action buttons sit in `[data-pull-request-action-pending]`, which is `true` while a merge or other action runs.
- **Performance:** animate only `transform` and `opacity` on large layers. The sidebar rail moves with `translateY`, not `background-position`. Selection highlights are neutral steel (`SEL` in `fx.py`), never amber, so colored monograms stay readable. Keep `:has()` arguments to single attribute selectors.
- **Colors** are only grays plus amber: `#ffb547`, `#ff9a2e` and `#ffe2a8`.
- **Reduced motion:** add any new animation to the `prefers-reduced-motion` rule.

## T3 Code internals this theme relies on

All of this came from reading the app bundle, `/Applications/T3 Code (Beta).app/Contents/Resources/app.asar`. To look again, extract it with `npx @electron/asar extract <asar> /tmp/t3asar/out`. The client is in `apps/server/dist/client/assets/`, and the server is in `apps/server/dist/*.mjs`.

- **The CSS limit is hardcoded:** `THEME_CSS_MAX_LENGTH = 5e4`, checked by the schema. It can't be raised through configuration.
- **CSS restrictions:** no `@import`, no `image-set()`, no `src()`. `url()` only works with `data:` or `#id`, and backslashes are rejected on the client. `<` and `>` are fine inside a quoted `url("data:…")`, which is why `enc()` escapes only `%`, `#` and `"`.
- **Background image:** `<themesDir>/<themeId>.{webp,png,jpg,jpeg}`, up to 16 MB, no symlinks. The client fetches it and sets `--theme-background-image: url("blob:…")` on `<html>`. Animated WebP plays. It's looked up **by theme ID, only for themes that come from the themes folder**.
- **Where installed themes live, and which wins:**
  - **Themes folder ("environment" themes):** `~/.t3/userdata/themes/<id>.json`. The server scans this folder, and the file name sets the ID; IDs `system`, `light`, `dark` and the built-ins are reserved. These show in Settings → Appearance **without** edit or remove buttons, and they're the only kind that gets a background image. **This is how Agent Works is installed.**
  - **Add theme (user library):** stored in browser localStorage under `t3code:themes:v1` in `~/Library/Application Support/t3code-v2/Local Storage`. These cards have edit, export and remove buttons, but **never get a background image**, so the WebP scene doesn't load for them.
  - **Lookup order:** built-ins first, then the user library, then the themes folder. A user-library theme with the same ID **hides** the folder theme. If the scene looks stale or missing, check Settings → Appearance for a removable card with the same name and remove it.
- **Which theme is active:** `~/.t3/userdata/settings.json`, key `defaultTheme`. Agents can set it with the `t3_theme_set` tool (`themeId: "agent-works"`). `t3_theme_read` lists folder themes along with `hasBackground`.
- **Stable selectors:** the in-app guide lists them, and `t3_theme_read` returns it. Other class names change between releases. This theme also uses these attributes, which the guide doesn't list:
  - `data-timeline-row-kind` values `working`, `work-live`, `thinking`, `work-toggle`
  - `data-streaming`
  - `data-slot="composer-shell"`
  - `.composer-tiptap`
  - `data-sidebar-row` (with `aria-current="page"` when open)
  - `data-testid` values `sidebar-working-header` and `sidebar-working-shelf-toggle`
  - `data-workspace-area="panel"`, `data-right-panel-tabbar`, `data-right-panel-surface-content`, `data-surface-subheader`, `data-thread-details-card`, `data-pull-request-action-pending`
  - `data-approval-detail`, `data-pending-user-input-toggle`, `data-command-palette`, `data-chat-workspace-drop-overlay`, `data-model-picker-selected-indicator`, `data-timeline-row-kind="proposed-plan"`, `data-highlighted` on `menu-item`, `command-item`, `select-item` and `combobox-item`

## Checking changes in the live app

- `t3_theme_set` reloads the theme. If a change doesn't show up, switch to `t3-chat` and back to `agent-works`.
- **Screenshots:** `screencapture -x` works. The display is Retina: screenshot pixels are 2.25× the click coordinates, which are in points. To click, post `CGEvent` mouse events from a small Swift helper; AppleScript `click at` doesn't reach the app.
- The web build at `http://127.0.0.1:3773` needs a pairing token, so check in the desktop app instead.
- **Check the reactive layer while a turn is running.** Your own turn counts: the lamps, sign and belt chase should be lit in any screenshot taken during it.
