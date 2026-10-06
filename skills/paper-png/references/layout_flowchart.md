# Layout: Fluxograma: /paper-png

Referência de layout para figuras do tipo **fluxograma** (pipeline, algoritmo, processo sequencial).

Ler quando o tipo identificado for fluxograma. Ver `style_guide.md` para paleta e funções.

---

## Quando usar este layout

- Pipeline com fases sequenciais (Fase 1 → Fase 2 → Fase 3)
- Algoritmo iterativo com loop de retorno
- Processo com ponto de decisão (sim/não)
- Fluxo de dados com etapas numeradas

---

## Estrutura vertical padrão

```
[GAP topo]

[FASE 1, Inicialização]
  pílula flutuante na borda superior
  cards lado a lado (modelo → predições)
  seta horizontal entre cards com label

[GAP + seta vertical]

[FASE 2, Loop (se houver)]
  pílula flutuante
  bloco de auditoria (largura total)
  ↓
  bloco de decisão (losango visual via bloco arredondado)
  sim ↓    não →
  bloco pior + bloco ajuste (lado a lado)
  loop rail (esquerda) com label t←t+1

[GAP + seta vertical]

[FASE 3, Saída]
  pílula flutuante
  card de resultado

[GAP]

[SUBGRUPOS, se o paper tiver taxonomia de grupos]
  tabela 2 colunas com chips coloridos
```

---

## Dimensões recomendadas

```python
W        = 1890   # px
PAD      = 116    # margem horizontal (maior quando há loop rail)
IPAD     = 26     # padding interno
IPAD_MID = 40     # gap entre cards 2c e 2d (maior para label S* caber)
PILL_H   = 52     # altura do espaço da pílula
GAP      = 52     # gap entre blocos de fase

# Alturas de cards
H_CARD1  = 250    # cards da fase 1
H_AUD    = 210    # bloco de auditoria
H_BOT    = 220    # linha 2c + 2d
H_DEC    = 200    # bloco de decisão (maior para Sim/Não caber)
H_P3     = 190    # fase 3
```

---

## Código estrutural (esqueleto)

