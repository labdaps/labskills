"""Testes do scripts/validate_graph.py da graph-lab. Stdlib pura (unittest).

Rodar da raiz do labskills:
    python3 -m pytest skills/graph-lab/tests
ou, sem pytest:
    python3 -m unittest discover -s skills/graph-lab/tests -v

As classes TestParse, TestCycleAndTopo e TestExitCodes vieram da suite do
claude-skill-graph-init. TestRegressaoAchados traz um teste por caso da
evidencia dos achados GI-01 e LSK-05: cada um aprovava um grafo com ciclo no
validador antigo, baseado em regex.

Contraprova: os testes de regressao rodam o script por linha de comando, e a
variavel VALIDATE_GRAPH_SCRIPT troca o script testado. Para ver os casos
falharem no validador antigo:
    git show 92dc441:skills/graph-lab/scripts/validate_graph.py > /tmp/antigo.py
    VALIDATE_GRAPH_SCRIPT=/tmp/antigo.py python3 -m pytest skills/graph-lab/tests -k Regressao
"""
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.environ.get(
    "VALIDATE_GRAPH_SCRIPT", os.path.join(ROOT, "scripts", "validate_graph.py")
)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.dont_write_bytecode = True  # nao deixa __pycache__ dentro de scripts/

import validate_graph as vg  # noqa: E402


VALID = """# Task Graph
```mermaid
graph TD
    A["[A] um"]
    B["[B] dois"]
    C["[C] tres"]
    A --> B
    B --> C
    A -.->|"−metrica"| C
    B -.->|"+metrica"| C
```
"""

CYCLE = """# Task Graph
```mermaid
graph TD
    A --> B
    B --> C
    C --> A
```
"""

LABELED_DEP = """```mermaid
graph TD
    A -->|ordem| B
```
"""


def mermaid(*lines):
    return "# Task Graph\n```mermaid\ngraph TD\n" + "\n".join(lines) + "\n```\n"


