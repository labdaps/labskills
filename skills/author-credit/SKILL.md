---
name: author-credit
description: >
  Monta a declaração de contribuição dos autores (CRediT) de um manuscrito, e antes disso
  levanta no repositório quem de fato fez o quê, para não atribuir trabalho a pessoa real
  por dedução. Pergunta apenas os papéis que a evidência não resolve, escreve a declaração
  no padrão da taxonomia e aplica em todos os artefatos do paper de uma vez (.tex, .docx,
  markdown), para não divergirem. Sub-comandos: `/author-credit` (levanta, pergunta e
  escreve), `/author-credit check` (audita uma declaração existente contra a evidência e
  contra os critérios de autoria do ICMJE), `/author-credit evidence` (só o levantamento,
  sem escrever) e `/author-credit order` (discute ordem de autoria e autor
  correspondente). Use SEMPRE que pedir "/author-credit", "adiciona o CRediT", "declaração
  de contribuição", "author contributions", "quem fez o quê no paper", "contribuição dos
  autores", "monta o CRediT", "credita os autores", "CRediT dos três autores", ou ao
  fechar um manuscrito que ainda não tem essa seção. NÃO confundir com /paper e
  /artigo (que escrevem o manuscrito inteiro).
---

# Skill: /author-credit: quem fez o quê, sem deduzir

Declaração de contribuição é afirmação formal sobre o trabalho de pessoas reais, assinada
por elas, num documento público. É a única seção do manuscrito onde um erro não é
imprecisão: é atribuir a alguém trabalho que não fez, ou apagar trabalho que fez.

**A regra que define esta skill: papel de autor não se deduz nem se preenche por padrão.**
O que a evidência mostra, se escreve. O que ela não mostra, se pergunta. Nunca se inventa,
nem "para completar", nem porque o conjunto de papéis ficaria estranho vazio.

---

## Passo 1: levantar a evidência antes de perguntar qualquer coisa

Perguntar tudo é preguiça e desperdiça o tempo do usuário; deduzir tudo é fabricação. O
meio-termo é levantar o que o repositório prova e perguntar só o resto.

```bash
git log --format='%an <%ae>' | sort | uniq -c | sort -rn        # volume por pessoa
git log --format='%h %an: %s' --author='<nome>'                 # o que cada um fez
git log --format='%an' --diff-filter=A -- <arquivo> | tail -1   # quem criou cada arquivo
git shortlog -sn --no-merges                                    # resumo
```

Vale levantar também, quando existir: quem abriu as issues e os PRs, quem aparece nos
notebooks, quem está no `CITATION.cff` ou no `AUTHORS`, e o histórico do manuscrito.

Mapear arquivo para papel CRediT, com parcimônia:

| Evidência no repositório | Papel que ela sustenta |
|---|---|
| Criou script de pipeline, módulo, notebook de análise | Software |
| Criou script de coleta, arquivo de dados processado | Data curation |
| Criou script de figura ou tabela | Visualization |
| Escreveu o manuscrito (commits em `paper/`) | Writing: original draft |
| Commits de revisão no manuscrito alheio | Writing: review and editing |
| Criou o repositório, definiu a estrutura | Project administration |

**O que o git nunca prova**, e portanto sempre se pergunta: Conceptualization,
Methodology, Supervision, Validation, Investigation, Funding acquisition, Resources.
Coautor sênior que não commita costuma ter exatamente esses, e a ausência dele no git não
é evidência de nada.

---

## Passo 2: perguntar só o que falta, com botões

Uma chamada da ferramenta AskUserQuestion, uma pergunta por autor cuja contribuição a evidência
não resolve, `multiSelect` ligado, com as opções agrupando papéis que costumam andar
juntos (Conceptualization e Supervision; Methodology e Formal analysis; Writing: review
and editing; Investigation e Validation).

Para os autores que a evidência resolve, **não perguntar em aberto: mostrar o que se
deduziu e pedir confirmação**, dizendo de onde saiu. "Deduzi dos 2 commits dele" é
verificável; "Software, Data curation" sozinho não é.

