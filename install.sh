#!/usr/bin/env bash
# Installs Agent Works HD into T3 Code: the theme JSON plus its animated background.
# Usage: ./install.sh            (themes dir defaults to ~/.t3/userdata/themes)
#        T3_THEMES_DIR=/path ./install.sh
set -euo pipefail
cd "$(dirname "$0")"
DIR=${T3_THEMES_DIR:-$HOME/.t3/userdata/themes}
ID=agent-works-hd
[ -f media/agent-works.webp ] || { echo "media/agent-works.webp missing; run render/render.sh" >&2; exit 1; }
mkdir -p out "$DIR"
python3 gen.py out >/dev/null
# T3 reads the id from the file name, so drop it from the JSON body.
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); d.pop("id",None); json.dump(d,open(sys.argv[2],"w"))' \
  "out/$ID.json" "$DIR/$ID.json"
cp media/agent-works.webp "$DIR/$ID.webp"
echo "Installed to $DIR/$ID.{json,webp}"
echo "In T3 Code: Settings > Appearance > Agent Works HD"
