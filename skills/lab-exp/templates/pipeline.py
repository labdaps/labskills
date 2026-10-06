# %% [markdown]
# # TITULO DO EXPERIMENTO
#
# Uma frase dizendo o que se prediz, para quem, e em que momento a predicao acontece.
#
# TRES COISAS QUE PRECISAM ESTAR RESPONDIDAS ANTES DE QUALQUER MODELO:
#
# 1. **Momento da predicao**: qual instante do cuidado? Toda variavel posterior a ele e
#    vazamento. Escreva o instante aqui, por extenso.
# 2. **Desfecho**: quem nao teve o evento realmente nao teve, ou so nao foi observado? Se for
#    o segundo caso, censura e criterio de elegibilidade, nunca preditor.
# 3. **Auditoria**: qual variavel, sozinha, da AUC alta demais? Ela e causa ou consequencia?

# %%
# !pip install -q Boruta catboost lightgbm xgboost shap openpyxl "tabpfn==2.0.9"

# %%
import os
import re
import json
import time
import unicodedata
import warnings

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss, confusion_matrix,
                             roc_auc_score, roc_curve)
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from scipy.stats import rankdata

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from tabpfn import TabPFNClassifier

warnings.filterwarnings("ignore")
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 220)
sns.set_theme(style="whitegrid", context="notebook")
matplotlib.rcParams["figure.dpi"] = 110

# Versoes antigas do Boruta usam aliases numpy removidos. O shim deixa o import funcionar.
for _alias, _tipo in [("float", float), ("int", int), ("bool", bool), ("object", object)]:
    if not hasattr(np, _alias):
        setattr(np, _alias, _tipo)
from boruta import BorutaPy  # noqa: E402

# %% [markdown]
# ## Configuracao

# %%
SEED = 42
ALVO = "TROQUE_PELO_DESFECHO"

TEST_SIZE = 0.30
N_SPLITS = 5
N_REPEATS = 5
BORUTA_MAX_ITER = 80
BORUTA_PERC = 90        # 100 e o criterio original, rigido demais com poucos eventos
MAX_MISSING = 0.70
IND_MISSING = 0.20
SENS_ALVO = 0.80
N_BOOT = 2000

CAMINHOS_DADOS = [
    "data/TROQUE.xlsx",
    "/content/drive/MyDrive/TROQUE.xlsx",
]
DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results") \
    if "__file__" in globals() else "results"
os.makedirs(DIR_RESULTADOS, exist_ok=True)
rng = np.random.default_rng(SEED)

_LEGENDAS = os.path.join(DIR_RESULTADOS, "legendas.json")


def salvar_fig(nome, legenda=""):
    """Salva a figura e registra a legenda ao lado dela, para o relatorio nunca descolar."""
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_RESULTADOS, nome), dpi=300, bbox_inches="tight",
                facecolor="white")
    plt.show()
    # Fora do notebook, plt.show() nao fecha a figura, e o shap.summary_plot, que desenha nos
    # eixos correntes, sai por cima da figura anterior.
    plt.close("all")
    if legenda:
        atual = {}
        if os.path.exists(_LEGENDAS):
            with open(_LEGENDAS, encoding="utf-8") as f:
                atual = json.load(f)
        atual[nome] = legenda
        with open(_LEGENDAS, "w", encoding="utf-8") as f:
            json.dump(atual, f, ensure_ascii=False, indent=1)


def salvar_tab(df, nome):
    df.to_csv(os.path.join(DIR_RESULTADOS, nome), index=False, encoding="utf-8-sig")
    return df


# %% [markdown]
# ## 1. Carga, nomes e valores impossiveis
#
# Nome de coluna vira ASCII uma vez so, porque acento quebra o codigo dependendo do encoding
# com que o arquivo e lido. Valor impossivel vira missing por faixa de plausibilidade, nunca
# por lista de valores digitada a mao, que para de casar quando o banco e atualizado.

# %%
def sem_acento(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"_+", "_", re.sub(r"[^0-9a-zA-Z_]+", "_", texto)).strip("_")


LIMITES_PLAUSIVEIS = {
    # "coluna": (minimo, maximo),
}


