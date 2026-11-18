#!/usr/bin/env bash
# Renders the idle "sleep" frame: out/sleep.svg -> media/agent-works-sleep.webp (960x640, about 15 KB).
# gen.py embeds it in the theme CSS (base64), so it must stay small: the CSS limit is 50,000 characters.
# Scale 2 keeps every scene pixel a crisp 2x2 block; dimming it here (-modulate) both darkens the
# idle factory and makes it compress better. Rerun when the scene changes (alongside render.sh).
# Usage: render/sleep.sh
set -euo pipefail
cd "$(dirname "$0")"
ROOT=..
[ -d node_modules/puppeteer-core ] || npm i --silent
python3 $ROOT/gen.py $ROOT/out
mkdir -p build/sleep
node page.mjs $ROOT/out/sleep.svg build/sleep.html 2 sleep
node capture.mjs build/sleep.html build/sleep 2 15 0
magick build/sleep/t0.png -modulate 72 build/sleep/dim.png
cwebp -quiet -q 60 -sns 0 -f 0 -m 6 -sharp_yuv build/sleep/dim.png -o $ROOT/media/agent-works-sleep.webp
ls -l $ROOT/media/agent-works-sleep.webp
echo "run python3 gen.py out (or ./install.sh) to embed it"
