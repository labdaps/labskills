# -*- coding: utf-8 -*-
"""
figkit: primitivas para figura de desenho metodologico em SVG puro.

Sem dependencia externa. A saida e um SVG vetorial que o export.sh converte em
PNG de 300 dpi e em PDF usando o Chrome headless.

Copie este arquivo para a pasta de figuras do projeto e escreva o layout em cima
dele. Os numeros do estudo ficam num modulo separado (figure_data.py), nunca
aqui e nunca embutidos no layout: e isso que impede a versao retrato e a
paisagem de divergirem num valor.
"""

import io
import os

# ---------------------------------------------------------------- paleta
# Okabe-Ito, segura para as formas comuns de daltonismo. As luminancias sao
# distintas o bastante para a figura sobreviver a impressao em preto e branco,
# mas nunca dependa so do matiz: acrescente rotulo, posicao ou traco.
INK    = "#15191F"
MUTED  = "#5C6672"
FAINT  = "#8A94A0"
RULE   = "#D3DAE2"
PANEL  = "#F6F8FB"
PANEL2 = "#EDF1F6"
WHITE  = "#FFFFFF"

BLUE   = "#0072B2"   # neutro informativo, ou a condicao de referencia
ORANGE = "#D55E00"   # o que falhou, ou a condicao que degrada
GREEN  = "#009E73"   # o que funcionou
AMBER  = "#E69F00"   # resultado fraco ou ambiguo
SKY    = "#56B4E9"
TEAL   = "#3D7FA6"
PURPLE = "#CC79A7"

FONT = "Arial, Helvetica, 'Liberation Sans', sans-serif"

# Corpo de texto em unidades, para uma tela de 1000 de largura impressa em
# 180 mm. Ver a tabela de tipografia no SKILL.md antes de descer disso.
PT5, PT6, PT7 = 9.8, 11.8, 13.7


def wrap(s, width_units, size, pad=0.0, ratio=0.53):
    """Quebra o texto pela largura disponivel em unidades do SVG.

    A razao 0,53 aproxima a largura media do glifo da Arial em relacao ao corpo.
    E conservadora de proposito: erra para a linha curta, nao para o estouro.
    Mesmo assim, confira no PNG renderizado, porque estimativa e estimativa.
    """
    limit = max(1, int((width_units - pad) / (size * ratio)))
    words, lines, cur = s.split(" "), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > limit:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


def check_columns(bottom, ends, tol=12):
    """Falha se alguma coluna acabar antes das outras e deixar bloco branco.

    Chame no fim do gerador. Espaco vazio numa figura de artigo le como conteudo
    faltando, entao isso e erro, nao aviso.
    """
    for label, end in ends.items():
        folga = bottom - end
        print(f"  {label} termina em {end:.0f}, folga {folga:.0f}")
        assert abs(folga) <= tol, (
            f"{label} deixa {folga:.0f} unidades em branco. Redistribua conteudo "
            f"entre as colunas ou aumente o elemento que carrega o conceito do "
            f"artigo, em vez de so abrir espacamento entre blocos.")


