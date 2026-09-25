#!/usr/bin/env python3
"""Valida o task-graph.md gerado pela skill graph-lab.

Fonte canonica: labdaps/labskills, skills/graph-lab/scripts/validate_graph.py,
com testes em skills/graph-lab/tests/. Copias em outros repositorios devem ser
identicas a este arquivo: corrija aqui e copie.

Uso: python3 validate_graph.py task-graph.md

- Le o primeiro bloco ```mermaid do arquivo (graph TD ou flowchart)
- Separa cada linha em statements (';' fora de aspas, formas e rotulos)
- Rotulo entre aspas e forma de no (A["..."], A(...), A{...}, A>...],
  A@{...}) sao blocos opacos: colchete, parentese ou seta dentro deles
  nao vira aresta
- ':::classe' depois do no e ignorado
- Cadeia (A --> B --> C) gera uma aresta por ligacao, e '&' expande
  (A & B --> C gera A --> C e B --> C)
- Ligacao solida ou grossa (A --> B, --->, ---, ==>, ===, -- texto -->,
  == texto ==>) -> depends_on: B depende de A; '|rotulo|' e ignorado
- Ligacao pontilhada (A -.->|"x"| B, -.-, -. texto .->) -> impacts: fora
  do ciclo e da ordem, listada no relatorio com o rotulo
- '<-->' (e '<==>', '<-.->') gera a ligacao nos dois sentidos
- Linha com operador de ligacao que nao vira aresta (sintaxe fora do
  subconjunto acima, ligacao sem destino, '~~~') -> exit 2 com a linha
- Detecta ciclos via DFS sobre as arestas depends_on
- Imprime a ordem topologica via Kahn

Exit codes: 0 = ok | 1 = ciclo detectado | 2 = arquivo/bloco invalido
Zero dependencias externas (stdlib apenas).
"""
import re
import sys
from collections import defaultdict, deque

MERMAID_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)

# Statements que nao declaram no nem aresta (cabecalho, subgrafo, estilo).
SKIP_RE = re.compile(
    r"(?:graph|flowchart|subgraph|end|classDef|class|style|linkStyle|click"
    r"|direction|accTitle|accDescr)\b"
)
# Id de no: letras, digitos e '_', com '-' so entre eles (A-->B e A, --> B).
ID_RE = re.compile(r"\w+(?:-\w+)*")
CLASS_RE = re.compile(r":::[\w-]+")
LABEL_RE = re.compile(r"\s*\|([^|]*)\|")
WS_RE = re.compile(r"\s*")

# Operadores de ligacao, na ordem de tentativa: (tipo, regex).
# 'dep' = depends_on, 'imp' = impacts. O grupo 'bi' marca a ponta '<'.
_SOLID_END = r"(?:--+>|---+|--[ox](?!\w))"
_THICK_END = r"(?:==+>|===+|==[ox](?!\w))"
_DOTTED_END = r"\.+-(?:>|[ox](?!\w))?"
LINK_RES = [
    ("dep", re.compile(r"(?P<bi><)?" + _SOLID_END)),
    ("dep", re.compile(r"(?P<bi><)?" + _THICK_END)),
    ("imp", re.compile(r"(?P<bi><)?-" + _DOTTED_END)),
    ("dep", re.compile(r"(?P<bi><)?--(?![->.])\s*(?P<text>.+?)\s*" + _SOLID_END)),
    ("dep", re.compile(r"(?P<bi><)?==(?![=>])\s*(?P<text>.+?)\s*" + _THICK_END)),
    ("imp", re.compile(r"(?P<bi><)?-\.(?!\.*-)\s*(?P<text>.+?)\s*" + _DOTTED_END)),
]
# Indicio de operador de ligacao numa linha que nao parseou (inclui os
# erros de digitacao A -> B e A => B, que o Mermaid tambem rejeita).
LINK_HINT_RE = re.compile(r"--|==|-\.|~~|->|=>|<-")
QUOTED_RE = re.compile(r'"[^"]*"')

_PAIR = {"[": "]", "(": ")", "{": "}"}


class GraphSyntaxError(ValueError):
    """Linha com operador de ligacao que nao gerou aresta."""

    def __init__(self, lineno, line, reason):
        super().__init__(f"linha {lineno}: {reason}: {line}")
        self.lineno = lineno
        self.line = line
        self.reason = reason


class _Fail(Exception):
    """Falha interna de parse de um statement."""


def _split_statements(line):
    """Divide a linha em ';' que nao estejam dentro de aspas, formas ou |rotulo|."""
    parts, buf = [], []
    quote = pipe = False
    depth = 0
    for c in line:
        if quote:
            quote = c != '"'
        elif c == '"':
            quote = True
        elif c in "[({":
            depth += 1
        elif c in "])}":
            depth = max(0, depth - 1)
        elif c == "|" and depth == 0:
            pipe = not pipe
        elif c == ";" and depth == 0 and not pipe:
            parts.append("".join(buf))
            buf = []
            continue
        buf.append(c)
    parts.append("".join(buf))
    return [p.strip() for p in parts if p.strip()]


