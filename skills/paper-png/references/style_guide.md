# Style Guide: Figuras Científicas para Papers

Referência canônica de estilo para a skill `/paper-png`.
Lida apenas quando a skill for executada, não precisa ficar em contexto sempre.

---

## Princípios editoriais (Elsevier / JMLR / NeurIPS)

- **Paleta neutra**, tons pastel <5% saturação + no máximo UM acento sóbrio
- **Sem gradientes, sombras ou hachuras**
- **Bordas finas e uniformes**, `line width=0.55pt` equivalente (1-2px em PIL)
- **Cantos ligeiramente arredondados**, `radius=10-14px` em 1890px de largura
- **Tipografia serifada/monoespaçada**, DejaVu para PIL, mathptmx/Times para TikZ
- **Matemática inline**, usar Unicode diretamente: `∀`, `∈`, `∃`, `←`, `≤`, `η`, `ŷ`, `∩`

---

## Paleta de cores (valores RGB)

### Tons neutros (preenchimento de blocos)
```python
NEUTRALFILL = (244, 245, 248, 255)   # cinza 95%, blocos genéricos
```

### Fases / categorias (5-8% saturação máxima)
```python
PHASE_COLORS = {
    'init':      {'bg': (240,234,252,255), 'bd': (172,140,218,255), 'tx': (82,36,152,255)},   # lilás, inicialização
    'loop':      {'bg': (255,251,240,255), 'bd': (228,182,90,255),  'tx': (162,96,0,255)},    # âmbar, loop iterativo
    'output':    {'bg': (234,248,240,255), 'bd': (115,188,145,255), 'tx': (18,105,52,255)},   # verde, saída/resultado
    'audit':     {'bg': (237,230,252,255), 'bd': (170,146,218,255), 'tx': (72,28,144,255)},   # lilás, auditoria/análise
    'decision':  {'bg': (255,244,218,255), 'bd': (232,168,56,255),  'tx': (112,68,0,255)},    # creme, decisão
    'correction':{'bg': (252,232,238,255), 'bd': (232,150,174,255), 'tx': (158,26,74,255)},   # rosé, correção/ajuste
    'model':     {'bg': (244,245,248,255), 'bd': (192,198,214,255), 'tx': (65,78,98,255)},    # cinza, modelo/entrada
    'data':      {'bg': (232,240,252,255), 'bd': (135,178,244,255), 'tx': (26,85,182,255)},   # azul, dados/predições
}
```

### Acento único (usar em no máximo 1 elemento por figura)
```python
ACCENT_LOOP = (178, 52, 48, 255)    # bordô, arco de retorno / loop
ACCENT_NAVY = (30, 58, 138, 255)    # navy, destaque alternativo
```

### Texto e setas
```python
ARROW_COLOR  = (148, 162, 180, 255)   # cinza médio, setas principais
GRAY_TEXT    = (65, 78, 98, 255)      # cinza escuro, texto de cards neutros
LGRAY_TEXT   = (138, 152, 172, 255)   # cinza claro, notas, subtítulos
MONO_TEXT    = (56, 68, 86, 255)      # cinza mono, fórmulas
BLUE_LABEL   = (50, 122, 205, 255)    # azul, labels de setas (ex: ŷ(0))
```

### Chips de subgrupos (para figuras com taxonomia)
```python
CHIP_COLORS = {
    'pink':   {'bg':(252,232,238,255), 'bd':(226,150,170,255), 'tx':(138,22,66,255)},
    'blue':   {'bg':(232,240,252,255), 'bd':(135,178,244,255), 'tx':(22,72,164,255)},
    'brown':  {'bg':(245,237,224,255), 'bd':(192,158,110,255), 'tx':(96,54,10,255)},
    'orange': {'bg':(255,242,216,255), 'bd':(228,178,95,255),  'tx':(110,52,0,255)},
    'teal':   {'bg':(222,245,240,255), 'bd':(116,194,182,255), 'tx':(8,70,62,255)},
    'green':  {'bg':(229,245,236,255), 'bd':(115,196,146,255), 'tx':(12,90,38,255)},
    'purple': {'bg':(237,230,252,255), 'bd':(170,146,218,255), 'tx':(64,22,134,255)},
}
```

---

## Tipografia (em canvas de 1890px de largura)

