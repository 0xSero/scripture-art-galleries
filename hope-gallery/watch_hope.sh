#!/bin/bash
# Rebuild the gallery every ten minutes while the downloads are still running,
# then once more when they stop, so the page always matches what has arrived.
cd "$(dirname "$0")"
while pgrep -f resolve.py > /dev/null; do
  sleep 600
  echo "--- rebuild $(date '+%H:%M:%S')" >> /tmp/hope-build.log
  bash make_hope.sh >> /tmp/hope-build.log 2>&1
done
echo "--- final rebuild $(date '+%H:%M:%S')" >> /tmp/hope-build.log
bash make_hope.sh >> /tmp/hope-build.log 2>&1
echo "--- DONE" >> /tmp/hope-build.log
