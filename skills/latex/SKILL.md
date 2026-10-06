---
name: latex
description: >
  Exporta um paper para LaTeX pronto para colar ou subir em outro lugar, resolvendo as dependências
  que fazem um projeto multi-arquivo não compilar fora da pasta original. Achata `\input`, embute o
  `.bib`, decide o que fazer com cada figura e prova o resultado compilando num diretório que só
  contém a entrega. Sub-comandos: `/latex` (pacote para editor online tipo Overleaf, Prism ou
  Authorea: um `main.tex` mais os arquivos de figura), `/latex paste` (arquivo único colável, sem
  figura), `/latex figures` (tenta reconstruir figura como código pgfplots), `/latex zip`,
  `/latex arxiv`, `/latex from <arquivo>` (converte md, docx ou odt para tex) e `/latex check`
  (compila isolado e compara com o original). Use SEMPRE que pedir "/latex", "me manda o tex",
  "exporta pro overleaf", "joga no prism", "manda o main.tex", "cola o latex aqui", "prepara pro
  arxiv", "transforma esse paper em latex", "converte pra tex", "junta tudo num arquivo só",
  "por que meu tex não compila fora da pasta", ou entregar um paper pedindo para levar a outro
  editor. NÃO confundir com /paper (que escreve o manuscrito em .docx) nem com /update-paper (que
  atualiza números nos .tex).
---

# Skill: /latex, levar um paper para outro lugar

Um manuscrito real não é um arquivo, é uma árvore: preâmbulo, tabelas, figuras e bibliografia em
arquivos separados. Isso é bom para manter e péssimo para mover. Colado num editor online, ele não
compila, e o erro que aparece não diz o que faltou.

Esta skill move o paper sem quebrá-lo, e **prova que não quebrou** em vez de afirmar.

O usuário publica em IA clínica e epidemiologia. Não explicar o que é preâmbulo, bibtex nem classe
de documento.

---

## A regra que define esta skill

> Nenhuma entrega sai daqui sem ter sido compilada **num diretório que contém apenas os arquivos
> entregues**. Compilar na pasta de origem não prova nada: lá está tudo que a entrega talvez não
> tenha, e a dependência que ficou faltando passa despercebida.

Depois de compilar, comparar com o original: mesmo número de páginas e **mesmo texto extraído**.
Diferente disso, o achatamento perdeu alguma coisa e é preciso achar o quê antes de entregar.

---

## Passo 1: descobrir o alvo, porque ele decide a forma

A mesma fonte gera quatro entregas diferentes. Perguntar antes de gerar, se não estiver óbvio.

| Alvo | Forma da entrega | Figuras |
|---|---|---|
| **Editor online** (Overleaf, Prism, Authorea) | `main.tex` único, mais os arquivos de figura soltos | mantidas, com caminho achatado para a raiz |
| **Colar no chat, num highlighter, num email** | um `.tex` só, nada mais | reconstruídas como código, ou moldura |
| **arXiv** | tarball com `.bbl` já resolvido | mantidas, formato aceito |
| **Sistema de submissão de revista** | conforme o guia da revista, quase sempre zip | mantidas, muitas vezes em arquivo separado |

O erro mais comum é entregar a forma de "colar no chat" para quem vai subir num editor online. O
editor **aceita upload**, então trocar figura por moldura ali joga fora o que o alvo suportava.

## Passo 2: as três dependências que dissolvem, e a que não dissolve

**`\input` e `\include`** dissolvem: basta inserir o conteúdo, recursivamente. Cuidar de ciclo e de
`\input` dentro de arquivo já embutido.

**A bibliografia** dissolve por dois caminhos:
- `filecontents`: embute o `.bib` inteiro dentro do `.tex`, e o LaTeX o grava em disco ao compilar.
  Precisa ficar **antes do `\documentclass`**. É o caminho para editor online, porque mantém o
  `.bib` editável.
- `.bbl` colado: a bibliografia já resolvida, sem precisar rodar bibtex. É o caminho do arXiv, e
  exige ter compilado uma vez antes para o `.bbl` existir.

