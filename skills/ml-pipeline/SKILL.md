---
name: ml-pipeline
description: Pipeline padrao de ML para projetos de saude. Data loading, preprocessing, train, eval com metricas clinicas. Triggers on /ml-pipeline.
---

# Skill: ml-pipeline

Cria ou modifica pipeline de Machine Learning para projetos de saude.

**Esta skill implementa, nao decide.** As decisoes de metodo (separacao, faltantes, sentinelas, encoding, balanceamento, modelos, metrica, ponto de corte, calibracao) sao da skill `ml-checkpoints`, que e a norma do laboratorio, e ficam registradas no `pipeline-decisions.md` do projeto. O porque de cada regra esta em `docs/aprendizados-pipeline-agentes.md`, no ai-lab-hub. Sem `pipeline-decisions.md`, rode a `ml-checkpoints` antes de escrever o pipeline. Se o codigo pedir uma decisao que nao esta registrada, pare e decida pela `ml-checkpoints`, em vez de escolher um padrao aqui.

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
- Carregar com dtypes corretos: codigo (municipio, CID, categoria do DataSUS) entra como texto ou categoria, nunca como quantidade
- Documentar shape, colunas, tipos

### 2. Separacao, antes de qualquer ajuste

Separe treino e teste antes de ajustar qualquer coisa, inclusive a busca de hiperparametros, pelo esquema do CP2 da `ml-checkpoints`: por grupo (StratifiedGroupKFold) quando um identificador repete, temporal quando a pergunta e se o modelo envelhece. Tudo o que aprende com o dado (imputacao, encoding, escalonamento, selecao, balanceamento, tuning) vive dentro do fold de treino, num `Pipeline` do sklearn ou do imblearn.

### 3. Preprocessing

Aplique o que o `pipeline-decisions.md` registrou no CP3 e no CP4 da `ml-checkpoints`:
- Missing: estrategia coluna a coluna, com indicador quando o CP3 pedir
- Sentinelas: por variavel, a partir do dicionario da base, antes de codificar e imputar. Nunca a mesma lista de valores no dado inteiro
- Encoding fixo: mapa de categorias tirado do dicionario, categorica mantida como categoria ate o pipeline e encoder ajustado no fold. Nada de `pd.Categorical(col).codes`, que numera o que aparece na amostra
- Scaling: conforme a familia de modelo (CP4 e CP6)

### 4. Feature Engineering

- Criar features clinicamente relevantes, todas disponiveis no momento da predicao (CP1)
- Selecao de features dentro do fold, pelo criterio do CP7
- Documentar cada feature criada e justificativa clinica

### 5. Treinamento

Os candidatos saem do CP6, sempre com a baseline (logistica ou escore clinico) na mesma particao. Algoritmos que o lab costuma usar:
1. LightGBM
2. XGBoost
3. CatBoost
4. Random Forest
5. Logistic Regression (baseline)
6. TabPFN (datasets pequenos < 10K)

Cross-validation: o esquema registrado no CP2 (StratifiedGroupKFold quando o identificador repete; StratifiedKFold so sem repeticao)
Balanceamento: nenhum, por padrao (CP5). `class_weight` so com a calibracao medida antes e depois (Brier e slope). Reamostragem (SMOTE) raramente, sempre dentro do fold de treino, nunca antes do split, e com recalibracao obrigatoria (CP9)

### 6. Avaliacao

Siga a skill `ml-eval-report`: a metrica principal do CP8, escolhida antes de rodar e reportada com IC, calibracao (CP9), ponto de corte fixado no treino pelo custo clinico e SHAP com direcao (CP10).

### 7. Salvar

- Modelo: joblib/pickle com versao, junto com o encoder e o mapa de categorias
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
- **Balanceamento**: `balancing="none"` e o padrao (CP5). Qualquer outro valor roda so no treino de cada fold e exige a calibracao medida antes e depois.
- **Sentinelas**: o `SentinelReplacer` do app troca a mesma lista de valores em todas as colunas, o que contraria o CP3 (sentinela e por variavel). Deixe `null_sentinels` vazio e trate o ignorado coluna a coluna no preprocess do desfecho, a partir do dicionario.

### Calibracao (CP9)
```python
cal = calibrate_model(model, X, y, method="sigmoid")  # sigmoid (Platt) | isotonic
# cal traz: brier_before, brier_after, brier_delta, cal_model
```
Modelo de risco clinico precisa de probabilidade calibrada, nao so de bom AUROC. Reporte o Brier antes e depois.

### Janelas temporais
Todo desfecho define `observation_window_days` (look-back das features) e `prediction_window_days` (look-ahead do desfecho). Garanta que nenhuma feature use informacao posterior ao fim da janela de observacao (sem leakage temporal).
