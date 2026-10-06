---
name: papers
description: Levanta papers científicos sobre metodologias de IA aplicadas à medicina publicados nos últimos 7 dias, sobre um tópico específico que o usuário fornece. Use esta skill SEMPRE que o usuário pedir "/papers", "papers da semana", "o que saiu essa semana sobre [tópico]", "varrer arxiv/pubmed/medrxiv", "levantamento semanal de papers", "novidades em IA médica", "papers recentes sobre [tema]", "o que foi publicado essa semana em IA médica", "semana de [tópico]", "últimos papers sobre IA em saúde". A skill pergunta o tópico ao ser iniciada (se não for fornecido na mesma mensagem), varre arXiv, PubMed e medRxiv no intervalo dos últimos 7 dias em paralelo, filtra por relevância metodológica em IA/ML aplicada a saúde, deduplica por DOI e entrega lista estruturada inline com título, autores, venue, data, abstract destacado, link e DOI, pronta para triagem. Diferente da /radar-academico (busca manual por consulta web, baixa PDFs e resume), a /papers roda um script contra as APIs das três fontes.
---

# Skill `/papers`: Papers de IA em Medicina da Última Semana

## Visão geral

Recebe um tópico do usuário, varre arXiv + PubMed + medRxiv nos últimos 7 dias, filtra pelos que tratam de metodologia de IA aplicada à medicina, deduplica e entrega uma lista estruturada inline, pronta para triagem. O fluxo natural depois é rodar `/abstract [link]` ou `/paper-review [link]` nos papers que valerem a pena ler.

---

## Passo 1: Obter o tópico

A skill pode ser acionada de duas formas:

| Como o usuário aciona | Ação |
|---|---|
| `/papers` (sem tópico) | Pergunte: **"Qual tópico você quer varrer esta semana? Ex: 'LLMs para extração de EHR', 'modelos de predição de sepse', 'fairness em radiologia', 'foundation models para imagem médica'."** E espere a resposta. |
| `/papers LLMs para EHR` | Use o tópico fornecido direto, não pergunte de novo. |
| "papers da semana sobre X" | Use X como tópico direto. |

**IMPORTANTE, tradução PT→EN:** As bases (arXiv, PubMed, medRxiv) indexam em inglês. Se o tópico vier em português, **traduza para inglês técnico** antes de passar para o script. Exemplos:
- "LLMs para extração de EHR" → `"LLM EHR extraction"`
- "predição de sepse" → `"sepsis prediction"`
- "fairness em radiologia" → `"fairness radiology"`
- "modelos fundacionais para imagem médica" → `"foundation models medical imaging"`

Mantenha o tópico curto (2-5 palavras-chave), sem conectores. Se o usuário já deu em inglês, passe direto.

---

## Passo 2: Rodar o script de varredura

O script bundlado em `scripts/fetch_papers.py` faz todo o trabalho: bate nas 3 APIs em paralelo, parseia XML/JSON, filtra por data + relevância de IA, deduplica por DOI e devolve markdown pronto.