**Figura não dissolve.** Arquivo binário não entra em arquivo de texto, e não adianta insistir. O
que existe é a árvore de decisão do passo seguinte.

## Passo 3: a decisão de figura

Nesta ordem, e a primeira que couber vence:

**1. Dá para reconstruir como código?** Gráfico feito de dados que você tem (linha, barra, dispersão,
haltere, intervalo) vira `pgfplots` a partir dos números. Ganha muito: vetorial, fonte igual à do
documento, editável dentro do editor, e o arquivo fica de fato único. Vale quando os dados cabem em
algumas centenas de coordenadas.

- `pgfplots` compila com tectonic sem instalação extra. Verificado.
- O backend PGF do matplotlib (`matplotlib.use("pgf")` e `savefig("x.pgf")`) exporta o gráfico como
  código LaTeX, mas **exige um binário `pdflatex` de verdade**; só tectonic não serve, e o erro é
  `'pdflatex' not found`. Pior: ele grava um `.pgf` truncado antes de falhar, então checar o
  código de saída, não a existência do arquivo.

**2. O alvo aceita upload?** Editor online, zip e tarball aceitam. Então manter `\includegraphics` e
entregar os arquivos junto, **achatando o caminho**: tirar `\graphicspath` e o diretório do nome,
para que o upload na raiz resolva. Dizer ao usuário, na entrega, exatamente quais arquivos subir e
onde.

**3. Nada disso?** Foto, micrografia, captura de tela, render complexo, ou alvo que só aceita texto:
trocar por moldura com o nome do arquivo, preservando legenda e label, e **entregar os arquivos ao
usuário à parte**. A moldura mantém a diagramação e deixa o buraco visível, que é melhor que sumir
com a figura.

### A armadilha do underscore

Nome de figura quase sempre tem `_`, que em modo texto é subscrito matemático. Qualquer moldura ou
rótulo que imprima o nome do arquivo quebra a compilação com `Missing $ inserted`, e o erro aponta
para a linha da figura, não para a causa. Escapar `_ # $ % & { } ~ ^ \` antes de imprimir nome de
arquivo. Isso derrubou a primeira versão deste próprio fluxo.

## Passo 4: gerar

O script `"${CLAUDE_SKILL_DIR}/scripts/flatten_tex.py"` desta skill faz o achatamento:

```bash
# editor online: main.tex mais as figuras soltas
python flatten_tex.py paper/manuscript.tex -o main.tex --figures keep-flat

# colar: arquivo único, figura vira moldura
python flatten_tex.py paper/manuscript.tex -o standalone.tex --figures placeholder

