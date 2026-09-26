"""Testes do scripts/validate_marketplace.py. Stdlib pura (unittest).

Rodar da raiz do labskills:
    python3 -m pytest tests
ou, sem pytest:
    python3 -m unittest discover -s tests -v

TestRepositorio roda o validador sobre este repositório. TestCasosQuebrados monta um
marketplace mínimo numa pasta temporária, quebra uma regra por teste e confere
que o validador acusa exatamente aquela quebra, para provar que cada checagem
morde e não só que o repositório atual passa.
"""
import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "validate_marketplace", RAIZ / "scripts" / "validate_marketplace.py"
)
vm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vm)


class TestRepositorio(unittest.TestCase):
    def test_marketplace_do_repositorio_valido(self):
        self.assertEqual(vm.validar(RAIZ), [])

    def test_publicados_batem_com_o_marketplace(self):
        # Um plugin novo entra em PLUGINS_PUBLICADOS no mesmo PR, para ganhar a
        # proteção contra renomeação. Este teste lembra quem esqueceu.
        dados = json.loads((RAIZ / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(p["name"] for p in dados["plugins"]), sorted(vm.PLUGINS_PUBLICADOS))

    def test_cada_skill_do_install_sh_vira_plugin(self):
        # install.sh copia toda pasta de skills/; o marketplace precisa cobrir as mesmas.
        dados = json.loads((RAIZ / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        no_marketplace = sorted(c.split("/")[-1] for p in dados["plugins"] for c in p["skills"])
        em_disco = sorted(p.name for p in (RAIZ / "skills").iterdir() if p.is_dir())
        self.assertEqual(no_marketplace, em_disco)


README_BASE = """# teste

```
/plugin marketplace add org/repo
/plugin install um@mkt
/plugin install dois@mkt
```

```json
{
  "extraKnownMarketplaces": {
    "mkt": {"source": {"source": "github", "repo": "org/repo"}}
  },
  "enabledPlugins": {"um@mkt": true}
}
```
"""

MARKETPLACE_BASE = {
    "name": "mkt",
    "description": "marketplace de teste",
    "owner": {"name": "LABDAPS"},
    "plugins": [
        {"name": "um", "description": "a", "source": "./", "strict": False, "skills": ["./skills/alfa"]},
        {"name": "dois", "description": "b", "source": "./", "strict": False, "skills": ["./skills/beta"]},
    ],
}


class TestCasosQuebrados(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for nome in ("alfa", "beta"):
            pasta = self.tmp / "skills" / nome
            pasta.mkdir(parents=True)
            (pasta / "SKILL.md").write_text(f"---\nname: {nome}\ndescription: x\n---\n", encoding="utf-8")
        (self.tmp / ".claude-plugin").mkdir()
        (self.tmp / "README.md").write_text(README_BASE, encoding="utf-8")
        self.dados = copy.deepcopy(MARKETPLACE_BASE)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def validar(self, publicados=("um", "dois")):
        (self.tmp / ".claude-plugin" / "marketplace.json").write_text(json.dumps(self.dados), encoding="utf-8")
        return vm.validar(self.tmp, marketplace="mkt", repo="org/repo", publicados=publicados)

    def assertUmErro(self, erros, trecho):
        self.assertEqual(len(erros), 1, erros)
        self.assertIn(trecho, erros[0])

    def test_base_valida(self):
        self.assertEqual(self.validar(), [])

    def test_json_invalido(self):
        (self.tmp / ".claude-plugin" / "marketplace.json").write_text("{", encoding="utf-8")
        erros = vm.validar(self.tmp, marketplace="mkt", repo="org/repo", publicados=())
        self.assertUmErro(erros, "JSON inválido")

    def test_sem_marketplace_json(self):
        erros = vm.validar(self.tmp, marketplace="mkt", repo="org/repo", publicados=())
        self.assertUmErro(erros, "falta marketplace.json")

    def test_nome_do_marketplace_mudou(self):
        self.dados["name"] = "outro"
        self.assertUmErro(self.validar(), "name do marketplace")

    def test_sem_owner(self):
        del self.dados["owner"]
        self.assertUmErro(self.validar(), "owner.name")

    def test_campo_desconhecido_na_entrada(self):
        entrada = self.dados["plugins"][0]
        entrada["skils"] = entrada.pop("skills")
        erros = self.validar()
        self.assertTrue(any("campo desconhecido 'skils'" in e for e in erros), erros)
        self.assertTrue(any("skills precisa ser uma lista" in e for e in erros), erros)

    def test_nome_de_plugin_com_maiuscula(self):
        self.dados["plugins"][1]["name"] = "Dois"
        erros = self.validar(publicados=("um",))
        self.assertTrue(any("precisa ser minúsculo" in e for e in erros), erros)

    def test_plugin_repetido(self):
        self.dados["plugins"][1]["name"] = "um"
        erros = self.validar(publicados=("um",))
        self.assertTrue(any("aparece mais de uma vez" in e for e in erros), erros)

    def test_skill_fora_de_todo_plugin(self):
        self.dados["plugins"][1]["skills"] = ["./skills/alfa"]
        erros = self.validar()
        self.assertTrue(any("'beta' não está em nenhum plugin" in e for e in erros), erros)
        self.assertTrue(any("'alfa' está em mais de um plugin" in e for e in erros), erros)

    def test_skill_nova_sem_plugin(self):
        pasta = self.tmp / "skills" / "gama"
        pasta.mkdir()
        (pasta / "SKILL.md").write_text("---\nname: gama\ndescription: x\n---\n", encoding="utf-8")
        self.assertUmErro(self.validar(), "'gama' não está em nenhum plugin")

    def test_caminho_inexistente(self):
        self.dados["plugins"][1]["skills"].append("./skills/delta")
        self.assertUmErro(self.validar(), "./skills/delta não existe")

    def test_caminho_que_sai_da_raiz(self):
        self.dados["plugins"][1]["skills"] = ["./skills/../skills/beta"]
        erros = self.validar()
        self.assertTrue(any("'..'" in e for e in erros), erros)

    def test_caminho_fora_de_skills(self):
        self.dados["plugins"][1]["skills"] = ["./beta"]
        erros = self.validar()
        self.assertTrue(any("forma ./skills/<nome>" in e for e in erros), erros)

    def test_source_diferente_da_raiz(self):
        self.dados["plugins"][0]["source"] = "./skills/alfa"
        self.assertUmErro(self.validar(), "source precisa ser")

    def test_strict_true(self):
        self.dados["plugins"][0]["strict"] = True
        self.assertUmErro(self.validar(), "strict precisa ser false")

    def test_version_fixa(self):
        self.dados["plugins"][0]["version"] = "1.0.0"
        self.assertUmErro(self.validar(), "não fixe version")

    def test_plugin_publicado_removido_sem_renames(self):
        self.dados["plugins"][1]["name"] = "tres"
        erros = self.validar()
        self.assertTrue(any("plugin publicado 'dois' sumiu" in e for e in erros), erros)

    def test_plugin_publicado_renomeado_com_renames(self):
        self.dados["plugins"][1]["name"] = "tres"
        self.dados["renames"] = {"dois": "tres"}
        readme = README_BASE.replace("dois@mkt", "tres@mkt")
        (self.tmp / "README.md").write_text(readme, encoding="utf-8")
        self.assertEqual(self.validar(), [])

    def test_plugin_json_na_raiz(self):
        (self.tmp / ".claude-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
        self.assertUmErro(self.validar(), ".claude-plugin/plugin.json na raiz")

    def test_pasta_de_componente_na_raiz(self):
        (self.tmp / "commands").mkdir()
        self.assertUmErro(self.validar(), "commands na raiz")

    def test_readme_sem_instalacao_de_um_plugin(self):
        (self.tmp / "README.md").write_text(README_BASE.replace("/plugin install dois@mkt\n", ""), encoding="utf-8")
        self.assertUmErro(self.validar(), "'/plugin install dois@mkt'")

    def test_readme_sem_trecho_de_settings(self):
        readme = README_BASE[: README_BASE.index("```json")]
        (self.tmp / "README.md").write_text(readme, encoding="utf-8")
        self.assertUmErro(self.validar(), "trecho de .claude/settings.json")

    def test_readme_habilita_plugin_inexistente(self):
        (self.tmp / "README.md").write_text(README_BASE.replace('"um@mkt": true', '"zeta@mkt": true'), encoding="utf-8")
        self.assertUmErro(self.validar(), "'zeta@mkt'")

    def test_readme_com_repo_errado(self):
        (self.tmp / "README.md").write_text(README_BASE.replace('"repo": "org/repo"', '"repo": "org/outro"'), encoding="utf-8")
        self.assertUmErro(self.validar(), "extraKnownMarketplaces precisa declarar")

    def test_readme_com_formato_antigo_de_lista(self):
        # Formato que circula em resumo não oficial e que o Claude Code não lê:
        # lista de repositórios em vez de objeto por nome de marketplace.
        errado = README_BASE.replace(
            '"mkt": {"source": {"source": "github", "repo": "org/repo"}}', ""
        ).replace('"extraKnownMarketplaces": {\n    \n  }', '"extraKnownMarketplaces": ["org/repo"]')
        (self.tmp / "README.md").write_text(errado, encoding="utf-8")
        self.assertUmErro(self.validar(), "extraKnownMarketplaces precisa declarar")


if __name__ == "__main__":
    unittest.main()
