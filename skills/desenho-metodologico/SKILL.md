---
name: desenho-metodologico
description: >
  Gera figura de desenho metodológico de artigo científico (graphical abstract, study design schematic, methods overview) em SVG vetorial, com exportação para PNG 300 dpi e PDF via Chrome headless, sem depender de cairo, Inkscape ou Illustrator. Extrai os números do próprio manuscrito, declara cada um como constante rastreável, monta o layout em faixas ou colunas, renderiza e inspeciona a imagem antes de entregar. Use SEMPRE que o usuário pedir "/desenho-metodologico", "faz a figura de metodologia", "monta o graphical abstract", "figura de desenho do estudo", "study design figure", "infográfico do artigo", "figura que resume o método", "diagrama de ponta a ponta do estudo", "flowchart do estudo", "figura de fluxo do paper", ou mandar um manuscrito pedindo uma imagem que consolide base, variáveis, metodologia e avaliação. Acionar também quando alguém disser que a figura do artigo está pobre, confusa ou que precisa de versão em paisagem ou retrato. NÃO confundir com /paper-png (figura ilustrativa a partir do conteúdo de um paper, em PNG raster), /infografico (estilo colorido do laboratório) nem /artigo (escreve o texto do manuscrito).
---

# /desenho-metodologico: figura de desenho de estudo pronta para submissão

Uma figura de metodologia boa não é decoração. Ela é o único lugar do artigo onde um revisor consegue, em quinze segundos, entender o que entrou, o que foi feito e o que saiu. Se ele precisa voltar ao texto para entender a figura, a figura falhou.

**Princípio-mãe: todo número da figura tem que existir no manuscrito.** Nada de arredondar, nada de inventar rótulo, nada de "aproximadamente". Se o texto diz 5.745, a figura diz 5.745. Se a figura precisa de um número que o texto não tem, o número não entra: vira pergunta para o autor.

---

## O nome certo

Quem pede costuma não saber o nome, e chega falando "quase um infográfico". Os termos corretos:

| Termo | Quando se usa |
|---|---|
| **Graphical abstract** | figura de capa da submissão, formato largo, resume o artigo inteiro |
| **Study design schematic** | figura de métodos dentro do corpo do artigo |
| **Methods overview figure** | sinônimo do anterior, comum em revistas de informática médica |
| **Study flow diagram** | só o fluxo de elegibilidade e exclusão, no espírito do CONSORT e do STROBE |

Diga o nome ao usuário. Ele quase sempre vai precisar dele para conversar com a revista.

---

## Passo 1: extrair os números antes de desenhar

Leia o manuscrito e o material suplementar. Monte a lista do que a figura precisa carregar e, para cada item, anote de onde veio (tabela, seção, linha). Nunca desenhe a partir da memória do que leu.

Números que quase sempre entram numa figura de estudo preditivo:

- tamanho da coorte, período, critério de elegibilidade e o n depois de cada corte
- número de centros ou hospitais, e o n de cada um
- desfechos e a prevalência de cada um
- número de preditores, agrupados por natureza clínica
- estratégia de partição, imputação e harmonização
- algoritmos, método de tuning, número de ajustes
- métrica primária, métricas secundárias
- volume de experimentos (quantos modelos, quantas comparações)
- hipóteses e o veredito de cada uma

**Confira a aritmética.** Se a soma dos n por centro tem que dar o N total, escreva o `assert` no gerador. Erro de soma numa figura publicada vira erratum.

## Passo 2: gerar por script, nunca desenhar à mão

Copie `"${CLAUDE_SKILL_DIR}/scripts/figkit.py"` para a pasta de figuras do projeto e escreva um gerador em cima dele, usando `"${CLAUDE_SKILL_DIR}/templates/build_figure.template.py"` como ponto de partida.

Motivo: quando o autor mudar um número (e ele vai mudar), a correção é uma linha e um reexport. Figura desenhada no Illustrator apodrece na primeira revisão.

Estrutura de arquivos que funciona:

```
figures/
  figkit.py                    primitivas, paleta, Canvas
  figure_data.py               os números, um por constante, com a fonte no comentário
  build_figure.py              layout retrato
  build_figure_landscape.py    layout paisagem
  export.sh                    SVG para PNG e PDF
```

Separar os dados do layout é o que garante que a versão retrato e a paisagem nunca divirjam num número.

## Passo 3: layout

Duas formas, e a escolha depende do destino:

**Retrato, faixas horizontais.** Cinco a seis faixas numeradas, leitura de cima para baixo. É a forma natural de figura de página inteira no corpo do artigo. Sequência que funciona: coorte, preditores e preparação, treinamento, o desenho experimental, avaliação e resultados.

**Paisagem, colunas.** Três colunas, leitura de cima para baixo e depois da esquerda para a direita, com régua vertical fina separando. É a forma de graphical abstract, slide e pôster.