# arXiv: bibliografia já resolvida
python flatten_tex.py paper/manuscript.tex -o main.tex --bib bbl
```

Ele avisa cada arquivo embutido e conta as figuras tratadas. Aviso de `\input` não encontrado é para
ser investigado, não ignorado: significa que a entrega vai sair incompleta.

## Passo 5: provar

Não é opcional e não é "compilei na pasta e funcionou".

```bash
mkdir /tmp/prova && cp main.tex fig*.pdf /tmp/prova/   # só o que vai ser entregue
cd /tmp/prova && ls -1                                  # mostrar que está sozinho
tectonic -X compile main.tex
```

Depois, comparar com o original:

```python
import pymupdf
a, b = pymupdf.open("main.pdf"), pymupdf.open("../original/manuscript.pdf")
assert a.page_count == b.page_count
assert "".join(p.get_text() for p in a) == "".join(p.get_text() for p in b)
```

Conferir também, no PDF gerado: zero `[?]` de citação não resolvida, e a contagem de referências
igual à do original. Citação quebrada é o sintoma mais comum de bibliografia mal embutida, e ela
não gera erro de compilação.

Abrir ao menos uma página com figura e uma com tabela, com o Read, antes de entregar.

## Passo 6: entregar

Enviar os arquivos com `SendUserFile`, não colar 800 linhas no chat. Colar só faz sentido para
documento curto, tipo cover letter, que cabe numa tela.

### Figura entregue ao usuário é sempre PNG

Regra sem exceção, e ela é sobre o **canal**, não sobre o documento.

- No **documento**, a figura é o que o Passo 3 decidiu: código pgfplots, ou binário vetorial.
- No **chat**, a figura é **PNG**, sempre, mesmo quando o documento usa outra coisa.

O motivo é que PNG é a única forma que abre em qualquer lugar sem ferramenta. `.tex` de pgfplots não
é imagem nenhuma até alguém compilar, e PDF de figura, mandado no chat, abre num visualizador
separado, some entre os anexos e não dá para olhar de relance. Quem pede "manda as figuras" quer
**ver**, e responder com um arquivo que não se vê é não responder.

Com figura em código, o PNG não existe de graça: é preciso compilar cada figura isolada, em
`standalone`, e rasterizar o PDF resultante. Isso tem que ser um passo explícito do gerador, porque
enquanto as figuras eram matplotlib o PNG saía junto no `savefig` e ninguém pensava nele. Ao migrar
para pgfplots, o PNG desaparece em silêncio, e o sintoma só aparece quando alguém pede as figuras.

Manter o **nome idêntico** ao que o manuscrito usa (`fig4_janela.png` para `\input{figures/fig4_janela}`),
para não haver dúvida sobre qual é qual.

Se o usuário for **subir** as figuras num destino que precisa delas como arquivo, aí sim mandar
também o vetorial, e dizer qual é para ver e qual é para subir. PNG para olhar, PDF para o documento.

### Onde colocar

Junto dos arquivos, dizer em uma linha: **onde colocar cada um**. Para editor online, é "sobe os N na
raiz do projeto, sem criar subpasta", porque criar subpasta quebra o caminho achatado do Passo 3.

---

## Sub-comandos

### `/latex`
Padrão: pacote para editor online. Gera `main.tex` com preâmbulo, tabelas e `.bib` embutidos e
figuras por nome simples, mais os arquivos de figura. Prova pelo Passo 5 e entrega pelo Passo 6.

### `/latex paste`
Arquivo único de verdade, para colar. Tenta reconstruir figura como código (Passo 3, item 1); o que
não der vira moldura e vai ao usuário à parte. Precisa compilar em diretório vazio.

### `/latex figures`
Só a reconstrução de figura em `pgfplots`, a partir dos dados que geraram o gráfico. Entregar a
comparação lado a lado com a figura original antes de substituir: reconstrução que muda a leitura do
gráfico é regressão, não melhoria.

### `/latex zip`
Pasta inteira do paper em zip, com `tables/`, `figures/` e o `.bib`. Avisar que o editor online não
roda o gerador de assets: se os dados mudarem, regerar localmente e resubir.

### `/latex arxiv`
Tarball com `.bbl` resolvido, sem `\input` pendente e sem arquivo que o arXiv rejeita. Compilar
antes para produzir o `.bbl`.

### `/latex from <arquivo>`
Converte `.md`, `.docx` ou `.odt` para `.tex`. Usa pandoc; **pandoc não está instalado nesta
máquina**, então checar antes e, faltando, dizer isso em vez de fingir a conversão. Conversão
automática erra tabela complexa e equação: revisar essas duas coisas sempre.

### `/latex check`
Só o Passo 5 sobre uma entrega que já existe: compila isolado, compara com o original e reporta
divergência. Útil depois de mexer no projeto à mão.

---

## Fechamento

Reportar sempre:

- que compilou **em diretório isolado**, quantas páginas, e se o texto extraído bate com o original;
- o que foi embutido e o que ficou como arquivo separado;
- para cada figura, qual dos três caminhos do Passo 3 foi usado e por quê;
- onde o usuário deve colocar cada arquivo no destino;
- que as figuras foram entregues em PNG, e, quando também houver vetorial, qual é para ver e qual é
  para subir.

Próximo passo pertinente: `/paper check` para auditar o manuscrito antes de submeter, `/journal`
para escolher o destino, `/paper cover` para a carta ao editor.