def carregar_e_limpar(verbose=True):
    caminho = next((c for c in CAMINHOS_DADOS if os.path.exists(c)), None)
    if caminho is None:
        raise FileNotFoundError("Nenhum caminho de CAMINHOS_DADOS existe.")
    d = pd.read_excel(caminho)
    d = d.rename(columns={c: sem_acento(c) for c in d.columns})
    if verbose:
        print(f"Lendo: {caminho}\nDimensao bruta: {d.shape[0]} linhas, {d.shape[1]} colunas")
    for col, (lo, hi) in LIMITES_PLAUSIVEIS.items():
        if col in d.columns:
            fora = ((d[col] < lo) | (d[col] > hi)).sum()
            if fora and verbose:
                print(f"  {col}: {fora} valor(es) fora de [{lo}, {hi}] -> missing")
            d.loc[(d[col] < lo) | (d[col] > hi), col] = np.nan
    return d


df_full = carregar_e_limpar()

# %% [markdown]
# ## 2. Elegibilidade e lista de vazamento
#
# Cada bloco diz por que a variavel sai. A regra e sempre a mesma: se a informacao so existe
# depois do momento da predicao, ela nao pode ser preditor.

# %%
VAZAMENTO_DESFECHO = []      # o desfecho, suas variantes e o que e derivado dele
VAZAMENTO_DATA = []          # datas posteriores ao momento da predicao
POS_MOMENTO = []             # medido depois do momento da predicao
IDENTIFICADORES = ["id", "nome"]
CONSTANTES = []              # coluna com um unico valor na coorte

# Mantidas de proposito, cada uma com a justificativa escrita:
MANTIDAS_COM_JUSTIFICATIVA = {
    # "coluna": "por que ela ja era conhecida no momento da predicao",
}

TODAS_REMOVIDAS = (VAZAMENTO_DESFECHO + VAZAMENTO_DATA + POS_MOMENTO
                   + IDENTIFICADORES + CONSTANTES)


def montar_coorte(d, verbose=True):
    """Aplica elegibilidade e remove vazamento. Devolve X, y, fluxograma e a coorte."""
    elegivel = pd.Series(True, index=d.index)      # TROQUE pelo criterio real
    coorte = d.loc[elegivel].reset_index(drop=True)
    X = coorte.drop(columns=[c for c in TODAS_REMOVIDAS if c in coorte.columns] + [ALVO])
    X = X.drop(columns=X.select_dtypes(include=["datetime64[ns]"]).columns)
    y = coorte[ALVO].astype(int).to_numpy()
    fluxo = {"n_inicial": len(d), "n_analisado": int(elegivel.sum()), "eventos": int(y.sum()),
             "taxa_evento": round(float(y.mean()), 4), "candidatas": X.shape[1],
             "EPV_candidatas": round(float(y.sum() / max(X.shape[1], 1)), 2)}
    if verbose:
        for k, v in fluxo.items():
            print(f"  {k:20s} {v}")
    return X, y, fluxo, coorte


X_df, y, fluxo, coorte = montar_coorte(df_full)
salvar_tab(pd.DataFrame([fluxo]), "tab01_fluxograma.csv")

# %% [markdown]
# ## 3. Auditoria automatica de vazamento
#
# A lista manual cobre o que se conhece. A auditoria pega o que passou: variavel que sozinha
# separa quase perfeitamente o desfecho e suspeita de ser consequencia, e nao causa.

# %%
def auc_univariada(coluna, alvo):
    m = coluna.notna()
    if m.sum() < 30 or len(np.unique(alvo[m])) < 2 or coluna[m].nunique() < 2:
        return np.nan
    a = roc_auc_score(alvo[m], coluna[m])
    return max(a, 1 - a)


auditoria = pd.DataFrame({
    "variavel": X_df.columns,
    "auc_univariada": [auc_univariada(X_df[c], y) for c in X_df.columns],
    "missing_pct": (X_df.isna().mean() * 100).round(1).to_numpy(),
}).sort_values("auc_univariada", ascending=False)
auditoria["suspeita_vazamento"] = auditoria["auc_univariada"] >= 0.80
print(auditoria.head(10).to_string(index=False))
suspeitas = auditoria.loc[auditoria["suspeita_vazamento"], "variavel"].tolist()
print(f"\nSinalizadas (AUC >= 0.80): {suspeitas or 'nenhuma'}")
salvar_tab(auditoria, "tab02_auditoria_vazamento.csv")

