#!/bin/sh
# US English gate: uses the skills repo's checker when it is present.
if [ -f "$HOME/projects/skills/tools/us-english.py" ]; then
  python3 "$HOME/projects/skills/tools/us-english.py" styles >/dev/null || { echo "UK spellings in styles/; run the checker with --fix" >&2; exit 1; }
fi

# Install every style in this repo. No CLI exists for output styles; Claude Code
# just reads ~/.claude/output-styles, so a copy is the whole mechanism.
#
#   ./install.sh              install all
#   ./install.sh shipmate     install one
set -e
cd "$(dirname "$0")"

DEST="$HOME/.claude/output-styles"
mkdir -p "$DEST"

if [ $# -gt 0 ]; then
    for name in "$@"; do
        [ -f "styles/$name.md" ] || { echo "no such style: $name" >&2; exit 1; }
        cp "styles/$name.md" "$DEST/"
        echo "  installed $name"
    done
else
    cp styles/*.md "$DEST/"
    for f in styles/*.md; do echo "  installed $(basename "$f" .md)"; done
fi

echo
echo "Set one active in ~/.claude/settings.json, using the name: field from the file:"
grep -h '^name:' styles/*.md | sed 's/^name: /  { "outputStyle": "/; s/$/" }/'
