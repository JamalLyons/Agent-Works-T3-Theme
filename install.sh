#!/usr/bin/env bash
# Installs or updates the Agent Works theme in T3 Code's themes folder.
# Usage: ./install.sh [-y]      -y skips the "update existing install?" prompt
#        T3_THEMES_DIR=/path ./install.sh
set -euo pipefail
cd "$(dirname "$0")"
DIR=${T3_THEMES_DIR:-$HOME/.t3/userdata/themes}
ID=agent-works
YES=0; [ "${1:-}" = "-y" ] && YES=1

[ -f media/agent-works.webp ] || { echo "media/agent-works.webp is missing. Run render/render.sh first." >&2; exit 1; }

if [ -e "$DIR/$ID.json" ] || [ -e "$DIR/$ID.webp" ]; then
  echo "Agent Works is already installed in $DIR."
  if [ $YES -eq 0 ]; then
    [ -t 0 ] || { echo "Run with -y to update without a prompt." >&2; exit 1; }
    read -r -p "Replace it with this version? [y/N] " ans
    case "$ans" in y|Y|yes|YES) ;; *) echo "Nothing changed."; exit 0 ;; esac
  fi
fi

mkdir -p out "$DIR"
python3 gen.py out >/dev/null
# T3 takes the theme id from the file name, so drop it from the JSON body.
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); d.pop("id",None); json.dump(d,open(sys.argv[2],"w"))' \
  "out/$ID.json" "$DIR/$ID.json"
cp media/agent-works.webp "$DIR/$ID.webp"
echo "Installed $DIR/$ID.json and $DIR/$ID.webp"
echo "In T3 Code: Settings > Appearance > Agent Works"
