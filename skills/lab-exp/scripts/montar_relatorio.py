"""Monta relatorio.html embutindo as figuras de results/ como data URI.

O artifact publicado nao carrega imagem de fora, entao a figura vai dentro do arquivo, que
tambem passa a abrir offline.

Convencao: no relatorio_template.html, {{fig01_nome_da_figura}} e trocado pelo <figure> da
figura results/fig01_nome_da_figura.png. A legenda vem de results/legendas.json, escrito pelo
proprio pipeline quando salva a figura, para a legenda nunca se descolar do que ela descreve.
"""
import base64
import json
import os
import re

AQUI = os.getcwd()
TEMPLATE = os.path.join(AQUI, "relatorio_template.html")
DESTINO = os.path.join(AQUI, "relatorio.html")
FIGURAS = os.path.join(AQUI, "results")
LEGENDAS = os.path.join(FIGURAS, "legendas.json")


def data_uri(caminho):
    with open(caminho, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")


def main():
    if not os.path.exists(TEMPLATE):
        raise FileNotFoundError(f"{TEMPLATE} nao existe.")
    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()

    legendas = {}
    if os.path.exists(LEGENDAS):
        with open(LEGENDAS, encoding="utf-8") as f:
            legendas = json.load(f)

    usadas, total = 0, 0
    for chave in re.findall(r"\{\{([a-z0-9_]+)\}\}", html):
        caminho = os.path.join(FIGURAS, f"{chave}.png")
        if not os.path.exists(caminho):
            raise FileNotFoundError(f"{caminho} nao existe, rode o pipeline antes")
        legenda = legendas.get(f"{chave}.png", "")
        if not legenda:
            print(f"  aviso: {chave}.png sem legenda em legendas.json")
        total += os.path.getsize(caminho)
        usadas += 1
        bloco = (f'<figure class="wide">\n'
                 f'  <img src="{data_uri(caminho)}" alt="{chave}">\n'
                 f'  <figcaption>{legenda}</figcaption>\n'
                 f'</figure>')
        html = html.replace("{{" + chave + "}}", bloco)

    sobrou = re.findall(r"\{\{[^}]+\}\}", html)
    if sobrou:
        raise ValueError(f"placeholders nao resolvidos: {sobrou}")

    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write(html)

    disponiveis = [n for n in sorted(os.listdir(FIGURAS)) if n.endswith(".png")]
    fora = [n for n in disponiveis if f"{{{{{n[:-4]}}}}}" not in open(
        TEMPLATE, encoding="utf-8").read()]
    print(f"{DESTINO}: {len(html) / 1e6:.2f} MB ({usadas} figuras, {total / 1e6:.2f} MB de PNG)")
    if fora:
        print(f"  figuras em results/ que ficaram de fora do relatorio: {fora}")


if __name__ == "__main__":
    main()
