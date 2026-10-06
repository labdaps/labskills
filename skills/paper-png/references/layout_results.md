# Layout: Figura de Resultado: /paper-png

Referência de layout para figuras do tipo **resultado**: comparação de modelos,
tabela de métricas visual, ranking de métodos.

Ler quando o tipo for figura de resultado ou comparativo.

---

## Quando usar este layout

- Tabela de métricas do paper (Tabela 1, Tabela 2, etc.)
- Comparação de modelos/baselines
- Ranking de métodos com métricas numéricas
- Ablation study visual

---

## Estrutura

```
[CABEÇALHO]
  Título da figura (negrito, 32px)
  Fonte: "Adaptado de <Autor et al., Ano>"

[TABELA VISUAL]
  Linha de cabeçalho (fundo navy, texto branco)
  Linhas alternadas (cinza 95% / branco)
  Coluna de modelo (negrito)
  Colunas de métricas (coloridas por performance)
  Linha de destaque para o melhor modelo

[LEGENDA DE CORES]
  ● Verde: melhor resultado
  ● Âmbar: resultado intermediário
  ● Cinza: baseline / referência
```

---

## Paleta de performance

```python
BEST_BG    = (229, 245, 236, 255)   # verde suave, melhor resultado
BEST_BD    = (115, 196, 146, 255)   # borda verde
BEST_TX    = (18, 105, 52, 255)     # texto verde escuro

MID_BG     = (255, 249, 228, 255)   # âmbar suave, resultado médio
MID_TX     = (112, 68, 0, 255)

BASE_BG    = (244, 245, 248, 255)   # cinza, baseline
BASE_TX    = (65, 78, 98, 255)

HEADER_BG  = (30, 58, 138, 255)    # navy, cabeçalho da tabela
HEADER_TX  = (255, 255, 255, 255)  # branco

ROW_ALT    = (248, 249, 253, 255)  # cinza muito claro, linhas alternadas
ROW_WHITE  = (255, 255, 255, 255)
```

---

## Dimensões recomendadas

```python
W          = 1890   # largura padrão
PAD        = 80     # margem (sem loop, PAD menor)
ROW_H      = 72     # altura de cada linha da tabela
HEADER_H   = 80     # altura do cabeçalho
COL_WIDTHS = [...]  # calcular proporcionalmente ao conteúdo
```

---

## Esqueleto de código

```python
# Cabeçalho da tabela
y = PAD + 80  # após título
rr(draw, [PAD, y, PAD+CW, y+HEADER_H], 8,
   (30,58,138,255), (30,58,138,255), 2)
# Células do cabeçalho centradas
for i, col in enumerate(COLS):
    TC(draw, col, col_cx[i], y+HEADER_H//2, F(24,bold=True), (255,255,255,255))

y += HEADER_H

# Linhas de dados
for j, (model, *metrics) in enumerate(ROWS):
    row_bg = ROW_ALT if j%2==0 else ROW_WHITE
    # Linha de destaque para melhor modelo
    if model == BEST_MODEL:
        row_bg = BEST_BG
    rr(draw, [PAD, y, PAD+CW, y+ROW_H], 0, row_bg, (200,210,228,255), 1)

    # Nome do modelo (negrito, alinhado à esquerda)
    TL(draw, model, PAD+20, y+ROW_H//2, F(26,bold=True), (20,22,38,255))

    # Métricas (centradas, coloridas)
    for i, val in enumerate(metrics):
        color = BEST_TX if val == best_vals[i] else (20,22,38,255)
        TC(draw, val, col_cx[i+1], y+ROW_H//2, F(26,mono=True), color)

    y += ROW_H
```

---

## Adaptações comuns

### Negrito para o melhor valor por coluna
Identificar o melhor valor em cada coluna (max ou min dependendo da métrica)
e usar `F(26, bold=True)` + cor verde para esse valor.

### Seta de melhoria (delta)
Para papers que mostram ganho relativo ao baseline:
```python
# Delta em cor verde com seta ↑
TC(draw, f"↑ +{delta:.1f}%", cx, y, F(22), (18,105,52,255))
```

### Seção de ablation
Separar grupos com linha horizontal mais espessa (2px) e label de grupo
no lado esquerdo em itálico.
