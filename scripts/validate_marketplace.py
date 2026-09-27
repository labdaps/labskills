#!/usr/bin/env python3
"""Valida o marketplace de plugins do Claude Code deste repositório. Roda no CI e localmente.

O labskills é um marketplace (`.claude-plugin/marketplace.json`) com um plugin por
domínio. Cada plugin usa a raiz do repositório como `source` e lista as suas skills
no campo `skills`, então as pastas de `skills/` não mudam de lugar e o `install.sh`
continua servindo de alternativa. Como o `source` é a raiz, a entrada do marketplace
é o próprio manifesto do plugin: não existe `plugin.json` por plugin.

Checa:
- JSON válido, com `name`, `owner.name` e `plugins`, sem campo desconhecido
- nome do marketplace estável e nomes de plugin em minúsculas, sem repetição
- nenhum plugin já publicado some sem entrada em `renames`: o nome é a chave que
  os projetos guardam no `enabledPlugins` do `.claude/settings.json`
- cada plugin tem `description`, `source` igual a "./", `strict` false e `skills`
- cada caminho de skill começa com ./skills/, não tem "..", existe e tem SKILL.md
- toda pasta de skills/ aparece em exatamente um plugin
- nenhuma entrada fixa `version`: sem ela, quem instala recebe cada commit
- a raiz não tem `.claude-plugin/plugin.json` nem pasta ou arquivo de componente
  padrão (commands/, agents/, hooks/, .mcp.json...), que entraria em todos os plugins
- o README ensina a instalar cada plugin, e o trecho de `.claude/settings.json`
  dele declara este marketplace e só plugins que existem

Sem dependências externas: só stdlib. Sai com código 1 se houver qualquer erro.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MARKETPLACE = "labdaps"
REPO = "labdaps/labskills"

# Plugins já anunciados. Os projetos guardam "<plugin>@labdaps" no enabledPlugins,
# então tirar um nome daqui, ou do marketplace.json, quebra quem o usa. Para
# renomear ou remover, acrescente o nome antigo em "renames" no marketplace.json.
PLUGINS_PUBLICADOS = ("grafo", "ml", "paper", "datasus")

NOME_RE = re.compile(r"^[a-z][a-z0-9-]*$")

# Chaves que o Claude Code lê no marketplace.json. Ele ignora chave desconhecida sem
# avisar, e um "skils" digitado errado faria o plugin carregar a pasta skills/ inteira.
CAMPOS_TOPO = {
    "$schema", "name", "owner", "plugins", "description", "version", "metadata",
    "forceRemoveDeletedPlugins", "allowCrossMarketplaceDependenciesOn", "renames",
}
CAMPOS_ENTRADA = {
    # campos próprios da entrada
    "name", "source", "description", "version", "category", "tags", "strict",
    "relevance", "dependencies", "defaultEnabled", "displayName", "metadata",
    "headers", "headersHelper",
    # campos do plugin.json que a entrada também aceita
    "author", "homepage", "repository", "license", "keywords", "skills",
    "commands", "agents", "hooks", "mcpServers", "lspServers", "outputStyles",
    "workflows", "experimental", "userConfig", "channels", "settings",
}

# Caminhos que o Claude Code carrega por padrão na raiz de um plugin. Com source "./",
# qualquer um deles na raiz do repositório entraria em todos os plugins de uma vez.
COMPONENTES_NA_RAIZ = (
    ".claude-plugin/plugin.json", "commands", "agents", "hooks", "output-styles",
    "workflows", "themes", "monitors", "bin", ".mcp.json", ".lsp.json",
    "settings.json", "SKILL.md",
)

BLOCO_JSON_RE = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


def _carregar(caminho: Path) -> tuple[dict | None, str | None]:
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"falta {caminho.name} em {caminho.parent.name}/"
    except json.JSONDecodeError as exc:
        return None, f"JSON inválido: {exc}"
    if not isinstance(dados, dict):
        return None, "o marketplace.json precisa ser um objeto JSON"
    return dados, None


def _checar_topo(dados: dict, marketplace: str) -> list[str]:
    erros = []
    for chave in sorted(set(dados) - CAMPOS_TOPO):
        erros.append(f"campo desconhecido no topo: '{chave}'")
    if dados.get("name") != marketplace:
        erros.append(
            f"name do marketplace é {dados.get('name')!r}, esperado '{marketplace}': "
            "o nome é o sufixo @ de todo plugin instalado e não pode mudar"
        )
    dono = dados.get("owner")
    if not isinstance(dono, dict) or not str(dono.get("name", "")).strip():
        erros.append("owner.name é obrigatório")
    if not str(dados.get("description", "")).strip():
        erros.append("falta description do marketplace")
    return erros


def _checar_entrada(i: int, entrada: object, root: Path) -> tuple[list[str], list[str]]:
    """Devolve (erros, caminhos de skill normalizados) de uma entrada de plugin."""
    if not isinstance(entrada, dict):
        return [f"plugins[{i}] não é um objeto"], []
    nome = entrada.get("name")
    rotulo = f"plugin '{nome}'" if nome else f"plugins[{i}]"
    erros = []

    if not isinstance(nome, str) or not NOME_RE.match(nome):
        erros.append(
            f"{rotulo}: name precisa ser minúsculo, começar por letra e usar só "
            "letras, dígitos e hífen"
        )
    for chave in sorted(set(entrada) - CAMPOS_ENTRADA):
        erros.append(f"{rotulo}: campo desconhecido '{chave}'")
    if not str(entrada.get("description", "")).strip():
        erros.append(f"{rotulo}: falta description")
    if entrada.get("source") != "./":
        erros.append(
            f"{rotulo}: source precisa ser \"./\", a raiz do repositório, para as "
            "skills continuarem em skills/<nome>/"
        )
    if entrada.get("strict") is not False:
        erros.append(
            f"{rotulo}: strict precisa ser false, para a entrada ser o manifesto "
            "e um plugin.json na raiz virar erro em vez de se misturar a ela"
        )
    if "version" in entrada:
        erros.append(
            f"{rotulo}: não fixe version; sem ela quem instala acompanha os commits, "
            "com ela só recebe mudança quando o número muda"
        )

    skills = entrada.get("skills")
    if not isinstance(skills, list) or not skills:
        erros.append(
            f"{rotulo}: skills precisa ser uma lista não vazia de caminhos; sem ela o "
            "plugin carregaria a pasta skills/ inteira"
        )
        return erros, []

    caminhos = []
    for caminho in skills:
        if not isinstance(caminho, str):
            erros.append(f"{rotulo}: caminho de skill não é texto: {caminho!r}")
            continue
        if ".." in caminho or "\\" in caminho:
            erros.append(f"{rotulo}: caminho com '..' ou barra invertida: {caminho}")
            continue
        partes = caminho.rstrip("/").split("/")
        if len(partes) != 3 or partes[:2] != [".", "skills"] or not partes[2]:
            erros.append(
                f"{rotulo}: caminho de skill precisa ter a forma ./skills/<nome>: {caminho}"
            )
            continue
        pasta = root / "skills" / partes[2]
        if not (pasta / "SKILL.md").is_file():
            erros.append(f"{rotulo}: {caminho} não existe ou não tem SKILL.md")
            continue
        caminhos.append(partes[2])
    return erros, caminhos


def _checar_readme(root: Path, nomes: set[str], marketplace: str, repo: str) -> list[str]:
    readme = root / "README.md"
    if not readme.is_file():
        return ["falta README.md"]
    texto = readme.read_text(encoding="utf-8")
    erros = []

    if f"/plugin marketplace add {repo}" not in texto:
        erros.append(f"README não mostra '/plugin marketplace add {repo}'")
    for nome in sorted(nomes):
        if f"/plugin install {nome}@{marketplace}" not in texto:
            erros.append(f"README não mostra '/plugin install {nome}@{marketplace}'")

    blocos = [b for b in BLOCO_JSON_RE.findall(texto) if "extraKnownMarketplaces" in b]
    if not blocos:
        erros.append("README não tem o trecho de .claude/settings.json (extraKnownMarketplaces)")
    trechos = []
    for bloco in blocos:
        try:
            trechos.append(json.loads(bloco))
        except json.JSONDecodeError as exc:
            erros.append(f"README: trecho de settings.json com JSON inválido: {exc}")

    for trecho in trechos:
        if not isinstance(trecho, dict):
            erros.append("README: o trecho de settings.json precisa ser um objeto JSON")
            continue
        conhecidos = trecho.get("extraKnownMarketplaces")
        declarado = conhecidos.get(marketplace) if isinstance(conhecidos, dict) else None
        fonte = declarado.get("source") if isinstance(declarado, dict) else None
        if fonte != {"source": "github", "repo": repo}:
            erros.append(
                f"README: extraKnownMarketplaces precisa declarar '{marketplace}' com "
                f'"source": {{"source": "github", "repo": "{repo}"}}'
            )
        habilitados = trecho.get("enabledPlugins")
        if not isinstance(habilitados, dict) or not habilitados:
            erros.append("README: o trecho de settings.json não tem enabledPlugins")
            continue
        for chave, valor in habilitados.items():
            plugin, _, sufixo = chave.partition("@")
            if sufixo != marketplace or plugin not in nomes:
                erros.append(f"README: enabledPlugins cita '{chave}', que não é plugin deste marketplace")
            if not isinstance(valor, bool):
                erros.append(f"README: enabledPlugins['{chave}'] precisa ser true ou false")
    return erros


def validar(
    root: Path = ROOT,
    *,
    marketplace: str = MARKETPLACE,
    repo: str = REPO,
    publicados: tuple[str, ...] = PLUGINS_PUBLICADOS,
) -> list[str]:
    """Devolve a lista de erros do marketplace em `root`. Lista vazia significa válido."""
    dados, erro = _carregar(root / ".claude-plugin" / "marketplace.json")
    if erro:
        return [erro]

    erros = _checar_topo(dados, marketplace)

    plugins = dados.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        return erros + ["plugins precisa ser uma lista não vazia"]

    nomes: list[str] = []
    dono_da_skill: dict[str, list[str]] = {}
    for i, entrada in enumerate(plugins):
        erros_entrada, skills = _checar_entrada(i, entrada, root)
        erros.extend(erros_entrada)
        nome = entrada.get("name") if isinstance(entrada, dict) else None
        if isinstance(nome, str):
            nomes.append(nome)
        for skill in skills:
            dono_da_skill.setdefault(skill, []).append(str(nome))

    for nome in sorted({n for n in nomes if nomes.count(n) > 1}):
        erros.append(f"plugin '{nome}' aparece mais de uma vez")

    renames = dados.get("renames", {})
    if not isinstance(renames, dict):
        erros.append("renames precisa ser um objeto")
        renames = {}
    for nome in publicados:
        if nome not in nomes and nome not in renames:
            erros.append(
                f"plugin publicado '{nome}' sumiu do marketplace sem entrada em renames; "
                f"projetos que declaram '{nome}@{marketplace}' deixariam de carregá-lo"
            )

    pastas = sorted(p.name for p in (root / "skills").iterdir() if p.is_dir()) if (root / "skills").is_dir() else []
    for skill in pastas:
        donos = dono_da_skill.get(skill, [])
        if not donos:
            erros.append(f"skill '{skill}' não está em nenhum plugin do marketplace")
        elif len(donos) > 1:
            erros.append(f"skill '{skill}' está em mais de um plugin: {', '.join(donos)}")
    # Skill citada no marketplace sem pasta em skills/ já foi acusada em
    # _checar_entrada ("não existe ou não tem SKILL.md") e não chega a dono_da_skill.

    for relativo in COMPONENTES_NA_RAIZ:
        if (root / relativo).exists():
            erros.append(
                f"{relativo} na raiz entraria em todos os plugins, porque o source de "
                "cada um é a raiz do repositório"
            )

    erros.extend(_checar_readme(root, set(nomes), marketplace, repo))
    return erros


def main() -> int:
    erros = validar()
    if erros:
        print(f"FALHOU: marketplace com {len(erros)} problema(s):\n")
        for erro in erros:
            print(f"  - {erro}")
        return 1
    dados = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    print(f"OK: marketplace {dados['name']} com {len(dados['plugins'])} plugins.")
    for entrada in dados["plugins"]:
        skills = ", ".join(c.rstrip("/").split("/")[-1] for c in entrada["skills"])
        print(f"  - {entrada['name']}: {skills}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
