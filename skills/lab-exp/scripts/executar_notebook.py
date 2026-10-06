"""Executa o notebook e grava a versao com as saidas dentro.

Quem abre o executado ja ve numero e figura, sem esperar a execucao inteira. O limpo continua
sendo o que vai para o Colab.

Vale como teste de integracao: se qualquer celula quebrar, o arquivo executado nao e gerado.
Foi assim que apareceu uma primeira celula com IndentationError que a checagem de sintaxe nao
pegava, porque ela ignorava as linhas iniciadas por "!".
"""
import os
import sys

import nbformat
from nbclient import NotebookClient

AQUI = os.getcwd()
NOME = os.path.basename(AQUI)
# Sem argumento: <pasta>.ipynb. Com argumento: executa outro notebook do mesmo projeto.
ORIGEM = os.path.join(AQUI, sys.argv[1] if len(sys.argv) > 1 else f"{NOME}.ipynb")
DESTINO = os.path.splitext(ORIGEM)[0] + "_executado.ipynb"
TIMEOUT = int(os.environ.get("LAB_TIMEOUT", "14400"))   # 4 horas por celula


def main():
    if not os.path.exists(ORIGEM):
        raise FileNotFoundError(f"{ORIGEM} nao existe. Rode gerar_notebook.py antes.")
    nb = nbformat.read(ORIGEM, as_version=4)
    nb.metadata.setdefault("kernelspec", {"display_name": "Python 3", "language": "python",
                                          "name": "python3"})
    cliente = NotebookClient(nb, timeout=TIMEOUT, kernel_name="python3",
                             resources={"metadata": {"path": AQUI}}, allow_errors=False)
    print(f"Executando {len(nb.cells)} celulas de {ORIGEM}...")
    cliente.execute()
    nbformat.write(nb, DESTINO)

    com_saida = sum(1 for c in nb.cells if c.get("outputs"))
    figuras = sum(1 for c in nb.cells for o in c.get("outputs", [])
                  if "image/png" in o.get("data", {}))
    erros = sum(1 for c in nb.cells for o in c.get("outputs", [])
                if o.get("output_type") == "error")
    print(f"{DESTINO}: {com_saida} celulas com saida, {figuras} figuras, {erros} erros")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
