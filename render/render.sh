#!/usr/bin/env bash
# End-to-end: gen.py -> page -> 300 frames (20 s @ 15 fps) -> animated WebP + poster.
# Usage: render/render.sh [scale=2] [quality=85] [fps=10]
set -euo pipefail
cd "$(dirname "$0")"
SCALE=${1:-2}; Q=${2:-85}; FPS=${3:-10}
ROOT=..
[ -d node_modules/puppeteer-core ] || npm i --silent
python3 $ROOT/gen.py $ROOT/out
rm -rf build/frames && mkdir -p build/frames
node page.mjs $ROOT/out/factory.svg build/page.html "$SCALE"
node capture.mjs build/page.html build/frames "$SCALE" $FPS
# frame durations in whole ms that add up to exactly 20 s (15 fps alternates 66/67 ms)
args=(-loop 0 -lossy -q "$Q" -m 6 -mixed)
i=0
for f in build/frames/f*.png; do
  d=$(( (i + 1) * 1000 / FPS - i * 1000 / FPS )); args+=(-d $d "$f"); i=$((i+1))
done
img2webp "${args[@]}" -o $ROOT/media/agent-works.webp
cp build/frames/f$(printf %04d $((FPS * 42 / 5))).png $ROOT/media/agent-works-poster.png
ls -l $ROOT/media/agent-works.webp
echo "run ./install.sh to publish it"
