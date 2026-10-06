"""Monta o zip de compartilhamento e o requirements.txt com as versoes que rodaram.

Regra do pacote: entra tudo que e preciso para ler, auditar e reproduzir, e nao entra dado de
paciente. Quem precisa rodar ja tem o banco, e um zip circula muito mais facil que um banco de
prontuario deveria circular.
"""
import hashlib
import importlib
import os
import zipfile
from importlib import metadata

AQUI = os.getcwd()
NOME = os.path.basename(AQUI)
DESTINO = os.path.join(AQUI, f"{NOME}.zip")

# Raiz: tudo isso entra, se existir. Dado fica de fora por extensao e por pasta.
EXTENSOES = (".py", ".ipynb", ".html", ".md", ".txt", ".log", ".toml", ".cfg")
EXCLUIR_NOMES = {f"{NOME}.zip"}
EXCLUIR_PASTAS = {"data", "__pycache__", ".git", ".venv", ".ipynb_checkpoints"}
EXCLUIR_EXTENSOES = (".xlsx", ".xls", ".csv", ".parquet", ".dta", ".sav")

PACOTES = ["sklearn", "numpy", "pandas", "scipy", "matplotlib", "seaborn", "xgboost",
           "lightgbm", "catboost", "tabpfn", "shap", "statsmodels", "boruta", "openpyxl",
           "torch", "nbclient", "nbformat", "sksurv", "patsy", "markdown"]
# sksurv e tabpfn brigam pelo sklearn: o tabpfn exige abaixo de 1.7 e o scikit-survival novo
# puxa versao acima. A combinacao que funciona esta pinada no requirements gerado.
NOME_PYPI = {"sklearn": "scikit-learn", "boruta": "Boruta", "sksurv": "scikit-survival"}


def gerar_requirements():
    """Le a versao dos metadados da distribuicao, e nao de __version__.

    Pacote sem __version__, como o Boruta, sairia sem pino. E o sufixo local do torch (+cpu)
    nao instala do PyPI padrao, entao ele sai do pino e vira comentario.
    """
    linhas = ["# Versoes efetivamente usadas na execucao deste experimento.",
              "# Se o torch estiver listado, a roda de CPU instala assim:",
              "#   pip install torch --index-url https://download.pytorch.org/whl/cpu"]
    for modulo in PACOTES:
        nome = NOME_PYPI.get(modulo, modulo)
        try:
            versao = metadata.version(nome)
        except metadata.PackageNotFoundError:
            try:
                versao = getattr(importlib.import_module(modulo), "__version__", None)
            except ImportError:
                continue
        linhas.append(f"{nome}=={versao.split('+')[0]}" if versao else nome)
    caminho = os.path.join(AQUI, "requirements.txt")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    return caminho


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 16), b""):
            h.update(bloco)
    return h.hexdigest()[:12]


def main():
    gerar_requirements()

    raiz = sorted(n for n in os.listdir(AQUI)
                  if os.path.isfile(os.path.join(AQUI, n))
                  and n.endswith(EXTENSOES)
                  and not n.endswith(EXCLUIR_EXTENSOES)
                  and n not in EXCLUIR_NOMES)
    if not raiz:
        raise FileNotFoundError("nenhum arquivo de codigo ou entrega na raiz")

    total = 0
    with zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        print("raiz")
        for nome in raiz:
            caminho = os.path.join(AQUI, nome)
            total += os.path.getsize(caminho)
            z.write(caminho, f"{NOME}/{nome}")
            print(f"  {nome:44s} {os.path.getsize(caminho) / 1e3:9.1f} kB")

        if os.path.isdir(os.path.join(AQUI, "results")):
            arquivos = sorted(os.listdir(os.path.join(AQUI, "results")))
            for nome in arquivos:
                caminho = os.path.join(AQUI, "results", nome)
                total += os.path.getsize(caminho)
                z.write(caminho, f"{NOME}/results/{nome}")
            figuras = sum(1 for n in arquivos if n.endswith(".png"))
            print(f"\nresults\n  {figuras} figuras, {len(arquivos) - figuras} tabelas e metadados")

    # results/ entra inteiro, csv de resultado agregado incluso. O que fica de fora e planilha
    # de dado bruto na raiz e a pasta data/.
    print(f"\nfora do pacote, de proposito: {', '.join(sorted(EXCLUIR_PASTAS))} "
          f"e planilha de dado bruto na raiz ({', '.join(EXCLUIR_EXTENSOES)})")
    print("  dado de paciente nao viaja em zip. Quem precisa rodar ajusta CAMINHOS_DADOS.")
    print(f"\n{DESTINO}")
    print(f"  {os.path.getsize(DESTINO) / 1e6:.2f} MB compactado, "
          f"{total / 1e6:.2f} MB descompactado, sha256 {sha256(DESTINO)}")


if __name__ == "__main__":
    main()
