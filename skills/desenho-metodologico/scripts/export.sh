#!/usr/bin/env bash
# Converte cada SVG da pasta em PNG de 300 dpi e em PDF vetorial, usando o Chrome
# headless que ja existe na maquina. Sem cairo, sem Inkscape, sem pip install.
#
# As dimensoes sao lidas do proprio SVG, entao mudar o tamanho da figura no
# gerador nao exige mexer aqui. A largura impressa alvo e 180 mm: 7,087 pol,
# o que a 300 dpi pede 2126 px e da um fator de escala de 2,126.
#
# Ajuste TARGET_MM se a revista pedir largura de coluna unica (geralmente 85 mm).
set -e
cd "$(dirname "$0")"

CHROME="${CHROME:-/c/Program Files/Google/Chrome/Application/chrome.exe}"
[ -x "$CHROME" ] || CHROME="$(command -v google-chrome || command -v chromium || echo "$CHROME")"

HERE="$(pwd -W 2>/dev/null || pwd)"
TARGET_MM="${TARGET_MM:-180}"
SCALE="${SCALE:-2.126}"

shopt -s nullglob
for svg in *.svg; do
  base="${svg%.svg}"
  read -r WIDTH HEIGHT < <(python - "$svg" <<'PY'
import re, sys
head = open(sys.argv[1], encoding="utf-8").read(400)
print(re.search(r'width="(\d+)"', head).group(1),
      re.search(r'height="(\d+)"', head).group(1))
PY
)
  PAGE_H=$(python -c "print(round($TARGET_MM * $HEIGHT / $WIDTH))")
  PROFILE=$(mktemp -d)

  cat > _wrap.html <<HTML
<!doctype html><meta charset="utf-8">
<style>
  @page { size: ${TARGET_MM}mm ${PAGE_H}mm; margin: 0; }
  html,body { margin:0; padding:0; background:#fff; }
  svg { display:block; width:${WIDTH}px; height:${HEIGHT}px; }
</style>
HTML
  cat "$svg" >> _wrap.html

  "$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
    --user-data-dir="$PROFILE" \
    --force-device-scale-factor=$SCALE --window-size=$WIDTH,$HEIGHT \
    --screenshot="$HERE/$base.png" "file:///$HERE/_wrap.html" 2>/dev/null

  "$CHROME" --headless --disable-gpu --no-sandbox \
    --user-data-dir="$PROFILE" --no-pdf-header-footer \
    --print-to-pdf="$HERE/$base.pdf" "file:///$HERE/_wrap.html" 2>/dev/null

  rm -rf "$PROFILE" _wrap.html
  echo "$base: ${WIDTH}x${HEIGHT} unidades, pagina ${TARGET_MM}x${PAGE_H} mm"
done

echo
echo "Agora ABRA o PNG e olhe. Estouro de texto e sobreposicao nao aparecem no codigo."
