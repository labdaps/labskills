---
name: ml-timeseries
description: Setup de modelos de series temporais para saude. Skforecast, ARIMA, LSTM, Prophet. Triggers on /ml-timeseries.
---

# Skill: ml-timeseries

Pipeline especializado para previsao de series temporais em saude.

## Bibliotecas preferidas

| Lib | Uso |
|-----|-----|
| skforecast | Forecasting com sklearn (LightGBM, XGBoost) |
| statsmodels | ARIMA, SARIMAX, decomposicao |
| prophet | Sazonalidade complexa, feriados |
| pytorch/LSTM | Sequencias longas, dados multivaridos |
| tslearn | Clustering de series |

## Passos

### 1. Analise exploratoria

- Plot da serie completa
- Decomposicao: tendencia, sazonalidade, residuo
- Teste de estacionariedade (ADF, KPSS)
- ACF e PACF para identificar lags

### 2. Preprocessing

- Frequencia: garantir indice temporal regular (resample se necessario)
- Missing: interpolacao temporal (nao ffill/bfill cegamente)
- Outliers: IQR ou z-score, mas considerar surtos epidemiologicos como reais
- Diferenciacao se nao-estacionaria

### 3. Feature engineering temporal

- Lags: 1, 7, 14, 28 dias (ou equivalente da frequencia)
- Rolling: media e std movel (7, 14, 30 dias)
- Calendario: dia da semana, mes, feriado, estacao
- Exogenas: clima, campanhas de vacinacao, eventos de saude publica

### 4. Modelagem

**Abordagem escalonada:**
1. Baseline: naive (ultimo valor), media movel
2. Estatistico: ARIMA/SARIMAX
3. ML: skforecast com LightGBM (ForecasterAutoreg)
4. Deep: LSTM se dados > 1000 pontos

**Validacao:** TimeSeriesSplit ou expanding window. NUNCA shuffle em series temporais.

### 5. Metricas

- MAE, RMSE, MAPE
- Coverage do intervalo de confianca
- Plot: observado vs previsto com banda de confianca

### 6. Forecast

- Horizonte definido pelo usuario
- Intervalos de confianca (80% e 95%)
- Salvar previsoes em CSV com timestamps
