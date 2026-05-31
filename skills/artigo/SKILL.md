---
name: artigo
description: |
  Reune evidencias cientificas e escreve artigos academicos em IA medica e saude com rigor metodologico. Aplica reporting guidelines (TRIPOD+AI, STROBE, PRISMA, CONSORT, STARD, ARRIVE, CARE, GRADE), estrutura IMRaD, citacoes Vancouver/AMA, e remove padroes de escrita gerados por IA. Pipeline em 7 fases: scoping, evidence gathering, methods design, drafting, anti-IA polish, peer-review interno, submission package. Triggers on /artigo, "escreve um paper sobre", "monta o manuscrito", "estrutura artigo cientifico", "redige um artigo", "reune evidencias para artigo", "prepara submissao".
---

# Skill: artigo

Pipeline completo de escrita de artigo cientifico em IA medica e saude. Combina busca de evidencias, design metodologico, redacao IMRaD, anti padrao IA e checklist de submissao.

## Quando usar

- `/artigo` para iniciar do zero ou continuar manuscrito
- Pedidos como "escreve um paper sobre X", "monta o manuscrito", "redige IMRaD", "reune evidencias para o tema Y"
- Quando ha resultados de pipeline ML prontos e precisa transformar em manuscrito
- Antes de submeter: rodar fase 5 (anti-IA) e fase 6 (peer-review interno)

## Detectar tipo de estudo

Antes de qualquer coisa, identificar o tipo. Cada tipo usa uma reporting guideline diferente:

| Tipo de estudo | Guideline | Quando usar |
|---|---|---|
| Modelo preditivo de IA/ML | **TRIPOD+AI 2024** | Predicao clinica, classificacao, regressao em saude |
| Estudo observacional | **STROBE** | Coortes, caso-controle, transversal |
| Revisao sistematica/meta-analise | **PRISMA 2020** | Sintese de evidencias |
| Ensaio clinico randomizado | **CONSORT 2025** | RCTs |
| Acuracia diagnostica | **STARD** | Sensibilidade, especificidade, AUC de teste diagnostico |
| Protocolo de trial | **SPIRIT** | Submissao de protocolo |
| Estudo pre-clinico animal | **ARRIVE** | Modelos animais |
| Case report | **CARE** | Relato de caso |
| Avaliacao da qualidade da evidencia | **GRADE** | Forca de recomendacao |

Se em duvida, perguntar ao usuario. Documentar a guideline escolhida no manuscrito.

## Pipeline de 7 fases

### Fase 1: Scoping

Coletar com o usuario:
- **Pergunta de pesquisa** em formato PICO/PECO/PIRD
- **Tipo de estudo** (ver tabela acima)
- **Journal alvo** (define formato, word limit, citation style)
- **Dados disponiveis** (pipeline ML pronto? resultados de qual experimento? dataset? csv? metricas em json?)
- **Co-autores** e ordem
- **Deadline**

Saida: `paper/scoping.md` com tudo isso registrado.

### Fase 2: Evidence gathering

Buscar literatura relevante. Usar em paralelo:

```bash
# PubMed via E-utilities
# arXiv via API
# Google Scholar via scraping (cuidado com rate limit)
# Semantic Scholar API (recomendado: tem citation graph)
```

Para cada paper relevante:
1. Salvar PDF em `paper/refs/`
2. Extrair: titulo, autores, ano, DOI, journal, abstract, metodo, resultados principais, contribuicao, limitacoes
3. Classificar epistemicamente: forte/moderada/fraca evidencia (criterios GRADE quando aplicavel)
4. Categorizar em buckets: gap, metodologia, comparacao, validacao externa

Saida: `paper/refs/literature_review.md` com matriz de evidencias e `references.bib` com BibTeX.

**Filtros recomendados:**
- Recencia: priorizar ultimos 5 anos para metodos, ultimos 10 para fundamentos
- Journal impact: nao excluir, mas anotar
- Validacao em populacao similar (LATAM, SUS, populacao brasileira) eh diferencial

### Fase 3: Methods design

Estruturar com base no tipo de estudo. Para TRIPOD+AI 2024 (preditivo):

