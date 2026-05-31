#!/usr/bin/env python3
"""Valida as skills do repositorio. Roda no CI e localmente.

Checa, para cada skills/<nome>/SKILL.md:
- existe SKILL.md
- tem frontmatter YAML com name e description
- o campo name bate com o nome da pasta
- nao ha segredos obvios (tokens, e-mails, IPs, caminhos pessoais)
- a skill esta linkada no README.md

Sem dependencias externas: so stdlib.
Sai com codigo 1 se houver qualquer erro.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
README = ROOT / "README.md"

# Padroes que nao podem aparecer no conteudo das skills
SECRET_PATTERNS = [
    (r"gho_[A-Za-z0-9]{20,}", "token GitHub"),
    (r"sk-ant-[A-Za-z0-9-]{20,}", "chave Anthropic"),
    (r"sk-[A-Za-z0-9]{20,}", "chave de API"),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}", "token Slack"),
    (r"AKIA[0-9A-Z]{16}", "chave AWS"),
    (r"discord(?:app)?\.com/api/webhooks/\d+/", "webhook Discord"),
    (r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "endereco IP"),
    (r"/Users/[a-z][a-z0-9._-]+/", "caminho pessoal de maquina"),
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "e-mail"),
]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    fields: dict[str, str] = {}
    for line in m.group(1).splitlines():
        # captura "chave:" no nivel raiz (valor pode estar inline ou em bloco abaixo)
        km = re.match(r"^([a-zA-Z_]+):(.*)$", line)
        if km:
            fields[km.group(1)] = km.group(2).strip()
    return fields


def main() -> int:
    errors: list[str] = []

    if not SKILLS_DIR.is_dir():
        print("ERRO: pasta skills/ nao encontrada")
        return 1

    readme_text = README.read_text(encoding="utf-8") if README.exists() else ""
    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())

    if not skill_dirs:
        print("ERRO: nenhuma skill em skills/")
        return 1

    for d in skill_dirs:
        name = d.name
        skill_md = d / "SKILL.md"

        if not skill_md.exists():
            errors.append(f"{name}: falta SKILL.md")
            continue

        text = skill_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)

        if fm is None:
            errors.append(f"{name}: SKILL.md sem frontmatter YAML (--- ... ---)")
        else:
            if "name" not in fm:
                errors.append(f"{name}: frontmatter sem campo 'name'")
            elif fm["name"] and fm["name"] != name:
                errors.append(
                    f"{name}: campo name='{fm['name']}' nao bate com a pasta '{name}'"
                )
            if "description" not in fm:
                errors.append(f"{name}: frontmatter sem campo 'description'")

        # link no README
        if readme_text and f"skills/{name}/SKILL.md" not in readme_text:
            errors.append(f"{name}: nao esta linkada no README.md")

        # scan de segredos em todos os arquivos da skill
        for f in d.rglob("*"):
            if not f.is_file():
                continue
            try:
                content = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for pat, label in SECRET_PATTERNS:
                hit = re.search(pat, content)
                if hit:
                    rel = f.relative_to(ROOT)
                    errors.append(f"{name}: possivel {label} em {rel}: '{hit.group(0)}'")

    if errors:
        print(f"FALHOU com {len(errors)} problema(s):\n")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: {len(skill_dirs)} skills validadas, sem problemas.")
    for d in skill_dirs:
        print(f"  - {d.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
