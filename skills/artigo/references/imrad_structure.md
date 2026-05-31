# IMRaD: estrutura detalhada

## Title

- Maximo 15 palavras (varia por journal)
- Inclui: populacao, intervencao/exposicao, desfecho, tipo de estudo
- Evitar: jargao excessivo, perguntas, exclamacoes
- Bom: "Machine learning prediction of 30-day mortality after hospital admission for community-acquired pneumonia: a retrospective cohort study"
- Ruim: "Using AI to predict death" (vago)

## Abstract estruturado (250-300 palavras tipico)

```
Background (2 frases):
  - Por que isso importa
  - Qual e o gap

Methods (3-4 frases):
  - Tipo de estudo, populacao, periodo
  - Intervencao/exposicao
  - Desfecho primario
  - Analise estatistica/algoritmo

Results (3-4 frases):
  - N total, demografia chave
  - Resultado principal com IC 95%
  - Resultado secundario relevante

Conclusion (1-2 frases):
  - O que isso significa
  - Implicacoes praticas
```

## Introduction (3 paragrafos, 400-600 palavras)

**P1: Importancia clinica**
- Prevalencia, mortalidade, custo da condicao
- Numeros concretos com referencias
- Impacto em saude publica (especialmente para SUS)

**P2: Estado da arte e gap**
- O que ja foi feito (citar 5-10 refs principais)
- Limitacoes da literatura existente
- Gap especifico que voce vai preencher

**P3: Objetivo**
- Pergunta de pesquisa clara
- Hipotese se aplicavel
- Linha sobre o que sera apresentado

## Methods (peca mais longa, 800-1500 palavras)

Para artigos de IA/ML em saude (TRIPOD+AI):

### Subsecoes obrigatorias:

**Study Design and Population**
- Tipo de estudo
- Source of data (DataSUS? hospital? prontuario eletronico? linkage?)
- Periodo
- Inclusion/exclusion criteria
- Approval ethics (CEP/CONEP numero)

**Outcome**
- Definicao precisa
- Codigos CID-10 se aplicavel
- Time horizon
- Como foi avaliado (gold standard)

**Predictors**
- Tabela completa em supplementary
- Para cada: nome, tipo, unidade, fonte
- Tratamento de missing
- Tratamento de sentinel values (9, 99, 999)
- Encoding

**Sample Size**
- Justificativa
- Para preditivo: events per variable (EPV >= 10, idealmente >= 20)
- Para deep learning: regra de Riley

**Statistical Analysis / ML Pipeline**
- Pre-processing (passo a passo)
- Algorithms (todos testados, nao so o melhor)
- Hyperparameter tuning (search space, criterio)
- Cross-validation strategy (k, stratification)
- Train/test split (temporal? aleatorio?)
- Performance measures (AUROC, AUPRC, calibration, NRI, IDI)
- Software e versoes (Python X.Y, scikit-learn X.Y, etc)

**Validation**
- Internal: bootstrap optimism-corrected
- External: descrever coorte separada
- Subgroup analysis (sexo, idade, regiao, comorbidades)

**Fairness/Bias**
- Performance por subgrupos demograficos
- Gaps documentados

## Results (600-1000 palavras + tabelas/figuras)

**Sequencia padrao:**

1. **Flow diagram** (figura): de N inicial ate N analisado
2. **Tabela 1**: caracteristicas baseline da populacao
   - Colunas: total, ou separado por outcome
   - Linhas: idade, sexo, comorbidades, lab results
   - Sempre N (%) ou mediana (IQR)
3. **Resultados primarios**:
   - Performance do modelo: AUROC, AUPRC com IC 95%
   - Calibration plot
   - Decision curve analysis
4. **Resultados secundarios**:
   - Feature importance / SHAP
   - Subgroup analysis
   - Sensitivity analysis
5. **Validacao externa** (se houver)

**Regras de ouro:**
- Numeros consistentes entre texto, tabelas, figuras
- Sempre IC 95% com point estimate
- Sempre N junto com %
- P-values com 2 ou 3 casas decimais; <0.001 quando muito pequeno
- Nao repetir no texto o que esta na tabela; resumir e destacar

## Discussion (4 paragrafos, 800-1200 palavras)

**P1: Principal achado**
- 1 frase resumindo o resultado principal
- Contextualizar dentro da pergunta de pesquisa
- O que e novo

**P2: Comparacao com literatura**
- Citar refs principais da Introduction
- Por que seu resultado eh diferente/igual
- Mecanismos plausiveis

**P3: Implicacoes clinicas e limitacoes**
- Implicacoes: como isso muda pratica clinica?
- Limitacoes: sample size, single center, missing data, retrospectivo, vies
- Generalizabilidade: para que populacao vale?

**P4: Trabalhos futuros e conclusao**
- O que falta ser feito
- Conclusao em 1-2 frases (espelhar abstract)

**NUNCA fazer na Discussion:**
- Repetir results literalmente
- Ir alem do que os dados suportam
- Citar referencias novas que nao estavam na intro
- Esconder limitacoes importantes

## Tables and Figures

**Tabela 1 (baseline):**
```
                    Total (n=X)   Outcome+ (n=Y)   Outcome- (n=Z)   p-value
Age, median (IQR)   65 (54-72)    68 (58-75)       63 (52-70)       <0.001
Female, n (%)       423 (47.2)    180 (45.0)       243 (48.6)       0.32
Diabetes, n (%)     289 (32.3)    150 (37.5)       139 (27.8)       <0.001
...
```

**Figuras essenciais para paper de ML:**
1. Study flow diagram
2. ROC curve (com IC 95% sombreado)
3. Calibration plot (com Brier e ICI)
4. Decision curve analysis
5. Feature importance ou SHAP summary
6. Subgroup forest plot

**Caption:** auto-suficiente, leitor entende sem ler o texto.

## References

- Vancouver style (numerico) ou AMA, depende do journal
- Verificar DOI de TODAS as refs
- Usar Zotero/Mendeley/BibTeX
- Limit varia: 30-50 para original, 100+ para review

## Supplementary Material

- S1 Table: lista completa de variaveis
- S2 Table: hyperparameter search results
- S3 Figure: subgroup analyses
- S4 Code: link para repo GitHub com commit hash
- S5 Checklist: TRIPOD+AI preenchido
- S6 Data dictionary