```python
# ═══ FASE 1 ══════════════════════════════
y = GAP
block_top = draw_phase_block(draw, PAD, y, PAD+CW, PH1_H, P['p1_bg'], P['p1_bd'])
draw_pill(draw, draw, CX, y, PILL_H, "FASE 1", "Inicialização", ...)

# cards lado a lado
HALF = (CW - 3*IPAD)//2
C1X0 = PAD+IPAD; C1X1 = C1X0+HALF
C2X0 = C1X1+IPAD; C2X1 = C2X0+HALF
CY0  = block_top + IPAD
rr(draw, [C1X0, CY0, C1X1, CY0+H_CARD1], 12, ...)
rr(draw, [C2X0, CY0, C2X1, CY0+H_CARD1], 12, ...)
arr_h(draw, C1X1, C2X0, CY0+H_CARD1//2, ARROW_COLOR)

y += PH1_H
arr_v(draw, CX, y, y+GAP, ARROW_COLOR)
y += GAP

# ═══ FASE 2 ══════════════════════════════
PH2_Y0 = y
block_top2 = draw_phase_block(draw, PAD, y, PAD+CW, PH2_H, ...)

# pílula: desenhar DEPOIS do bloco
draw_pill(draw, draw, CX, y, PILL_H, "FASE 2: Loop iterativo", None, ...)

AX0 = PAD+IPAD; AX1 = PAD+CW-IPAD; ACX = (AX0+AX1)//2
AY0 = block_top2 + IPAD; AY1 = AY0 + H_AUD
badge(draw, AX0+32, AY0+H_AUD//2, "2a", (102,52,216,255))
rr(draw, [AX0, AY0, AX1, AY1], 12, ...)
TC(draw, "Auditoria: ...", ACX, AY0+48, F(30,bold=True), ...)

# 2c + 2d
BY0 = AY1+48; BY1 = BY0+H_BOT
HALF_BOT = (CW - 2*IPAD - IPAD_MID)//2
B2CX0 = PAD+IPAD;        B2CX1 = B2CX0+HALF_BOT
B2DX0 = B2CX1+IPAD_MID;  B2DX1 = PAD+CW-IPAD
arr_v(draw, (B2CX0+B2CX1)//2, AY1, BY0, ARROW_COLOR)

# S* pill entre 2c e 2d
AMY = BY0+H_BOT//2
arr_h(draw, B2CX1, B2DX0, AMY, ARROW_COLOR)
pcx = (B2CX1+B2DX0)//2
LF = F(22,mono=True)
lw_, lh_ = TW(draw, "S*", LF); LP=8
rr(draw, [pcx-lw_//2-LP, AMY-lh_-LP-10, pcx+lw_//2+LP, AMY-10], 6, ...)
TC(draw, "S*", pcx, AMY-lh_//2-LP-10, LF, ...)

# 2b decisão
DX0=PAD+IPAD; DX1=PAD+CW-IPAD; DCX=(DX0+DX1)//2
DY0=BY1+48; DY1=DY0+H_DEC; DCY=(DY0+DY1)//2
rr(draw, [DX0,DY0,DX1,DY1], 12, ...)

# Sim / Não com inset de 68px
SIM_TXT = "↑ Sim: t ← t+1,  volta a 2a"
NAO_TXT = "Não: saída →"
sw, sh = TW(draw, SIM_TXT, F(25,bold=True))
nw, nh = TW(draw, NAO_TXT, F(25,bold=True))
ly = DY1 - 54 - sh//2
draw.text((DX0+68, ly), SIM_TXT, font=F(25,bold=True), fill=LOOP_COLOR)
draw.text((DX1-68-nw, ly), NAO_TXT, font=F(25,bold=True), fill=OUT_COLOR)

# Loop rail
RAIL = 52
LRX = RAIL; LY_B = DCY; LY_T = AY0+H_AUD//2
draw.line([(DX0,LY_B),(LRX,LY_B)], fill=LOOP_COLOR, width=3)
draw.line([(LRX,LY_B),(LRX,LY_T)], fill=LOOP_COLOR, width=3)
draw.line([(LRX,LY_T),(AX0,LY_T)], fill=LOOP_COLOR, width=3)
draw.polygon([(AX0-13,LY_T-7),(AX0-13,LY_T+7),(AX0,LY_T)], fill=LOOP_COLOR)
LL_TXT = "t←t+1"; ll_w, ll_h = TW(draw, LL_TXT, F(19,mono=True,bold=True))
draw.text((LRX+5, (LY_B+LY_T)//2-ll_h//2), LL_TXT, font=F(19,mono=True,bold=True), fill=LOOP_COLOR)
```

---

## Adaptações por conteúdo do paper

### Paper sem loop de retorno (pipeline linear)
- Remover rail e bloco de decisão
- PAD pode ser 80 (sem necessidade de rail)
- Usar setas verticais simples entre todos os blocos

### Paper com mais de 3 fases
- Adicionar fases extras seguindo o mesmo padrão
- Aumentar H total proporcionalmente
- Manter GAP=52 entre todas as fases

### Paper com 2 caminhos paralelos (ex: treino/teste)
- Usar dois cards lado a lado em vez de sequência vertical
- Conectar com seta de merge abaixo
- Labels "Treino" / "Teste" ou equivalente nos cards

### Paper sem subgrupos (sem bloco C)
- Omitir completamente a seção de subgrupos
- H total = GAP + PH1 + GAP + PH2 + GAP + PH3 + 48

---

## Notas sobre o bloco de decisão

O losango real do TikZ é difícil no PIL. A abordagem aprovada:
- Usar `rounded_rectangle` com raio menor (12px) para o bloco de decisão
- Usar `fill=decfill` (creme) para distinguir visualmente
- Badge "2b" no canto superior esquerdo
- Pergunta de decisão centralizada no topo do bloco
- "Sim" (vermelho) e "Não" (verde) na parte inferior do bloco,
  medidos com `TW()` e posicionados com inset fixo de 68px das bordas internas