# %% [markdown]
# ## 4. Pre-processamento e Boruta como etapas do pipeline
#
# Tudo que aprende parametro do dado (mediana, quais colunas cair, o que o Boruta confirma) e
# transformador, ajustado so no treino de cada fold. E o que separa AUC honesta de AUC otimista.

# %%
class PreProcessador(BaseEstimator, TransformerMixin):
    """Descarta coluna quase vazia ou constante, imputa mediana, marca ausencia informativa."""

    def __init__(self, max_missing=MAX_MISSING, ind_missing=IND_MISSING):
        self.max_missing = max_missing
        self.ind_missing = ind_missing

    def fit(self, X, y=None):
        X = pd.DataFrame(X)
        frac = X.isna().mean()
        constante = X.nunique(dropna=True) <= 1
        self.colunas_ = X.columns[(frac <= self.max_missing) & (~constante)].tolist()
        self.descartadas_ = X.columns[(frac > self.max_missing) | constante].tolist()
        self.indicadores_ = [c for c in self.colunas_ if frac[c] >= self.ind_missing]
        self.medianas_ = X[self.colunas_].median(numeric_only=True)
        self.nomes_ = self.colunas_ + [f"{c}__ausente" for c in self.indicadores_]
        return self

    def transform(self, X):
        X = pd.DataFrame(X)
        Z = X[self.colunas_].copy()
        ind = {f"{c}__ausente": Z[c].isna().astype(float) for c in self.indicadores_}
        Z = Z.fillna(self.medianas_).fillna(0.0)
        if ind:
            Z = pd.concat([Z, pd.DataFrame(ind, index=Z.index)], axis=1)
        return Z[self.nomes_].astype(float)

    def get_feature_names_out(self, input_features=None):
        return np.asarray(self.nomes_, dtype=object)


class SelecaoBoruta(BaseEstimator, TransformerMixin):
    """Boruta (Kursa e Rudnicki, 2010) com plano B quando nada e confirmado.

    Cada variavel ganha uma copia embaralhada, a shadow feature. So e confirmada a variavel
    real que bate a melhor sombra em mais rodadas do que o acaso explicaria, por teste binomial
    com Bonferroni. E selecao de todas as variaveis relevantes, nao do menor conjunto
    suficiente, que e a pergunta certa quando o objetivo tambem e entender o fenomeno.
    """

    def __init__(self, max_iter=BORUTA_MAX_ITER, perc=BORUTA_PERC, incluir_tentativas=True,
                 top_k_minimo=5, random_state=SEED, verbose=False):
        self.max_iter = max_iter
        self.perc = perc
        self.incluir_tentativas = incluir_tentativas
        self.top_k_minimo = top_k_minimo
        self.random_state = random_state
        self.verbose = verbose

    def fit(self, X, y):
        X = pd.DataFrame(X)
        floresta = RandomForestClassifier(n_estimators=300, max_depth=5,
                                          class_weight="balanced_subsample", n_jobs=-1,
                                          random_state=self.random_state)
        boruta = BorutaPy(floresta, n_estimators="auto", perc=self.perc,
                          max_iter=self.max_iter, random_state=self.random_state, verbose=0)
        boruta.fit(X.to_numpy(), np.asarray(y))
        nomes = np.array(X.columns.tolist())
        self.confirmadas_ = nomes[boruta.support_].tolist()
        self.tentativas_ = nomes[boruta.support_weak_].tolist()
        self.ranking_ = pd.Series(boruta.ranking_, index=nomes).sort_values()

        sel = list(self.confirmadas_)
        if self.incluir_tentativas:
            sel += [c for c in self.tentativas_ if c not in sel]
        if not sel:
            floresta.fit(X, y)
            sel = pd.Series(floresta.feature_importances_,
                            index=nomes).nlargest(self.top_k_minimo).index.tolist()
            self.recorreu_ao_plano_b_ = True
            if self.verbose:
                print(f"    Boruta nao confirmou nada, usando top {self.top_k_minimo}")
        else:
            self.recorreu_ao_plano_b_ = False
        self.selecionadas_ = sel
        return self

    def transform(self, X):
        return pd.DataFrame(X)[self.selecionadas_]

    def get_feature_names_out(self, input_features=None):
        return np.asarray(self.selecionadas_, dtype=object)


