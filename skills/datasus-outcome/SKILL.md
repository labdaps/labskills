---
name: datasus-outcome
description: Adiciona um novo desfecho preditivo ao app lab-ai-prediction do LABDAPS. Cria a subclasse de OutcomeConfig em core/outcomes/, registra no __init__, na metodologia e no catalogo, e segue o padrao dos desfechos existentes (SIH, SIM, SINASC, SINAN). Triggers on /datasus-outcome, "novo desfecho", "adiciona um outcome", "criar um desfecho no datasus", "modelar X no datasus".
---

# Skill: datasus-outcome

Cria um novo desfecho preditivo no app [lab-ai-prediction](https://github.com/fabianofilho/lab-ai-prediction), o app canonico do laboratorio. O datasus-ai-prediction e o fork labdaps/datasus-ai-prediction sao linhagens arquivadas: contribua so no lab-ai-prediction. Cada desfecho e uma subclasse de `OutcomeConfig`, e a plataforma pluga o resto (download, coorte, treino, avaliacao) automaticamente.

## Quando usar

- `/datasus-outcome` para adicionar um desfecho novo
- "quero modelar [desfecho] com dados do DataSUS"
- "adiciona um outcome de [condicao]"
- Ao contribuir com o repo do laboratorio

## Antes de comecar, definir com o usuario

1. **Desfecho clinico** e o que predizer (ex: obito neonatal, abandono de TB).
2. **Fonte(s)**, pela chave do downloader do app: `SIH`, `SIM`, `SINASC` ou uma do SINAN (`SINAN_TB`, `SINAN_DENG`, `SINAN_HANS`, `SINAN_CHIK`, `SINAN_VIOL`, `SINAN_IEXO`, `SINAN_AIDS`, `SINAN_SIFA`).
3. **Evento indice** (linha = qual evento? alta, nascimento, notificacao).
4. **Momento da predicao** (admissao, alta, notificacao): o que ja se sabe nesse instante. Toda variavel registrada depois dele e vazamento (CP1 da `ml-checkpoints`).
5. **Janela de observacao** (look-back das features, em dias).
6. **Janela de predicao** (look-ahead do desfecho, em dias).
7. **Codigos do rotulo**, tirados do dicionario da base: quais sao positivo, quais sao negativo e quais sao censura ou ignorado. Censura e ignorado saem da coorte; nunca viram 0.
8. **Precisa de record linkage** entre sistemas? Hoje nenhum desfecho do app tem linkage validado no dado publico: o SIM nao pareia com o SIH (a `mortalidade_hospitalar` usa so o obito intra-hospitalar) e o linkage SINASC e SIM da `mortalidade_neonatal` esta em desenvolvimento. Desfecho que depende de linkage entra como `dev` ate o pareamento 1:1 ser validado.

Sem leakage temporal: nenhuma feature pode usar informacao posterior ao momento da predicao.

## Passos

### 1. Olhar um desfecho existente parecido

Antes de escrever, ler um desfecho da mesma fonte em `core/outcomes/` como molde:
- SIH: `permanencia_prolongada.py` (predicao na admissao, sem o que so existe na alta)
- SINASC: `prematuridade.py`, `baixo_peso_nascer.py`
- SINAN: `abandono_tb.py` (rotulo com censura, excluida por `sinan.drop_censored`) e `dengue_grave.py` (campos que definem o desfecho fora das features e da coorte)

Os mapas de codigo ja conferidos no app (SITUA_ENCE da TB, CLASSI_FIN da dengue, CLASSOPERA da hanseniase) estao travados em `tests/test_rotulos.py`: parta deles em vez de reescrever o mapa.

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
            data_sources=["SIH"],              # chave do downloader: SIH, SINASC, SINAN_TB...
            observation_window_days=365,
            prediction_window_days=30,
            requires_linkage=False,
            icon="local_hospital",
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
        # definir evento indice, aplicar janelas, derivar target_col:
        # 1 positivo, 0 negativo, NaN para censura e ignorado. Depois tirar da
        # coorte as linhas sem rotulo e registrar quantas sairam, como
        # sinan.drop_censored faz na TB.
        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        """Feature engineering sem leakage. Categorica fica como categoria: o
        pipeline do app a codifica dentro do fold (encoding fixo, CP4 da
        ml-checkpoints). Nada de pd.Categorical(...).codes, que numera o que
        aparece na amostra."""
        df = cohort.copy()
        if "IDADE" in df.columns:
            df["age_group"] = eng.age_group(df["IDADE"])  # faixas fixas
        if "DIAG_PRINC" in df.columns:
            df["diag_chapter"] = df["DIAG_PRINC"].str[:1].str.upper().astype("category")
        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        """Series binaria (0/1) do desfecho. Sem fillna(0): censura e ignorado
        ja sairam no build_cohort, entao um NaN aqui e erro, nao negativo."""
        return cohort[self.target_col].astype(int)
```

### 3. Registrar

Os testes offline do app falham se faltar o registro, a metodologia ou, no SIH, o momento da predicao.

Em `core/outcomes/__init__.py`, adicionar uma entrada no dict `_REGISTRY` (so metadados, import preguicoso) e no grupo certo de `OUTCOME_GROUPS`:

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

Depois:
- `core/methodology.py`: entrada em `METHODOLOGY` com `pull` (como a coorte e montada) e `target` (definicao operacional do rotulo, com os codigos positivos, negativos e de censura); `caveat` para ressalva.
- `pages/datasus.py`: o card do desfecho no `OUTCOME_GROUPS` da pagina, com `status: "dev"` ate a validacao com dado real.
- `tests/test_invariants.py`: as colunas que definem o alvo na `LEAK_BLACKLIST`.
- `tests/test_vazamento.py`: desfecho do SIH em `SIH_ADMISSAO` ou `SIH_NA_ALTA`, conforme o momento da predicao.
- Um teste com os codigos brutos do rotulo (positivo, negativo, censura, em branco), no molde de `tests/test_rotulos.py`.

### 4. Testar

```bash
pytest -m "not network" -q
streamlit run app.py
```

Os testes offline precisam passar. Na pagina de Analise, o desfecho novo deve aparecer na etapa 1. Rodar o wizard ate Resultados com um estado/ano pequeno e conferir:
- A coorte tem linhas e o `class_balance` mostra prevalencia plausivel (nao 0% nem 100%).
- O log mostra quantos casos sairam por censura ou rotulo ignorado, e o numero faz sentido.
- O treino roda (`train_cv`) e gera AUROC/AUPRC, calibracao e SHAP.
- Nenhuma feature de leakage no SHAP (ex: algo que so existe apos o desfecho).

## Checklist antes do PR

- [ ] `key` unica e igual ao nome do arquivo
- [ ] Os 3 metodos abstratos implementados
- [ ] `data_sources` com a chave do downloader (`SINAN_TB`, nao `SINAN`)
- [ ] `suggested_features` existem na coorte e sao clinicamente justificadas
- [ ] Momento da predicao declarado e nenhuma feature registrada depois dele
- [ ] Censura e ignorado fora da coorte, nunca como 0, com a contagem no log
- [ ] Categoricas como categoria, sem `pd.Categorical(...).codes`
- [ ] Registrado no `_REGISTRY`, em `OUTCOME_GROUPS`, em `METHODOLOGY` e no card de `pages/datasus.py`
- [ ] `pytest -m "not network"` verde
- [ ] Testado de ponta a ponta com dado real pequeno
- [ ] Prevalencia do target faz sentido clinico
