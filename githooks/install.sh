#!/bin/sh
# Installs this repo's versioned git hooks into .git/hooks (which git
# itself never tracks). Run once after cloning: `sh githooks/install.sh`
set -e
ROOT="$(git rev-parse --show-toplevel)"
cp "$ROOT/githooks/pre-push" "$ROOT/.git/hooks/pre-push"
chmod +x "$ROOT/.git/hooks/pre-push"
echo "Installed pre-push hook."
