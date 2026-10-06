#!/usr/bin/env python3
"""Achata um projeto LaTeX multi-arquivo em um unico .tex.

O problema que resolve: um manuscrito real puxa preamble, tabelas, figuras e
bibliografia de arquivos separados. Colado sozinho num editor, ele nao compila.
Este script resolve as tres dependencias que dao para resolver e e explicito sobre
a unica que nao da.

  \\input{x}         -> conteudo de x.tex, recursivamente
  \\bibliography{y}  -> o .bib embutido via filecontents, ou o .bbl ja resolvido
  \\includegraphics  -> mantido (modo keep) ou trocado por moldura (modo placeholder)

Figura binaria nao entra em arquivo de texto. Em modo placeholder o .tex compila em
diretorio vazio, com uma moldura no lugar de cada figura, preservando legenda e
label. Em modo keep, o .tex precisa das figuras ao lado.

Uso:
    python flatten_tex.py paper/manuscript.tex -o saida.tex
    python flatten_tex.py paper/manuscript.tex -o saida.tex --figures placeholder
    python flatten_tex.py paper/manuscript.tex -o saida.tex --bib bbl
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

RE_INPUT = re.compile(r"^([^%\n]*?)\\(?:input|include)\{([^}]+)\}", re.M)
RE_BIB = re.compile(r"^([^%\n]*?)\\bibliography\{([^}]+)\}", re.M)
RE_GRAPHICS = re.compile(r"\\includegraphics(\[[^\]]*\])?\{([^}]+)\}")
RE_GRAPHICSPATH = re.compile(r"^\s*\\graphicspath\{[^\n]*\}\s*$", re.M)


ESCAPES = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
           "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
           "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}


def escapa_tex(s: str) -> str:
    """Escapa os caracteres especiais para imprimir um nome de arquivo como texto."""
    return "".join(ESCAPES.get(c, c) for c in s)


def resolve(nome: str, base: Path, ext: str = ".tex") -> Path | None:
    p = (base / nome)
    for cand in (p, p.with_suffix(ext), Path(str(p) + ext)):
        if cand.is_file():
            return cand
    return None


def inline_inputs(texto: str, base: Path, vistos: set[Path], prof: int = 0) -> str:
    """Substitui \\input recursivamente. Para em ciclo e em profundidade absurda."""
    if prof > 12:
        raise RuntimeError("profundidade de \\input maior que 12; ha ciclo?")

    def troca(m: re.Match) -> str:
        prefixo, nome = m.group(1), m.group(2).strip()
        alvo = resolve(nome, base)
        if alvo is None:
            print(f"  [AVISO] \\input{{{nome}}} nao encontrado, mantido como estava")
            return m.group(0)
        if alvo.resolve() in vistos:
            raise RuntimeError(f"ciclo de \\input em {alvo}")
        vistos.add(alvo.resolve())
        corpo = alvo.read_text(encoding="utf-8")
        corpo = inline_inputs(corpo, alvo.parent, vistos, prof + 1)
        print(f"  embutido: {alvo}")
        return (f"{prefixo}\n"
                f"% ---8<--- inicio de {alvo.name} (embutido por flatten_tex.py)\n"
                f"{corpo.rstrip()}\n"
                f"% ---8<--- fim de {alvo.name}\n")

    return RE_INPUT.sub(troca, texto)


def embute_bib(texto: str, base: Path, modo: str, raiz: Path) -> str:
    """Embute a bibliografia. `filecontents` mantem o .bib; `bbl` cola o resultado."""
    def troca(m: re.Match) -> str:
        prefixo, nomes = m.group(1), m.group(2)
        if modo == "bbl":
            bbl = raiz.with_suffix(".bbl")
            if not bbl.is_file():
                print(f"  [AVISO] {bbl.name} nao existe; compile uma vez antes de usar --bib bbl")
                return m.group(0)
            print(f"  embutido: {bbl} (bibliografia ja resolvida)")
            return (f"{prefixo}\n% ---8<--- {bbl.name} embutido\n"
                    f"{bbl.read_text(encoding='utf-8').rstrip()}\n% ---8<--- fim\n")
        blocos = []
        for nome in [n.strip() for n in nomes.split(",")]:
            alvo = resolve(nome, base, ".bib")
            if alvo is None:
                print(f"  [AVISO] .bib '{nome}' nao encontrado")
                continue
            # filecontents grava o .bib ao compilar, entao o arquivo unico basta
            blocos.append(f"\\begin{{filecontents}}[overwrite,noheader]{{{alvo.name}}}\n"
                          f"{alvo.read_text(encoding='utf-8').rstrip()}\n"
                          f"\\end{{filecontents}}")
            print(f"  embutido: {alvo} (via filecontents)")
        if not blocos:
            return m.group(0)
        bibs = ",".join(Path(n.strip()).name for n in nomes.split(","))
        return f"{prefixo}\\bibliography{{{bibs}}}", blocos
    # duas passadas: filecontents precisa ficar ANTES de \documentclass
    pre_blocos: list[str] = []

    def troca_wrap(m: re.Match) -> str:
        r = troca(m)
        if isinstance(r, tuple):
            pre_blocos.extend(r[1])
            return r[0]
        return r

    texto = RE_BIB.sub(troca_wrap, texto)
    if pre_blocos:
        texto = "\n".join(pre_blocos) + "\n\n" + texto
    return texto


def trata_figuras(texto: str, modo: str) -> str:
    if modo == "keep":
        return texto

    if modo == "keep-flat":
        # Editor tipo Overleaf: o autor sobe os arquivos soltos na raiz do projeto.
        # Tira \graphicspath e o diretorio do nome, para que includegraphics resolva
        # com as figuras ao lado do .tex.
        def achata(m: re.Match) -> str:
            opts = m.group(1) or ""
            return f"\\includegraphics{opts}{{{Path(m.group(2)).name}}}"
        n = len(RE_GRAPHICS.findall(texto))
        texto = RE_GRAPHICSPATH.sub("", texto)
        texto = RE_GRAPHICS.sub(achata, texto)
        print(f"  {n} figura(s) com caminho achatado para a raiz")
        return texto

    def troca(m: re.Match) -> str:
        # Nome de figura quase sempre tem _, que em modo texto e subscrito matematico
        # e derruba a compilacao com "Missing $ inserted". Escapar antes de imprimir.
        nome = escapa_tex(m.group(2))
        return ("\\fbox{\\begin{minipage}[c][0.22\\textheight][c]{0.9\\textwidth}"
                "\\centering\\ttfamily\\small "
                f"[figura: {nome}]\\\\[0.4em]"
                "\\rmfamily\\footnotesize (arquivo nao incluido neste .tex unico)"
                "\\end{minipage}}")

    texto = RE_GRAPHICSPATH.sub("", texto)
    n = len(RE_GRAPHICS.findall(texto))
    texto = RE_GRAPHICS.sub(troca, texto)
    print(f"  {n} figura(s) trocada(s) por moldura")
    return texto


def main() -> int:
    ap = argparse.ArgumentParser(description="Achata um projeto LaTeX num unico .tex")
    ap.add_argument("entrada")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--figures", choices=["keep", "keep-flat", "placeholder"], default="keep",
                    help="keep: mantem caminhos. keep-flat: figuras na raiz (editor online). "
                         "placeholder: compila sozinho, sem figura")
    ap.add_argument("--bib", choices=["filecontents", "bbl", "none"], default="filecontents")
    args = ap.parse_args()

    raiz = Path(args.entrada).resolve()
    if not raiz.is_file():
        raise SystemExit(f"[ERRO] nao encontrei {raiz}")
    base = raiz.parent
    print(f"Achatando {raiz.name}")

    texto = raiz.read_text(encoding="utf-8")
    texto = inline_inputs(texto, base, {raiz})
    if args.bib != "none":
        texto = embute_bib(texto, base, args.bib, raiz)
    texto = trata_figuras(texto, args.figures)

    cab = ("% Arquivo unico gerado por flatten_tex.py a partir de "
           f"{raiz.name}.\n"
           "% Nao editar aqui se o projeto multi-arquivo ainda for a fonte da verdade:\n"
           "% edite os originais e gere de novo.\n")
    if args.figures == "placeholder":
        cab += "% Figuras trocadas por moldura; este arquivo compila em diretorio vazio.\n"
    else:
        cab += "% As figuras precisam estar ao lado deste arquivo.\n"

    saida = Path(args.output)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(cab + texto, encoding="utf-8")
    print(f"\n  {saida}  ({len(cab + texto):,} bytes, {len((cab + texto).splitlines()):,} linhas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
