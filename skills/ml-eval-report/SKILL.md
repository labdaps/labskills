---
name: ml-eval-report
description: Gera relatorio de avaliacao de modelo ML com metricas, graficos e comparacao. Triggers on /ml-eval-report.
---

# Skill: ml-eval-report

Gera relatorio completo de avaliacao de modelo de Machine Learning.

As regras de metrica, ponto de corte, calibracao e interpretabilidade sao da skill `ml-checkpoints` (CP8 a CP10), a norma do laboratorio; esta skill monta o relatorio a partir das decisoes registradas no `pipeline-decisions.md` do projeto. O porque de cada regra esta em `docs/aprendizados-pipeline-agentes.md`, no ai-lab-hub.

## Passos

### 1. Identificar modelo e dados

- Localizar modelo treinado (pickle/joblib) ou codigo de treinamento
- Identificar conjunto de teste (X_test, y_test)
- Verificar tipo de problema: classificacao binaria, multiclasse, regressao
- Ler no `pipeline-decisions.md` a metrica principal e o ponto de corte escolhidos no CP8

### 2. Gerar predicoes

```python
y_prob = model.predict_proba(X_test)[:, 1]  # para classificacao
# corte: o ponto de corte registrado no CP8, fixado no treino pelo custo
# clinico. Nunca model.predict(), que classifica no 0,5 implicito.
y_pred = (y_prob >= corte).astype(int)
```

### 3. Metricas - Classificacao binaria

```python
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    classification_report, brier_score_loss,
    confusion_matrix
)
```

Tabela de metricas, todas com IC95% (bootstrap ou variacao entre folds). A metrica principal e a do CP8, escolhida antes de rodar; acuracia fica de fora, porque em desfecho raro ela e alta sem o modelo acertar nada (CP5):
| Metrica | Valor | IC95% |
|---------|-------|-------|
| Metrica principal (CP8) | | |
| AUROC | | |
| AUPRC | | |
| Sensibilidade no corte do CP8 | | |
| Especificidade no corte do CP8 | | |
| F1-Score no corte do CP8 | | |
| Brier Score | | |
| Slope e intercepto de calibracao | | |

### 4. Graficos

Gerar e salvar em `results/`:
1. **ROC Curve** com AUC no titulo
2. **Precision-Recall Curve** com AP no titulo
3. **Confusion Matrix** (heatmap)
4. **Calibration Plot** (observed vs predicted)
5. **Feature Importance** (top 20)
6. **SHAP com direcao** (beeswarm ou summary), obrigatorio em saude (CP10): se o `shap` nao estiver instalado, instale em vez de pular
7. **Decision curve**, quando o CP8 a escolheu

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
ev.threshold_metrics(y, res["oof_probs"], threshold=corte)  # corte do CP8, nunca o default 0,5
```

### Comparacao entre estados/periodos
Para checar transportabilidade do modelo entre UFs ou anos:
```python
ev.metrics_comparison_table(comparison_results)
ev.calibration_comparison_chart(...)
ev.shap_comparison_chart(...)
```

### O que sempre reportar
A metrica principal do CP8 com IC, AUROC e AUPRC, **Brier antes e depois da calibracao**, calibracao visual, SHAP global com direcao, e a tabela de metricas por subgrupo. AUROC alto sem calibracao e sem analise de equidade nao basta para um modelo de risco em saude.
