# -*- coding: utf-8 -*-
"""
Template de gerador de figura de desenho metodologico, versao PAISAGEM em tres
colunas. Copie, renomeie e substitua o conteudo. Para a versao retrato, troque
as tres colunas por faixas horizontais e mantenha o resto.

Antes de comecar: escreva figure_data.py com os numeros do estudo, um por
constante, e a fonte de cada um no comentario (tabela, secao, linha). O layout
nunca carrega numero literal.

Ciclo de trabalho:
  python build_figure.py && bash export.sh
  abra o PNG e OLHE
  corrija, repita ate nao sobrar estouro nem sobreposicao
"""

# Outras cores da paleta em figkit: FAINT, ORANGE, GREEN, AMBER, SKY; e wrap() para quebrar texto.
from figkit import (
    Canvas, check_columns,
    MUTED, PANEL, WHITE, BLUE,
)
# from figure_data import COHORT, PREDICTORS, STRATEGIES, HYPOTHESES  # etc

# ---------------------------------------------------------------- geometria
# 1520 x 950 em 180 mm de largura deixa o corpo de 10,5 unidades em torno de
# 5,5 pt. Declare aqui a que ponto o corpo corresponde e diga isso na entrega.
W, H = 1520, 950
L, R = 24, 1496
TOP, BOTTOM = 76, 908          # todas as colunas terminam em BOTTOM

C1, C1W = 24, 486
C2, C2W = 530, 486
C3, C3W = 1036, 460

c = Canvas(W, H)
c.header(L, R,
         title="Titulo que diz o que foi feito, nao o que se espera do leitor",
         subtitle="Coorte · centros · N · desfechos · metodos",
         title_size=22, sub_size=13.5)

for x in (C1 + C1W + 20, C2 + C2W + 20):
    c.line(x, TOP, x, BOTTOM, "#E6EBF1", 1.0)

# ================================================================ coluna 1
c.band_title(C1, 84, "1 · Cohort")

c.rect(C1, 94, C1W, 48, PANEL)
c.text(C1 + 12, 114, "Fonte de dados", size=13, weight="bold")
c.text(C1 + 12, 131, "Criterio de inclusao, periodo", size=11.5, fill=MUTED)
c.arrow_down(C1 + C1W / 2, 142, 156)

c.rect(C1, 156, C1W, 46, WHITE, BLUE, 1.6)
c.text(C1 + 12, 178, "N apos os cortes", size=15, weight="bold", fill=BLUE)

# Tabela com barra de proporcao. Deixe `gap` folgado, senao o numero encosta na
# barra na linha de valor maximo, que e o erro classico deste bloco.
# c.bar_table(x=C1 + 2, y0=232, rows=ROWS, columns=[
#     dict(label="n", x=C1 + 62, w=64, gap=38, color=FAINT, vmax=NMAX,
#          fmt=lambda v: f"{v:,.0f}"),
#     dict(label="Desfecho", x=C1 + 184, w=52, gap=38, color=BLUE, vmax=100,
#          fmt=lambda v: f"{v:.1f}%"),
# ], row_h=15, size=11, right=C1 + C1W)

C1_END = BOTTOM     # ajuste os blocos ate a coluna fechar aqui de verdade

# ================================================================ coluna 2
c.band_title(C2, 84, "2 · Modelling")

# O elemento que carrega o conceito do artigo vive aqui e merece o maior
# espaco. Se a coluna sobrar branca, cresca ele antes de abrir espacamento.
# c.matrix(x=C2 + 56, y=496, n=10, cell=36, diag_color=BLUE, off_color=GREEN)

C2_END = BOTTOM

# ================================================================ coluna 3
c.band_title(C3, 84, "3 · Results")

sy = 94
# for (color, titulo, badge, corpo), min_h in zip(STRATEGIES, (76, 76, 128)):
#     h, body_end = c.card(C3, sy, C3W, color, titulo, corpo, badge=badge,
#                          body_size=10.3, line_step=14, min_h=min_h)
#     sy += h + 10

C3_END = BOTTOM

c.footer(L, R, 924,
         note="Numeros como reportados no manuscrito (indique tabela e secao).",
         credit="Rede ou grupo")
c.save("study_design_landscape.svg")

# Nenhuma coluna pode acabar antes das outras e deixar bloco branco embaixo.
check_columns(BOTTOM, {"C1": C1_END, "C2": C2_END, "C3": C3_END})
