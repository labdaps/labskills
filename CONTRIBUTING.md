# Como contribuir

Este repositório é do LABDAPS. Estudantes e professores podem propor skills novas ou melhorar as existentes. Não precisa ser especialista em Claude Code: se você tem um fluxo que repete (rodar um modelo, formatar um resultado, revisar um paper), ele provavelmente vira uma skill.

## O formato de uma skill

Cada skill é uma pasta dentro de `skills/` com um arquivo `SKILL.md`:

```
skills/
  minha-skill/
    SKILL.md          # obrigatório
    references/        # opcional: material de apoio que a skill consulta
```

O `SKILL.md` começa com um cabeçalho YAML e depois as instruções em Markdown:

```markdown
---
name: minha-skill
description: O que a skill faz e quando deve ser acionada. Inclua os gatilhos, ex: "Triggers on /minha-skill, 'monta o X', 'gera o Y'".
---

# Skill: minha-skill

Uma frase explicando o objetivo.

## Quando usar

- `/minha-skill`
- Pedidos como "..."

## Passos

### 1. ...
### 2. ...
```

Regras do `description`:

- Escreva em uma linha densa. É esse texto que o Claude usa para decidir se aciona a skill, então liste os gatilhos reais (comando `/`, frases em linguagem natural).
- Seja específico sobre o domínio (saúde, ML, escrita) para não disparar fora de hora.

## Passo a passo para adicionar uma skill

1. Faça fork ou crie um branch: `git checkout -b skill/minha-skill`
2. Crie `skills/minha-skill/SKILL.md` seguindo o formato acima.
3. Teste localmente: copie para `~/.claude/skills/` e acione no Claude Code para confirmar que ela dispara e funciona.
4. Adicione a skill na tabela do [README.md](README.md).
5. Valide antes de subir: `python scripts/validate_skills.py` (checa frontmatter, nome da pasta, link no README e ausência de segredos). O CI roda essa mesma checagem em cada PR.
6. Commit e abra um Pull Request descrevendo o que a skill faz e em qual cenário do laboratório ela ajuda.

## Padrões do repositório

- **Português correto**, com acentuação normal.
- **Sem dados pessoais ou segredos**: nada de tokens, caminhos absolutos da sua máquina (`/Users/seunome/...`), e-mails, IPs de servidor ou credenciais. Skills são genéricas e reutilizáveis por todo o lab.
- **Sem travessões decorativos, aspas tipográficas ou reticências Unicode.** Use vírgula, ponto, aspas retas e três pontos normais.
- **Uma skill, um propósito.** Se ela faz coisas demais, divida.
- **Caminhos relativos e configuráveis.** Pergunte ao usuário ou infira do contexto em vez de fixar caminhos.

## Revisão

PRs são revisados por mantenedores do LABDAPS. O foco da revisão é: a skill é genérica, não vaza dados pessoais, dispara nos gatilhos certos e ajuda de fato em um fluxo do laboratório.
