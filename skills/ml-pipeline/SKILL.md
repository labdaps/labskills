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
