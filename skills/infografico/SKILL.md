---
name: infografico
description: >
  Gera infográficos e diagramas científicos coloridos no estilo visual usado nos papers do
  LABDAPS (ex: diagrama de fluxo do multicalibração no artigo IACOV, mcalibration/assets/
  diagrama_multicalibration.png), paleta pastel Material Design, caixas arredondadas,
  badges numerados, setas de fluxo/decisão. Cobre dois formatos: (1) figura de metodologia
  COM texto, pra usar dentro do paper; (2) imagem TOC/graphical abstract SEM texto, pro
  campo "TOC image" de submissão em revista (JMIR e afins não aceitam texto na imagem,
  salvo exceção). Use SEMPRE que o usuário pedir "/infografico", "faz um infográfico desse
  pipeline", "diagrama colorido pro artigo", "imagem TOC pra revista", "graphical abstract",
  "figura estilo IACOV/multicalibração", "usa o mesmo estilo do outro diagrama", ou pedir
  para reaproveitar a identidade visual de um diagrama anterior do lab.
---

# Skill: /infografico: Infográficos e imagens TOC no estilo LABDAPS

Duas saídas possíveis, escolher com o usuário antes de gerar:

- **Figura de metodologia** (fluxograma, pipeline, arquitetura): pode e deve ter texto,
  fórmulas, badges numerados. Vai dentro do paper como Figure ou Multimedia Appendix.
- **Imagem TOC / graphical abstract**: zero texto, zero fórmula. Vai no campo "TOC image"
  da submissão (ex: JMIR, ver `/paper` e o fluxo de submissão). Formato quadrado
  (recomendado 1200x1200px), conceito visual reconhecível sem legenda.

Se o projeto já tiver uma figura nesse estilo (ex.: diagrama de metodologia de um artigo
anterior do laboratório), reler essa imagem com Read antes de gerar algo novo: a figura
existente é a fonte da verdade, não esta paleta escrita.

---

## Paleta (Material Design, pastel)

Fundo de cada caixa usa o tom 100, borda o tom 300-400, texto de título quase preto
(`#212121`), nota/subtítulo em itálico cinza (`#616161`). Painéis de fundo (agrupando
várias caixas, tipo "Fase 1/2/3") usam o tom 50 do mesmo par de cor.

| Papel semântico | 50 (painel bg) | 100 (caixa bg) | 300 (borda) | 700 (texto forte/header) |
|---|---|---|---|---|
| Neutro / entrada | `#FAFAFA` | `#E0E0E0` | `#BDBDBD` | `#424242` |
| Predição / dado inicial | `#E3F2FD` | `#BBDEFB` | `#64B5F6` | `#1976D2` |
| Auditoria / processo | `#F3E5F5` | `#E1BEE7` | `#BA68C8` | `#7B1FA2` |
| Decisão | `#FFF3E0` | `#FFE0B2` | `#FFB74D` | `#F57C00` |
| Correção / atenção | `#FFEBEE` | `#FFCDD2` | `#E57373` | `#D32F2F` |
| Saída / sucesso | `#E8F5E9` | `#C8E6C9` | `#81C784` | `#388E3C` |
| Categoria geográfica/clínica | `#E0F2F1` | `#B2DFDB` | `#4DB6AC` | `#00796B` |
| Categoria demográfica alternativa | `#FCE4EC` | `#F8BBD0` | `#F06292` | `#C2185B` |

Setas: cinza escuro `#424242` pro fluxo normal, vermelho `#C62828` pra loop/retorno ou
caminho negativo, verde `#2E7D32` pra caminho positivo/saída. Badge de passo: círculo
sólido laranja `#FB8C00` com número/letra branco bold dentro.

Não inventar tom fora dessa tabela. Se precisar de uma categoria nova, escolher o par
50/100/300/700 de uma cor Material padrão (ex: Indigo, Amber) e manter a mesma lógica de
4 tons.

---

## Estilo de caixa e tipografia