```
Methods/
  Study Design and Population
    - Source of data (DataSUS? hospital? prontuario eletronico?)
    - Inclusion/exclusion criteria
    - Sample size justification
    - Data linkage if applicable

  Outcome
    - Definicao clara, com codigos CID se aplicavel
    - Time horizon

  Predictors
    - Tabela completa: nome, tipo (numerica/categorica), unidade, missing rate
    - Sentinel values tratados (9, 99, 999)
    - Encoding usado

  Sample Size
    - Calculo baseado em events per variable (EPV >= 10 minimo, idealmente >= 20)
    - Para deep learning: regra de Riley para amostra minima

  Missing Data
    - Padrao MCAR/MAR/MNAR
    - Estrategia: imputacao (qual?), exclusao, multiple imputation

  Statistical Analysis / ML Pipeline
    - Algoritmos testados
    - Hiperparametros e search
    - Cross-validation strategy
    - Train/test split (com data temporal se houver)
    - Metricas: AUROC, AUPRC, calibration (Brier, ICI), DCA

  Validation
    - Internal: bootstrap optimism-corrected
    - External: testar em coorte separada
    - Subgroup analysis

  Fairness/Bias (TRIPOD+AI especifico)
    - Avaliacao por subgrupos demograficos
    - Performance gaps documentados

  Code and Data Availability
    - Repo GitHub
    - Versao do codigo (commit hash)
    - Dados disponiveis sob requisicao? Restricoes LGPD/HIPAA?
```

Saida: `paper/manuscript.md` com secao Methods completa.

### Fase 4: Drafting IMRaD

Escrever na ordem que faz sentido:

1. **Methods primeiro** (mais facil, ja foi planejada)
2. **Results** (objetivo, segue methods)
3. **Discussion**
4. **Introduction** (por ultimo, escreve com clareza do que foi achado)
5. **Abstract** (ultimo, sintetiza tudo)
6. **Title** (iterar varias vezes)

Para Results:
- Tabela 1: caracteristicas baseline da populacao
- Tabela 2: performance do modelo (com IC 95%)
- Figuras: ROC, calibration, feature importance, SHAP
- Numeros consistentes entre texto, tabelas, figuras
- Sempre IC 95% junto com point estimate
- Sempre numero de eventos junto com taxa

Para Discussion (4 paragrafos):
1. Principal achado em 1 frase + contextualizacao
2. Comparacao com literatura (citar refs da Fase 2)
3. Implicacoes clinicas e limitacoes
4. Trabalhos futuros e conclusao

Para Introduction (3 paragrafos):
1. Importancia clinica do problema (com numeros: prevalencia, mortalidade, custo)
2. Estado da arte e gap (citar refs)
3. Objetivo do estudo + hipotese

Para Abstract (estruturado):
- Background (2 frases)
- Methods (3 frases)
- Results (3 frases com numeros)
- Conclusion (1 frase)

### Fase 5: Anti-IA polish

Padroes de IA para REMOVER (em ingles):

1. "delve into", "delve deeper" -> "examine", "explore"
2. "It is important to note" -> deletar ou reescrever
3. "navigate the complexities" -> "address the challenges"
4. "in the realm of" -> "in"
5. "shed light on" -> "reveal", "show"
6. "leveraging" -> "using"
7. "underscore" -> "show", "demonstrate"
8. "robust" usado em todo paragrafo -> variar
9. "comprehensive" repetido -> remover ou variar
10. "moreover", "furthermore", "additionally" em excesso -> conectores naturais
11. Listas com 3 items terminando em "and" sempre -> variar estrutura
12. Frases comecando com "In conclusion" -> reescrever
13. "It is worth noting" -> deletar
14. Hifens em excesso para juntar conceitos -> reescrever
15. "Cutting-edge" -> "current", "recent"
16. "Game-changing" -> "significant", "important"
17. "Pivotal" em excesso -> variar
18. "Plays a crucial role" -> "is important for", "contributes to"

Em portugues:
1. "Vale ressaltar" -> deletar
2. "Cabe destacar" -> deletar
3. "E importante notar" -> deletar
4. "No ambito de" -> "em"
5. "No contexto de" usado em excesso -> reescrever
6. Travessoes (em dash —, en dash –) -> sempre virgula ou ponto
7. Aspas tipograficas " " -> retas " "
8. Reticencias Unicode -> tres pontos normais

Tambem:
- Frases longas demais (> 35 palavras): quebrar
- Voz passiva em excesso: alternar com ativa
- "Methodology" usado quando "methods" basta
- Variar inicio de paragrafos (nao todos com "The")

### Fase 6: Peer-review interno