def run_cli(content):
    with tempfile.NamedTemporaryFile(
        "w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        path = f.name
    try:
        proc = subprocess.run(
            [sys.executable, "-B", SCRIPT, path], capture_output=True, text=True,
            encoding="utf-8",
        )
        return proc.returncode, proc.stdout
    finally:
        os.unlink(path)


class TestParse(unittest.TestCase):
    def test_valid_graph(self):
        nodes, deps, impacts = vg.parse(VALID)
        self.assertEqual(nodes, {"A", "B", "C"})
        self.assertEqual(sorted(deps), [("A", "B"), ("B", "C")])
        self.assertEqual(len(impacts), 2)

    def test_impacts_not_in_deps(self):
        _, deps, impacts = vg.parse(VALID)
        self.assertNotIn(("A", "C"), deps)
        self.assertIn(("A", "−metrica", "C"), impacts)

    def test_dep_with_label(self):
        nodes, deps, _ = vg.parse(LABELED_DEP)
        self.assertEqual(deps, [("A", "B")])

    def test_no_mermaid_block(self):
        self.assertIsNone(vg.parse("# sem grafo aqui"))


class TestCycleAndTopo(unittest.TestCase):
    def test_no_cycle(self):
        nodes, deps, _ = vg.parse(VALID)
        self.assertIsNone(vg.find_cycle(nodes, deps))

    def test_cycle_detected(self):
        nodes, deps, _ = vg.parse(CYCLE)
        cycle = vg.find_cycle(nodes, deps)
        self.assertIsNotNone(cycle)
        self.assertEqual(cycle[0], cycle[-1])
        self.assertGreaterEqual(len(set(cycle)), 3)

    def test_topo_order(self):
        nodes, deps, _ = vg.parse(VALID)
        order = vg.topo_order(nodes, deps)
        self.assertEqual(order, ["A", "B", "C"])


class TestExitCodes(unittest.TestCase):
    def test_exit_0_valid(self):
        code, out = run_cli(VALID)
        self.assertEqual(code, 0)
        self.assertIn("Ordem topologica", out)

    def test_exit_1_cycle(self):
        code, out = run_cli(CYCLE)
        self.assertEqual(code, 1)
        self.assertIn("CICLO DETECTADO", out)

    def test_exit_2_no_block(self):
        code, _ = run_cli("# nada de mermaid")
        self.assertEqual(code, 2)

    def test_exit_2_no_args(self):
        proc = subprocess.run(
            [sys.executable, "-B", SCRIPT], capture_output=True, text=True
        )
        self.assertEqual(proc.returncode, 2)


class TestRegressaoAchados(unittest.TestCase):
    """Um teste por caso da evidencia. Todos passavam com exit 0 no validador
    antigo, que perdia a aresta e deixava o ciclo escapar."""

    def assertCiclo(self, content, aresta):
        code, out = run_cli(content)
        self.assertEqual(code, 1, f"ciclo nao detectado:\n{out}")
        self.assertIn("CICLO DETECTADO", out)
        self.assertIn(f"  {aresta}\n", out, "a aresta perdida deveria aparecer")

    def test_gi01_lsk05_cadeia(self):
        """GI-01 e LSK-05: A --> B --> C perdia B --> C."""
        self.assertCiclo(mermaid("    A --> B --> C", "    C --> A"), "B --> C")

    def test_gi01_colchete_no_rotulo(self):
        """GI-01: o colchete de '[N1] ingestao' fechava a forma e N1 --> N2 sumia."""
        self.assertCiclo(
            mermaid('    N1["[N1] ingestao"] --> N2["[N2] treino"]', "    N2 --> N1"),
            "N1 --> N2",
        )

    def test_gi01_lsk05_e_comercial(self):
        """GI-01 e LSK-05: A & B --> C perdia A --> C."""
        self.assertCiclo(mermaid("    A & B --> C", "    C --> A"), "A --> C")

    def test_gi01_parentese_no_rotulo(self):
        """GI-01 (nota do verificador): 'treino (XGBoost)' perdia a aresta."""
        self.assertCiclo(
            mermaid('    N1["treino (XGBoost)"] --> N2["avaliacao"]', "    N2 --> N1"),
            "N1 --> N2",
        )

    def test_lsk05_colchete_nas_duas_arestas(self):
        """LSK-05: com rotulo nas duas pontas saiam 0 arestas depends_on."""
        content = mermaid(
            '    N1["[N1] ingestao"] --> N2["[N2] missing"]',
            '    N2["[N2] missing"] --> N1["[N1] ingestao"]',
        )
        code, out = run_cli(content)
        self.assertEqual(code, 1, out)
        self.assertIn("Arestas depends_on: 2", out)

    def test_lsk05_classe_nao_vira_no(self):
        """LSK-05: 'N1:::done --> N2' criava o no fantasma 'done' e escondia o ciclo."""
        content = mermaid("    N1:::done --> N2", "    N2 --> N1")
        self.assertCiclo(content, "N1 --> N2")
        _, out = run_cli(content)
        self.assertIn("Nos: 2 -> N1, N2", out)

    def test_lsk05_seta_grossa(self):
        """LSK-05: 'B ==> A' era ignorado."""
        self.assertCiclo(mermaid("    A --> B", "    B ==> A"), "B --> A")


class TestSintaxeAceita(unittest.TestCase):
    def deps(self, *lines):
        return vg.parse(mermaid(*lines))[1]

    def test_ligacao_aberta_e_dependencia(self):
        self.assertEqual(self.deps("    A --- B"), [("A", "B")])

    def test_texto_no_meio_nao_cria_no(self):
        nodes, deps, _ = vg.parse(mermaid("    A -- ordem --> B"))
        self.assertEqual(nodes, {"A", "B"})
        self.assertEqual(deps, [("A", "B")])

    def test_seta_dentro_do_rotulo_e_opaca(self):
        nodes, deps, _ = vg.parse(mermaid('    N1["[N1] migrar A --> B"]'))
        self.assertEqual(nodes, {"N1"})
        self.assertEqual(deps, [])

    def test_pontilhada_nao_entra_no_ciclo(self):
        content = mermaid("    A --> B", '    B -.->|"−calibracao"| A')
        nodes, deps, impacts = vg.parse(content)
        self.assertEqual(deps, [("A", "B")])
        self.assertEqual(impacts, [("B", "−calibracao", "A")])
        self.assertEqual(run_cli(content)[0], 0)

    def test_pontilhada_com_texto(self):
        _, deps, impacts = vg.parse(mermaid("    A -. −calibracao .-> B"))
        self.assertEqual(deps, [])
        self.assertEqual(impacts, [("A", "−calibracao", "B")])

    def test_e_comercial_nos_dois_lados(self):
        self.assertEqual(
            self.deps("    A & B --> C & D"),
            [("A", "C"), ("A", "D"), ("B", "C"), ("B", "D")],
        )

    def test_bidirecional_vira_ciclo(self):
        code, _ = run_cli(mermaid("    A <--> B"))
        self.assertEqual(code, 1)

    def test_ponto_e_virgula_separa_statements(self):
        self.assertEqual(self.deps("    A-->B; B-->C;"), [("A", "B"), ("B", "C")])

    def test_formas_de_no(self):
        self.assertEqual(
            self.deps("    N1([a]) --> N2[(b)] --> N3((c)) --> N4>d] --> N5{{e}}"),
            [("N1", "N2"), ("N2", "N3"), ("N3", "N4"), ("N4", "N5")],
        )

    def test_estilo_e_subgrafo_ignorados(self):
        nodes, deps, _ = vg.parse(mermaid(
            "    subgraph S1 [dados]",
            "    A --> B",
            "    end",
            "    classDef done fill:#9f6,stroke-width:2px;",
            "    class A done",
            "    style B stroke-dasharray: 5 5",
        ))
        self.assertEqual(nodes, {"A", "B"})
        self.assertEqual(deps, [("A", "B")])

    def test_template_e_exemplo_da_skill_validam(self):
        for rel in ("templates/task-graph.template.md", "examples/example-refactor.md"):
            with self.subTest(arquivo=rel):
                with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
                    code, out = run_cli(f.read())
                self.assertEqual(code, 0, out)


class TestFalhaFechada(unittest.TestCase):
    """Linha com operador de ligacao que nao vira aresta sai com exit 2."""

    def assertExit2(self, *lines):
        code, out = run_cli(mermaid("    A --> B", *lines))
        self.assertEqual(code, 2, out)
        self.assertIn("ERRO: linha", out)
        return out

    def test_ligacao_sem_destino(self):
        out = self.assertExit2("    B -->")
        self.assertIn("linha 5 ", out)
        self.assertIn("B -->", out)

    def test_seta_de_um_traco(self):
        self.assertExit2("    B -> C")

    def test_ligacao_invisivel(self):
        self.assertExit2("    B ~~~ C")

    def test_lixo_depois_do_destino(self):
        self.assertExit2("    B --> C D")

    def test_parse_levanta_erro_com_a_linha(self):
        with self.assertRaises(vg.GraphSyntaxError) as ctx:
            vg.parse(mermaid("    A --> B", "    B -->"))
        self.assertEqual(ctx.exception.lineno, 5)
        self.assertEqual(ctx.exception.line, "B -->")


if __name__ == "__main__":
    unittest.main()
