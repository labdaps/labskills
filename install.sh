#!/usr/bin/env bash
# Instala todas as skills deste repositorio em ~/.claude/skills/
#
# É a alternativa ao marketplace de plugins labdaps (ver README). Quem instala
# os plugins pelo marketplace não precisa deste script, e os dois juntos
# carregam cada skill duas vezes.
#
# Copia o conteudo de cada skill, item a item, para dentro de $DEST/<nome>/.
# Assim uma segunda execucao atualiza a instalacao em vez de aninhar a pasta
# (cp -r pasta/ destino-existente cria destino/pasta no GNU cp). Ficam de
# fora tests/ e __pycache__/: os testes dos scripts sao infraestrutura deste
# repositorio, rodam no CI e nao servem a skill instalada.
set -e

DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
SRC="$(cd "$(dirname "$0")/skills" && pwd)"
EXCLUIR=" tests __pycache__ "

mkdir -p "$DEST"

count=0
for dir in "$SRC"/*/; do
  name="$(basename "$dir")"
  mkdir -p "$DEST/$name"
  for item in "$dir"*; do
    case "$EXCLUIR" in
      *" $(basename "$item") "*) continue ;;
    esac
    cp -R "$item" "$DEST/$name/"
  done
  echo "instalada: $name"
  count=$((count + 1))
done

echo ""
echo "$count skills instaladas em $DEST"
echo "Abra o Claude Code e acione com /<nome-da-skill> ou em linguagem natural."
echo "Se você instalou os plugins do marketplace labdaps, não use também este script."