**Como invocar:**

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/fetch_papers.py" --topic "TOPICO AQUI" --days 7
```

Parâmetros:
- `--topic` (obrigatório): o tópico fornecido pelo usuário, entre aspas
- `--days` (opcional, padrão 7): janela em dias
- `--max-per-source` (opcional, padrão 25): limite por fonte antes do merge
- `--no-pubmed` / `--no-arxiv` / `--no-medrxiv`: desabilitar fontes específicas se o usuário pedir

O script só usa a biblioteca padrão do Python (sem `pip install`).

---

## Passo 3: Receber e apresentar o resultado

O script imprime markdown já formatado no stdout. **Sua tarefa é repassar o output direto pro usuário**, com um cabeçalho curto e um rodapé com próximo passo.

**Cabeçalho (antes do output do script):**
```
🔎 Varredura de papers, **[tópico]**
Janela: [data_inicio] → [data_fim] (últimos 7 dias)
```

**Corpo:** output literal do script (não reformate, não resuma).

**Rodapé (depois do output):** oferecer `/abstract [link]` para o resumo estruturado de
qualquer item da lista.

---

## Passo 4: Casos especiais

| Situação | O que fazer |
|---|---|
| Script retornou 0 papers | Informe de forma clara: "Nenhum paper novo encontrado nos últimos 7 dias pra esse tópico." Sugira ampliar a janela: "Quer que eu tente com 14 ou 30 dias?" |
| Script falhou numa das fontes | O script já reporta "⚠️ Fonte X indisponível" e segue com as outras. Só repasse. |
| Script falhou completamente (erro de conexão, timeout) | Faça fallback usando `web_fetch` manualmente: arXiv em `http://export.arxiv.org/api/query?search_query=all:"{topic}"+AND+cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=20`, depois PubMed E-utilities, depois medRxiv. Filtre pelos últimos 7 dias no client-side. |
| Usuário pede janela diferente | Use `--days N` |
| Usuário pede mais papers | Use `--max-per-source 50` |
| Usuário pede só uma fonte | Use `--no-X` nas outras |

---

## Passo 5: Comportamento esperado

- **Sempre perguntar o tópico** se não foi fornecido, não chute.
- **Nunca invente papers.** Se o script não achou, não preencha com "papers similares que você pode gostar". Seja honesto com 0 resultados.
- **Não resuma nem reformate** o output do script. Ele já foi projetado pra ficar legível, repasse cru.
- **Não traduza títulos nem autores.** Mantenha no idioma original (inglês).
- **Priorize papers com DOI**, o script já faz isso na ordenação, mas se for listar só um subset, DOI primeiro.
- **Não cite pra usuário** os URLs internos das APIs (arXiv API, E-utilities), só os links finais dos papers.

---

## Passo 6: Formato de saída esperado (referência)

O script produz algo assim pra cada paper:

```
### 1. [Título completo do paper]
**Autores:** Smith J, Kumar R, Tanaka Y, et al.
**Fonte:** arXiv · cs.CL · 2026-04-15
**DOI/ID:** [10.48550/arXiv.2604.12345](https://arxiv.org/abs/2604.12345)
**Abstract (destaque):** Propõe um framework de LLM fine-tunado em notas clínicas do MIMIC-IV para extração de comorbidades, atingindo F1 de 0.89 vs 0.74 do baseline BERT-clinical...
```

Papers separados por linha em branco. Numeração sequencial. Ordenação por data decrescente (mais recente primeiro).

---

## Exemplos de acionamento

| Usuário diz | O que você faz |
|---|---|
| `/papers` | Pergunte o tópico |
| `/papers foundation models radiologia` | Rode o script com `--topic "foundation models radiologia"` |
| `papers da semana sobre sepsis prediction` | Rode o script com `--topic "sepsis prediction"` |
| `o que saiu esse mês em LLM clínico?` | Rode o script com `--topic "clinical LLM"` e `--days 30` |
| `me mostra só do PubMed` | Rode com `--no-arxiv --no-medrxiv` |
| (depois da lista) `resume o primeiro` | Rode `/abstract [URL do paper #1]` |

---

## Nota técnica sobre as fontes

- **arXiv**: varre categorias `cs.AI, cs.LG, cs.CL, cs.CV, stat.ML, q-bio.QM`. Filtra client-side por data de submissão e keywords médicas (health, clinical, medical, patient, hospital, EHR, diagnosis, etc.) no título ou abstract.
- **PubMed**: usa E-utilities (esearch + efetch). Query combina o tópico com filtros MeSH de IA (`artificial intelligence`, `machine learning`, `deep learning`, `neural networks, computer`) + faixa de `PDAT` (publication date) dos últimos N dias.
- **medRxiv**: usa API oficial, baixa todos os preprints no intervalo de datas e filtra client-side por keywords do tópico + menção metodológica de IA.

Dedup: por DOI primeiro, depois por título normalizado (lowercase, sem pontuação, primeiros 80 chars).
