"""Extrai o esqueleto verificavel do spec a partir do pipeline e da execucao.

A regra da skill: nada entra no documento que nao exista no codigo ou no log. Este script le
pipeline.py com o parser do proprio Python, le run.log e olha results/, e devolve o esqueleto.
Quem escreve a prosa depois e o agente, mas so sobre o que saiu daqui.

Uso: python extrair_spec.py [caminho_do_pipeline] > spec_esqueleto.md
"""
import ast
import json
import os
import re
import sys

AQUI = os.getcwd()
PIPELINE = sys.argv[1] if len(sys.argv) > 1 else "pipeline.py"
LOG = "run.log"
RESULTS = "results"


def literal(no):
    try:
        return ast.literal_eval(no)
    except (ValueError, TypeError, SyntaxError):
        return None


def extrair_do_codigo(caminho):
    fonte = open(caminho, encoding="utf-8").read()
    arvore = ast.parse(fonte)
    linhas = fonte.splitlines()

    parametros, listas, funcoes, classes = {}, {}, [], []
    for no in arvore.body:
        if isinstance(no, ast.Assign) and len(no.targets) == 1 and isinstance(no.targets[0], ast.Name):
            nome = no.targets[0].id
            valor = literal(no.value)
            if not nome.isupper() or valor is None:
                continue
            # Comentario na mesma linha explica a escolha: e parte do spec.
            comentario = ""
            m = re.search(r"#\s*(.+)$", linhas[no.lineno - 1])
            if m:
                comentario = m.group(1).strip()
            if isinstance(valor, (list, tuple, dict, set)):
                listas[nome] = valor
            else:
                parametros[nome] = {"valor": valor, "comentario": comentario}
        elif isinstance(no, ast.FunctionDef):
            doc = ast.get_docstring(no) or ""
            funcoes.append({"nome": no.name, "resumo": doc.split("\n")[0] if doc else "",
                            "doc": doc})
        elif isinstance(no, ast.ClassDef):
            doc = ast.get_docstring(no) or ""
            classes.append({"nome": no.name, "resumo": doc.split("\n")[0] if doc else "",
                            "doc": doc})

    # Etapas: os cabecalhos das celulas de markdown, na ordem em que rodam.
    etapas = []
    for i, linha in enumerate(linhas):
        if linha.startswith("# %% [markdown]"):
            for j in range(i + 1, min(i + 6, len(linhas))):
                bruto = linhas[j]
                if not bruto.startswith("#"):
                    continue
                # Tira so o "#" do comentario Python. O que sobrar comecando com "#" e o
                # cabecalho markdown. lstrip("# ") comeria os dois de uma vez e nunca casaria.
                t = bruto[1:].lstrip()
                if t.startswith("#"):
                    etapas.append({"titulo": t.lstrip("#").strip(),
                                   "nivel": len(t) - len(t.lstrip("#")), "linha": j + 1})
                    break
    return {"parametros": parametros, "listas": listas, "funcoes": funcoes,
            "classes": classes, "etapas": etapas, "n_linhas": len(linhas)}


def extrair_do_log(caminho):
    if not os.path.exists(caminho):
        return {"existe": False}
    texto = open(caminho, encoding="utf-8", errors="ignore").read()
    resumo = ""
    if "RESUMO" in texto:
        resumo = texto[texto.index("RESUMO"):][:2000]
    erros = [linha for linha in texto.splitlines()
             if re.search(r"Traceback|Error:|Exception", linha)]
    return {"existe": True, "linhas": len(texto.splitlines()), "resumo": resumo,
            "erros": erros[:5]}


def extrair_dos_resultados(pasta):
    if not os.path.isdir(pasta):
        return {"existe": False}
    arquivos = sorted(os.listdir(pasta))
    tabelas, figuras = [], []
    for n in arquivos:
        caminho = os.path.join(pasta, n)
        if n.endswith(".csv"):
            with open(caminho, encoding="utf-8-sig") as f:
                cabecalho = f.readline().strip()
                n_linhas = sum(1 for _ in f)
            tabelas.append({"arquivo": n, "linhas": n_linhas, "colunas": cabecalho})
        elif n.endswith(".png"):
            figuras.append(n)
    legendas = {}
    if os.path.exists(os.path.join(pasta, "legendas.json")):
        legendas = json.load(open(os.path.join(pasta, "legendas.json"), encoding="utf-8"))
    return {"existe": True, "tabelas": tabelas, "figuras": figuras, "legendas": legendas}


