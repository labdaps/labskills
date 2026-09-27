#!/usr/bin/env bash
# Instala as skills deste repositório em ~/.claude/skills/ (ou em $CLAUDE_SKILLS_DIR)
#
# É a alternativa ao marketplace de plugins labdaps (ver README). Quem instala
# os plugins pelo marketplace não precisa deste script, e os dois juntos
# carregam cada skill duas vezes.
#
# Uso:
#   ./install.sh                             copia todas as skills de skills/
#   ./install.sh --plugin grafo --plugin ml  copia só as skills desses plugins
#
# O --plugin, repetível, lê a composição de cada plugin em
# .claude-plugin/marketplace.json e precisa de Python 3. Serve para a cópia
# versionada em <projeto>/.claude/skills/, que não deve levar skill de plugin
# que o projeto não usaria (ver README, "Declarar os plugins num projeto").
#
# Copia o conteudo de cada skill, item a item, para dentro de $DEST/<nome>/.
# Assim uma segunda execucao atualiza a instalacao em vez de aninhar a pasta
# (cp -r pasta/ destino-existente cria destino/pasta no GNU cp). Ficam de
# fora tests/ e __pycache__/: os testes dos scripts sao infraestrutura deste
# repositorio, rodam no CI e nao servem a skill instalada.
set -e

DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
RAIZ="$(cd "$(dirname "$0")" && pwd)"
SRC="$RAIZ/skills"
EXCLUIR=" tests __pycache__ "

plugins=()
while [ $# -gt 0 ]; do
  case "$1" in
    --plugin)
      if [ -z "${2:-}" ]; then
        echo "erro: --plugin precisa do nome de um plugin do marketplace labdaps" >&2
        exit 2
      fi
      plugins+=("$2")
      shift 2
      ;;
    --plugin=*)
      plugins+=("${1#--plugin=}")
      shift
      ;;
    -h|--help)
      sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "erro: argumento desconhecido: $1 (use --plugin <nome> ou --help)" >&2
      exit 2
      ;;
  esac
done

if [ ${#plugins[@]} -eq 0 ]; then
  nomes="$(cd "$SRC" && for d in */; do echo "${d%/}"; done)"
else
  PY="$(command -v python3 || command -v python || true)"
  if [ -z "$PY" ]; then
    echo "erro: o --plugin precisa de Python 3 para ler o marketplace.json" >&2
    exit 2
  fi
  nomes="$("$PY" - "$RAIZ/.claude-plugin/marketplace.json" "${plugins[@]}" <<'PY'
import json
import sys

arquivo, pedidos = sys.argv[1], sys.argv[2:]
with open(arquivo, encoding="utf-8") as f:
    por_nome = {p["name"]: p for p in json.load(f)["plugins"]}
faltam = [n for n in pedidos if n not in por_nome]
if faltam:
    sys.exit(
        f"erro: plugin inexistente no marketplace: {', '.join(faltam)}. "
        f"Os plugins são: {', '.join(por_nome)}"
    )
vistos = []
for nome in pedidos:
    for caminho in por_nome[nome]["skills"]:
        skill = caminho.rstrip("/").split("/")[-1]
        if skill not in vistos:
            vistos.append(skill)
print("\n".join(vistos))
PY
  )" || exit 1
fi

mkdir -p "$DEST"

count=0
for name in $nomes; do
  dir="$SRC/$name/"
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
echo "Não combine esta cópia com os plugins do marketplace labdaps, instalados na"
echo "sua conta ou habilitados no .claude/settings.json do projeto: as duas versões"
echo "carregam juntas e cada skill aparece duas vezes."
