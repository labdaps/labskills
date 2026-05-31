---
name: ml-pipeline
description: Pipeline padrao de ML para projetos de saude. Data loading, preprocessing, train, eval com metricas clinicas. Triggers on /ml-pipeline.
---

# Skill: ml-pipeline

Cria ou modifica pipeline de Machine Learning para projetos de saude.

## Estrutura padrao

```
data/
  raw/            # dados brutos
  processed/      # dados processados
src/
  data/           # loading e preprocessing
  features/       # feature engineering
  models/         # treinamento e avaliacao
  utils/          # helpers
notebooks/        # exploracaao e analise
configs/          # hiperparametros
```

## Passos

### 1. Data Loading

- Identificar fonte (CSV, Parquet, DataSUS, API)
- Carregar com dtypes corretos
- Documentar shape, colunas, tipos

### 2. Preprocessing

- Missing values: avaliar padrao (MCAR/MAR/MNAR)
- Sentinel values: 9, 99, 999 sao comuns em dados de saude
- Encoding: OneHot para categoricas baixa cardinalidade, Target/Label para alta
- Scaling: StandardScaler para modelos lineares, desnecessario para tree-based

### 3. Feature Engineering

- Criar features clinicamente relevantes
- Feature selection: importancia, correlacao, VIF
- Documentar cada feature criada e justificativa clinica

### 4. Treinamento

Algoritmos preferidos (ordem):
1. LightGBM (padrao)
2. XGBoost
3. CatBoost
4. Random Forest
5. Logistic Regression (baseline)
6. TabPFN (datasets pequenos < 10K)

Cross-validation: StratifiedKFold (k=5 ou k=10)
Balanceamento: SMOTE ou class_weight='balanced'

### 5. Avaliacao

Metricas obrigatorias para classificacao binaria:
- AUROC, AUPRC
- Sensibilidade, Especificidade
- F1-Score
- Calibration (Brier Score)

Graficos: ROC curve, PR curve, calibration plot, feature importance.

### 6. Salvar

- Modelo: joblib/pickle com versao
- Metricas: JSON ou CSV
- Graficos: PNG em results/

## Convencoes do LABDAPS (datasus-ai-prediction)

O pipeline de referencia do laboratorio e o [datasus-ai-prediction](https://github.com/fabianofilho/datasus-ai-prediction). Ao escrever codigo que vai conviver com ele, siga estas convencoes em vez do esqueleto generico acima.

### Modulos
- `core/outcomes/` - cada desfecho e uma subclasse de `OutcomeConfig` (ver skill `datasus-outcome`).
- `core/features/cohort.py` - `CohortBuilder(outcome).build(raw) -> cohort`, depois `.get_Xy(cohort) -> (X, y)` e `.split(...)`.
- `core/models/pipeline.py` - treino e calibracao.
- `core/models/evaluation.py` - graficos Plotly (ver skill `ml-eval-report`).
- `core/data/` - downloaders por sistema (SIH, SIM, SINASC, SINAN) e `linker.py` para record linkage.

### Treino (assinatura real)
```python
from core.models.pipeline import train_cv, calibrate_model

res = train_cv(
    X, y,
    algorithm="lgbm",      # lgbm | xgb | catboost | rf | logreg
    n_folds=5,             # StratifiedKFold(shuffle=True, random_state=42)
    balancing="none",      # none | smote_over | class_weight
)
# res traz: fold_metrics, mean_metrics, oof_probs, feature_importances, model, X_columns
```

Pontos-chave do padrao do lab:
- **Out-of-fold probs**: metricas e graficos usam `oof_probs` (predicao de cada fold no seu hold-out), nao predicao no treino. Evita vazamento e da estimativa honesta.
- **Balanceamento dentro do fold**: SMOTE ou `class_weight` so no treino de cada fold, nunca antes do split.
- **Sentinels de saude**: 9, 99, 999 sao missing codificados no DataSUS. O preprocessor (`SentinelReplacer`) troca por NaN antes de imputar.

### Calibracao (sempre, em saude)
```python
cal = calibrate_model(model, X, y, method="sigmoid")  # sigmoid (Platt) | isotonic
# cal traz: brier_before, brier_after, brier_delta, cal_model
```
Modelo de risco clinico precisa de probabilidade calibrada, nao so de bom AUROC. Reporte o Brier antes e depois.

### Janelas temporais
Todo desfecho define `observation_window_days` (look-back das features) e `prediction_window_days` (look-ahead do desfecho). Garanta que nenhuma feature use informacao posterior ao fim da janela de observacao (sem leakage temporal).