Dizer com todas as letras, quando for o caso, que uma pessoa não aparece no repositório, e
**dizer junto que isso não significa ausência de contribuição**. Sem essa segunda metade a
frase soa como acusação, e o usuário responde defendendo o colega em vez de informando o
papel.

---

## Passo 3: escrever

Os 14 papéis da taxonomia CRediT, e não invente outros:

Conceptualization, Data curation, Formal analysis, Funding acquisition, Investigation,
Methodology, Project administration, Resources, Software, Supervision, Validation,
Visualization, Writing: original draft, Writing: review and editing.

Formato, que a maioria dos journals aceita:

> **Author contributions.** Following the CRediT taxonomy. **Nome A:** papéis em ordem
> alfabética. **Nome B:** papéis. All authors read and approved the final manuscript.

Regras de escrita:

- Papéis em **ordem alfabética** dentro de cada autor, que é a convenção da taxonomia, e
  não em ordem de importância.
- Autores na **mesma ordem da folha de rosto**.
- **Funding acquisition só entra se houve financiamento.** Se a seção de declarações diz
  "no external funding was received", esse papel não pode aparecer, e essa contradição
  passa despercebida com frequência.
- Nome oficial do papel é "Writing: original draft" e "Writing: review and editing".
  A taxonomia oficial usa travessão, que a regra de pontuação deste usuário proíbe: usar
  **dois pontos**, que mantém o nome reconhecível.
- Fechar com "All authors read and approved the final manuscript", que a maioria dos
  journals exige separadamente.

---

## Passo 4: aplicar em todos os artefatos, não em um

Um manuscrito costuma existir em mais de uma forma ao mesmo tempo: `paper/manuscript.tex`,
o gerador do `.docx`, às vezes um markdown. **Escrever a declaração em um só é criar
divergência silenciosa**, e o CRediT é justamente a seção que ninguém relê antes de
submeter.

Editar todos, e conferir depois que os dois textos batem:

```bash
grep -c 'CRediT' paper/manuscript.tex scripts/build_docx.py
```

Se algum artefato tinha marcador de pendência (`\missing{}` no LaTeX, `[PENDING]` no
Word), confirmar que ele sumiu dos dois.

---

## `/author-credit check`: auditar uma declaração existente

Além de conferir contra a evidência do repositório, rodar os quatro critérios do ICMJE,
que são cumulativos: contribuição substancial à concepção ou à análise; redação ou revisão
crítica; aprovação da versão final; e responsabilidade por todos os aspectos do trabalho.

Sinalizar, sem acusar, e deixando a decisão com o usuário:

- **Autor só com Writing: review and editing.** Não cumpre o primeiro critério do ICMJE
  sozinho. Pode ser que a contribuição exista e não tenha sido declarada; pode ser
  autoria de cortesia. Perguntar.
- **Autor sem nenhum papel declarado.**
- **Funding acquisition declarado com financiamento negado nas declarações.**
- **Papel que não existe na taxonomia**, tipo "Statistical analysis", que é Formal
  analysis.
- **Ninguém com Writing: original draft.** Alguém escreveu.

## `/author-credit order`

Ordem de autoria não é CRediT e não se resolve por evidência de commit: é negociação da
área. Entregar o que a evidência sugere e as convenções aplicáveis (primeiro autor com
mais Software e Writing: original draft; último com Supervision e Funding; correspondente
normalmente primeiro ou último), e devolver a decisão ao usuário. Nunca reordenar autores
por conta própria.

---

## Fechamento

Reportar:

- de onde veio cada papel: evidência do repositório, ou resposta do usuário;
- quem não aparecia no repositório, se houve alguém;
- em quais artefatos a declaração foi escrita, e que os marcadores de pendência sumiram;
- qualquer sinal do ICMJE que tenha aparecido, como pergunta e não como veredito.
