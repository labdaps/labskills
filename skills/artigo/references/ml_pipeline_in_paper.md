# Como reportar pipeline ML em paper

Guia pratico de como descrever pipeline de ML/IA na secao Methods, alinhado com TRIPOD+AI 2024.

## Estrutura recomendada

### 1. Data and outcome

```
We used data from [SOURCE] including [N] patients admitted between
[DATE1] and [DATE2]. The primary outcome was [OUTCOME], defined as
[OPERATIONAL DEFINITION] with ICD-10 codes [CODES]. The time horizon
was [TIMEFRAME].
```

### 2. Predictors

```
We considered [N] candidate predictors available at [TIMEPOINT, e.g.,
hospital admission]. Variables included demographic [list],
clinical [list], laboratory [list], and [other categories].

A complete list of variables, units, missing rates, and encoding
strategies is provided in Supplementary Table S1.

Sentinel values (9, 99, 999) were treated as missing for [VARIABLES].
Continuous variables were [scaled/not scaled]; categorical variables
were encoded using [one-hot/target encoding].
```

### 3. Missing data

```
Overall missingness was [X%], with [VAR1] (15.3%) and [VAR2] (8.7%)
having the highest rates. We assumed a missing-at-random (MAR) pattern.

Missing values were imputed using [METHOD, e.g., multiple imputation
by chained equations with M=10 imputations / median imputation /
forward fill / etc.]. Imputation was fit only on training data and
applied to test data to prevent leakage.
```

### 4. Sample size

```
With [N_EVENTS] events and [N_PREDICTORS] predictors, our events-per-variable
(EPV) ratio was [EPV], exceeding the recommended threshold of 10
(ideally 20) for clinical prediction models [REF Riley et al].
```

### 5. Algorithms

```
We trained and compared the following algorithms:
- Logistic regression (baseline) with L2 regularization
- Random forest
- Gradient boosting machines (LightGBM, XGBoost, CatBoost)
- TabPFN (for sample sizes <10,000)

[Optionally: Why these were chosen]
```

### 6. Hyperparameter tuning

```
Hyperparameters were tuned using [METHOD, e.g., Bayesian optimization
via Optuna with 100 trials, or grid search]. The search space is detailed
in Supplementary Table S2. Tuning used [INNER CV STRATEGY, e.g., 5-fold
stratified cross-validation on the training set] to prevent leakage.
```

### 7. Validation strategy

```
We used a temporal split: data from [DATE_RANGE_TRAIN] was used for
training and data from [DATE_RANGE_TEST] was used for testing. This
split simulates prospective deployment.

Internal validation used [METHOD, e.g., 5-fold stratified cross-validation]
with optimism correction via bootstrap (200 resamples).

External validation was performed on a separate cohort from [SOURCE],
including [N_EXT] patients.
```

### 8. Performance measures

```
Discrimination was assessed using AUROC and AUPRC with 95% confidence
intervals (calculated via bootstrap, 1000 resamples).

Calibration was assessed using:
- Calibration plot (with bins, observed vs expected)
- Brier score
- Integrated Calibration Index (ICI)
- Calibration intercept and slope

Clinical utility was assessed using decision curve analysis (DCA)
across a range of threshold probabilities.

Subgroup analyses were performed by sex, age (>65 vs <=65), region,
and comorbidity burden.
```

### 9. Fairness/Bias (TRIPOD+AI specific)

```
We evaluated model performance separately by demographic subgroups
(race/color: white, black, brown, yellow, indigenous; sex: male, female;
region: 5 macro-regions of Brazil) and report performance gaps.

We discuss the implications of these gaps in the Discussion section.
```

### 10. Reproducibility

```
All analyses were performed in Python [VERSION] using scikit-learn [VERSION],
LightGBM [VERSION], and other packages listed in the requirements file.
Random seeds were fixed at [SEED] for all stochastic operations.

The full source code is available at https://github.com/[REPO] (commit
[HASH]). The analysis can be reproduced using Docker [IMAGE]. Data is
available [from the corresponding author upon reasonable request /
in a public repository / restricted due to LGPD/CEP].
```

## Erros comuns a evitar

### 1. Data leakage temporal
- Train com dados de 2023, test com dados de 2020? -> NAO
- Sempre usar split temporal coerente com deployment

### 2. Leakage de feature engineering
- Calcular media populacional usando train+test -> NAO
- Sempre fit no train, transform no test

### 3. Hyperparameter tuning no test
- Selecionar threshold otimizando F1 no test set -> NAO
- Tudo no train via inner CV

### 4. Reportar so a melhor metrica
- "Our best model achieved AUROC=0.85" -> qual modelo? em qual fold?
- Reportar todos os modelos testados, com IC 95%

### 5. Calibration esquecida
- Discrimination sem calibration eh incompleto para uso clinico
- Sempre incluir calibration plot

### 6. Single split
- "We split 70/30" -> e variabilidade?
- Usar k-fold CV ou repeated splits

### 7. Subgrupos so se conveniente
- Reportar performance por subgrupos mesmo se piorar o modelo
- Eh exigencia de TRIPOD+AI

### 8. Codigo "available upon request"
- Quase ninguem responde quando solicitado
- Disponibilizar publicamente no GitHub

### 9. Hyperparameters nao reportados
- "Tuned via grid search" -> qual grid?
- Sempre Supplementary Table com search space e melhor combo

### 10. Versao de software omitida
- "We used scikit-learn" -> qual versao?
- Resultados podem mudar entre versoes

## Templates de tabelas

### Tabela: Performance overview

| Model | AUROC (95% CI) | AUPRC (95% CI) | Brier | ICI |
|---|---|---|---|---|
| Logistic regression | 0.78 (0.75, 0.81) | 0.45 (0.41, 0.49) | 0.18 | 0.03 |
| Random forest | 0.82 (0.79, 0.85) | 0.52 (0.48, 0.56) | 0.16 | 0.02 |
| LightGBM | 0.85 (0.82, 0.88) | 0.58 (0.54, 0.62) | 0.14 | 0.02 |
| XGBoost | 0.85 (0.82, 0.88) | 0.57 (0.53, 0.61) | 0.14 | 0.02 |
| **CatBoost** | **0.86 (0.83, 0.89)** | **0.60 (0.56, 0.64)** | **0.13** | **0.01** |

(Bold = selected final model)

### Tabela: Subgroup performance

| Subgroup | N | AUROC (95% CI) |
|---|---|---|
| Overall | 5000 | 0.86 (0.83, 0.89) |
| Female | 2400 | 0.85 (0.81, 0.89) |
| Male | 2600 | 0.87 (0.83, 0.90) |
| Age <=65 | 2800 | 0.84 (0.80, 0.88) |
| Age >65 | 2200 | 0.88 (0.84, 0.91) |
| Region Norte | 800 | 0.81 (0.74, 0.87) |
| Region Nordeste | 1200 | 0.85 (0.81, 0.89) |
| Region Centro-Oeste | 600 | 0.84 (0.78, 0.90) |
| Region Sudeste | 1800 | 0.87 (0.83, 0.90) |
| Region Sul | 600 | 0.86 (0.81, 0.91) |

## Citar metodologia

Sempre citar:
- Riley RD et al. Calculating the sample size for new clinical prediction models. Stat Med. 2019.
- Steyerberg EW. Clinical Prediction Models. Springer.
- Collins GS et al. TRIPOD+AI statement. BMJ. 2024.
- Vickers AJ. Decision curve analysis. JAMA. 2008.
- Kapoor S, Narayanan A. Leakage and the reproducibility crisis. Patterns. 2023.
