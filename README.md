# Agent Works — a T3 Code theme

A calm, animated pixel-art factory for [T3 Code](https://github.com/pingdotgg/t3code). Little TV-headed agent robots run a box assembly line in the grays of a '90s black-and-white CRT.

![Agent Works preview](media/preview.gif)

## What's in the scene

- A box drops from the chute when the lever robot pulls it, then rides the belt and stops at each station on a 4-second loop.
- The inspector robot gives it a ✓, the press stamps a label, the tape robot seals it, and the box tips into the bin.
- On the factory floor, one robot carries a box and another sweeps.
- Clouds and chimney smoke drift past the windows, a steam pipe puffs, the clock ticks, the lamps and the sign flicker.
- Scanlines, a vignette and a slow rolling band give it the old-CRT look.
- A small robot perches on the composer's top edge, follows the end of your text and types faster while you're typing.
- The animation pauses when the system's "reduce motion" setting is on.

## Install

```sh
cp agent-works.json ~/.t3/userdata/themes/agent-works.json
```

Then pick **Agent Works** in T3 Code's appearance settings.

## How it works

The scene is a 480×320 pixel-art SVG with its CSS keyframe animations inside it. It's embedded as a `data:` URI in the theme's `css` field, so the theme is one self-contained JSON file (~44K of the 50K character limit). The stations sit to the sides so the chat column covers only the quiet middle of the wall.

`gen.py` builds everything: sprites, scene layout, animation timing, the composer mascot, the rest of the UI styling and the color roles.

```sh
python3 gen.py out   # writes out/agent-works.json and out/factory.svg
```

To install your rebuilt version, add `"id": "agent-works"` to `out/agent-works.json` and copy it into `~/.t3/userdata/themes/`.
