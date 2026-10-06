---
name: paper-png
description: >
  Gera figuras científicas de alta qualidade (PNG 300 DPI, fundo transparente) a partir do
  conteúdo de um paper científico, recebido como PDF anexo, link de URL, ou DOI, seguindo
  o estilo editorial de journals como Elsevier, JMLR e NeurIPS: paleta neutra, tipografia
  serifada, bordas finas, sem gradientes. Use esta skill SEMPRE que o usuário pedir
  "/paper-png", "gera uma figura para o paper", "cria uma imagem científica", "diagrama para
  publicação", "figura para artigo", "ilustração para o meu paper", "converte em figura de
  journal", "gera PNG do diagrama", "cria figura científica do paper", ou quando um PDF /
  link de paper for enviado com pedido de ilustração, diagrama de fluxo, figura de
  metodologia, figura de resultado ou qualquer figura destinada a publicação acadêmica.
  Produz PNG 300 DPI com fundo transparente, pronto para \includegraphics{} no LaTeX.
---

# Skill /paper-png: gerador de figuras científicas para papers

Transforma conteúdo de um artigo científico (PDF, URL ou DOI) em figura PNG de alta
resolução, no estilo visual de journals de referência (Elsevier / JMLR / NeurIPS).

---

## Quando acionar

- Gatilho explícito: `/paper-png`
- PDF de paper + pedido de figura, diagrama, fluxograma ou ilustração
- Link ou DOI de paper + pedido de figura
- Pedidos como: "cria uma figura da metodologia", "diagrama do pipeline", "figura de resultado",
  "ilustra o algoritmo", "figura para o meu artigo", "gera uma imagem científica"

---

## Fluxo de execução

### Passo 1: Ler a referência de estilo

Antes de qualquer código, ler:

```
"${CLAUDE_SKILL_DIR}/references/style_guide.md"
```

Este arquivo contém: paleta de cores exata, tamanhos de fonte, hierarquia tipográfica,
regras de layout e os valores Python prontos para copiar.

---

### Passo 2: Obter o conteúdo do paper

**Caso A, PDF anexado:**
- Ler o PDF com a ferramenta Read (ou `pdftotext` se for longo)
- Extrair: título, autores, venue/ano, objetivo, metodologia/pipeline, resultados principais

**Caso B, URL ou link:**
- Usar `web_fetch` na URL fornecida
- Se for arXiv (`arxiv.org/abs/XXXX`), converter para PDF: `arxiv.org/pdf/XXXX`
- Extrair as mesmas seções do Caso A

**Caso C, DOI:**
- Construir URL: `https://doi.org/{DOI}` e usar `web_fetch`
- Se for paywall, tentar `web_search` com título + "PDF" ou "preprint"
- Extrair o que for acessível; indicar ao usuário se o acesso for parcial

**Conteúdo mínimo necessário para prosseguir:**
- Título do paper e autores
- Objetivo / problema central
- Metodologia ou pipeline (etapas, componentes, fluxo)
- Se pedido de figura de resultado: métricas numéricas principais

---

### Passo 3: Identificar o tipo de figura

Com base no conteúdo extraído e no pedido do usuário, classificar:

| Tipo | Quando usar | Referência de layout |
|---|---|---|
| **Fluxograma** | Pipeline, algoritmo iterativo, processo com decisão | `"${CLAUDE_SKILL_DIR}/references/layout_flowchart.md"` |
| **Diagrama de arquitetura** | Modelo ML, sistema com componentes, DAG | `"${CLAUDE_SKILL_DIR}/references/layout_architecture.md"` |
| **Figura de resultado** | Tabela de métricas visual, comparação de modelos | `"${CLAUDE_SKILL_DIR}/references/layout_results.md"` |
| **Diagrama conceitual** | Taxonomia, hierarquia, relação entre conceitos | adaptar `layout_architecture.md` |

Se o usuário especificou o tipo, usar esse. Se não, inferir do conteúdo e confirmar:

> "Vou gerar um **fluxograma** da metodologia. Correto, ou prefere outro tipo?"

---

### Passo 4: Gerar a figura (Python + PIL)

**Especificações obrigatórias:**

