# labskills

Skills do Claude Code para o LABDAPS (Laboratório de Big Data e Análise Preditiva em Saúde, FSP-USP). Repositório colaborativo e aberto: estudantes e professores adicionam, melhoram e compartilham skills que ajudam no fluxo de trabalho do laboratório, de modelagem preditiva em saúde até escrita e submissão de artigos.

## O que é uma skill

Uma skill é um conjunto de instruções em Markdown que o Claude Code carrega sob demanda para executar uma tarefa especializada. Cada skill vive em `skills/<nome>/SKILL.md`, com um cabeçalho YAML (`name`, `description`) que define quando ela é acionada. Saiba mais em [docs.claude.com/claude-code](https://docs.claude.com/en/docs/claude-code/skills).

## Plugins e skills disponíveis

As skills são distribuídas como plugins do Claude Code. Cada plugin agrupa as skills de um domínio, e este repositório é o marketplace `labdaps`, o catálogo de onde os plugins são instalados. Quem instala escolhe só os domínios de que precisa e recebe as atualizações do repositório sem copiar pasta. Saiba mais em [code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins/overview).

| Plugin | Skills | Quando instalar |
|--------|--------|-----------------|
| `grafo` | graph-lab | Em projeto que roda experimento: o ai-lab-hub exige o grafo antes de despachar os agentes. |
| `ml` | ml-checkpoints, ml-pipeline, ml-eval-report, ml-timeseries | Em projeto que treina, ajusta ou avalia modelo. A ml-checkpoints é a norma de método do laboratório. |
| `paper` | paper-review, peer-review, paper-scaffold, artigo, radar-academico, update-paper | Em projeto que busca literatura ou escreve artigo. |
| `datasus` | datasus-outcome | No app lab-ai-prediction e em projeto que cria desfecho nele. |

### Plugin `grafo`

| Skill | O que faz |
|-------|-----------|
| [graph-lab](skills/graph-lab/SKILL.md) | Modela a tarefa como grafo dirigido antes de rodar código: cada etapa vira nó com métrica de sucesso, e efeitos colaterais entre métricas (imputação vs. calibração, seleção de features vs. interpretabilidade) são auditados antes da execução. Perfil geral para engenharia e perfil saúde/ML, obrigatório quando a tarefa treina modelo, com as 7 fases de projeto do laboratório, checklist anti-leakage e regra de dados. É a skill de grafo canônica do laboratório e substitui a graph-init. |

### Plugin `ml`

| Skill | O que faz |
|-------|-----------|
| [ml-checkpoints](skills/ml-checkpoints/SKILL.md) | Conduz o pipeline por checkpoints interativos: diagnostica a base carregada (missing, sentinelas, cardinalidade, repetição de paciente, vazamento) e em cada etapa oferece só as estratégias que os dados permitem, da separação à interpretabilidade, registrando cada decisão com o motivo medido. |
| [ml-pipeline](skills/ml-pipeline/SKILL.md) | Pipeline padrão de ML para projetos de saúde: executa as decisões registradas pela ml-checkpoints e segue a API do [lab-ai-prediction](https://github.com/fabianofilho/lab-ai-prediction) (separação antes do tuning, train_cv, OOF probs, calibração, janelas temporais). |
| [ml-eval-report](skills/ml-eval-report/SKILL.md) | Relatório de avaliação reusando `core/models/evaluation.py`: ROC, PR, calibração, SHAP, métricas por subgrupo e comparação entre estados/períodos. |
| [ml-timeseries](skills/ml-timeseries/SKILL.md) | Setup de modelos de séries temporais em saúde (skforecast, ARIMA, LSTM, Prophet). |

### Plugin `paper`

| Skill | O que faz |
|-------|-----------|
| [paper-review](skills/paper-review/SKILL.md) | Leitura crítica estruturada de artigo externo: resumo, metodologia, pontos fortes e fracos. |
| [peer-review](skills/peer-review/SKILL.md) | Simula revisão por pares do seu próprio manuscrito antes de submeter: nota 1-5 por dimensão (Abstract, Métodos, Resultados, etc.), lista de revisões prioritárias e decisão editorial (Aceito / Revisões menores / Revisões maiores / Rejeitar). |
| [paper-scaffold](skills/paper-scaffold/SKILL.md) | Estrutura de artigo com seções, checklist e template LaTeX/Markdown. |
| [artigo](skills/artigo/SKILL.md) | Pipeline em 7 fases de escrita de artigo em IA médica com reporting guidelines (TRIPOD+AI, STROBE, PRISMA, CONSORT, STARD). |
| [radar-academico](skills/radar-academico/SKILL.md) | Busca semanal de papers por tema, filtra, baixa PDFs e resume. |
| [update-paper](skills/update-paper/SKILL.md) | Atualiza seções de resultados em LaTeX quando análises ou métricas mudam. |

### Plugin `datasus`

| Skill | O que faz |
|-------|-----------|
| [datasus-outcome](skills/datasus-outcome/SKILL.md) | Adiciona um novo desfecho preditivo ao app [lab-ai-prediction](https://github.com/fabianofilho/lab-ai-prediction): subclasse de `OutcomeConfig`, registro, metodologia, censura e checklist anti-leakage. |

## Como usar

### Pelo marketplace (recomendado)

Numa sessão do Claude Code, registre o marketplace uma vez e instale os plugins que quiser:

```
/plugin marketplace add labdaps/labskills
/plugin install grafo@labdaps
/plugin install ml@labdaps
/plugin install paper@labdaps
/plugin install datasus@labdaps
```

No terminal, os mesmos passos são `claude plugin marketplace add labdaps/labskills` e `claude plugin install grafo@labdaps`. O identificador de instalação é sempre `<plugin>@labdaps`.

As skills mantêm o nome: `/graph-lab` continua acionando a graph-lab, assim como o pedido em linguagem natural. A forma completa, com o plugin na frente, é `/grafo:graph-lab`, e serve quando outro comando já ocupa o nome curto.

Os plugins não fixam versão, então cada commit na `main` vira uma versão nova. Para receber as mudanças, rode `/plugin marketplace update labdaps` ou ligue a atualização automática do marketplace `labdaps` no painel `/plugin`.

**Não misture com o `install.sh`.** Se você já instalou por cópia, apague de `~/.claude/skills/` as pastas das skills que agora vêm de plugin. As duas versões carregam juntas: a cópia fica com o nome curto e parada no dia em que foi feita, e o plugin só responde pelo nome com prefixo.

### Declarar os plugins num projeto

Um projeto do laboratório declara no `.claude/settings.json`, versionado, o marketplace e os plugins que usa. Quem clona o repositório e confia na pasta ao abrir o Claude Code recebe os plugins sem instalar nada à mão.

```json
{
  "extraKnownMarketplaces": {
    "labdaps": {
      "source": {
        "source": "github",
        "repo": "labdaps/labskills"
      }
    }
  },
  "enabledPlugins": {
    "grafo@labdaps": true,
    "ml@labdaps": true,
    "paper@labdaps": true
  }
}
```

Esse é o conjunto de um projeto de pesquisa que treina modelo e escreve artigo, como o datasus-preprocessing-benchmark e o sinan-continual-learning. O plugin `datasus` fica de fora de propósito: entra só no app lab-ai-prediction e em projeto que cria desfecho nele, com a linha `"datasus@labdaps": true`. Em outro projeto, a datasus-outcome dispararia em pedidos de "novo desfecho" mandando editar código que o projeto não tem.

Detalhes que costumam pegar:

- Se o projeto já tem `.claude/settings.json`, acrescente as duas chaves às que ele já tem. O comando `claude plugin marketplace add labdaps/labskills --scope project`, rodado na raiz do projeto, grava a parte do marketplace.
- O Claude Code só registra o marketplace depois que a pessoa aceita o diálogo de confiança da pasta. Antes disso, a chave é ignorada sem aviso.
- Sessão na nuvem (Claude Code na web) não instala os plugins declarados no `.claude/settings.json` do repositório. Veja abaixo como escolher.

#### Projeto aberto na nuvem: plugins ou cópia versionada

Na nuvem valem só as skills ativadas na conta do claude.ai e as que o projeto versiona em `.claude/skills/`. Cada projeto escolhe um dos dois caminhos, nunca os dois: fora da nuvem, a cópia e os plugins carregam juntos, e cada skill aparece duas vezes (`/graph-lab` e `/grafo:graph-lab`).

- **Todos trabalham no projeto só na máquina local:** fique com os plugins, pelo trecho acima. Eles se atualizam sozinhos.
- **Alguém abre o projeto no Claude Code na web:** fique com a cópia versionada, que também vale na máquina local. Copie só as skills dos plugins que o projeto habilitaria, para não levar a datasus-outcome a projeto que não é o app. Na raiz do clone do labskills:

  ```bash
  CLAUDE_SKILLS_DIR=<projeto>/.claude/skills ./install.sh --plugin grafo --plugin ml --plugin paper
  ```

  No `.claude/settings.json` do projeto, use este trecho no lugar do anterior. Ele desliga, só nesse projeto, os plugins labdaps de quem os instalou na própria conta, que senão carregariam junto com a cópia:

  ```json
  {
    "enabledPlugins": {
      "grafo@labdaps": false,
      "ml@labdaps": false,
      "paper@labdaps": false,
      "datasus@labdaps": false
    }
  }
  ```

  A cópia não se atualiza sozinha: rode o mesmo comando depois de cada `git pull` do labskills e versione o resultado. O script não apaga nada, então skill ou arquivo que saiu do labskills precisa ser apagado à mão.

### Por cópia, com o `install.sh` (alternativa)

Para quem não usa plugins, ou precisa das skills como pastas em `~/.claude/skills/`:

```bash
git clone https://github.com/labdaps/labskills.git
cd labskills
./install.sh
```

O script copia as skills para `~/.claude/skills/`, deixando-as disponíveis em qualquer projeto do Claude Code. Rodar de novo, depois de um `git pull`, atualiza os arquivos já instalados. A pasta `tests/` de uma skill fica de fora: ela guarda os testes dos scripts, que rodam no CI deste repositório e não servem à skill instalada.

#### Instalar uma skill específica

```bash
cp -r skills/peer-review ~/.claude/skills/
```

Na cópia manual de uma skill com `tests/` (hoje, a `graph-lab`), apague essa pasta do destino. Para copiar só as skills de um plugin, com a mesma exclusão de `tests/`, use `./install.sh --plugin ml` (repetível, um `--plugin` por plugin).

Depois é só acionar no Claude Code: `/peer-review` ou pedir em linguagem natural ("faz peer review do meu manuscrito", "revisa meu artigo como revisor de journal").

## Como contribuir

Toda contribuição é bem-vinda. Veja [CONTRIBUTING.md](CONTRIBUTING.md) para o guia completo de como criar, testar e abrir PR de uma skill nova, incluindo em qual plugin ela entra.

## Licença

[MIT](LICENSE). Use, adapte e compartilhe.
