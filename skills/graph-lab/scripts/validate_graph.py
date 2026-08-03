#!/usr/bin/env python3
"""Valida o task-graph.md gerado pela skill graph-init.

Uso: python3 scripts/validate_graph.py task-graph.md

- Extrai o primeiro bloco Mermaid (graph TD) do arquivo
- Arestas solidas  (A --> B)            -> depends_on: B depende de A
- Arestas pontilhadas (A -.->|"x"| B)   -> impacts: fora do ciclo/topo, listadas no relatorio
- Detecta ciclos via DFS sobre as arestas depends_on
- Imprime a ordem topologica via Kahn

Exit codes: 0 = ok | 1 = ciclo detectado | 2 = arquivo/bloco invalido
Zero dependencias externas (stdlib apenas).
"""
import re
import sys
from collections import defaultdict, deque

ID = r"[A-Za-z_][\w-]*"
BRACKET = r"(?:[\[\(\{][^\]\)\}]*[\]\)\}])?"
# A[...] --> B  ou  A -->|label| B   (aresta solida = depends_on)
DEP_RE = re.compile(rf"({ID}){BRACKET}\s*-->\s*(?:\|[^|]*\|\s*)?({ID})")
# A -.->|"+/-metrica"| B             (aresta pontilhada = impacts)
IMPACT_RE = re.compile(rf"({ID}){BRACKET}\s*-\.->\s*(?:\|([^|]*)\|\s*)?({ID})")
NODE_RE = re.compile(rf"^\s*({ID})\s*[\[\(\{{]")
MERMAID_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)


def parse(text):
    m = MERMAID_RE.search(text)
    if not m:
        return None
    block = m.group(1)
    nodes, deps, impacts = set(), [], []
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith(("graph", "flowchart", "%%")):
            continue
        # impacts primeiro: linhas com -.-> nao contem --> mas por clareza
        for src, label, dst in IMPACT_RE.findall(line):
            impacts.append((src, (label or "").strip().strip('"'), dst))
            nodes.update((src, dst))
        if "-.->" not in line:
            for src, dst in DEP_RE.findall(line):
                deps.append((src, dst))
                nodes.update((src, dst))
        nm = NODE_RE.match(line)
        if nm:
            nodes.add(nm.group(1))
    return nodes, deps, impacts


def find_cycle(nodes, deps):
    """DFS: retorna a lista de nos de um ciclo, ou None."""
    adj = defaultdict(list)
    for src, dst in deps:
        adj[src].append(dst)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}
    parent = {}

    def dfs(u):
        color[u] = GRAY
        for v in adj[u]:
            if color[v] == GRAY:  # aresta de retorno -> ciclo
                cycle = [v, u]
                w = u
                while w != v:
                    w = parent[w]
                    cycle.append(w)
                cycle.reverse()
                return cycle
            if color[v] == WHITE:
                parent[v] = u
                found = dfs(v)
                if found:
                    return found
        color[u] = BLACK
        return None

    for n in sorted(nodes):
        if color[n] == WHITE:
            found = dfs(n)
            if found:
                return found
    return None


def topo_order(nodes, deps):
    """Kahn: ordem topologica estavel (desempate alfabetico)."""
    adj = defaultdict(list)
    indeg = {n: 0 for n in nodes}
    for src, dst in deps:
        adj[src].append(dst)
        indeg[dst] += 1
    queue = deque(sorted(n for n in nodes if indeg[n] == 0))
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        ready = []
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
        for v in sorted(ready):
            queue.append(v)
    return order


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(sys.argv) != 2:
        print("Uso: python3 scripts/validate_graph.py task-graph.md")
        return 2
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"ERRO: nao consegui ler o arquivo: {e}")
        return 2

    parsed = parse(text)
    if parsed is None:
        print("ERRO: nenhum bloco ```mermaid encontrado no arquivo.")
        return 2
    nodes, deps, impacts = parsed
    if not nodes:
        print("ERRO: bloco Mermaid vazio ou sem nos reconheciveis.")
        return 2

    print(f"Nos: {len(nodes)} -> {', '.join(sorted(nodes))}")
    print(f"Arestas depends_on: {len(deps)}")
    for src, dst in deps:
        print(f"  {src} --> {dst}")
    print(f"Arestas impacts: {len(impacts)}")
    for src, label, dst in impacts:
        sign = "(-)" if label.startswith(("-", "−")) else "(+)" if label.startswith("+") else "(?)"
        print(f"  {src} -.-> {dst}  impacts{sign} {label}")

    cycle = find_cycle(nodes, deps)
    if cycle:
        print()
        print(f"CICLO DETECTADO: {' --> '.join(cycle)}")
        print("O grafo e invalido. Volte a fase CONNECT e remova a dependencia circular.")
        return 1

    order = topo_order(nodes, deps)
    print()
    print("Sem ciclos. Ordem topologica:")
    for i, n in enumerate(order, 1):
        print(f"  {i}. {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