| Elemento | Fonte | Tamanho | Estilo |
|---|---|---|---|
| Label de fase (pill) | DejaVu Sans Bold | 29px | MAIÚSCULAS |
| Título de card | DejaVu Sans Bold | 30px | Normal |
| Fórmula matemática | DejaVu Sans Mono | 28px | Normal |
| Nota/subtítulo | DejaVu Sans Oblique | 23px | Itálico |
| Badge de etapa (2a, 2b...) | DejaVu Sans Bold | 22px | Branco sobre círculo |
| Label de seta | DejaVu Sans Mono | 20px | Normal |
| Rail de loop | DejaVu Sans Mono Bold | 19px | Normal |
| Chip de categoria | DejaVu Sans Bold | 23-24px | Normal |
| Cabeçalho de seção (SG) | DejaVu Sans Bold | 28-29px | Normal |

**Escala para outras larguras de canvas:**
- 1600px → multiplicar por 0.85
- 2200px → multiplicar por 1.16

---

## Dimensões de canvas

### Largura padrão
```python
W = 1890   # px → 300 DPI → 16 cm (margem Elsevier single-column)
```

### Cálculo dinâmico de altura
A altura deve ser **calculada** com base no conteúdo, não fixada.
Estrutura de cálculo:

```python
GAP   = 52    # espaço entre blocos de fase
PAD   = 100   # margem horizontal (deixa espaço para rail de loop se houver)
IPAD  = 26    # padding interno dos cards

# Altura de cada bloco = PILL_H + IPAD + soma(cards internos + gaps) + IPAD
PILL_H = 52   # espaço da pílula de fase acima do bloco

# Altura total = GAP_topo + Σ(fases) + Σ(GAPs entre fases) + GAP_base
TOTAL_H = GAP + ph1_h + GAP + ph2_h + ... + GAP + sg_h + 48
```

### Proporções alvo por tipo de figura
| Tipo | Proporção W:H |
|---|---|
| Fluxograma simples (3 fases) | 1 : 1.1-1.3 |
| Fluxograma com loop (algoritmo) | 1 : 1.1-1.2 |
| Diagrama de arquitetura | 1 : 0.8-1.1 (pode ser paisagem) |
| Figura de resultado (tabela visual) | 1 : 0.6-0.9 |
| Diagrama conceitual (taxonomia) | 1 : 0.7-1.0 |

---

## Funções auxiliares Python (copiar direto)

