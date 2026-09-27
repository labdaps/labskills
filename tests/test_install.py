"""Testes do install.sh. Stdlib pura (unittest); precisam de bash.

Rodar da raiz do labskills:
    python3 -m pytest tests

A cópia versionada em <projeto>/.claude/skills/ é feita com --plugin, e não pode
levar skill de plugin que o projeto não habilita: a datasus-outcome, por exemplo,
dispararia em pedido de novo desfecho num projeto que não é o app.
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASH = shutil.which("bash")


def _skills_do_plugin(*plugins):
    dados = json.loads((RAIZ / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    por_nome = {p["name"]: p["skills"] for p in dados["plugins"]}
    return sorted({c.rstrip("/").split("/")[-1] for nome in plugins for c in por_nome[nome]})


@unittest.skipUnless(BASH, "precisa de bash")
class TestInstall(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.dest = self.tmp / "projeto" / ".claude" / "skills"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def instalar(self, *args):
        env = dict(os.environ, CLAUDE_SKILLS_DIR=str(self.dest))
        return subprocess.run(
            [BASH, str(RAIZ / "install.sh"), *args],
            env=env, capture_output=True, text=True, check=False,
        )

    def instaladas(self):
        return sorted(p.name for p in self.dest.iterdir()) if self.dest.is_dir() else []

    def test_sem_argumento_copia_todas_sem_tests(self):
        r = self.instalar()
        self.assertEqual(r.returncode, 0, r.stderr)
        em_disco = sorted(p.name for p in (RAIZ / "skills").iterdir() if p.is_dir())
        self.assertEqual(self.instaladas(), em_disco)
        self.assertFalse((self.dest / "graph-lab" / "tests").exists())

    def test_segunda_execucao_nao_aninha(self):
        self.instalar()
        r = self.instalar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.dest / "graph-lab" / "graph-lab").exists())

    def test_plugin_copia_so_as_skills_dele(self):
        r = self.instalar("--plugin", "grafo", "--plugin=ml", "--plugin", "paper", "--plugin", "ml")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.instaladas(), _skills_do_plugin("grafo", "ml", "paper"))
        self.assertNotIn("datasus-outcome", self.instaladas())
        self.assertFalse((self.dest / "graph-lab" / "tests").exists())

    def test_plugin_inexistente_falha_sem_copiar_nada(self):
        r = self.instalar("--plugin", "grafo", "--plugin", "zeta")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("zeta", r.stderr)
        self.assertEqual(self.instaladas(), [])

    def test_plugin_sem_nome_falha(self):
        r = self.instalar("--plugin")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.instaladas(), [])

    def test_argumento_desconhecido_falha(self):
        r = self.instalar("grafo")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("argumento desconhecido", r.stderr)
        self.assertEqual(self.instaladas(), [])


if __name__ == "__main__":
    unittest.main()
