---
name: ml-eval-report
description: Gera relatorio de avaliacao de modelo ML com metricas, graficos e comparacao. Triggers on /ml-eval-report.
---

# Skill: ml-eval-report

Gera relatorio completo de avaliacao de modelo de Machine Learning.

## Passos

### 1. Identificar modelo e dados

- Localizar modelo treinado (pickle/joblib) ou codigo de treinamento
- Identificar conjunto de teste (X_test, y_test)
- Verificar tipo de problema: classificacao binaria, multiclasse, regressao

### 2. Gerar predicoes

```python
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]  # para classificacao
```

### 3. Metricas - Classificacao binaria

```python
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    classification_report, brier_score_loss,
    confusion_matrix
)
```

Tabela de metricas:
| Metrica | Valor |
|---------|-------|
| AUROC | |
| AUPRC | |
| Sensibilidade | |
| Especificidade | |
| F1-Score | |
| Brier Score | |
| Accuracy | |

### 4. Graficos

Gerar e salvar em `results/`:
1. **ROC Curve** com AUC no titulo
2. **Precision-Recall Curve** com AP no titulo
3. **Confusion Matrix** (heatmap)
4. **Calibration Plot** (observed vs predicted)
5. **Feature Importance** (top 20)
6. **SHAP Summary Plot** (se shap instalado)

### 5. Comparacao de modelos (se aplicavel)

Se houver multiplos modelos, gerar tabela comparativa e grafico de barras.

### 6. Salvar relatorio

- Metricas em `results/metrics.json`
- Graficos em `results/figures/`
- Print resumo no terminal

## Convencoes do LABDAPS (datasus-ai-prediction)

No pipeline do laboratorio ([datasus-ai-prediction](https://github.com/fabianofilho/datasus-ai-prediction)) a avaliacao ja esta pronta em `core/models/evaluation.py`, com graficos **Plotly** (interativos, nao matplotlib). Reuse essas funcoes em vez de reimplementar.

### Use as out-of-fold probs
O `train_cv` devolve `oof_probs`. Todos os graficos recebem `(y_true, oof_probs)`, nao predicao no treino.

```python
from core.models import evaluation as ev

ev.roc_chart(y, res["oof_probs"])
ev.pr_chart(y, res["oof_probs"])
ev.calibration_chart(y, res["oof_probs"], n_bins=10)
ev.threshold_curve_chart(y, res["oof_probs"])
ev.importance_chart(res["feature_importances"], top_n=20)
ev.fold_metrics_table(res["fold_metrics"])
```

### Explicabilidade (SHAP) e obrigatoria em saude
```python
ev.shap_summary(res["model"], X)        # importancia global
ev.shap_beeswarm(res["model"], X)       # direcao do efeito
ev.shap_waterfall_chart(res["model"], X, case_idx=0)  # explicacao de um caso
```

### Equidade: metricas por subgrupo
Modelo clinico precisa ser auditado por subgrupo (sexo, raca/cor, faixa etaria, regiao). Nao reporte so a metrica agregada.
```python
ev.subgroup_metrics_table(y, res["oof_probs"], groups)  # AUROC/sens/esp por grupo
ev.threshold_metrics(y, res["oof_probs"], threshold=0.5)
```

### Comparacao entre estados/periodos
Para checar transportabilidade do modelo entre UFs ou anos:
```python
ev.metrics_comparison_table(comparison_results)
ev.calibration_comparison_chart(...)
ev.shap_comparison_chart(...)
```

### O que sempre reportar
AUROC e AUPRC, **Brier antes e depois da calibracao**, calibracao visual, SHAP global, e a tabela de metricas por subgrupo. AUROC alto sem calibracao e sem analise de equidade nao basta para um modelo de risco em saude.
