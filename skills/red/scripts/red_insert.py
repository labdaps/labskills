#!/usr/bin/env python3
"""
red_insert.py: insere blocos de sugestão em vermelho num .docx JÁ EXISTENTE,
preservando estilos, numeração, cabeçalhos e rodapés do original.

Uso:
    python red_insert.py entrada.docx saida.docx --json sugestoes.json

Formato do JSON (lista de inserções):

[
  {
    "anchor": "trecho literal e único que já existe no documento",
    "position": "after",                  // "after" (padrão) ou "before"
    "title": "Sugestões de inclusão - 1.1",
    "bullets": ["primeira sugestão", "segunda sugestão"]
  },
  {
    "anchor": "outro trecho do documento",
    "note": "Sugestao: fechar a definicao da metrica antes do piloto."
  },
  {
    "at": "end",                          // bloco no fim do documento
    "title": "Observacoes transversais",
    "bullets": ["..."]
  }
]

Regras:
- O ancora precisa casar com EXATAMENTE UM paragrafo. Se casar com zero ou com
  varios, o script aborta e lista os candidatos: aumente o trecho ate ficar unico.
- Nada do texto original e alterado. As insercoes sao sempre aditivas.
"""

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
RED = "C00000"

PARA_RE = re.compile(r"<w:p[ >].*?</w:p>|<w:p/>", re.DOTALL)
TEXT_RE = re.compile(r"<w:t[^>]*>(.*?)</w:t>", re.DOTALL)


def para_text(p_xml: str) -> str:
    """Texto visivel de um paragrafo, juntando todos os runs."""
    return "".join(TEXT_RE.findall(p_xml))


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def run(text: str, bold: bool = False) -> str:
    rpr = f'<w:rPr>{"<w:b/>" if bold else ""}<w:color w:val="{RED}"/></w:rPr>'
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def title_para(text: str) -> str:
    """Titulo do bloco: vermelho, negrito, com barra lateral vermelha."""
    ppr = (
        "<w:pPr>"
        '<w:pBdr><w:left w:val="single" w:sz="12" w:space="6" w:color="' + RED + '"/></w:pBdr>'
        '<w:spacing w:before="160" w:after="80"/>'
        '<w:ind w:left="170"/>'
        "</w:pPr>"
    )
    return f"<w:p>{ppr}{run(text, bold=True)}</w:p>"


def bullet_para(text: str) -> str:
    """Item do bloco. Usa marcador literal + recuo pendente de proposito: injetar
    numbering.xml num documento de terceiro e fragil e pode quebrar as listas
    existentes."""
    ppr = (
        "<w:pPr>"
        '<w:spacing w:after="60"/>'
        '<w:ind w:left="510" w:hanging="170"/>'
        "</w:pPr>"
    )
    return f"<w:p>{ppr}{run(chr(0x2022) + '  ' + text)}</w:p>"


def note_para(text: str) -> str:
    ppr = '<w:pPr><w:spacing w:before="60" w:after="80"/></w:pPr>'
    return f"<w:p>{ppr}{run(text)}</w:p>"


def build_block(item: dict) -> str:
    out = []
    if item.get("title"):
        out.append(title_para(item["title"]))
    for b in item.get("bullets", []) or []:
        out.append(bullet_para(b))
    if item.get("note"):
        out.append(note_para(item["note"]))
    if not out:
        raise SystemExit("Insercao sem conteudo: informe 'title'+'bullets' ou 'note'.")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("saida")
    ap.add_argument("--json", required=True, help="arquivo JSON com as insercoes")
    args = ap.parse_args()

    items = json.loads(Path(args.json).read_text(encoding="utf-8"))
    if isinstance(items, dict):
        items = [items]

    with zipfile.ZipFile(args.entrada) as z:
        names = z.namelist()
        blobs = {n: z.read(n) for n in names}

    xml = blobs["word/document.xml"].decode("utf-8")

    # Indexa os paragrafos do corpo
    paras = [(m.start(), m.end(), m.group(0)) for m in PARA_RE.finditer(xml)]
    if not paras:
        raise SystemExit("Nenhum paragrafo encontrado em word/document.xml.")

    # Resolve as ancoras primeiro (falha cedo, antes de mexer no arquivo)
    plan = []  # (posicao_de_insercao_no_xml, bloco)
    for item in items:
        block = build_block(item)

        if item.get("at") == "end":
            body_end = xml.rfind("<w:sectPr")
            if body_end == -1:
                body_end = xml.rfind("</w:body>")
            plan.append((body_end, block))
            continue

        anchor = item.get("anchor")
        if not anchor:
            raise SystemExit("Cada insercao precisa de 'anchor' ou de \"at\": \"end\".")

        a = norm(anchor)
        hits = [(s, e, p) for (s, e, p) in paras if a in norm(para_text(p))]
        if len(hits) == 0:
            raise SystemExit(f"Ancora nao encontrada: {anchor!r}")
        if len(hits) > 1:
            print(f"Ancora ambigua ({len(hits)} ocorrencias): {anchor!r}", file=sys.stderr)
            for (_, _, p) in hits[:6]:
                print("  - " + para_text(p)[:110], file=sys.stderr)
            raise SystemExit("Aumente o trecho da ancora ate ficar unico.")

        s, e, _ = hits[0]
        pos = e if item.get("position", "after") == "after" else s
        plan.append((pos, block))

    # Aplica de tras pra frente para nao deslocar os offsets
    for pos, block in sorted(plan, key=lambda t: -t[0]):
        xml = xml[:pos] + block + xml[pos:]

    blobs["word/document.xml"] = xml.encode("utf-8")

    Path(args.saida).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.saida, "w", zipfile.ZIP_DEFLATED) as z:
        for n in names:
            z.writestr(n, blobs[n])

    print(f"ok: {len(plan)} bloco(s) inserido(s) em {args.saida}")


if __name__ == "__main__":
    main()