def main():
    if not os.path.exists(PIPELINE):
        raise SystemExit(f"{PIPELINE} nao existe. Rode na raiz do projeto.")
    codigo = extrair_do_codigo(PIPELINE)
    log = extrair_do_log(LOG)
    res = extrair_dos_resultados(RESULTS)

    print(f"# Esqueleto do spec: {os.path.basename(AQUI)}\n")
    print(f"Extraido de `{PIPELINE}` ({codigo['n_linhas']} linhas), "
          f"`{LOG}` e `{RESULTS}/`. Nada aqui foi escrito de memoria.\n")

    print("## Etapas, na ordem em que rodam\n")
    for e in codigo["etapas"]:
        print(f"{'  ' * max(e['nivel'] - 1, 0)}- {e['titulo']}  (linha {e['linha']})")

    print("\n## Parametros de decisao\n")
    print("Cada um destes e uma escolha que muda o resultado e precisa estar justificada.\n")
    print("| parametro | valor | comentario no codigo |")
    print("|---|---|---|")
    for nome, p in codigo["parametros"].items():
        print(f"| `{nome}` | `{p['valor']}` | {p['comentario'] or '-'} |")

    print("\n## Regras declaradas como lista\n")
    for nome, valor in codigo["listas"].items():
        if isinstance(valor, dict):
            print(f"\n**`{nome}`** ({len(valor)} itens)\n")
            for k, v in valor.items():
                print(f"- `{k}`: {v}")
        else:
            print(f"\n**`{nome}`** ({len(valor)} itens): "
                  + ", ".join(f"`{v}`" for v in list(valor)[:40]))

    print("\n## Pecas do pipeline e o que cada uma resolve\n")
    for c in codigo["classes"]:
        print(f"- **`{c['nome']}`** (classe): {c['resumo']}")
    for f in codigo["funcoes"]:
        if f["resumo"]:
            print(f"- **`{f['nome']}`**: {f['resumo']}")

    print("\n## Execucao\n")
    if log["existe"]:
        print(f"- `run.log` com {log['linhas']} linhas")
        print(f"- erros no log: {len(log['erros'])}"
              + (f" -> {log['erros'][0][:120]}" if log["erros"] else " (nenhum)"))
        if log["resumo"]:
            print("\n```\n" + log["resumo"].strip()[:1500] + "\n```")
    else:
        print("- AVISO: run.log nao existe. O pipeline nao foi executado ou a saida nao foi "
              "registrada. Sem isso o spec nao tem lastro.")

    print("\n## Artefatos produzidos\n")
    if res["existe"]:
        print(f"{len(res['tabelas'])} tabelas e {len(res['figuras'])} figuras.\n")
        print("| tabela | linhas | colunas |")
        print("|---|---|---|")
        for t in res["tabelas"]:
            print(f"| `{t['arquivo']}` | {t['linhas']} | {t['colunas'][:90]} |")
        print()
        for f in res["figuras"]:
            print(f"- `{f}`: {res['legendas'].get(f, 'SEM LEGENDA REGISTRADA')}")
    else:
        print("- AVISO: pasta results/ nao existe.")

    print("\n## Buracos a preencher na prosa\n")
    faltando = []
    if not log["existe"]:
        faltando.append("a execucao nao esta registrada")
    if res["existe"]:
        sem_legenda = [f for f in res["figuras"] if f not in res["legendas"]]
        if sem_legenda:
            faltando.append(f"figuras sem legenda: {sem_legenda}")
    sem_doc = [f["nome"] for f in codigo["funcoes"] if not f["resumo"]]
    if sem_doc:
        faltando.append(f"funcoes sem docstring: {sem_doc}")
    for f in faltando:
        print(f"- {f}")
    if not faltando:
        print("- nenhum")


if __name__ == "__main__":
    main()
