#!/usr/bin/env bash
# Instala todas as skills deste repositorio em ~/.claude/skills/
set -e

DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
SRC="$(cd "$(dirname "$0")/skills" && pwd)"

mkdir -p "$DEST"

count=0
for dir in "$SRC"/*/; do
  name="$(basename "$dir")"
  cp -r "$dir" "$DEST/$name"
  echo "instalada: $name"
  count=$((count + 1))
done

echo ""
echo "$count skills instaladas em $DEST"
echo "Abra o Claude Code e acione com /<nome-da-skill> ou em linguagem natural."
