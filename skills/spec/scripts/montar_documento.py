"""Converte um .md em documento HTML com o sistema de design do laboratorio.

Uma fonte so: o markdown e versionado no repositorio e e dele que sai o HTML publicado, para
documento e repositorio nunca divergirem.

Uso: python montar_documento.py DOCUMENTACAO.md "Titulo do documento"
"""
import os
import sys

import markdown

from _casca import ESTILO, FONTES, SCRIPT

ORIGEM = sys.argv[1] if len(sys.argv) > 1 else "DOCUMENTACAO.md"
TITULO = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(os.getcwd())
DESTINO = os.path.splitext(ORIGEM)[0] + ".html"

ACOES = """<div class="acoes">
  <button id="baixar" class="principal" hidden>Baixar o documento</button>
  <button id="imprimir">Salvar em PDF</button>
  <span class="aviso" id="aviso" role="status" aria-live="polite"></span>
</div>"""


def main():
    texto = open(ORIGEM, encoding="utf-8").read()
    corpo = markdown.markdown(
        texto, extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"])
    # As tabelas do markdown saem sem o container que rola, e tabela larga empurraria a pagina.
    corpo = corpo.replace("<table>", '<div class="tabela"><table>').replace(
        "</table>", "</table></div>")
    html = (f"<title>{TITULO}</title>\n{FONTES}\n{ESTILO}\n"
            f'<div class="wrap">\n{ACOES}\n{corpo}\n</div>\n{SCRIPT}\n')
    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"{DESTINO}: {len(html) / 1000:.1f} kB, "
          f"{corpo.count('<h2')} secoes, {corpo.count('<table>')} tabelas")


if __name__ == "__main__":
    main()
