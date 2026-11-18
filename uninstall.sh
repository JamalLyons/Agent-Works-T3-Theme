#!/usr/bin/env bash
# Removes the Agent Works theme from T3 Code's themes folder.
# Deletes only agent-works.json and its background image; nothing else in the folder is touched.
# Usage: ./uninstall.sh [-y]
set -euo pipefail
DIR=${T3_THEMES_DIR:-$HOME/.t3/userdata/themes}
ID=agent-works
YES=0; [ "${1:-}" = "-y" ] && YES=1

files=()
for f in "$DIR/$ID.json" "$DIR/$ID.webp" "$DIR/$ID.png" "$DIR/$ID.jpg" "$DIR/$ID.jpeg"; do
  # only plain files we put there; never follow symlinks
  if [ -f "$f" ] && [ ! -L "$f" ]; then files+=("$f"); fi
done

if [ ${#files[@]} -eq 0 ]; then
  echo "Agent Works is not installed in $DIR."
  exit 0
fi

echo "This removes:"
printf '  %s\n' "${files[@]}"
if [ $YES -eq 0 ]; then
  [ -t 0 ] || { echo "Run with -y to remove without a prompt." >&2; exit 1; }
  read -r -p "Remove Agent Works? [y/N] " ans
  case "$ans" in y|Y|yes|YES) ;; *) echo "Nothing removed."; exit 0 ;; esac
fi

rm -- "${files[@]}"
echo "Removed. If Agent Works was your active theme, pick another one in Settings > Appearance."