Entregue as duas quando não souber o destino. Custa quase nada se os dados estiverem separados do layout, e evita uma rodada inteira de ida e volta.

### Regra dura: não deixar espaço em branco

**Todas as colunas terminam na mesma altura. Toda faixa ocupa a largura toda.** Coluna que acaba antes e deixa um bloco vazio embaixo é entrega incompleta, não escolha de design. Revisor lê como descuido, e o autor lê como conteúdo faltando.

Como fechar de verdade:

1. Defina `TOP` e `BOTTOM` no topo do script e registre onde cada coluna terminou.
2. Ao final, verifique com `assert` e falhe se a folga passar da tolerância. O template já traz isso pronto.
3. Se sobrar folga, **redistribua conteúdo entre as colunas** ou **aumente o elemento que merece destaque**. Não resolva só abrindo espaçamento entre blocos, porque continua parecendo vazio.
4. Use `min_h` nos cartões para forçar a altura exata e fechar a coluna no ponto certo.

O elemento que merece crescer é o que carrega o conceito do artigo. Num estudo de transfer NxN, é a matriz fonte por alvo. Num ensaio, é o fluxo de randomização. Dê espaço a ele antes de dar espaço a texto.

## Passo 4: tipografia e cor

**Tamanho de fonte.** O que importa é a razão entre o corpo e a largura da tela, não o número de unidades. Para largura impressa de 180 mm:

| Corpo desejado | Unidades numa tela de 1000 de largura |
|---|---|
| 5 pt (piso da Nature) | 9,8 |
| 6 pt | 11,8 |
| 7 pt (preferência de várias revistas) | 13,7 |

Declare no cabeçalho do script a que ponto o corpo corresponde na largura alvo, e diga isso ao usuário na entrega. Se a revista exigir 7 pt e o conteúdo não couber, a saída é quebrar em duas figuras, não encolher a fonte em silêncio.

**Cor.** Use Okabe-Ito, que é segura para as formas comuns de daltonismo. O `figkit` já traz a paleta. Escolha cores com luminâncias diferentes o bastante para a figura sobreviver à impressão em preto e branco, e não dependa só do matiz para distinguir categorias: acrescente rótulo, posição ou traço.

**Cor tem semântica.** Verde para o que funcionou, vermelho e laranja para o que não funcionou, âmbar para o resultado fraco, azul para o neutro ou informativo. Não use vermelho num resultado que é apenas nuançado: isso faz o leitor ler fracasso onde o autor tem achado. Se um resultado depende do nível de análise, rotule os dois níveis e use cor neutra.

## Passo 5: renderizar e olhar

**Você não sabe se a figura está certa até ver a imagem.** Estouro de texto, sobreposição e corte não aparecem no código. Todo layout hand-coded erra na primeira tentativa.

O ciclo é: gerar SVG, exportar PNG, **abrir o PNG e olhar**, corrigir, repetir. Duas ou três rodadas é normal. Faça recortes das regiões densas quando a imagem inteira ficar pequena demais para julgar.

O que sempre quebra:

- rótulo de cabeçalho de tabela colando no seguinte
- valor numérico encostando na barra quando o valor é o máximo da escala
- nota longa vazando da caixa que a contém
- legenda estourando para fora da coluna
- último item de um painel passando da borda de baixo

## Passo 6: exportar

`"${CLAUDE_SKILL_DIR}/scripts/export.sh"` usa o Chrome headless que já está instalado. Sem cairo, sem Inkscape, sem `pip install`. Ele lê largura e altura do próprio SVG, então mudar o tamanho da figura não exige mexer no script de conversão.

Entregue três formatos: **SVG** (editável), **PDF** (vetorial, é o que a revista quer) e **PNG a 300 dpi** (para e-mail, slide e preview).

---

## Regras

**Número medido ou nada.** Se o manuscrito não traz o número, ele não entra na figura. Pergunte ao autor.

**Aritmética conferida por assert.** Soma de subgrupos, total de experimentos, contagem de células. Escreva a verificação no gerador.

**Nenhum espaço em branco.** Colunas fecham na mesma altura, verificado por assert.

**A figura não pode contradizer o texto.** Se o manuscrito diz que uma hipótese não foi sustentada, a figura não diz que foi. Quando o autor pedir um veredito mais forte do que o texto sustenta, diga isso em uma ou duas frases, ofereça a versão que resolve o problema de leitura sem falsear o resultado, e deixe a decisão com ele.

**Olhe a imagem antes de entregar.** Nunca declare pronto sem ter inspecionado o PNG renderizado.

**Português correto e sem pontuação decorativa** na conversa e nos comentários do código. O conteúdo da figura segue o idioma do manuscrito, que quase sempre é inglês.

---

## Entrega

1. Os arquivos, nos três formatos, e o gerador.
2. Onde cada número foi conferido.
3. O ponto tipográfico efetivo na largura alvo, e o que fazer se a revista exigir mais.
4. O que ficou de fora e por quê.
