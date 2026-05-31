---
name: radar-academico
description: Busca semanal de papers academicos por tema, filtra relevantes, baixa PDFs e gera resumo. Triggers on /radar-academico ou quando o usuario pede para buscar papers novos.
---

# Skill: radar-academico

Executa o radar semanal de papers academicos. Busca, filtra, baixa e resume.

## Quando usar

- Quando o usuario pede `/radar-academico`
- Busca semanal de papers por tema (ex: multicalibration, fairness)
- Quando o usuario quer atualizar sua base de papers

## Passos

### 1. Definir parametros de busca

Perguntar ou inferir do contexto:

- **Tema(s)**: ex: multicalibration, fairness in ML, calibration
- **Periodo**: ultima semana por padrao
- **Fontes**: arXiv, Semantic Scholar, PubMed (conforme tema)
- **Diretorio destino**: padrao `mcalibration/docs/` (ou o que o usuario indicar)

### 2. Buscar papers

Usar WebSearch para cada tema/fonte:

```
site:arxiv.org "multicalibration" OR "multi-calibration"
site:arxiv.org "algorithmic fairness" calibration
```

Para cada resultado:

- Titulo
- Autores
- Data de publicacao
- Link do abstract
- Link do PDF

### 3. Filtrar relevancia

Criterios de filtragem:

- Publicado no periodo solicitado
- Relevante ao tema (ler abstract se necessario)
- Remover duplicatas de buscas anteriores (verificar PDFs ja existentes no diretorio destino)

Apresentar lista filtrada ao usuario para confirmacao antes de baixar.

### 4. Baixar PDFs

Para cada paper aprovado:

```bash
curl -L -o "<diretorio>/<nome-normalizado>.pdf" "<url-pdf>"
```

Nomear arquivos como: `2026-04_autor-principal_titulo-curto.pdf`

### 5. Gerar resumo

Criar ou atualizar arquivo `radar-resumo.md` no diretorio destino:

```markdown
# Radar Academico - YYYY-MM-DD

## Papers encontrados: N | Relevantes: M | Baixados: K

### 1. Titulo do Paper
- **Autores**: ...
- **Data**: ...
- **Resumo**: 2-3 frases sobre contribuicao principal
- **Arquivo**: nome-do-pdf.pdf
- **Link**: url
```

### 6. Confirmar

Mostrar resumo ao usuario com contagem de papers novos adicionados.
