---
name: abstract
description: >
  Extrai as informações principais de qualquer paper científico em tópicos estruturados
  (Introdução/Problema, Métodos, Resultados, Limitações, Relevância), em prosa direta e densa,
  sem numeração e sem widget visual, ideal para leitura rápida e triagem de literatura.
  Use SEMPRE que o usuário pedir "/abstract", "extrai o abstract", "resume em tópicos", "quais
  os pontos principais", "resumo estruturado do paper", "tópicos do paper", "me dá os pontos do
  artigo", "síntese rápida do paper", "lê esse paper e me resume", "o que esse artigo diz em
  resumo", ou enviar URL, DOI, PDF ou trecho de paper pedindo extração rápida e estruturada.
  Diferente da /paper-review (leitura crítica com pontos fortes e fracos), a /abstract é uma
  extração textual compacta: 5 tópicos em markdown, sem julgamento, pronta em segundos. Acionar mesmo que o pedido seja informal ou breve.
---

# Skill `/abstract`: Extração Estruturada de Paper

## Objetivo

Extrair as informações essenciais de um paper científico em **5 tópicos fixos**, em prosa
direta e densa, para triagem rápida antes de decidir se vale ler inteiro ou aprofundar com
`/paper-review`.

---

## Workflow

### Passo 1: Obter o conteúdo

Aceitar qualquer forma de input:

| Input | Ação |
|---|---|
| URL (Nature, arXiv, PubMed, medRxiv...) | `web_fetch` na URL |
| DOI (`10.xxxx/...`) | `web_fetch` em `https://doi.org/{DOI}` |
| PDF anexado | Ler via ferramentas de leitura de arquivo |
| Texto colado (abstract, trecho) | Usar direto do contexto |
| Já lido na conversa atual | Reutilizar, não buscar de novo |

Se a URL retornar paywall sem conteúdo, tentar `https://pubmed.ncbi.nlm.nih.gov/?term={DOI}`
como fallback para abstract público. Deixar claro se só o abstract foi lido (sem fulltext).

---

### Passo 2: Extrair nos 5 tópicos

Produzir **exatamente esta estrutura**, em markdown, sem headers de seção extra:

```
### [Título completo]
**Autores:** [sobrenome1, sobrenome2, et al.] · **Venue:** [journal/conferência · ano] · **DOI:** [link]

**Introdução / Problema**
[2-4 frases: qual lacuna ou limitação motivou o estudo, qual a aposta central dos autores]

**Métodos**
[3-5 frases: dataset, população, desenho experimental, arquitetura ou abordagem principal,
comparadores utilizados]

**Resultados**
[3-5 frases: principais métricas numéricas, comparações com baseline, desfechos primários.
Incluir números concretos sempre que disponíveis]

**Limitações**
[2-3 frases: o que os autores reconhecem como falhas, escopo restrito, vieses potenciais,
o que ainda falta validar]

**Relevância**
[2-3 frases: por que isso importa, para pesquisa, clínica ou gestão de IA em saúde.
Conexão direta com o contexto do leitor quando pertinente: a linha de pesquisa do
laboratório, o projeto em andamento, a prática clínica ou a regulação de IA em saúde]
```

---

## Diretrizes de qualidade

- **Números sempre que existirem**: não omitir métricas, p-valores, tamanhos de amostra
- **Sem invenção**: se um campo não tiver informação suficiente no texto disponível, escrever
  "Não disponível no texto acessado", nunca preencher com suposição
- **Limitações honestas**: se o paper não tiver seção explícita de limitações, inferir da
  Discussion, mas sinalizar "(inferido da discussão)"
- **Prosa densa, sem bullets internos**: cada tópico é um parágrafo contínuo, não lista
- **Sem jargão não-explicado**: siglas devem aparecer expandidas na primeira ocorrência
- **Comprimento total**: ~250-400 palavras no corpo dos 5 tópicos

---

## Diferença de escopo em relação a skills similares

| Skill | Formato | Quando usar |
|---|---|---|
| `/abstract` | 5 tópicos em markdown, sem visual | Triagem rápida, leitura em 30 s |
| `/paper-review` | Leitura crítica: metodologia, pontos fortes e fracos | Decidir se o paper sustenta uma citação |
| `/papers` | Lista dos papers da semana sobre um tópico | Descobrir o que saiu, antes de triar |

---

## Exemplos de acionamento

| O usuário diz | O que fazer |
|---|---|
| `/abstract https://arxiv.org/abs/2504.12345` | `web_fetch` na URL, extrair 5 tópicos |
| `/abstract` (após mostrar paper na conversa) | Reutilizar conteúdo já lido, não buscar |
| "me dá os pontos principais desse paper" + PDF | Ler PDF, extrair 5 tópicos |
| "resume esse DOI: 10.1038/s41586-026-10675-5" | `web_fetch` em `https://doi.org/10.1038/s41586-026-10675-5` |
| "quais os tópicos desse artigo?" + URL colada | `web_fetch` na URL, extrair 5 tópicos |