class Canvas(object):
    def __init__(self, width, height):
        self.w, self.h = width, height
        self.out = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" font-family="{FONT}">',
            f'<rect width="{width}" height="{height}" fill="{WHITE}"/>',
        ]

    # ----------------------------------------------------------- primitivas
    def add(self, s):
        self.out.append(s)

    @staticmethod
    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def rect(self, x, y, w, h, fill=WHITE, stroke=RULE, sw=1.0, r=4, dash=None, op=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' fill-opacity="{op}"' if op is not None else ""
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ' stroke="none"'
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                 f'rx="{r}" fill="{fill}"{o}{st}{d}/>')

    def circle(self, cx, cy, r, fill):
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"/>')

    def text(self, x, y, s, size=13, fill=INK, weight="normal", anchor="start",
             spacing=None, style=None):
        ls = f' letter-spacing="{spacing}"' if spacing else ""
        fs = f' font-style="{style}"' if style else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
                 f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{ls}{fs}>'
                 f'{self.esc(s)}</text>')

    def lines(self, x, y, items, size=10.3, fill=MUTED, step=None):
        """Escreve uma lista de linhas e devolve o y da ultima."""
        step = step if step is not None else size + 1.2
        for i, ln in enumerate(items):
            self.text(x, y + i * step, ln, size=size, fill=fill)
        return y + max(0, len(items) - 1) * step

    def line(self, x1, y1, x2, y2, stroke=RULE, sw=1.0):
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{stroke}" stroke-width="{sw}"/>')

    def arrow_down(self, x, y1, y2, color=FAINT, sw=1.6):
        self.line(x, y1, x, y2 - 5, color, sw)
        self.add(f'<path d="M {x-4:.1f} {y2-5.5:.1f} L {x+4:.1f} {y2-5.5:.1f} '
                 f'L {x:.1f} {y2:.1f} Z" fill="{color}"/>')

    def arrow_right(self, x1, x2, y, color=FAINT, sw=1.6):
        self.line(x1, y, x2 - 5, y, color, sw)
        self.add(f'<path d="M {x2-5.5:.1f} {y-4:.1f} L {x2-5.5:.1f} {y+4:.1f} '
                 f'L {x2:.1f} {y:.1f} Z" fill="{color}"/>')

    def rotated(self, x, y, s, size=10.5, fill=MUTED, weight="bold"):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
                 f'fill="{fill}" text-anchor="middle" font-weight="{weight}" '
                 f'transform="rotate(-90 {x:.1f} {y:.1f})">{self.esc(s)}</text>')

    # ------------------------------------------------------------- rotulos
    def band_title(self, x, y, label, color=MUTED):
        """Rotulo de etapa: barra curta colorida mais o nome em versalete."""
        self.add(f'<rect x="{x:.1f}" y="{y-9:.1f}" width="3.5" height="11" rx="1.5" '
                 f'fill="{color}"/>')
        self.text(x + 9, y, label.upper(), size=11.5, fill=color, weight="bold",
                  spacing="1.3")

    @staticmethod
    def pill_w(label, size, pad=7):
        return len(label) * size * 0.58 + pad * 2

    def pill(self, x, y, label, fill, size=10.5, h=15):
        w = self.pill_w(label, size)
        self.rect(x, y, w, h, fill=fill, stroke=None, r=h / 2.0)
        self.text(x + w / 2.0, y + h - 4.6, label, size=size, fill=WHITE,
                  weight="bold", anchor="middle")
        return w

    def header(self, left, right, title, subtitle, title_size=20.5, sub_size=13,
               rule_y=62):
        self.text(left, 30, title, size=title_size, weight="bold")
        self.text(left, 50, subtitle, size=sub_size, fill=MUTED)
        self.line(left, rule_y, right, rule_y, RULE, 1.2)

    def footer(self, left, right, y, note, credit=""):
        self.line(left, y, right, y, RULE, 0.8)
        self.text(left, y + 14, note, size=10, fill=FAINT)
        if credit:
            self.text(right, y + 14, credit, size=10, fill=FAINT, anchor="end")

    # -------------------------------------------------------------- blocos
    def bar_table(self, x, y0, rows, columns, row_h=14, size=11, right=None):
        """Tabela compacta com barra de proporcao atras de cada numero.

        `rows`: lista de (rotulo, [valor1, valor2, ...]).
        `columns`: lista de dicts com as chaves
            label  cabecalho da coluna
            x      onde a trilha comeca
            w      largura da trilha
            gap    distancia da trilha ate a borda direita do numero
            color  cor do preenchimento
            vmax   valor que corresponde a trilha cheia
            fmt    funcao que formata o valor para texto

        Devolve o y da ultima linha. Deixe `gap` folgado o bastante para o numero
        nao encostar na barra quando o valor for o maximo da escala, e deixe o
        cabecalho do rotulo longe o bastante do primeiro cabecalho de coluna:
        esses dois sao os erros que mais aparecem no render.
        """
        self.text(x, y0, "", size=size)
        for col in columns:
            self.text(col["x"], y0, col["label"], size=size - 0.5, fill=FAINT,
                      weight="bold")
        if right:
            self.line(x - 2, y0 + 4, right, y0 + 4, RULE, 0.8)

        y = y0
        for i, (label, values) in enumerate(rows):
            y = y0 + 18 + i * row_h
            self.text(x, y, label, size=size, weight="bold")
            for col, val in zip(columns, values):
                self.rect(col["x"], y - 7.5, col["w"], 8, PANEL2, None, r=2)
                self.rect(col["x"], y - 7.5, col["w"] * val / col["vmax"], 8,
                          col["color"], None, r=2)
                self.text(col["x"] + col["w"] + col["gap"], y, col["fmt"](val),
                          size=size - 0.5, anchor="end", fill=MUTED)
        return y

    def card(self, x, y, w, color, title, body, badge=None, body_size=10.5,
             line_step=None, extra_h=0.0, min_h=0.0):
        """Cartao com barra colorida a esquerda, titulo, corpo e etiqueta.

        Devolve (altura total, y da ultima linha do corpo). `extra_h` reserva
        espaco abaixo do corpo para um elemento grafico. `min_h` forca a altura
        minima, que e como se fecha uma coluna sem deixar sobra branca.

        A cor carrega significado: verde para o que funcionou, laranja para o
        que falhou, ambar para o fraco, azul para o neutro. Nao use laranja num
        resultado apenas nuancado, porque o leitor le fracasso onde o autor tem
        achado.
        """
        step = line_step if line_step is not None else body_size + 0.7
        body_lines = wrap(body, w - 32, body_size) if isinstance(body, str) else body
        body_end = 33 + len(body_lines) * step
        h = max(body_end + 6 + extra_h, min_h)
        self.rect(x, y, w, h, WHITE, RULE, 1.0)
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="4" height="{h:.1f}" '
                 f'fill="{color}" rx="2"/>')
        self.text(x + 16, y + 18, title, size=13, weight="bold", fill=color)
        if badge:
            self.pill(x + w - 12 - self.pill_w(badge, 10), y + 7, badge, color,
                      size=10, h=15)
        self.lines(x + 16, y + 33, body_lines, size=body_size, step=step)
        return h, y + body_end

    def matrix(self, x, y, n, cell, diag_color, off_color, off_op=0.28, gap=3, r=2):
        """Matriz n por n com a diagonal destacada.

        Serve para desenho fonte por alvo, comparacao par a par, ou qualquer
        grade em que a diagonal signifique alguma coisa. Costuma ser o elemento
        que carrega o conceito do artigo: de espaco a ele antes de dar espaco a
        texto, e use ele para fechar a folga de uma coluna curta.
        """
        for i in range(n):
            for j in range(n):
                col = diag_color if i == j else off_color
                op = None if i == j else off_op
                self.rect(x + j * cell, y + i * cell, cell - gap, cell - gap,
                          col, None, r=r, op=op)
        return x + n * cell, y + n * cell

    def tree(self, x, y, size, fill):
        """Arvore de decisao estilizada, para ilustrar ensemble ou boosting."""
        s = size
        self.add(f'<path d="M {x:.1f} {y:.1f} L {x - s*0.45:.1f} {y + s*0.8:.1f} '
                 f'L {x + s*0.45:.1f} {y + s*0.8:.1f} Z" fill="{fill}"/>')
        self.add(f'<rect x="{x - s*0.06:.1f}" y="{y + s*0.8:.1f}" '
                 f'width="{s*0.12:.1f}" height="{s*0.2:.1f}" fill="{fill}"/>')

    def tree_strip(self, x, y, n_first, n_second, color_first, color_second,
                   size=11, gap=13):
        """Dois grupos de arvores separados por um mais.

        Le como "modelo existente mais o que foi acrescentado", que e a forma
        mais direta de explicar continuacao de boosting ou fine-tuning sem
        gastar um paragrafo.
        """
        for i in range(n_first):
            self.tree(x + i * gap, y, size, color_first)
        self.text(x + n_first * gap - 4, y + 10, "+", size=15, fill=FAINT,
                  weight="bold")
        for i in range(n_second):
            self.tree(x + (n_first + 1) * gap + 5 + i * gap, y, size, color_second)
        return x + (n_first + n_second + 1) * gap + 14

    # --------------------------------------------------------------- saida
    def save(self, filename, outdir=None):
        self.add("</svg>")
        outdir = outdir or os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(outdir, filename)
        with io.open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.out))
        print("escrito:", filename, os.path.getsize(path), "bytes")
        return path