# %% [markdown]
# ## 5. Modelos
#
# A logistica regularizada e referencia obrigatoria: com poucas dezenas de eventos ela costuma
# empatar ou ganhar de gradient boosting, e um trabalho de predicao clinica precisa mostrar essa
# comparacao. O ensemble e media de postos, nao de probabilidade: com peso de classe a logistica
# preve risco medio de 0.45 e as arvores preveem 0.045, entao a media simples seria a logistica
# disfarcada. O preco e que o ensemble so tem metrica de ordenacao, nao de calibracao.

# %%
NOME_ENSEMBLE = "Ensemble (media de postos)"
NOME_TABPFN = "TabPFN"
ORDEM_SIMPLICIDADE = ["Regressao logistica", "Random Forest", "CatBoost", "XGBoost",
                      "LightGBM", NOME_TABPFN, NOME_ENSEMBLE]


def modelos_base(n_pos, n_neg):
    razao = n_neg / max(n_pos, 1)
    return {
        "Regressao logistica": Pipeline([
            ("escala", StandardScaler()),
            ("clf", LogisticRegression(penalty="l2", C=0.1, class_weight="balanced",
                                       max_iter=5000, solver="liblinear", random_state=SEED))]),
        "Random Forest": RandomForestClassifier(
            n_estimators=500, max_depth=5, min_samples_leaf=5,
            class_weight="balanced_subsample", n_jobs=-1, random_state=SEED),
        "XGBoost": XGBClassifier(
            n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.8,
            colsample_bytree=0.8, reg_lambda=1.0, scale_pos_weight=razao,
            eval_metric="logloss", n_jobs=-1, random_state=SEED),
        "LightGBM": LGBMClassifier(
            n_estimators=300, max_depth=3, num_leaves=7, learning_rate=0.05,
            min_child_samples=10, subsample=0.8, colsample_bytree=0.8,
            class_weight="balanced", n_jobs=-1, random_state=SEED, verbose=-1),
        "CatBoost": CatBoostClassifier(
            iterations=300, depth=3, learning_rate=0.05, l2_leaf_reg=3.0,
            auto_class_weights="Balanced", verbose=False, allow_writing_files=False,
            random_seed=SEED),
        # Transformer pre-treinado em dado sintetico: nao treina, o conjunto de treino inteiro
        # entra como contexto no forward pass. E o regime de poucas centenas de linhas e poucas
        # colunas. Nao tem peso de classe, e por isso costuma ser o melhor calibrado.
        NOME_TABPFN: TabPFNClassifier(device="cpu", n_estimators=4, random_state=SEED,
                                      ignore_pretraining_limits=True),
    }


GRADES = {
    "Regressao logistica": {"clf__C": [0.01, 0.03, 0.1, 0.3, 1.0, 3.0]},
    "Random Forest": {"max_depth": [3, 4, 5, 7, None], "min_samples_leaf": [2, 5, 10, 20],
                      "max_features": ["sqrt", 0.3, 0.5]},
    "XGBoost": {"max_depth": [2, 3, 4], "learning_rate": [0.01, 0.03, 0.05, 0.1],
                "n_estimators": [200, 300, 500], "subsample": [0.6, 0.8, 1.0],
                "colsample_bytree": [0.6, 0.8, 1.0], "reg_lambda": [1.0, 5.0, 10.0]},
    "LightGBM": {"max_depth": [2, 3, 4], "num_leaves": [3, 7, 15],
                 "learning_rate": [0.01, 0.03, 0.05, 0.1], "n_estimators": [200, 300, 500],
                 "min_child_samples": [5, 10, 20]},
    "CatBoost": {"depth": [2, 3, 4], "learning_rate": [0.01, 0.03, 0.05, 0.1],
                 "iterations": [200, 300, 500], "l2_leaf_reg": [1.0, 3.0, 10.0]},
    NOME_TABPFN: {"n_estimators": [4, 8], "softmax_temperature": [0.75, 0.9, 1.0]},
}


def n_combinacoes(grade):
    total = 1
    for valores in grade.values():
        total *= len(valores)
    return total


def sem_paralelismo_interno(modelo):
    """Desliga o paralelismo do modelo antes de entrar na busca paralela.

    Sem isso cada processo do joblib abre uma thread por nucleo e a busca chega a nao terminar.
    """
    m = clone(modelo)
    ajuste = {p: 1 for p in m.get_params() if p == "n_jobs" or p.endswith("__n_jobs")}
    if isinstance(m, CatBoostClassifier):
        ajuste["thread_count"] = 1
    return m.set_params(**ajuste) if ajuste else m


