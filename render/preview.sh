#!/usr/bin/env bash
# Builds media/preview.gif: 20 s loop, lights off for the first half, on (with flicker) for the second.
# Needs render/build/frames from render.sh.
set -euo pipefail
cd "$(dirname "$0")"
ROOT=..
python3 $ROOT/gen.py $ROOT/out >/dev/null
FPS=$(( $(ls build/frames/f*.png | wc -l) / 20 ))   # match the last render.sh
SCALE=$(( $(magick identify -format %w build/frames/f0000.png) / 480 ))
rm -rf build/lights && node preview.mjs $ROOT/out/lights.svg build/lights $FPS $SCALE
# lights opacity: 0 until 10 s, flicker 10.0-10.35 s, then on; screen-blend over the scene
OP="if(lt(T,10),0,if(lt(T,10.07),0.9,if(lt(T,10.13),0.1,if(lt(T,10.2),1,if(lt(T,10.27),0.3,1)))))"
ffmpeg -loglevel error -y -framerate $FPS -i build/frames/f%04d.png -framerate $FPS -i build/lights/l%04d.png \
  -filter_complex "[1]format=rgba,colorchannelmixer=aa=1,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='alpha(X,Y)*($OP)'[l];\
[0][l]overlay=format=auto,scale=720:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];\
[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" $ROOT/media/preview.gif
ls -l $ROOT/media/preview.gif
