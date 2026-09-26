# CLAUDE.md

Instruções para o Claude Code ao trabalhar neste repositório.

## Sobre este projeto

`labskills` é o repositório colaborativo de skills do Claude Code do LABDAPS (Laboratório de Big Data e Análise Preditiva em Saúde, FSP-USP). Estudantes e professores contribuem com skills que ajudam no fluxo do laboratório: modelagem preditiva em saúde, avaliação de modelos, séries temporais, revisão e escrita de artigos científicos.

## Estrutura

```
.claude-plugin/marketplace.json  # marketplace labdaps: cada plugin lista as skills do seu domínio
skills/<nome>/SKILL.md           # cada skill, com cabeçalho YAML name + description
skills/<nome>/references/        # material de apoio opcional da skill
scripts/validate_skills.py       # valida skills e marketplace; roda no CI
scripts/validate_marketplace.py  # regras do marketplace, chamadas pelo validate_skills.py
tests/                           # testes do validador do marketplace
install.sh                       # alternativa ao marketplace: copia as skills para ~/.claude/skills/
CONTRIBUTING.md                  # guia para adicionar skills
```

O repositório é o marketplace de plugins `labdaps` do Claude Code. Cada plugin (`grafo`, `ml`, `paper`, `datasus`) usa a raiz como `source` e lista as suas skills no campo `skills` da entrada, então as skills ficam em `skills/<nome>/` e o `install.sh` continua funcionando. Não existe `plugin.json` por plugin: a entrada do `marketplace.json` é o manifesto.

## Ao adicionar ou editar skills

- Cada skill é uma pasta `skills/<nome>/` com `SKILL.md`. O `name` no YAML deve bater com o nome da pasta.
- O `description` é uma linha densa com os gatilhos reais (comando `/`, frases em linguagem natural). É o que decide o acionamento.
- Mantenha as skills genéricas e reutilizáveis. Nada específico de um projeto ou máquina.
- Toda skill entra em exatamente um plugin. Ao adicionar uma, acrescente `./skills/<nome>` à lista `skills` do plugin do domínio em `.claude-plugin/marketplace.json` e a linha na tabela desse plugin no README.md. O critério está no CONTRIBUTING.md.
- Não crie, renomeie nem remova plugin sem combinar no PR. O nome do plugin e o do marketplace são a chave que os projetos guardam no `.claude/settings.json`: renomear exige entrada em `renames` no `marketplace.json`, e plugin novo entra em `PLUGINS_PUBLICADOS` no `scripts/validate_marketplace.py`.
- Não fixe `version` nas entradas e não crie `plugin.json`, `commands/`, `agents/`, `hooks/` ou `.mcp.json` na raiz: como a raiz é o `source` de todos os plugins, isso entraria em todos eles.
- Script que a skill manda rodar é citado como `"${CLAUDE_SKILL_DIR}/scripts/<arquivo>"`, que o Claude Code resolve tanto no plugin quanto na cópia do `install.sh`.
- Antes do commit: `python3 scripts/validate_skills.py`, `python3 -m pytest tests skills/graph-lab/tests` e `ruff check .`.

## Regras de conteúdo

- Sem dados pessoais ou segredos: nada de tokens, e-mails, IPs, credenciais ou caminhos absolutos de máquina pessoal.
- Português correto, com acentuação normal.
- Sem travessões (em dash, en dash), hífens decorativos como separador, aspas tipográficas ou reticências Unicode. Use vírgula, ponto, dois pontos, aspas retas e três pontos normais.
- Prefira editar a reescrever arquivos inteiros.