def escolher_campeao(auc_por_modelo, margem=0.01):
    """Maior AUC, empate ate `margem` resolvido a favor do modelo mais simples.

    Regra declarada antes de olhar o resultado. Com poucas dezenas de eventos, diferenca de AUC
    abaixo de 0.01 e ruido, e nesse caso o modelo mais simples e o que se defende.
    """
    melhor = max(auc_por_modelo.values())
    empatados = [m for m, a in auc_por_modelo.items() if melhor - a <= margem]
    return sorted(empatados, key=lambda m: ORDEM_SIMPLICIDADE.index(m))[0]


def postos(p):
    return rankdata(p) / len(p)


# %% [markdown]
# ## 6. Motor da validacao cruzada
#
# O Boruta roda uma vez por fold, no treino do fold, e o mesmo conjunto alimenta todos os
# modelos daquele fold. Quantos folds mantem cada variavel e a analise de estabilidade, que vale
# mais que uma lista unica tirada de um ajuste so.

# %%
def rodar_cv(X, y, n_repeats=N_REPEATS, boruta_iter=BORUTA_MAX_ITER, semente=SEED, verbose=True):
    cv = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=n_repeats, random_state=semente)
    nomes = list(modelos_base(1, 1).keys())
    oof = {m: np.full((n_repeats, len(y)), np.nan) for m in nomes}
    contagem, n_sel, t0 = {}, [], time.time()

    for k, (i_tr, i_te) in enumerate(cv.split(X, y)):
        rep = k // N_SPLITS
        prep = PreProcessador().fit(X.iloc[i_tr])
        Ztr, Zte = prep.transform(X.iloc[i_tr]), prep.transform(X.iloc[i_te])
        sel = SelecaoBoruta(max_iter=boruta_iter, random_state=semente + k).fit(Ztr, y[i_tr])
        Ztr_s, Zte_s = sel.transform(Ztr), sel.transform(Zte)
        n_sel.append(len(sel.selecionadas_))
        for v in sel.selecionadas_:
            contagem[v] = contagem.get(v, 0) + 1
        for nome, modelo in modelos_base(y[i_tr].sum(), len(i_tr) - y[i_tr].sum()).items():
            oof[nome][rep, i_te] = clone(modelo).fit(Ztr_s, y[i_tr]).predict_proba(Zte_s)[:, 1]
        if verbose and (k + 1) % N_SPLITS == 0:
            print(f"  repeticao {rep + 1}/{n_repeats} ({time.time() - t0:.0f}s, "
                  f"media de {np.mean(n_sel):.1f} variaveis por fold)")

    oof[NOME_ENSEMBLE] = np.full((n_repeats, len(y)), np.nan)
    for r in range(n_repeats):
        oof[NOME_ENSEMBLE][r] = np.mean([postos(oof[m][r]) for m in nomes], axis=0)

    n_folds = N_SPLITS * n_repeats
    estabilidade = (pd.DataFrame({"variavel": list(contagem), "folds": list(contagem.values())})
                    .assign(freq=lambda d: (d["folds"] / n_folds).round(3))
                    .sort_values("folds", ascending=False).reset_index(drop=True))
    return oof, estabilidade, float(np.mean(n_sel))


def tabela_metricas_cv(oof, y):
    linhas = []
    for nome, pred in oof.items():
        a, ap, br = [], [], []
        for r in range(pred.shape[0]):
            m = ~np.isnan(pred[r])
            a.append(roc_auc_score(y[m], pred[r][m]))
            ap.append(average_precision_score(y[m], pred[r][m]))
            br.append(np.nan if nome == NOME_ENSEMBLE else brier_score_loss(y[m], pred[r][m]))
        linhas.append({"modelo": nome, "AUC_media": float(np.mean(a)),
                       "AUC": f"{np.mean(a):.3f} ({np.min(a):.3f} a {np.max(a):.3f})",
                       "AUC_PR": f"{np.mean(ap):.3f}",
                       "Brier": "nao se aplica" if nome == NOME_ENSEMBLE
                       else f"{np.nanmean(br):.3f}"})
    return pd.DataFrame(linhas).sort_values("AUC_media", ascending=False)


