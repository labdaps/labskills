---
name: datasus-outcome
description: Adiciona um novo desfecho preditivo ao pipeline datasus-ai-prediction do LABDAPS. Cria a subclasse de OutcomeConfig em core/outcomes/, registra no __init__ e segue o padrao dos desfechos existentes (SIH, SIM, SINASC, SINAN). Triggers on /datasus-outcome, "novo desfecho", "adiciona um outcome", "criar um desfecho no datasus", "modelar X no datasus".
---

# Skill: datasus-outcome

Cria um novo desfecho preditivo no pipeline [datasus-ai-prediction](https://github.com/fabianofilho/datasus-ai-prediction). Esse e o ponto de contribuicao principal do repo: cada desfecho e uma subclasse de `OutcomeConfig`. A plataforma pluga o resto (download, coorte, treino, avaliacao) automaticamente.

## Quando usar

- `/datasus-outcome` para adicionar um desfecho novo
- "quero modelar [desfecho] com dados do DataSUS"
- "adiciona um outcome de [condicao]"
- Ao contribuir com o repo do laboratorio

## Antes de comecar, definir com o usuario

1. **Desfecho clinico** e o que predizer (ex: obito neonatal, abandono de TB).
2. **Fonte(s)**: SIH, SIM, SINASC ou qual SINAN (Dengue, TB, Hanseniase, AIDS, Sifilis, Chikungunya, Violencia, Intoxicacao).
3. **Evento indice** (linha = qual evento? alta, nascimento, notificacao).
4. **Janela de observacao** (look-back das features, em dias).
5. **Janela de predicao** (look-ahead do desfecho, em dias).
6. **Precisa de record linkage** entre sistemas? (ex: SIH + SIM para mortalidade pos-alta).

Sem evitar leakage temporal: nenhuma feature pode usar informacao posterior ao fim da janela de observacao.

## Passos

### 1. Olhar um desfecho existente parecido

Antes de escrever, ler um desfecho da mesma fonte em `core/outcomes/` como molde:
- SIH puro: `readmissao_30d.py`, `permanencia_prolongada.py`
- SIH + SIM (linkage): `mortalidade_hospitalar.py`
- SINASC: `prematuridade.py`, `baixo_peso_nascer.py`
- SINAN: `dengue_grave.py`, `abandono_tb.py`

### 2. Criar `core/outcomes/<key>.py`

Subclasse de `OutcomeConfig` (dataclass abstrata) implementando os 3 metodos abstratos:

```python
"""<Descricao curta do desfecho>."""
from __future__ import annotations

import pandas as pd

from core.outcomes.base import OutcomeConfig
from core.data import sih as sih_prep          # ajustar para a fonte
from core.features import engineering as eng


class MeuDesfecho(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="meu_desfecho",                # unico, igual ao nome do arquivo
            name="Meu Desfecho",
            description="Prediz ... usando dados do ...",
            data_sources=["SIH"],              # ['SIH', 'SIM'] se precisar linkage
            observation_window_days=365,
            prediction_window_days=30,
            requires_linkage=False,
            icon="🏥",
            estimated_download_min=10,
            suggested_features=[
                "IDADE", "SEXO", "RACA_COR", "age_group",
                # features clinicamente justificadas, ja presentes na coorte
            ],
            target_col="meu_desfecho",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Tabelas brutas do DataSUS -> coorte achatada, 1 linha por evento indice."""
        df = sih_prep.preprocess(data["SIH"])
        # definir evento indice, aplicar janelas, derivar target_col (0/1)
        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        """Feature engineering: encoding, agregacoes. Sem leakage, tudo numerico."""
        df = cohort.copy()
        if "DIAG_PRINC" in df.columns:
            df["diag_chapter"] = eng.icd10_chapter(df["DIAG_PRINC"])
        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        """Series binaria (0/1) do desfecho."""
        return cohort[self.target_col].astype(int)
```

### 3. Registrar em `core/outcomes/__init__.py`

Adicionar uma entrada no dict `_REGISTRY` (so metadados, import preguicoso) e no grupo certo de `OUTCOME_GROUPS`:

```python
"meu_desfecho": {
    "module": "core.outcomes.meu_desfecho",
    "class":  "MeuDesfecho",
    "name":   "Meu Desfecho",
    "description": "Prediz ...",
    "data_sources": ["SIH"],
    "icon": "local_hospital",
    "estimated_download_min": 10,
},
```

### 4. Testar

```bash
streamlit run app.py
```

Na pagina de Analise, o desfecho novo deve aparecer na etapa 1. Rodar o wizard ate Resultados com um estado/ano pequeno e conferir:
- A coorte tem linhas e o `class_balance` mostra prevalencia plausivel (nao 0% nem 100%).
- O treino roda (`train_cv`) e gera AUROC/AUPRC, calibracao e SHAP.
- Nenhuma feature de leakage no SHAP (ex: algo que so existe apos o desfecho).

## Checklist antes do PR

- [ ] `key` unica e igual ao nome do arquivo
- [ ] Os 3 metodos abstratos implementados
- [ ] `suggested_features` existem na coorte e sao clinicamente justificadas
- [ ] Sem leakage temporal (features dentro da janela de observacao)
- [ ] Registrado no `_REGISTRY` e em `OUTCOME_GROUPS`
- [ ] Testado de ponta a ponta com dado real pequeno
- [ ] Prevalencia do target faz sentido clinico
