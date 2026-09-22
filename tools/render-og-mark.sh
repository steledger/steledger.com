#!/usr/bin/env bash
# Refresh the mark inside assets/og.png — the 1200×630 card link previews show.
#
#   tools/render-og-mark.sh
#
# This deliberately does NOT rebuild the card. The composition — the serif
# wordmark, the two-line subtitle, the rule, the domain — was made by hand and is
# the best-looking of the brand rasters; reproducing it from a script would mean
# guessing at fonts and spacing and would almost certainly come out worse.
#
# What it fixes is the one measurable defect: the mark in that file was scaled up
# from a small rasterisation, so the arc had no antialiasing at all — two colours
# along the curve where a clean render has a hundred — and the right side of the
# dome was visibly flattened. This paints that rectangle out and drops in a mark
# rendered at 2048 and brought down.
#
# Safe because the mark sits alone on flat background: it occupies x 181–340,
# y 176–405, and nothing else starts before x=400. If the layout ever moves,
# these numbers move with it.
set -euo pipefail

cd "$(dirname "$0")/.."
command -v convert >/dev/null || { echo "ImageMagick (convert) not found" >&2; exit 1; }

STONE="#eeece6"; PATINA="#3f6e5e"
X=181; Y=176; W=160; H=230          # where the mark sits, measured off the card
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

# logo.svg colours its path from a <style> block, which the rasteriser ignores —
# rendering it directly yields a silently black mark. Feed it an explicit fill.
python3 - "$TMP/flat.svg" "$PATINA" <<'PY'
import re, sys, pathlib
src = pathlib.Path("assets/logo.svg").read_text()
path = re.search(r'd="([^"]+)"', src).group(1)
pathlib.Path(sys.argv[1]).write_text(
    '<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">'
    f'<path fill="{sys.argv[2]}" fill-rule="evenodd" d="{path}"/></svg>\n'
)
PY

# 96 dpi is 1:1 for a 64-unit viewBox, so 3072 renders the master at 2048
convert -background none -density 3072 "$TMP/flat.svg" -trim +repage \
        -filter Lanczos -resize "${W}x${H}!" "$TMP/mark.png"

convert assets/og.png \
        -fill "$STONE" -draw "rectangle $((X-6)),$((Y-6)) $((X+W+6)),$((Y+H+6))" \
        "$TMP/mark.png" -geometry "+$X+$Y" -composite \
        assets/og.png

printf '  assets/og.png %s\n' "$(identify -format '%wx%h %B байт' assets/og.png)"
printf '  цветов вдоль дуги: %s (у ступенчатого края их 2)\n' \
       "$(convert assets/og.png -crop 90x60+180+170 +repage -format '%k' info:)"
