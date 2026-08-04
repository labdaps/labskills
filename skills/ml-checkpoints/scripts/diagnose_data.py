#!/usr/bin/env python3
"""Diagnostico dos dados que alimenta os checkpoints da skill ml-checkpoints.

Uso:
    python scripts/diagnose_data.py dados.csv --target obito
    python scripts/diagnose_data.py dados.parquet --target obito --id id_paciente --date dt_internacao
    python scripts/diagnose_data.py dados.csv --target obito --json > diagnostico.json

Le a base, mede o que decide as opcoes de cada checkpoint e imprime, para
CP2 a CP10, quais estrategias estao VIAVEL, DESACONSELHADO ou BLOQUEADO,
com o motivo medido. Nenhuma recomendacao sai daqui sem o numero que a
sustenta.

Dependencias: pandas e numpy. Exit codes: 0 = ok | 2 = erro de leitura ou argumento.
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
import pandas as pd

# Limiares. Sao o padrao do laboratorio, nao lei da natureza: ajuste com
# justificativa no registro de decisoes quando o desenho pedir.
MISSING_DESCARTE = 0.40      # acima disso, coluna candidata a descarte
MISSING_INDICADOR = 0.05     # acima disso, imputar exige indicador de missing
CARD_ONEHOT = 15             # cardinalidade maxima confortavel para one-hot
CARD_ALTA = 50               # acima disso, one-hot explode a matriz
QUASE_CONSTANTE = 0.99       # um unico valor cobrindo essa fracao das linhas
RATIO_ID = 0.95              # unicos/linhas acima disso: candidata a identificador
N_PEQUENO = 1000             # abaixo disso, holdout unico e instavel
MINORITARIA_MINIMA = 50      # casos da classe rara abaixo disso: CV repetida
EPV_MINIMO = 10              # casos da classe rara por feature
DESBALANCEAMENTO_SEVERO = 20  # razao majoritaria/minoritaria
LEAKAGE_AUC = 0.95           # AUC univariada acima disso: suspeita de vazamento
LEAKAGE_PUREZA = 0.98        # pureza de categoria acima disso: suspeita
SENTINELAS = (8, 9, 88, 99, 888, 999, 9999, -9, -99, -999)

VIAVEL, DESACONSELHADO, BLOQUEADO = "VIAVEL", "DESACONSELHADO", "BLOQUEADO"


def _fmt_pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def carregar(caminho: str) -> pd.DataFrame:
    baixo = caminho.lower()
    if baixo.endswith(".parquet"):
        return pd.read_parquet(caminho)
    if baixo.endswith((".xlsx", ".xls")):
        return pd.read_excel(caminho)
    if baixo.endswith((".tsv", ".tab")):
        return pd.read_csv(caminho, sep="\t")
    return pd.read_csv(caminho)


def auc_univariada(x: pd.Series, y: pd.Series) -> float | None:
    """AUC de uma variavel numerica contra desfecho binario, via postos.

    Equivalente a Mann-Whitney U normalizado. Retorna None quando nao da
    para calcular (sem variacao, ou uma das classes vazia apos remover NaN).
    """
    mask = x.notna() & y.notna()
    x, y = x[mask], y[mask]
    if x.nunique() < 2:
        return None
    pos = y == 1
    n_pos, n_neg = int(pos.sum()), int((~pos).sum())
    if n_pos == 0 or n_neg == 0:
        return None
    postos = x.rank(method="average")
    soma_pos = float(postos[pos].sum())
    auc = (soma_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    return float(max(auc, 1 - auc))  # direcao nao importa para suspeita


def pureza_categoria(x: pd.Series, y: pd.Series) -> float | None:
    """Fracao das linhas em que a categoria ja determina o desfecho.

    Uma coluna que separa o desfecho quase perfeitamente costuma ser
    consequencia dele, nao preditora.
    """
    mask = x.notna() & y.notna()
    x, y = x[mask], y[mask]
    if len(x) == 0 or x.nunique() < 2:
        return None
    tab = pd.crosstab(x, y)
    return float(tab.max(axis=1).sum() / tab.to_numpy().sum())


def parece_data(s: pd.Series) -> bool:
    if pd.api.types.is_datetime64_any_dtype(s):
        return True
    if not pd.api.types.is_object_dtype(s):
        return False
    amostra = s.dropna().astype(str).head(200)
    if amostra.empty:
        return False
    convertido = pd.to_datetime(amostra, errors="coerce", format="mixed")
    return convertido.notna().mean() > 0.8


def perfil_colunas(df: pd.DataFrame, alvo: str) -> list[dict]:
    n = len(df)
    perfis = []
    for col in df.columns:
        if col == alvo:
            continue
        s = df[col]
        n_unicos = int(s.nunique(dropna=True))
        faltantes = float(s.isna().mean())
        flags = []

        if faltantes >= MISSING_DESCARTE:
            flags.append("missing_alto")
        elif faltantes > MISSING_INDICADOR:
            flags.append("missing_medio")
        elif faltantes > 0:
            flags.append("missing_baixo")

        if n_unicos <= 1:
            flags.append("constante")
        elif n > 0 and float(s.value_counts(normalize=True, dropna=True).iloc[0]) >= QUASE_CONSTANTE:
            flags.append("quase_constante")

        # Identificador e rotulo, nunca medida continua: uma coluna float com
        # casas decimais e quase sempre exame ou sinal vital, nao chave.
        inteira_ou_texto = not pd.api.types.is_numeric_dtype(s) or bool(
            len(s.dropna()) and (s.dropna() == s.dropna().round()).all()
        )
        if n > 0 and n_unicos / n >= RATIO_ID and n_unicos > 20 and inteira_ou_texto:
            flags.append("candidata_id")

        if parece_data(s):
            flags.append("data")

        e_numerica = pd.api.types.is_numeric_dtype(s)
        if not e_numerica and "data" not in flags:
            if n_unicos > CARD_ALTA:
                flags.append("cardinalidade_alta")
            elif n_unicos > CARD_ONEHOT:
                flags.append("cardinalidade_media")

        if e_numerica and "candidata_id" not in flags:
            # Sentinela nao e "o numero 9 aparece": e um valor implausivel para
            # a escala da variavel, repetido o suficiente para ser codigo. Sem
            # essa checagem, codigo de municipio e prontuario viram falso positivo.
            nao_nulos_num = s.dropna()
            achados = []
            if len(nao_nulos_num):
                corte = float(np.nanpercentile(nao_nulos_num, 95)) * 3
                for v in SENTINELAS:
                    freq = float((nao_nulos_num == v).mean())
                    if freq >= 0.002 and (v < 0 or v > corte):
                        achados.append(v)
            if achados:
                flags.append("sentinela:" + ",".join(str(a) for a in sorted(achados)))

            # Codigo categorico lido como numero e o erro silencioso mais comum
            # em base de saude: codigo de municipio, CID numerico, tipo de
            # estabelecimento. O modelo passa a tratar como ordem o que e rotulo.
            # A deteccao e uma suspeita, nao um veredito: confirmar no CP4.
            nao_nulos = s.dropna()
            if len(nao_nulos) and 3 <= n_unicos <= 500 and n_unicos / n < 0.5:
                if bool((nao_nulos == nao_nulos.round()).all()):
                    flags.append("possivel_codigo")

        perfis.append(
            {
                "coluna": col,
                "dtype": str(s.dtype),
                "missing": faltantes,
                "n_unicos": n_unicos,
                "numerica": bool(e_numerica),
                "flags": flags,
            }
        )
    return perfis


def perfil_alvo(df: pd.DataFrame, alvo: str) -> dict:
    s = df[alvo]
    n_unicos = int(s.nunique(dropna=True))
    info: dict = {"nome": alvo, "missing": float(s.isna().mean()), "n_unicos": n_unicos}

    if n_unicos == 2:
        contagem = s.value_counts(dropna=True)
        minoritaria = int(contagem.min())
        majoritaria = int(contagem.max())
        info.update(
            {
                "tipo": "binaria",
                "classe_minoritaria": str(contagem.idxmin()),
                "n_minoritaria": minoritaria,
                "n_majoritaria": majoritaria,
                "prevalencia": float(minoritaria / contagem.sum()),
                "razao_desbalanceamento": float(majoritaria / minoritaria) if minoritaria else float("inf"),
            }
        )
    elif n_unicos <= 10 and not pd.api.types.is_float_dtype(s):
        contagem = s.value_counts(dropna=True)
        info.update(
            {
                "tipo": "multiclasse",
                "n_classes": n_unicos,
                "n_minoritaria": int(contagem.min()),
                "razao_desbalanceamento": float(contagem.max() / contagem.min()) if contagem.min() else float("inf"),
            }
        )
    elif pd.api.types.is_numeric_dtype(s):
        info.update({"tipo": "continua", "media": float(s.mean()), "desvio": float(s.std())})
    else:
        info.update({"tipo": "indefinida"})
    return info


def suspeitas_leakage(
    df: pd.DataFrame, alvo: str, perfis: list[dict], tipo_alvo: str, col_id: str | None = None
) -> list[dict]:
    if tipo_alvo != "binaria":
        return []
    y = df[alvo]
    codigos, _ = pd.factorize(y)
    y_bin = pd.Series((codigos == codigos[codigos >= 0][0]).astype(int), index=y.index)
    y_bin[y.isna()] = np.nan

    suspeitas = []
    for p in perfis:
        col = p["coluna"]
        if col == col_id or {"candidata_id", "data", "constante"} & set(p["flags"]):
            continue
        if p["numerica"]:
            auc = auc_univariada(df[col], y_bin)
            if auc is not None and auc >= LEAKAGE_AUC:
                suspeitas.append({"coluna": col, "criterio": "auc_univariada", "valor": round(auc, 4)})
        elif p["n_unicos"] <= CARD_ALTA:
            pureza = pureza_categoria(df[col], y_bin)
            if pureza is not None and pureza >= LEAKAGE_PUREZA:
                suspeitas.append({"coluna": col, "criterio": "pureza_categoria", "valor": round(pureza, 4)})
    return suspeitas


def perfil_grupo(df: pd.DataFrame, col_id: str | None) -> dict | None:
    if not col_id or col_id not in df.columns:
        return None
    contagem = df[col_id].value_counts(dropna=True)
    return {
        "coluna": col_id,
        "n_grupos": int(contagem.size),
        "linhas_por_grupo_max": int(contagem.max()) if contagem.size else 0,
        "linhas_por_grupo_media": float(contagem.mean()) if contagem.size else 0.0,
        "tem_repeticao": bool(contagem.size and contagem.max() > 1),
    }


def regras_checkpoints(d: dict) -> dict[str, list[dict]]:
    """Traduz o diagnostico em status por opcao, para cada checkpoint."""
    n = d["n_linhas"]
    alvo = d["alvo"]
    tipo = alvo.get("tipo")
    grupo = d.get("grupo")
    datas = [p["coluna"] for p in d["colunas"] if "data" in p["flags"]]
    # identificador, data e coluna de agrupamento nao sao preditoras
    nao_features = {p["coluna"] for p in d["colunas"] if {"candidata_id", "data", "constante"} & set(p["flags"])}
    if grupo:
        nao_features.add(grupo["coluna"])
    n_features = len([p for p in d["colunas"] if p["coluna"] not in nao_features])
    minoritaria = alvo.get("n_minoritaria")
    razao = alvo.get("razao_desbalanceamento")

    cp: dict[str, list[dict]] = {}

    # CP2: separacao dos dados
    opcoes = []
    if grupo and grupo["tem_repeticao"]:
        opcoes.append(
            {
                "opcao": "holdout aleatorio estratificado",
                "status": BLOQUEADO,
                "motivo": f"'{grupo['coluna']}' repete ate {grupo['linhas_por_grupo_max']} linhas por grupo; "
                f"split por linha coloca o mesmo grupo no treino e no teste",
            }
        )
        opcoes.append(
            {
                "opcao": "StratifiedGroupKFold pelo identificador",
                "status": VIAVEL,
                "motivo": f"{grupo['n_grupos']} grupos distintos em {n} linhas, media de "
                f"{grupo['linhas_por_grupo_media']:.1f} linhas por grupo",
            }
        )
    else:
        opcoes.append(
            {
                "opcao": "holdout aleatorio estratificado",
                "status": VIAVEL if n >= N_PEQUENO else DESACONSELHADO,
                "motivo": f"N={n}" + ("" if n >= N_PEQUENO else f", abaixo de {N_PEQUENO} o holdout unico varia demais entre sementes"),
            }
        )
    opcoes.append(
        {
            "opcao": "validacao cruzada repetida ou aninhada",
            "status": VIAVEL,
            "motivo": (
                f"classe rara com {minoritaria} casos, abaixo de {MINORITARIA_MINIMA}: e a unica forma de ter IC honesto"
                if isinstance(minoritaria, int) and minoritaria < MINORITARIA_MINIMA
                else "sempre disponivel, custa mais tempo de computacao"
            ),
        }
    )
    opcoes.append(
        {
            "opcao": "split temporal",
            "status": VIAVEL if datas else BLOQUEADO,
            "motivo": f"colunas de data detectadas: {', '.join(datas)}" if datas else "nenhuma coluna de data detectada",
        }
    )
    cp["CP2"] = opcoes

    # CP3: missing
    alto = [p["coluna"] for p in d["colunas"] if "missing_alto" in p["flags"]]
    medio = [p["coluna"] for p in d["colunas"] if "missing_medio" in p["flags"]]
    baixo = [p["coluna"] for p in d["colunas"] if "missing_baixo" in p["flags"]]
    sentinelas = [p["coluna"] for p in d["colunas"] if any(f.startswith("sentinela:") for f in p["flags"])]
    cp["CP3"] = [
        {
            "opcao": "modelo nativo a NaN (LightGBM, XGBoost, CatBoost)",
            "status": VIAVEL,
            "motivo": "trata missing como informacao; evita inventar valor, mas prende a familia de modelo",
        },
        {
            "opcao": "imputacao simples (mediana ou moda) com indicador",
            "status": VIAVEL if (medio or baixo) else DESACONSELHADO,
            "motivo": f"{len(medio)} coluna(s) entre {_fmt_pct(MISSING_INDICADOR)} e {_fmt_pct(MISSING_DESCARTE)} de missing"
            if medio
            else "pouco missing na base; imputar muda pouco",
        },
        {
            "opcao": "imputacao multipla (MICE)",
            "status": VIAVEL if medio else DESACONSELHADO,
            "motivo": "faz sentido com missing intermediario e correlacao entre variaveis; custa tempo e complica o relato",
        },
        {
            "opcao": "descartar colunas muito faltantes",
            "status": VIAVEL if alto else BLOQUEADO,
            "motivo": f"colunas acima de {_fmt_pct(MISSING_DESCARTE)}: {', '.join(alto)}" if alto else "nenhuma coluna nessa faixa",
        },
        {
            "opcao": "descartar linhas com missing (complete case)",
            "status": DESACONSELHADO,
            "motivo": "em saude, quem tem mais missing costuma ser quem tem menos acesso; a exclusao vira vies de selecao",
        },
        {
            "opcao": "tratar sentinelas antes de qualquer imputacao",
            "status": VIAVEL if sentinelas else BLOQUEADO,
            "motivo": f"valores tipo 9/99/999 encontrados em: {', '.join(sentinelas[:8])}"
            if sentinelas
            else "nenhum valor sentinela tipico encontrado",
        },
    ]

    # CP4: pre-processamento
    card_alta = [p["coluna"] for p in d["colunas"] if "cardinalidade_alta" in p["flags"]]
    card_media = [p["coluna"] for p in d["colunas"] if "cardinalidade_media" in p["flags"]]
    categoricas = [p["coluna"] for p in d["colunas"] if not p["numerica"] and "data" not in p["flags"]]
    codigos = [p["coluna"] for p in d["colunas"] if "possivel_codigo" in p["flags"] and p["coluna"] not in nao_features]
    cp["CP4"] = [
        {
            "opcao": "confirmar quais numericas sao codigo e nao quantidade",
            "status": VIAVEL if codigos else BLOQUEADO,
            "motivo": f"candidatas a codigo lido como numero: {', '.join(codigos[:10])}"
            + (f" e mais {len(codigos) - 10}" if len(codigos) > 10 else "")
            + ". Tratada como numero, o modelo le ordem onde so ha rotulo"
            if codigos
            else "nenhuma numerica com cara de codigo",
        },
        {
            "opcao": "one-hot encoding",
            "status": VIAVEL if categoricas and not card_alta else (DESACONSELHADO if card_alta else BLOQUEADO),
            "motivo": f"cardinalidade alta em: {', '.join(card_alta)}" if card_alta
            else (f"{len(categoricas)} categorica(s) com cardinalidade tratavel" if categoricas else "nenhuma categorica"),
        },
        {
            "opcao": "categoricas nativas (CatBoost, LightGBM)",
            "status": VIAVEL if card_alta or card_media else DESACONSELHADO,
            "motivo": f"resolve as de cardinalidade alta sem explodir a matriz: {', '.join((card_alta + card_media)[:8])}"
            if (card_alta or card_media)
            else "sem cardinalidade alta, one-hot ja resolve",
        },
        {
            "opcao": "target encoding",
            "status": DESACONSELHADO if card_alta else BLOQUEADO,
            "motivo": "so dentro do fold, senao vaza desfecho; e a fonte de leakage mais comum em competicao",
        },
        {
            "opcao": "escalonamento (StandardScaler)",
            "status": VIAVEL,
            "motivo": "necessario para modelo linear, SVM e KNN; irrelevante para arvore. Decisao condicional ao CP6",
        },
    ]

    # CP5: desbalanceamento
    if tipo in ("binaria", "multiclasse") and isinstance(razao, float):
        severo = razao >= DESBALANCEAMENTO_SEVERO
        cp["CP5"] = [
            {
                "opcao": "nao balancear, ajustar so o ponto de corte",
                "status": VIAVEL,
                "motivo": f"razao {razao:.1f} para 1; preserva a probabilidade calibrada, que e o que o clinico usa",
            },
            {
                "opcao": "class_weight balanceado",
                "status": VIAVEL if severo else DESACONSELHADO,
                "motivo": "mexe menos na probabilidade que reamostragem" if severo else f"razao {razao:.1f} para 1 nao justifica",
            },
            {
                "opcao": "SMOTE ou reamostragem",
                "status": DESACONSELHADO,
                "motivo": "so dentro do fold, e exige recalibrar depois: a prevalencia artificial desloca toda a probabilidade prevista",
            },
        ]
    else:
        cp["CP5"] = [{"opcao": "n/a", "status": BLOQUEADO, "motivo": f"desfecho '{tipo}' nao tem desbalanceamento de classe"}]

    # CP6: modelos candidatos
    epv = (minoritaria / n_features) if isinstance(minoritaria, int) and n_features else None
    cp["CP6"] = [
        {
            "opcao": "baseline obrigatoria (regressao logistica ou escore clinico)",
            "status": VIAVEL,
            "motivo": "sem baseline nao ha como dizer se o ganho do modelo complexo paga a perda de leitura clinica",
        },
        {
            "opcao": "gradient boosting (LightGBM, XGBoost, CatBoost)",
            "status": VIAVEL if n >= 500 else DESACONSELHADO,
            "motivo": f"N={n}" + ("" if n >= 500 else ", amostra pequena demais: risco alto de sobreajuste"),
        },
        {
            "opcao": "modelo linear regularizado",
            "status": VIAVEL,
            "motivo": (
                f"casos da classe rara por feature = {epv:.1f}, abaixo de {EPV_MINIMO}: modelo simples e mais honesto aqui"
                if epv is not None and epv < EPV_MINIMO
                else "boa referencia interpretavel"
            ),
        },
        {
            "opcao": "rede neural tabular",
            "status": DESACONSELHADO if n < 10000 else VIAVEL,
            "motivo": f"N={n}; em dado tabular de saude raramente bate boosting abaixo de dezenas de milhares de linhas",
        },
    ]

    # CP7: selecao de features
    cp["CP7"] = [
        {
            "opcao": "manter todas as features",
            "status": VIAVEL if epv is None or epv >= EPV_MINIMO else DESACONSELHADO,
            "motivo": f"{n_features} features candidatas"
            + ("" if epv is None or epv >= EPV_MINIMO else f", com apenas {epv:.1f} casos raros por feature"),
        },
        {
            "opcao": "selecao por conhecimento clinico",
            "status": VIAVEL,
            "motivo": "o unico criterio que sobrevive a validacao externa; exige um clinico na decisao",
        },
        {
            "opcao": "selecao por importancia dentro do fold",
            "status": VIAVEL,
            "motivo": "valido se a selecao acontecer dentro do fold de treino; fora dele e leakage",
        },
        {
            "opcao": "eliminacao recursiva (RFE)",
            "status": DESACONSELHADO if n < N_PEQUENO else VIAVEL,
            "motivo": "instavel em amostra pequena: a lista de features muda a cada semente",
        },
    ]

    # CP8: metrica principal
    if tipo == "binaria":
        prev = alvo.get("prevalencia", 0.5)
        cp["CP8"] = [
            {
                "opcao": "AUPRC como principal",
                "status": VIAVEL if prev < 0.10 else DESACONSELHADO,
                "motivo": f"prevalencia {_fmt_pct(prev)}; com desfecho raro a AUROC parece boa mesmo com muitos falsos positivos",
            },
            {
                "opcao": "AUROC como principal",
                "status": VIAVEL if prev >= 0.10 else DESACONSELHADO,
                "motivo": f"prevalencia {_fmt_pct(prev)}; adequada quando as classes nao sao extremas",
            },
            {
                "opcao": "sensibilidade em especificidade fixa",
                "status": VIAVEL,
                "motivo": "traduz direto para o uso clinico, se houver um ponto de operacao definido pelo servico",
            },
            {
                "opcao": "decision curve analysis",
                "status": VIAVEL,
                "motivo": "responde se usar o modelo e melhor que tratar todos ou ninguem, que e a pergunta do gestor",
            },
        ]
    elif tipo == "continua":
        cp["CP8"] = [
            {"opcao": "RMSE", "status": VIAVEL, "motivo": "penaliza erro grande; sensivel a outlier"},
            {"opcao": "MAE", "status": VIAVEL, "motivo": "mais robusto a outlier, mais facil de explicar"},
            {"opcao": "R2", "status": DESACONSELHADO, "motivo": "nao diz o erro na unidade clinica; use como complemento"},
        ]
    else:
        cp["CP8"] = [
            {"opcao": "macro F1", "status": VIAVEL, "motivo": "trata as classes com o mesmo peso"},
            {"opcao": "AUC one-vs-rest por classe", "status": VIAVEL, "motivo": "mostra qual classe o modelo nao aprendeu"},
        ]

    # CP9: calibracao
    cp["CP9"] = [
        {
            "opcao": "reportar calibracao sem recalibrar",
            "status": VIAVEL,
            "motivo": "minimo aceitavel em saude: slope, intercepto e Brier",
        },
        {
            "opcao": "Platt (sigmoid)",
            "status": VIAVEL,
            "motivo": "estavel em amostra pequena; primeira escolha quando ha reamostragem no pipeline",
        },
        {
            "opcao": "isotonica",
            "status": VIAVEL if n >= 5000 else DESACONSELHADO,
            "motivo": f"N={n}; abaixo de alguns milhares ela sobreajusta a curva de calibracao",
        },
    ]

    # CP10: interpretabilidade
    cp["CP10"] = [
        {
            "opcao": "SHAP com direcao por variavel",
            "status": VIAVEL,
            "motivo": "padrao do laboratorio; marque as variaveis cuja direcao contraria o esperado clinicamente",
        },
        {
            "opcao": "coeficientes do modelo linear",
            "status": VIAVEL,
            "motivo": "leitura direta, se a baseline linear entrar no relato",
        },
        {
            "opcao": "partial dependence",
            "status": VIAVEL,
            "motivo": "mostra a forma do efeito; limite a faixa com suporte amostral",
        },
        {
            "opcao": "importancia por permutacao",
            "status": DESACONSELHADO if any("cardinalidade_alta" in p["flags"] for p in d["colunas"]) else VIAVEL,
            "motivo": "com variaveis correlacionadas e de alta cardinalidade, ela distribui credito de forma enganosa",
        },
    ]

    return cp


def diagnosticar(df: pd.DataFrame, alvo: str, col_id: str | None, col_data: str | None) -> dict:
    perfis = perfil_colunas(df, alvo)
    info_alvo = perfil_alvo(df, alvo)

    if col_data and col_data in df.columns:
        for p in perfis:
            if p["coluna"] == col_data and "data" not in p["flags"]:
                p["flags"].append("data")

    d = {
        "n_linhas": int(len(df)),
        "n_colunas": int(df.shape[1]),
        "linhas_duplicadas": int(df.duplicated().sum()),
        "alvo": info_alvo,
        "colunas": perfis,
        "grupo": perfil_grupo(df, col_id),
        "suspeitas_leakage": suspeitas_leakage(df, alvo, perfis, info_alvo.get("tipo", ""), col_id),
    }
    d["checkpoints"] = regras_checkpoints(d)
    return d


def imprimir(d: dict) -> None:
    alvo = d["alvo"]
    print("=" * 72)
    print("DIAGNOSTICO DOS DADOS")
    print("=" * 72)
    print(f"Linhas: {d['n_linhas']}   Colunas: {d['n_colunas']}   Duplicadas: {d['linhas_duplicadas']}")
    print()

    print(f"Desfecho '{alvo['nome']}': {alvo.get('tipo')}")
    if alvo.get("tipo") == "binaria":
        print(
            f"  prevalencia {_fmt_pct(alvo['prevalencia'])} "
            f"({alvo['n_minoritaria']} casos da classe '{alvo['classe_minoritaria']}' "
            f"contra {alvo['n_majoritaria']}), razao {alvo['razao_desbalanceamento']:.1f} para 1"
        )
    if alvo.get("missing", 0) > 0:
        print(f"  ATENCAO: {_fmt_pct(alvo['missing'])} de missing no proprio desfecho")
    print()

    marcadas = [p for p in d["colunas"] if p["flags"]]
    if marcadas:
        print(f"Colunas com algo a decidir ({len(marcadas)} de {len(d['colunas'])}):")
        for p in sorted(marcadas, key=lambda x: -x["missing"]):
            print(f"  {p['coluna']:<28} missing {_fmt_pct(p['missing']):>7}  unicos {p['n_unicos']:>6}  {', '.join(p['flags'])}")
        print()

    if d.get("grupo"):
        g = d["grupo"]
        print(
            f"Agrupamento por '{g['coluna']}': {g['n_grupos']} grupos, "
            f"ate {g['linhas_por_grupo_max']} linhas por grupo"
            + ("  <- split aleatorio por linha vaza grupo entre treino e teste" if g["tem_repeticao"] else "")
        )
        print()

    if d["suspeitas_leakage"]:
        print("SUSPEITA DE VAZAMENTO (verifique antes de qualquer modelagem):")
        for s in d["suspeitas_leakage"]:
            print(f"  {s['coluna']:<28} {s['criterio']} = {s['valor']}")
        print("  Uma variavel que quase determina o desfecho costuma ser consequencia dele.")
        print()

    titulos = {
        "CP2": "CP2 separacao dos dados",
        "CP3": "CP3 dados faltantes",
        "CP4": "CP4 pre-processamento",
        "CP5": "CP5 desbalanceamento",
        "CP6": "CP6 modelos candidatos",
        "CP7": "CP7 selecao de features",
        "CP8": "CP8 metrica principal",
        "CP9": "CP9 calibracao",
        "CP10": "CP10 interpretabilidade",
    }
    print("=" * 72)
    print("OPCOES POR CHECKPOINT (status calculado a partir dos dados acima)")
    print("=" * 72)
    for chave, titulo in titulos.items():
        print(f"\n{titulo}")
        for o in d["checkpoints"][chave]:
            print(f"  [{o['status']:<14}] {o['opcao']}")
            print(f"                   {o['motivo']}")
    print()
    print("Nenhuma opcao BLOQUEADO deve ser oferecida ao usuario no checkpoint.")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="Diagnostico dos dados para a skill ml-checkpoints")
    ap.add_argument("arquivo", help="CSV, TSV, Parquet ou Excel")
    ap.add_argument("--target", required=True, help="coluna do desfecho")
    ap.add_argument("--id", dest="col_id", default=None, help="coluna que identifica a unidade (paciente, hospital)")
    ap.add_argument("--date", dest="col_data", default=None, help="coluna de data de referencia")
    ap.add_argument("--json", action="store_true", help="imprime o diagnostico em JSON")
    args = ap.parse_args()

    try:
        df = carregar(args.arquivo)
    except Exception as e:
        print(f"ERRO: nao consegui ler '{args.arquivo}': {e}")
        return 2

    if args.target not in df.columns:
        print(f"ERRO: coluna de desfecho '{args.target}' nao existe. Colunas: {', '.join(map(str, df.columns[:30]))}")
        return 2

    d = diagnosticar(df, args.target, args.col_id, args.col_data)

    if args.json:
        print(json.dumps(d, ensure_ascii=False, indent=2, default=str))
    else:
        imprimir(d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
