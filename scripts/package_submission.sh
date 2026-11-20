#!/usr/bin/env bash
# Build the single ZIP for the CSC316 final submission.
# Usage: scripts/package_submission.sh <process-book.pdf> <video.mp4>
set -euo pipefail
cd "$(dirname "$0")/.."
[ $# -eq 2 ] || { echo "usage: $0 <process-book.pdf> <video.mp4>" >&2; exit 1; }
book=$1; video=$2
for f in "$book" "$video" data/cleaned/q4_events.csv; do
  [ -f "$f" ] || { echo "missing: $f (run scripts/build_data.py for q4_events.csv)" >&2; exit 1; }
done
name=CSC316_NBA_Desperation_Meter
stage=$(mktemp -d)/$name
mkdir -p "$stage/process_book" "$stage/video" "$stage/data/cleaned" dist
git ls-files -z | xargs -0 -I{} rsync -R "{}" "$stage/"
cp data/cleaned/q4_events.csv "$stage/data/cleaned/"
cp "$book" "$stage/process_book/"
cp "$video" "$stage/video/"
printf 'Project website: https://kkkaa43.github.io/csc316-nba-late-game/\nCode: https://github.com/kkkaa43/csc316-nba-late-game\n' > "$stage/WEBSITE.txt"
rm -f "dist/$name.zip"
(cd "$(dirname "$stage")" && zip -qr "$OLDPWD/dist/$name.zip" "$name")
echo "wrote dist/$name.zip ($(du -h "dist/$name.zip" | cut -f1))"
