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