```python
W, H = <calculado dinamicamente>   # proporção retrato ~1:1.3 a 1:1.6
DPI  = 300
img  = Image.new("RGBA", (W, H), (0, 0, 0, 0))   # fundo TRANSPARENTE
```

**Fontes obrigatórias (DejaVu, suporte completo a Unicode/math):**
```python
SANS   = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SANS_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SANS_I = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'
MONO   = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
MONO_B = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
```

**Regras críticas de posicionamento:**
- SEMPRE usar `draw.textbbox((0,0), text, font=fnt)` para medir texto antes de posicionar
- NUNCA usar `anchor='lm'` ou `anchor='rm'` no PIL, calcular manualmente com textbbox
- Texto centrado: `cx - width//2, cy - height//2`
- Texto alinhado à direita: `x - width, cy - height//2`
- Verificar visualmente que nenhum elemento extrapola as bordas do canvas

**Paleta e estilo**, ver `"${CLAUDE_SKILL_DIR}/references/style_guide.md"` para valores exatos.

**Estrutura do código:**

```python
# 1. Importações
from PIL import Image, ImageDraw, ImageFont

# 2. Funções auxiliares (TW, TC, rr, arr_v, arr_h, badge, chip)
# 3. Paleta de cores
# 4. Cálculo de dimensões baseado no conteúdo
# 5. Criação do canvas RGBA transparente
# 6. Desenho: blocos de fase (se houver) → cards → setas → labels → badges
# 7. Salvar em <pasta de figuras do projeto>/<slug>.png com dpi=(300,300)
```

---

### Passo 5: Preview e validação

Antes de entregar, ler a imagem gerada com a ferramenta Read para verificar:

- [ ] Nenhum texto cortado ou extrapolando bordas
- [ ] Nenhum `□` (glifo ausente), se aparecer, substituir por ASCII equivalente
- [ ] Proporção retrato (largura < altura), sem espaço vazio excessivo
- [ ] Fundo transparente confirmado (RGBA, não RGB)
- [ ] Labels de setas dentro dos blocos correspondentes
- [ ] Rail de loop (se existir) visível e com label dentro do canvas

Se houver problemas, corrigir e regenerar antes de entregar.

---

### Passo 6: Entregar

Salvar o PNG com nome descritivo na pasta de figuras do projeto (`figures/` ou a que o
manuscrito já usa) e entregar com a ferramenta SendUserFile.

Incluir no texto:
- Dimensões e DPI confirmados
- Snippet LaTeX para uso imediato:
  ```latex
  \begin{figure}[t]
    \centering
    \includegraphics[width=\textwidth]{<nome_descritivo>.png}
    \caption{<sugestão de caption baseada no paper>}
    \label{fig:<slug>}
  \end{figure}
  ```

---

## Regras de qualidade inegociáveis

1. **Fundo transparente**, sempre `Image.new("RGBA", ...)`, nunca `"RGB"`
2. **300 DPI**, sempre `img.save(path, dpi=(300,300))`
3. **Sem overflow**, medir tudo com `textbbox` antes de posicionar
4. **Sem glifos quebrados**, testar símbolos matemáticos com DejaVu antes de usar
5. **Proporção retrato**, canvas altura > largura; eliminar espaço vazio com cálculo dinâmico de altura
6. **Paleta neutra**, sem cores saturadas; máximo um tom de destaque (bordô ou navy)
7. **Hierarquia legível**, título da fase bold 29px, título de card bold 30px, fórmula mono 28px, nota italic 23px (em 1890px de largura)
8. **Preview obrigatório**, nunca entregar sem ler a imagem gerada com a ferramenta Read

---

## Exemplos de uso

**Com PDF anexo:**
> `/paper-png` + arquivo PDF no upload
→ Extrai metodologia → gera fluxograma da pipeline

**Com URL:**
> `/paper-png https://arxiv.org/abs/2303.08774`
→ Busca o paper → identifica tipo de figura → gera

**Com instrução específica:**
> `/paper-png, quero uma figura de resultado com as métricas da Tabela 3`
→ Extrai Tabela 3 → gera figura de resultado com comparação visual de modelos

**Com DOI:**
> `/paper-png 10.1016/j.jbi.2023.104350, diagrama da arquitetura`
→ Acessa via doi.org → extrai arquitetura → gera diagrama de componentes
