#!/bin/bash
# publish.sh: the one way tothefinish.ai ships (2026-11-18).
#   build pages -> commit -> push -> wait until GitHub Pages serves it -> IndexNow ping for the pages that changed.
# Usage: tools/publish.sh "commit message" [--numbers-only]
#   --numbers-only: refuse to publish if anything other than Garmin-driven files changed
#   (data/progress.json, built pages, sitemap, pages/.facts-state.json). This is the auto-publish path
#   (Tyler 2026-11-18: "Yes, auto-publish numbers"); wording changes and new pages ship without it, through the voice gate (brain/social/voice-gate.md, since 2026-11-18).
set -u
SITE="$(cd "$(dirname "$0")/.." && pwd)"
MSG="${1:-Site update}"
MODE="${2:-}"
cd "$SITE" || exit 1
echo "== $(date '+%Y-%m-%d %H:%M') publish: $MSG"

git pull -q --rebase --autostash origin main || { echo "pull failed"; exit 1; }
python3 tools/build_pages.py || { echo "build failed"; exit 1; }
python3 tools/build_races.py || { echo "race page build failed"; exit 1; }
python3 tools/build_chicago.py || { echo "chicago page build failed"; exit 1; }

CHANGED=$(git status --porcelain -uall | awk '{print $NF}')
if [ -z "$CHANGED" ]; then echo "no change"; exit 0; fi

if [ "$MODE" = "--numbers-only" ]; then
  # built pages are allowed only if their source (questions.json, build script, index.html) did not change
  BAD=$(echo "$CHANGED" | grep -vE '^(data/(progress|races)\.json|sitemap\.xml|pages/\.facts-state\.json|[a-z0-9-]+/index\.html|episodes/index\.html)$' || true)
  if [ -n "$BAD" ]; then
    echo "numbers-only refused; these need approval: $(echo $BAD)"
    /usr/bin/osascript -e 'display notification "Site has non-number changes waiting for approval" with title "tothefinish.ai"' >/dev/null 2>&1
    exit 2
  fi
fi

git add -A
git commit -q -m "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push -q origin HEAD || { echo "push failed"; /usr/bin/osascript -e 'display notification "tothefinish.ai push failed" with title "Site publish"' >/dev/null 2>&1; exit 1; }
echo "pushed: $(git log --oneline -1)"

# pages that changed -> public URLs
URLS=$(echo "$CHANGED" | grep -E 'index\.html$' | sed -e 's#index\.html$##' -e 's#^#https://tothefinish.ai/#' | sort -u)
[ -z "$URLS" ] && { echo "no page URLs to ping"; exit 0; }

# wait (up to 6 min) until GitHub Pages serves the first changed page as built
FIRST=$(echo "$CHANGED" | grep -E 'index\.html$' | head -1)
WANT=$(shasum "$FIRST" | cut -c1-40)
for i in $(seq 1 24); do
  URL="https://tothefinish.ai/${FIRST%index.html}"
  GOT=$(curl -s -H 'Cache-Control: no-cache' "$URL?v=$(date +%s)" | shasum | cut -c1-40)
  [ "$GOT" = "$WANT" ] && { echo "live after ~$((i*15))s"; break; }
  sleep 15
done
python3 tools/indexnow.py $URLS
