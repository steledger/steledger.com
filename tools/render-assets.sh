#!/usr/bin/env bash
# Rasterise the brand mark from assets/logo.svg. Run after changing the SVG:
#
#   tools/render-assets.sh
#
# Needs ImageMagick with librsvg. Not part of tools/build.py and not run by CI —
# the PNGs are committed, this only regenerates them.
#
# Two traps, both of which produced wrong files before this script existed:
#
# 1. ImageMagick rasterises an SVG at its *natural* size and only then resizes.
#    logo.svg has a 64-unit viewBox, so `convert logo.svg -resize 512x512` renders
#    64×64 and scales it up 8× — the arc comes out as a staircase. Measured against
#    a high-resolution reference, that is 11.9% RMSE versus 0.47% for the route
#    below. `-density` is the lever: 96 dpi is the 1:1 default, so 96 × (2048/64)
#    = 3072 renders the master at 2048.
#
# 2. logo.svg colours the path from a <style> block, so the file can follow the
#    page's dark mode. librsvg here does not apply it and falls back to the
#    default fill, which is black — silently. Nothing errors; you just get a black
#    mark. So this script feeds the rasteriser a copy with the fill as an
#    attribute, and leaves logo.svg alone for the browser.
set -euo pipefail

cd "$(dirname "$0")/.."
command -v convert >/dev/null || { echo "ImageMagick (convert) not found" >&2; exit 1; }

PATINA="#3f6e5e"   # --patina, the light-theme brand colour
STONE="#eeece6"    # --stone, the page background
MASTER="$(mktemp -d)/master.png"
trap 'rm -rf "$(dirname "$MASTER")"' EXIT

# the path, with an explicit fill the rasteriser will honour
FLAT="$(dirname "$MASTER")/flat.svg"
python3 - "$FLAT" "$PATINA" <<'PY'
import re, sys, pathlib
src = pathlib.Path("assets/logo.svg").read_text()
path = re.search(r'd="([^"]+)"', src).group(1)
pathlib.Path(sys.argv[1]).write_text(
    '<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">'
    f'<path fill="{sys.argv[2]}" fill-rule="evenodd" d="{path}"/></svg>\n'
)
PY

# master at 2048: 96 dpi × (2048 / 64 viewBox units)
convert -background none -density 3072 "$FLAT" "$MASTER"

# everything else comes down from the master, never up from the SVG
convert "$MASTER" -filter Lanczos -resize 64x64   assets/logo.png
convert "$MASTER" -filter Lanczos -resize 512x512 assets/avatar-mark-512.png

# the square avatar: the mark knocked out of a patina slab, so it reads on a
# light or a dark profile page
convert -size 512x512 "xc:$PATINA" \
        \( "$MASTER" -filter Lanczos -resize 320x320 -fill "$STONE" -colorize 100 \) \
        -gravity center -compose over -composite \
        \( -size 512x512 "xc:none" -fill white -draw "roundrectangle 0,0,511,511,112,112" \) \
        -alpha set -compose dstin -composite \
        assets/avatar-512.png

# raster favicons, cut from the avatar. The page's favicon.svg is the bare mark,
# and an SVG-only site gets a generated letter from Google's favicon service —
# which is what Claude shows for a connector on this domain.
convert assets/avatar-512.png -filter Lanczos -resize 192x192 assets/icon-192.png
convert assets/avatar-512.png -filter Lanczos -resize 180x180 assets/apple-touch-icon.png
convert assets/avatar-512.png -filter Lanczos -define icon:auto-resize=48,32,16 assets/favicon.ico

for f in assets/logo.png assets/avatar-mark-512.png assets/avatar-512.png \
         assets/icon-192.png assets/apple-touch-icon.png; do
  printf '  %-32s %s\n' "$f" "$(identify -format '%wx%h %[colorspace]' "$f")"
done
