"""Converte pipeline.py (formato jupytext, marcadores # %%) no notebook do Colab.

Convencao: roda na raiz do projeto, le pipeline.py, escreve <nome-da-pasta>.ipynb.
O notebook entregue e gerado do mesmo arquivo que foi executado, para nao existir versao de
codigo que ninguem rodou.
"""
import json
import os
import re
import sys

AQUI = os.getcwd()
NOME = os.path.basename(AQUI)
# Sem argumento: pipeline.py vira <pasta>.ipynb. Com argumento: converte outro .py, util quando
# o projeto tem mais de uma analise (um pipeline principal e uma analise de sobrevida, por ex).
ORIGEM = os.path.join(AQUI, sys.argv[1] if len(sys.argv) > 1 else "pipeline.py")
DESTINO = os.path.join(AQUI, sys.argv[2] if len(sys.argv) > 2
                       else (f"{NOME}.ipynb" if len(sys.argv) < 2
                             else os.path.splitext(sys.argv[1])[0] + ".ipynb"))

# Roda no Colab e localmente. Sem o try, a primeira celula quebra fora do Colab.
PREFACIO_COLAB = """try:
    from google.colab import drive
    drive.mount('/content/drive')
except ImportError:
    pass   # fora do Colab, os dados vem de um dos caminhos locais de CAMINHOS_DADOS
"""


def dividir_celulas(texto):
    celulas, atual, tipo = [], [], "code"
    for linha in texto.splitlines():
        if linha.startswith("# %%"):
            if atual:
                celulas.append((tipo, "\n".join(atual).strip("\n")))
            atual, tipo = [], "markdown" if "[markdown]" in linha else "code"
        else:
            atual.append(linha)
    if atual:
        celulas.append((tipo, "\n".join(atual).strip("\n")))
    return [(t, c) for t, c in celulas if c.strip()]


def main():
    if not os.path.exists(ORIGEM):
        import glob
        candidatos = sorted(os.path.basename(c) for c in glob.glob(os.path.join(AQUI, "*.py"))
                            if os.path.basename(c).startswith(("pipeline", "sobrevida", "analise")))
        exemplo = candidatos[0] if candidatos else "pipeline.py"
        raise FileNotFoundError(
            f"{os.path.basename(ORIGEM)} nao existe nesta pasta. "
            f"Passe o arquivo como argumento. Candidatos aqui: {candidatos or 'nenhum'}. "
            f"Exemplo: python gerar_notebook.py {exemplo} saida.ipynb")
    with open(ORIGEM, encoding="utf-8") as f:
        texto = f.read()

    celulas = []
    for tipo, corpo in dividir_celulas(texto):
        if tipo == "markdown":
            fonte = "\n".join(re.sub(r"^# ?", "", linha) for linha in corpo.splitlines())
            celulas.append({"cell_type": "markdown", "metadata": {},
                            "source": fonte.splitlines(keepends=True)})
        else:
            # Casa a linha inteira do pip, seja qual for a lista de pacotes. Substituicao por
            # texto fixo para de casar quando a lista muda e deixa o resto da linha solto.
            corpo = re.sub(r"^# (!pip install .*)$", r"\1\n\n" + PREFACIO_COLAB.rstrip(),
                           corpo, flags=re.MULTILINE)
            corpo = corpo.replace(
                'DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '
                '"results") \\\n    if "__file__" in globals() else "results"',
                'DIR_RESULTADOS = "results"')
            celulas.append({"cell_type": "code", "execution_count": None, "metadata": {},
                            "outputs": [], "source": corpo.splitlines(keepends=True)})

    notebook = {"cells": celulas,
                "metadata": {"colab": {"provenance": [], "toc_visible": True},
                             "kernelspec": {"display_name": "Python 3", "name": "python3"},
                             "language_info": {"name": "python"}},
                "nbformat": 4, "nbformat_minor": 0}
    with open(DESTINO, "w", encoding="utf-8") as f:
        json.dump(notebook, f, ensure_ascii=False, indent=1)

    codigo = sum(1 for c in celulas if c["cell_type"] == "code")
    print(f"{DESTINO}: {len(celulas)} celulas ({codigo} de codigo)")


if __name__ == "__main__":
    main()