```python
from PIL import Image, ImageDraw, ImageFont

SANS   = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SANS_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SANS_I = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'
MONO   = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
MONO_B = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'

def F(size, bold=False, mono=False, italic=False):
    if mono:   return ImageFont.truetype(MONO_B if bold else MONO, size)
    if italic: return ImageFont.truetype(SANS_I, size)
    return ImageFont.truetype(SANS_B if bold else SANS, size)

def TW(draw, text, fnt):
    """Mede largura e altura do texto com precisão."""
    bb = draw.textbbox((0,0), text, font=fnt)
    return bb[2]-bb[0], bb[3]-bb[1]

def TC(draw, text, cx, cy, fnt, color):
    """Texto centrado em (cx, cy)."""
    w, h = TW(draw, text, fnt)
    draw.text((cx-w//2, cy-h//2), text, font=fnt, fill=color)

def TL(draw, text, x, cy, fnt, color):
    """Texto alinhado à esquerda, centrado verticalmente em cy."""
    _, h = TW(draw, text, fnt)
    draw.text((x, cy-h//2), text, font=fnt, fill=color)

def TR(draw, text, x, cy, fnt, color):
    """Texto alinhado à direita terminando em x, centrado verticalmente em cy."""
    w, h = TW(draw, text, fnt)
    draw.text((x-w, cy-h//2), text, font=fnt, fill=color)

def rr(draw, xy, r, fill, outline, lw=3):
    """Rounded rectangle."""
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=lw)

def arr_v(draw, x, y0, y1, col, lw=3, hs=12):
    """Seta vertical de y0 para y1."""
    draw.line([(x,y0),(x,y1-hs)], fill=col, width=lw)
    draw.polygon([(x-hs//2,y1-hs),(x+hs//2,y1-hs),(x,y1)], fill=col)

def arr_h(draw, x0, x1, y, col, lw=3, hs=12):
    """Seta horizontal de x0 para x1."""
    draw.line([(x0,y),(x1-hs,y)], fill=col, width=lw)
    draw.polygon([(x1-hs,y-hs//2),(x1-hs,y+hs//2),(x1,y)], fill=col)

def badge(draw, cx, cy, label, bg, r=18):
    """Círculo numerado (badge de etapa)."""
    draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill=bg)
    TC(draw, label, cx, cy, F(22,bold=True), (255,255,255,255))

def chip(draw, text, x, y, bg, bd, tx, fnt=None):
    """Chip colorido (para categorias/subgrupos)."""
    if fnt is None: fnt = F(23, bold=True)
    w, h = TW(draw, text, fnt)
    px, py = 18, 9
    W_ = w+2*px; H_ = h+2*py
    rr(draw, [x,y,x+W_,y+H_], 8, bg, bd, 2)
    draw.text((x+px, y+py), text, font=fnt, fill=tx)
    return W_, H_

def draw_phase_block(draw, x0, y, x1, total_h, bg, bd, pill_h=52):
    """
    Desenha bloco de fase com pílula flutuando na borda superior.
    Retorna y do topo do bloco (= y + pill_h).
    """
    block_top = y + pill_h
    draw.rounded_rectangle([x0, block_top, x1, y+total_h], radius=18, fill=bg, outline=bd, width=3)
    return block_top

def draw_pill(draw, img_draw, cx, y, pill_h, label, sub, bg, bd, tx):
    """
    Desenha pílula de fase SOBRE a borda do bloco.
    Chamar APÓS draw_phase_block.
    sub: subtítulo abaixo da pílula (ou None)
    """
    lw, _ = TW(img_draw, label, F(29, bold=True))
    pw = lw + 48
    ph_half = pill_h//2 - 4
    pill_cy = y + pill_h//2
    # Apaga a borda atrás da pílula
    img_draw.rectangle([cx-pw//2-1, pill_cy-ph_half-3,
                         cx+pw//2+1, pill_cy+ph_half+3], fill=bg)
    # Pílula
    img_draw.rounded_rectangle([cx-pw//2, pill_cy-ph_half,
                                  cx+pw//2, pill_cy+ph_half],
                                 radius=ph_half, fill=bg, outline=bd, width=2)
    TC(img_draw, label, cx, pill_cy, F(29,bold=True), tx)
    if sub:
        TC(img_draw, sub, cx, pill_cy+ph_half+16, F(22,italic=True), (138,152,172,255))
```

---

## Layout de pill de fase

**REGRA CRÍTICA:** sempre desenhar o bloco de fase PRIMEIRO, depois a pílula POR CIMA.

```python
# ✅ CORRETO
block_top = draw_phase_block(draw, PAD, y, PAD+CW, PH_H, bg, bd)
draw_pill(draw, draw, CX, y, PILL_H, "FASE 1", "Inicialização", bg, bd, tx)

# ❌ ERRADO: o bloco vai cobrir a pílula
draw_pill(...)
draw_phase_block(...)
```

---

## Regras de layout para setas de loop

Quando um fluxograma tem arco de retorno (loop):

1. `PAD = 100-120` (margem horizontal maior para o rail caber)
2. `RAIL_X = 52-60` (x do rail, sempre > 0, sempre < PAD)
3. Gap entre RAIL_X e `AX0 = PAD+IPAD` deve ser ≥ 80px para o label `t←t+1` caber
4. Label do rail: fonte mono 19px bold, ~82px de largura
5. O rail conecta: borda esquerda do bloco de decisão → RAIL_X → sobe → borda esquerda do bloco de auditoria
6. Labels "Sim" e "Não" dentro do bloco de decisão, com inset de 68px das bordas internas

---

## Checklist de validação antes de entregar

Leia a imagem com a ferramenta Read e verifique cada item:

```
[ ] Proporção W:H adequada ao tipo (sem espaço vazio > 10% do canvas)
[ ] Fundo transparente, modo RGBA, não RGB
[ ] Nenhum texto cortado na borda do canvas
[ ] Nenhum □ (glifo ausente), substituir por ASCII se aparecer
[ ] Pílulas de fase flutuando sobre bordas (não cortadas)
[ ] Labels de setas visíveis e dentro de seus blocos
[ ] Rail de loop (se houver) com label legível dentro do canvas
[ ] Sim/Não dentro do bloco de decisão (inset 68px)
[ ] S* ou outros labels entre cards dentro do gap (não saindo pelas bordas)
[ ] DPI = 300 confirmado no save
```