def _skip_block(s, i):
    """s[i] abre uma forma de no. Devolve o indice logo depois do fechamento.

    So conta o tipo de colchete que abriu a forma, e pula texto entre aspas,
    para que '(' ou ']' dentro do rotulo nao fechem a forma antes da hora.
    """
    if s[i] == ">":  # forma assimetrica: A>texto]
        opener, closer, depth, j = "[", "]", 1, i + 1
    else:
        opener, closer, depth, j = s[i], _PAIR[s[i]], 0, i
    while j < len(s):
        c = s[j]
        if c == '"':
            k = s.find('"', j + 1)
            if k < 0:
                raise _Fail("aspas sem fechamento")
            j = k + 1
            continue
        if c == opener:
            depth += 1
        elif c == closer:
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    raise _Fail("forma de no sem fechamento")


def _node(s, i):
    """Le um no (id, forma opcional, :::classe opcional). Devolve (id, fim)."""
    m = ID_RE.match(s, i)
    if not m:
        raise _Fail("esperava um no")
    node, j = m.group(0), m.end()
    if s.startswith("@{", j):
        j = _skip_block(s, j + 1)
    else:
        k = WS_RE.match(s, j).end()
        if k < len(s) and s[k] in "[({":
            j = _skip_block(s, k)
        elif j < len(s) and s[j] == ">":
            j = _skip_block(s, j)
    m = CLASS_RE.match(s, j)
    if m:
        j = m.end()
    return node, j


def _group(s, i):
    """Le um grupo de nos ligados por '&'. Devolve (lista de ids, fim)."""
    nodes = []
    while True:
        i = WS_RE.match(s, i).end()
        node, i = _node(s, i)
        nodes.append(node)
        k = WS_RE.match(s, i).end()
        if k < len(s) and s[k] == "&":
            i = k + 1
            continue
        return nodes, i


def _link(s, i):
    """Le um operador de ligacao em s[i]. Devolve (tipo, bidirecional, rotulo, fim)."""
    for kind, rx in LINK_RES:
        m = rx.match(s, i)
        if m:
            label = m.groupdict().get("text") or ""
            j = m.end()
            lm = LABEL_RE.match(s, j)
            if lm:
                label, j = lm.group(1), lm.end()
            return kind, bool(m.group("bi")), label.strip().strip('"'), j
    return None


def _statement(stmt):
    """Parseia um statement. Devolve (nos, deps, impacts)."""
    nodes, deps, impacts = set(), [], []
    left, i = _group(stmt, 0)
    nodes.update(left)
    while True:
        i = WS_RE.match(stmt, i).end()
        if i >= len(stmt):
            return nodes, deps, impacts
        link = _link(stmt, i)
        if link is None:
            raise _Fail("operador de ligacao nao reconhecido")
        kind, bi, label, i = link
        try:
            right, i = _group(stmt, i)
        except _Fail:
            raise _Fail("ligacao sem no de destino") from None
        nodes.update(right)
        for src in left:
            for dst in right:
                pairs = [(src, dst), (dst, src)] if bi else [(src, dst)]
                for a, b in pairs:
                    if kind == "dep":
                        deps.append((a, b))
                    else:
                        impacts.append((a, label, b))
        left = right


def parse(text):
    """Devolve (nos, deps, impacts) do primeiro bloco Mermaid, ou None sem bloco.

    Levanta GraphSyntaxError se uma linha com operador de ligacao nao gerar
    aresta, para o AUDIT falhar fechado em vez de aprovar um grafo incompleto.
    """
    m = MERMAID_RE.search(text)
    if not m:
        return None
    first_line = text.count("\n", 0, m.start(1)) + 1
    nodes, deps, impacts = set(), [], []
    for offset, raw in enumerate(m.group(1).splitlines()):
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue
        for stmt in _split_statements(line):
            if SKIP_RE.match(stmt):
                continue
            try:
                n, d, im = _statement(stmt)
            except _Fail as e:
                if LINK_HINT_RE.search(QUOTED_RE.sub("", stmt)):
                    raise GraphSyntaxError(first_line + offset, line, str(e)) from None
                continue  # linha sem ligacao e fora do subconjunto: ignorada
            nodes.update(n)
            deps.extend(d)
            impacts.extend(im)
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

    try:
        parsed = parse(text)
    except GraphSyntaxError as e:
        print(f"ERRO: linha {e.lineno} tem operador de ligacao que nao virou aresta ({e.reason}):")
        print(f"  {e.line}")
        print('Use A --> B para dependencia e A -.->|"-metrica"| B para efeito colateral.')
        return 2
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
