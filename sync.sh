#!/bin/bash
# Refresh the repository from the galleries on this machine and push.
# The hope gallery keeps downloading plates, so run this again to bring it up to date.
set -e
cd "$(dirname "$0")"
python3 ~/build_repo.py
git add -A
git -c user.name="0xSero" -c user.email="sero@0xsero.com" commit -m "Update the galleries" || echo "nothing new"
git push
