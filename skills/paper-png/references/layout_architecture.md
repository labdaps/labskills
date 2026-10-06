# Layout: Diagrama de Arquitetura: /paper-png

Referência de layout para figuras do tipo **arquitetura**: modelos de ML,
sistemas com componentes, DAGs, encoder-decoder, transformers, etc.

---

## Quando usar este layout

- Arquitetura de rede neural (camadas, blocos, skip connections)
- Sistema com componentes e interfaces (input → processo → output)
- DAG (grafo acíclico dirigido) de pipeline
- Diagrama encoder-decoder, attention, etc.

---

## Estrutura geral

```
[INPUT]
  bloco de entrada (dado bruto, imagem, texto)
  ↓
[MÓDULOS PRINCIPAIS]
  blocos em sequência ou em paralelo
  conexões com setas
  labels de dimensões ou operações
  ↓
[OUTPUT]
  bloco de saída
  label com shape/tipo do resultado
```

---

## Orientação do canvas

Para arquiteturas com muitos componentes horizontais:
```python
W, H = 1890, 1200   # paisagem, W > H
```

Para pipelines verticais:
```python
W, H = 1890, 2200   # retrato, W < H
```

---

## Convenções de blocos

```python
# Bloco de dado (entrada/saída)
DATA_STYLE = {'bg': (232,240,252,255), 'bd': (135,178,244,255), 'radius': 8}

# Bloco de módulo/camada
MODULE_STYLE = {'bg': (237,230,252,255), 'bd': (170,146,218,255), 'radius': 10}

# Bloco de operação (concat, add, pool)
OP_STYLE = {'bg': (255,249,228,255), 'bd': (232,168,56,255), 'radius': 6}

# Bloco de resultado
OUT_STYLE = {'bg': (229,245,236,255), 'bd': (115,196,146,255), 'radius': 10}
```

---

## Setas e conexões

```python
# Seta principal (forward pass)
arr_v(draw, x, y0, y1, (148,162,180,255))
arr_h(draw, x0, x1, y, (148,162,180,255))

# Skip connection (curva simulada com poliline)
SKIP_COLOR = (178,52,48,255)  # bordô
draw.line([(x_start, y_start), (x_right, y_start),
           (x_right, y_end),   (x_end, y_end)],
          fill=SKIP_COLOR, width=2)
# arrowhead manual no final

# Label de dimensão (ex: "512×256")
TC(draw, "512×256", cx, y_label, F(20,mono=True), (138,152,172,255))
```

---

## Adaptação para transformer

```
[Input Embedding]
     ↓
[Multi-Head Attention] ←──── Skip ────┐
     ↓                                │
[Add & Norm]  ───────────────────────┘
     ↓
[Feed Forward]  ←─── Skip ───────────┐
     ↓                               │
[Add & Norm]  ──────────────────────┘
     ↓
[Output]
```

Usar `SKIP_COLOR` (bordô) para os arcos de skip connection.

---

## Dimensões de componentes típicos

```python
# Bloco estreito (operação simples)
NARROW_W = 220; NARROW_H = 80

# Bloco largo (módulo principal)
WIDE_W = 480; WIDE_H = 120

# Gap vertical entre camadas
LAYER_GAP = 48

# Gap horizontal entre componentes paralelos
PARALLEL_GAP = 32
```
