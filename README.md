# Agent Works — a T3 Code theme

An animated pixel-art factory for [T3 Code](https://github.com/pingdotgg/t3code). Little TV-headed agent robots run a box assembly line in the grays of a '90s black-and-white CRT. When your agent starts working, the factory lights come on.

![Agent Works preview: idle, then the lights come on](media/preview.gif)

## What's in the scene

- **A high-detail animated background.** It's a 1440×960 WebP that loops every 20 seconds, with light shafts and drifting dust from the windows, a glow on bright pixels, floor reflections and soft shadows.
- **The assembly line.** A box drops from the chute and stops at each station. The inspector gives it a ✓. The press slams down with sparks, squashes the box and stamps a label. The tape robot seals it, and the box tips into the bin.
- **Around the line.** A welder throws sparks at the left wall, and steam drifts through the window light. A crane hook, a chain and a pipe in the foreground move at a different speed from the wall, which gives the scene depth. Robots walk across the floor.

**What reacts to T3 Code:**
- **The factory turns on while the agent works.** The amber lamps and the **AGENT WORKS** sign flicker on, chase lights run along the belt and the LEDs blink. When the turn ends, everything goes dark again.
- **Rows and composer.** The live work row gets an amber border with a moving belt underline, and the composer border turns amber.
- **CRT power-on.** A thin line opens into the scene when a chat loads.
- **The composer mascot.** A small robot sits on the composer's top edge and follows the end of your text. When you click in, an amber sweep crosses the top edge, and the robot's face lights up while it types.
- **Streaming replies** end with a blinking amber block cursor.
- **Reduced motion.** When the system's "reduce motion" setting is on, all animation stops.

## Install

```sh
./install.sh
```

Then in T3 Code, open **Settings → Appearance** and select **Agent Works**.

The script builds the theme and copies two files into `~/.t3/userdata/themes`:
- `agent-works.json`, the theme itself
- `agent-works.webp`, the animated background

To use a different themes folder, set `T3_THEMES_DIR`. Run the script again after any change.

## How it works

T3 Code limits a theme's CSS to 50,000 characters, but it also serves an image file named after the theme as `var(--theme-background-image)`. That image doesn't count toward the limit. So the scene is pre-rendered as an animated WebP, and the CSS (about 14K) is left for the parts that react to the app:

- **Lights on.** `[data-workspace-area="conversation"]:has([data-timeline-row-kind="working"], [data-timeline-row-kind="work-live"])` fades in a pseudo-element. It holds a small SVG of amber light (lamp cones, the sign, belt chase lights, LEDs), screen-blended over the scene. It uses the same `viewBox` and `center bottom / cover` sizing as the background, so it lines up at any window size.
- **Everything else** uses stable selectors from T3's theme guide.

**Files:**

| File | What it does |
|---|---|
| `gen.py` | Builds the source SVG scene (sprites, layout, animation timing), the composer mascot, the UI styling and the color roles. Writes `out/agent-works.json`, `out/factory.svg` and `out/lights.svg`. |
| `fx.py` | Holds the reactive layer: the light overlay, the CRT power-on, the work-row and composer effects, and the streaming cursor. |
| `render/render.sh` | Renders `out/factory.svg` in headless Brave with bloom, light shafts, dust and depth. It captures 300 frames and encodes `media/agent-works.webp`. Takes about 6.5 minutes and needs Brave, `img2webp` and Node. |
| `render/preview.sh` | Builds `media/preview.gif` from the rendered frames plus the light overlay. Needs `ffmpeg`. |
| `install.sh` | Builds the theme and copies the JSON and WebP into T3 Code's themes folder. |

**Rebuild steps:**

```sh
render/render.sh      # only after scene changes in gen.py
render/preview.sh     # optional: refresh the README GIF
./install.sh
```

**Rules for scene changes:**
- Everything in the scene must loop evenly in 20 seconds, so the WebP has no visible jump.
- Keep the middle of the wall (x 133 to 347 in scene units) calm, because the chat column covers it.

**Installing:** install through `./install.sh`, not **Add theme**. T3 only loads a background image for themes in its themes folder. A copy added with **Add theme** has no background and hides the folder copy, so if one exists, remove it in Settings → Appearance.

**Notes for agents:** [AGENTS.md](AGENTS.md) explains the build pipeline, the scene coordinates and the T3 Code internals this theme depends on.