Checklist por categoria:

**Rigor metodologico:**
- [ ] Reporting guideline aplicada (qual? linkar checklist preenchido)
- [ ] Sample size justificado
- [ ] Missing data tratado e reportado
- [ ] Multiple comparisons corrigidas se aplicavel
- [ ] IC 95% em todas metricas principais
- [ ] Validacao externa OU declaracao explicita de limitacao

**Transparencia:**
- [ ] Codigo disponivel (link)
- [ ] Dados disponiveis ou justificativa de restricao
- [ ] Pre-registro mencionado se houver
- [ ] Conflito de interesse declarado
- [ ] Aprovacao etica (CEP/CONEP) mencionada

**Clareza:**
- [ ] Abstract reflete fielmente o paper
- [ ] Numeros consistentes entre abstract, texto, tabelas
- [ ] Figuras tem caption auto-suficiente
- [ ] Acronimos definidos no primeiro uso
- [ ] Discussion nao supera o que os dados mostram

**Anti-leakage (especifico ML/IA):**
- [ ] Train/test split claro, sem leakage temporal
- [ ] Feature engineering nao usa info do test
- [ ] Hyperparameter tuning so no train (com inner CV)
- [ ] Calibration calculada no test, nao train
- [ ] Citar Kapoor & Narayanan se relevante (data leakage in ML)

**Etica e fairness:**
- [ ] Performance por subgrupos (idade, sexo, regiao, raca/cor)
- [ ] Discussao de potencial vies
- [ ] Limitacoes de generalizabilidade

### Fase 7: Submission package

Preparar pacote final:

```
paper/submission/
  manuscript.docx        # ou .tex
  abstract.txt          # texto puro para sistema do journal
  cover_letter.docx     # personalizado pro editor
  highlights.txt        # 3 a 5 bullets, max 85 chars cada
  graphical_abstract.png
  figures/
    fig1.tiff (300 DPI)
    fig2.tiff
    ...
  tables/
    table1.docx
    ...
  supplementary/
    s1_appendix.docx
    s1_code.zip
    s1_data.csv (se permitido)
  checklists/
    tripod_ai_checklist.pdf  # ou STROBE, PRISMA, etc
  authorship_form.docx
  conflict_of_interest.docx
```

Cover letter template:
```
Dear Editor,

We submit our manuscript "[TITULO]" for consideration as [TIPO DE ARTIGO]
in [JOURNAL].

[1 paragrafo sobre o problema e gap]
[1 paragrafo sobre o que fizemos e principal achado]
[1 paragrafo sobre por que importa pra audiencia do journal]

The manuscript has not been published or submitted elsewhere. All authors
contributed substantially and approved the final version. We declare no
conflict of interest.

[Nome corresponding author]
[Afiliacao]
[Email]
```

## Estrutura de arquivos esperada

```
paper/
  scoping.md
  manuscript.md           # ou manuscript.tex
  references.bib
  refs/
    literature_review.md
    *.pdf (papers baixados)
  data/
    cohort.csv (se publicavel)
  figures/
  tables/
  results/
    metrics.json
    *.png
  submission/
    (preparado na Fase 7)
```

## Notas importantes

- **NUNCA inventar referencias.** Cada citacao deve ter DOI ou PMID verificado.
- **NUNCA inventar numeros.** Resultados saem do `metrics.json` ou tabela do projeto.
- Se o usuario nao tiver dados, perguntar antes de comecar a escrever Methods.
- Se o journal alvo for diferente, ajustar word limit e formatting (verificar guidelines do journal).
- Para artigos da LABDAPS ou IA medica brasileira: priorizar dados do SUS (DataSUS), citar contexto brasileiro de saude publica.
- Citar Kapoor & Narayanan (2023) "Leakage and the reproducibility crisis in machine-learning-based science" quando discutir vies de leakage em IA medica.

## Referencias internas

- `references/reporting_guidelines.md`: detalhes de cada guideline
- `references/imrad_structure.md`: detalhes de cada secao
- `references/anti_ai_patterns.md`: lista expandida de padroes a remover
- `references/ml_pipeline_in_paper.md`: como reportar pipeline ML em paper

## Comandos auxiliares

Apos rodar a skill, pode-se:
- `/update-paper` para atualizar resultados quando metricas mudam
- `/paper-review` para fazer leitura critica
- `/iamed` para indexar o paper final no Notion
