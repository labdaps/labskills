---
name: update-paper
description: Atualiza secoes de resultados em arquivos LaTeX (.tex) quando analises, metricas ou CSVs mudam. Use apos rodar pipelines de ML/calibracao que geram novos resultados, apos correcoes de bugs que alteram numeros, ou quando o usuario pedir /update-paper ou "atualiza o paper/latex".
---

# Skill: update-paper

Sincroniza arquivos `.tex` do projeto com os resultados numericos mais recentes.
Trata apenas das secoes de resultados e metodologia afetadas pelas mudancas.

## Quando usar

- Apos rodar um pipeline que gera ou atualiza CSVs de resultados
- Apos correcao de bug que muda valores numericos
- Apos adicionar novo metodo ou regiao ao pipeline
- Quando o usuario pede `/update-paper`, "atualiza o paper", "atualiza o latex"
- Ao final de sessao com mudancas significativas em analises

## Passos

### 1. Mapear o projeto

Rodar em paralelo:

```bash
find . -name "*.tex" -not -path "./.git/*" | sort
find . -name "*.csv" -newer . -not -path "./.git/*" | sort
git diff HEAD --stat
git log --oneline -5
```

Identificar:
- Todos os `.tex` no projeto (paper principal, papers de experimentos)
- CSVs de resultados alterados desde o ultimo commit
- O que mudou no diff (novos metodos, regioes, metricas)

### 2. Ler os resultados atuais

Para cada CSV de resultados identificado, ler o conteudo completo.
Exemplos comuns em projetos de calibracao/ML:
- `plots/full_comparison.csv` -- resultados por metodo e regiao
- `plots/fairness_summary.csv` -- metricas de equidade
- `experiments/*/results.csv` -- resultados de experimentos especificos

Calcular os valores resumo que aparecem nos papers:
- Medias por metodo (mean across regions)
- Melhores/piores valores por metrica
- Deltas vs baseline

### 3. Ler os papers LaTeX

Ler cada `.tex` identificado no passo 1.
Localizar:
- Tabelas com resultados numericos (`\begin{tabular}` com valores decimais)
- Valores numericos citados no texto ("ECE = 0.0577", "$-18\%$", etc.)
- TODOs de atualizacao (comentarios `% TODO`)
- Seccoes de resultados e discussao

### 4. Identificar o que atualizar

Para cada valor numerico no `.tex`, verificar se difere dos resultados atuais nos CSVs.
Priorizar:
1. Tabelas de resultados (maior impacto, mais propenso a desatualizar)
2. Valores citados no abstract e conclusao
3. Valores citados na discussao
4. TODOs marcados no arquivo

Nao alterar:
- Equacoes e definicoes formais
- Referencias bibliograficas
- Secoes de metodologia (a menos que o metodo tenha mudado)
- Texto narrativo que nao depende de valores numericos especificos

### 5. Aplicar as atualizacoes

Atualizar apenas o que mudou. Para cada alteracao:
- Usar `Edit` para substituicoes pontuais (nunca reescrever o arquivo inteiro)
- Manter o estilo LaTeX existente (precisao decimal, formato de tabela)
- Remover comentarios `% TODO` dos itens resolvidos
- Adicionar comentario `% updated YYYY-MM-DD` nas tabelas alteradas

Regras de estilo (manter consistencia com o paper):
- Se o paper usa 4 casas decimais -> manter 4 casas
- Se usa `\textbf{}` para melhor resultado -> manter
- Se usa `\multirow` -> preservar estrutura

### 6. Verificar consistencia

Apos as edicoes, verificar:
- Abstract ainda reflete os melhores resultados?
- Conclusao ainda e valida com os novos numeros?
- Key findings na discussao continuam corretos?
- Numero de regioes/metodos citados no texto bate com os dados?

### 7. Reportar

Listar de forma concisa:
- Quais arquivos `.tex` foram alterados
- Quais tabelas/valores foram atualizados
- Se houver discrepancias que exigem revisao manual do usuario (ex: interpretacoes na discussao que mudaram de sentido)

## Notas importantes

- NUNCA alterar definicoes formais, equacoes matematicas ou metodologia
- NUNCA inferir interpretacoes clinicas -- apenas atualizar numeros
- Se o sentido de um achado mudou (ex: metodo A era melhor, agora metodo B e melhor),
  reportar ao usuario em vez de reescrever a interpretacao automaticamente
- Respeitar todas as regras de humanizacao do CLAUDE.md (sem travessoes, sem Unicode decorativo)
- Se o paper estiver em PT e EN, atualizar ambos
