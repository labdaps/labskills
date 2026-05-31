# CLAUDE.md

Instruções para o Claude Code ao trabalhar neste repositório.

## Sobre este projeto

`labskills` é o repositório colaborativo de skills do Claude Code do LABDAPS (Laboratório de Big Data e Análise Preditiva em Saúde, FSP-USP). Estudantes e professores contribuem com skills que ajudam no fluxo do laboratório: modelagem preditiva em saúde, avaliação de modelos, séries temporais, revisão e escrita de artigos científicos.

## Estrutura

```
skills/<nome>/SKILL.md        # cada skill, com cabeçalho YAML name + description
skills/<nome>/references/      # material de apoio opcional da skill
install.sh                     # instala todas as skills em ~/.claude/skills/
CONTRIBUTING.md                # guia para adicionar skills
```

## Ao adicionar ou editar skills

- Cada skill é uma pasta `skills/<nome>/` com `SKILL.md`. O `name` no YAML deve bater com o nome da pasta.
- O `description` é uma linha densa com os gatilhos reais (comando `/`, frases em linguagem natural). É o que decide o acionamento.
- Mantenha as skills genéricas e reutilizáveis. Nada específico de um projeto ou máquina.
- Ao adicionar uma skill, atualize a tabela no README.md.

## Regras de conteúdo

- Sem dados pessoais ou segredos: nada de tokens, e-mails, IPs, credenciais ou caminhos absolutos de máquina pessoal.
- Português correto, com acentuação normal.
- Sem travessões (em dash, en dash), hífens decorativos como separador, aspas tipográficas ou reticências Unicode. Use vírgula, ponto, dois pontos, aspas retas e três pontos normais.
- Prefira editar a reescrever arquivos inteiros.
