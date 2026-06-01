# labskills

Skills do Claude Code para o LABDAPS (Laboratório de Big Data e Análise Preditiva em Saúde, FSP-USP). Repositório colaborativo e aberto: estudantes e professores adicionam, melhoram e compartilham skills que ajudam no fluxo de trabalho do laboratório, de modelagem preditiva em saúde até escrita e submissão de artigos.

## O que é uma skill

Uma skill é um conjunto de instruções em Markdown que o Claude Code carrega sob demanda para executar uma tarefa especializada. Cada skill vive em `skills/<nome>/SKILL.md`, com um cabeçalho YAML (`name`, `description`) que define quando ela é acionada. Saiba mais em [docs.claude.com/claude-code](https://docs.claude.com/en/docs/claude-code/skills).

## Skills disponíveis

### DataSUS e pipeline do laboratório

| Skill | O que faz |
|-------|-----------|
| [datasus-outcome](skills/datasus-outcome/SKILL.md) | Adiciona um novo desfecho preditivo ao pipeline [datasus-ai-prediction](https://github.com/fabianofilho/datasus-ai-prediction): subclasse de `OutcomeConfig`, registro e checklist anti-leakage. |

### Ciência de dados e ML

| Skill | O que faz |
|-------|-----------|
| [ml-pipeline](skills/ml-pipeline/SKILL.md) | Pipeline padrão de ML para projetos de saúde, alinhado às convenções do datasus-ai-prediction (train_cv, OOF probs, calibração, janelas temporais). |
| [ml-eval-report](skills/ml-eval-report/SKILL.md) | Relatório de avaliação reusando `core/models/evaluation.py`: ROC, PR, calibração, SHAP, métricas por subgrupo e comparação entre estados/períodos. |
| [ml-timeseries](skills/ml-timeseries/SKILL.md) | Setup de modelos de séries temporais em saúde (skforecast, ARIMA, LSTM, Prophet). |

### Pesquisa e escrita científica

| Skill | O que faz |
|-------|-----------|
| [paper-review](skills/paper-review/SKILL.md) | Leitura crítica estruturada de artigo externo: resumo, metodologia, pontos fortes e fracos. |
| [peer-review](skills/peer-review/SKILL.md) | Simula revisão por pares do seu próprio manuscrito antes de submeter: nota 1-5 por dimensão (Abstract, Métodos, Resultados, etc.), lista de revisões prioritárias e decisão editorial (Aceito / Revisões menores / Revisões maiores / Rejeitar). |
| [paper-scaffold](skills/paper-scaffold/SKILL.md) | Estrutura de artigo com seções, checklist e template LaTeX/Markdown. |
| [artigo](skills/artigo/SKILL.md) | Pipeline em 7 fases de escrita de artigo em IA médica com reporting guidelines (TRIPOD+AI, STROBE, PRISMA, CONSORT, STARD). |
| [radar-academico](skills/radar-academico/SKILL.md) | Busca semanal de papers por tema, filtra, baixa PDFs e resume. |
| [update-paper](skills/update-paper/SKILL.md) | Atualiza seções de resultados em LaTeX quando análises ou métricas mudam. |

## Como usar

### Instalação rápida (todas as skills)

```bash
git clone https://github.com/labdaps/labskills.git
cd labskills
./install.sh
```

O script copia as skills para `~/.claude/skills/`, deixando-as disponíveis em qualquer projeto do Claude Code.

### Instalar uma skill específica

```bash
cp -r skills/peer-review ~/.claude/skills/
```

Depois é só acionar no Claude Code: `/peer-review` ou pedir em linguagem natural ("faz peer review do meu manuscrito", "revisa meu artigo como revisor de journal").

## Como contribuir

Toda contribuição é bem-vinda. Veja [CONTRIBUTING.md](CONTRIBUTING.md) para o guia completo de como criar, testar e abrir PR de uma skill nova.

## Licença

[MIT](LICENSE). Use, adapte e compartilhe.