def limiar_por_sensibilidade(y_true, prob, sens_min):
    """Maior limiar cuja sensibilidade ainda alcanca sens_min.

    roc_curve devolve limiares decrescentes e tpr crescente, entao o PRIMEIRO indice que
    satisfaz a restricao e o limiar mais alto que serve. Pegar o ultimo devolve sensibilidade 1
    e especificidade 0.
    """
    _, tpr, thr = roc_curve(y_true, prob)
    ok = tpr >= sens_min
    return float(thr[ok][0]) if ok.any() else 0.5


def metricas_completas(y_true, prob, limiar):
    pred = (prob >= limiar).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    return {"AUC": roc_auc_score(y_true, prob),
            "AUC_PR": average_precision_score(y_true, prob),
            "Sensibilidade": tp / max(tp + fn, 1), "Especificidade": tn / max(tn + fp, 1),
            "VPP": tp / max(tp + fp, 1), "VPN": tn / max(tn + fn, 1),
            "Brier": brier_score_loss(y_true, prob)}


def bootstrap_ic(y_true, prob, limiar, n=N_BOOT):
    guardado = {k: [] for k in metricas_completas(y_true, prob, limiar)}
    idx = np.arange(len(y_true))
    for _ in range(n):
        b = rng.choice(idx, size=len(idx), replace=True)
        if len(np.unique(y_true[b])) < 2:
            continue
        for k, v in metricas_completas(y_true[b], prob[b], limiar).items():
            guardado[k].append(v)
    return {k: (np.percentile(v, 2.5), np.percentile(v, 97.5)) for k, v in guardado.items()}


# %% [markdown]
# ## 7. Analise principal
#
# Daqui para baixo e especifico do experimento. O que nao muda: a estimativa que vale e a da
# validacao cruzada sobre a coorte inteira, e a amostra de teste existe para produzir o modelo
# final, o SHAP e a calibracao, nao para escolher modelo.

# %%
oof, estabilidade, media_sel = rodar_cv(X_df, y)
salvar_tab(estabilidade, "tab03_estabilidade_boruta.csv")
tabela_cv = tabela_metricas_cv(oof, y)
print(tabela_cv.drop(columns="AUC_media").to_string(index=False))
salvar_tab(tabela_cv.drop(columns="AUC_media"), "tab04_desempenho_cv.csv")
CAMPEAO = escolher_campeao(dict(zip(tabela_cv["modelo"], tabela_cv["AUC_media"])))
print(f"\nCampeao: {CAMPEAO}")

# %% [markdown]
# ## 8. SHAP
#
# TreeExplainer para arvore, LinearExplainer para a logistica, PermutationExplainer para o
# TabPFN, que nao tem estrutura que os outros saibam ler e por isso custa minutos. Devolve
# (valores, Z_usado) porque o explicador lento roda sobre uma subamostra.

# %%
import shap  # noqa: E402

MAX_LINHAS_SHAP_LENTO = 40
FUNDO_SHAP_LENTO = 20


def shap_valores(modelo, nome, Z):
    if nome == "Regressao logistica":
        Zt = modelo.named_steps["escala"].transform(Z)
        v = shap.LinearExplainer(modelo.named_steps["clf"], Zt).shap_values(Zt)
    elif nome == NOME_TABPFN:
        if len(Z) > MAX_LINHAS_SHAP_LENTO:
            Z = Z.sample(MAX_LINHAS_SHAP_LENTO, random_state=SEED).sort_index()
        fundo = shap.maskers.Independent(Z, max_samples=FUNDO_SHAP_LENTO)
        explicador = shap.PermutationExplainer(
            lambda A: modelo.predict_proba(pd.DataFrame(A, columns=Z.columns))[:, 1], fundo)
        v = explicador(Z, max_evals=2 * Z.shape[1] + 1, silent=True).values
    else:
        v = shap.TreeExplainer(modelo).shap_values(Z)
    if isinstance(v, list):
        v = v[1]
    v = np.asarray(v)
    if v.ndim == 3:
        v = v[:, :, 1]
    return v, Z


# %% [markdown]
# ## 9. Resumo

# %%
print("=" * 78)
print(f"Coorte ............. {len(y)} linhas, {y.sum()} eventos ({y.mean():.1%})")
print(f"Candidatas ......... {X_df.shape[1]} (EPV {fluxo['EPV_candidatas']})")
print(f"Campeao ............ {CAMPEAO}")
print(f"AUC .............. {tabela_cv.iloc[0]['AUC']}")
print(f"\nResultados em {DIR_RESULTADOS}")