- Cantos arredondados: raio proporcional a ~1.5-2% da largura do canvas.
- Borda: 2-3px na cor 300 do papel semântico.
- Título da caixa: bold, cor quase-preta, tamanho proporcional (~1.4-1.6% da largura do
  canvas em fonte).
- Fórmula/conteúdo técnico: fonte mono, tamanho ligeiramente menor que o título.
- Nota de rodapé da caixa: itálico, cinza, tamanho menor, entre parênteses ou linha solta.
- Setas com label: label sobre a linha, fundo transparente, mesma cor da seta.
- Legenda (quando houver): grade de 2 colunas, quadradinho de cor + label ao lado,
  alinhados à esquerda.

## Formatos de decisão (losango)

Usar losango (diamond) preenchido no tom 100 de "Decisão" só quando houver ramificação
condicional real (if/else do pipeline). Não usar losango decorativo sem lógica de decisão
por trás.

---

## Passo a passo

### 1. Confirmar o tipo de saída
Perguntar (se não estiver óbvio pelo pedido): figura de metodologia (com texto) ou
imagem TOC (sem texto)? Formato de saída (PNG, dimensões)?

### 2. Levantar o conteúdo
- Figura de metodologia: mesmo processo do `/paper-png`, extrair do paper/código as
  etapas, decisões, badges numerados (2a, 2b...) e legenda.
- Imagem TOC: extrair o CONCEITO CENTRAL do paper em uma frase (não o método, a metáfora
  visual). Ex.: "vários caminhos diferentes batendo no mesmo teto" para um paper sobre
  limite de desempenho por informação de features. Não copiar diagrama técnico do paper
  pro TOC, TOC é conceitual/iconográfico, não é fluxograma.

### 3. Gerar
- **Com texto (figura de metodologia):** Python + PIL. Medir todo texto com
  `draw.textbbox` antes de posicionar (nunca `anchor='lm'/'rm'` cego). Fundo transparente
  (`Image.new("RGBA", ...)`) se for entrar como Multimedia Appendix/figure do paper.
  Fontes: usar uma fonte do sistema Windows disponível (ex: `C:\Windows\Fonts\segoeui.ttf`
  e `segoeuib.ttf` para bold), não assumir caminho `/usr/share/fonts` do sandbox Linux.
- **Sem texto (imagem TOC):** construir como SVG (formas simples, sem `<text>`), depois
  rasterizar. Nesta máquina não há cairosvg/rsvg-convert/Inkscape instalados por padrão, 
  checar com `python -c "import cairosvg"` antes; se ausente, renderizar via Claude Browser:
  salvar o SVG embutido num HTML, abrir no browser, `resize_window` pro tamanho exato
  (ex: 1200x1200), `computer` screenshot com `save_to_disk: true`, e usar esse PNG.

### 4. Preview obrigatório
Ler a imagem gerada (Read) antes de entregar. Checar: nada cortado, nenhum glifo quebrado,
proporção correta, paleta bate com a tabela acima, e, se for imagem TOC, confirmar que
não sobrou nenhum texto/número/fórmula na imagem.

### 5. Entregar
- Figura de metodologia: caminho do PNG + sugestão de caption/legenda.
- Imagem TOC: caminho do PNG + lembrete de preencher, no upload, o campo de descrição
  com fonte/copyright/licença (ex: "Original illustration created by the author. Licensed
  under CC BY 4.0.", confirmar a licença com o usuário, não presumir).

---

## Regras inegociáveis

1. Paleta só da tabela acima, sem cor saturada fora dela, sem gradiente.
2. Imagem TOC nunca leva texto, número ou fórmula (regra da revista).
3. Sempre medir texto antes de posicionar (PIL), sem overflow de caixa.
4. Preview (Read) obrigatório antes de entregar qualquer imagem.
5. Se o pedido mencionar "estilo IACOV" ou "como o outro diagrama", reler
   `mcalibration/assets/diagrama_multicalibration.png` primeiro.
