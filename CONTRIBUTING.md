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
3. Coloque a skill em um plugin: acrescente `./skills/minha-skill` à lista `skills` de exatamente um plugin em `.claude-plugin/marketplace.json` (veja [Em qual plugin a skill entra](#em-qual-plugin-a-skill-entra)).
4. Teste localmente pelo clone, sem copiar pasta. Na raiz do repositório, abra o Claude Code assim:

   ```bash
   claude --plugin-dir . --settings '{"enabledPlugins": {"grafo@labdaps": false, "ml@labdaps": false, "paper@labdaps": false, "datasus@labdaps": false}}'
   ```

   O `--plugin-dir .` carrega as skills do seu branch como o plugin `labskills`, só nessa sessão. O `--settings` desliga, também só nessa sessão, os plugins do marketplace que você tenha instalado (um `false` por plugin do `marketplace.json`), que senão carregariam a versão publicada junto com a sua. Acione por `/labskills:minha-skill` e em linguagem natural para confirmar que ela dispara e funciona. Não copie para `~/.claude/skills/`: a cópia segue carregando depois do teste, ao lado do plugin. Se você já instalou pelo `install.sh`, a cópia antiga da skill também aparece, com o nome curto, e a versão em teste é a do prefixo `labskills:`.
5. Adicione a skill na tabela do plugin dela no [README.md](README.md).
6. Valide antes de subir: `python scripts/validate_skills.py` (checa frontmatter, nome da pasta, link no README, ausência de segredos e se a skill está em exatamente um plugin) e `python -m pytest tests skills/graph-lab/tests`. Com o Claude Code instalado, rode também `claude plugin validate .`. O CI roda essas checagens em cada PR.
7. Commit e abra um Pull Request descrevendo o que a skill faz e em qual cenário do laboratório ela ajuda.

## Em qual plugin a skill entra

O repositório é o marketplace `labdaps`, e cada plugin agrupa as skills de um domínio. Quem habilita um plugin carrega todas as skills dele, então escolha pelo projeto que vai instalar a skill:

| Plugin | Entra aqui | Exemplos |
|--------|------------|----------|
| `grafo` | planejamento da tarefa como grafo antes de executar | graph-lab |
| `ml` | modelagem preditiva: método, pipeline, avaliação, séries temporais | ml-checkpoints, ml-pipeline, ml-eval-report |
| `paper` | literatura e escrita científica: busca, leitura crítica, redação, revisão | artigo, peer-review, radar-academico |
| `datasus` | código e regras do domínio DataSUS e do app preditivo | datasus-outcome |

Se nenhum servir, proponha um plugin novo no PR em vez de forçar a skill num domínio alheio. Plugin novo precisa de nome curto em minúsculas, que não muda depois de publicado, porque os projetos o guardam no `.claude/settings.json` como `<plugin>@labdaps`. Pelo mesmo motivo, renomear ou remover plugin exige entrada em `renames` no `marketplace.json`.

## Padrões do repositório

- **Português correto**, com acentuação normal.
- **Sem dados pessoais ou segredos**: nada de tokens, caminhos absolutos da sua máquina (`/Users/seunome/...`), e-mails, IPs de servidor ou credenciais. Skills são genéricas e reutilizáveis por todo o lab.
- **Sem travessões decorativos, aspas tipográficas ou reticências Unicode.** Use vírgula, ponto, aspas retas e três pontos normais.
- **Uma skill, um propósito.** Se ela faz coisas demais, divida.
- **Caminhos relativos e configuráveis.** Pergunte ao usuário ou infira do contexto em vez de fixar caminhos.
- **Script da skill por `${CLAUDE_SKILL_DIR}`.** Se a skill manda rodar um script dela, escreva `python "${CLAUDE_SKILL_DIR}/scripts/<arquivo>"`: o Claude Code resolve o caminho tanto no plugin quanto na cópia do `install.sh`.

## Revisão

PRs são revisados por mantenedores do LABDAPS. O foco da revisão é: a skill é genérica, não vaza dados pessoais, dispara nos gatilhos certos e ajuda de fato em um fluxo do laboratório.
