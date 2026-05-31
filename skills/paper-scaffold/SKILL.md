---
name: paper-scaffold
description: Gera estrutura de artigo cientifico com secoes, checklist e template LaTeX/Markdown. Triggers on /paper-scaffold.
---

# Skill: paper-scaffold

Cria estrutura completa para escrita de artigo cientifico.

## Passos

### 1. Coletar informacoes

Perguntar ao usuario:
- **Tipo:** original research, review, short communication, letter
- **Area:** ML em saude, epidemiologia, clinical AI, etc.
- **Journal alvo:** (para adaptar formato e word limit)
- **Dados/resultados** ja disponiveis

### 2. Gerar estrutura

```markdown
# Titulo (provisorio)

## Abstract
- Background (2-3 frases)
- Methods (2-3 frases)
- Results (2-3 frases)
- Conclusion (1-2 frases)
- Keywords: []

## 1. Introduction
- Contexto do problema
- Gap na literatura
- Objetivo do estudo

## 2. Methods
### 2.1 Study Design and Population
### 2.2 Data Sources
### 2.3 Variables
### 2.4 Statistical Analysis / ML Pipeline
### 2.5 Ethical Considerations

## 3. Results
### 3.1 Descriptive Statistics
### 3.2 Main Analysis
### 3.3 Sensitivity Analysis

## 4. Discussion
- Principal achado
- Comparacao com literatura
- Implicacoes clinicas
- Limitacoes
- Trabalhos futuros

## 5. Conclusion

## References

## Supplementary Material
```

### 3. Checklist pre-submissao

- [ ] TRIPOD (se modelo preditivo)
- [ ] STROBE (se observacional)
- [ ] CONSORT (se trial)
- [ ] PRISMA (se review)
- [ ] Dados e codigo disponiveis?
- [ ] Conflitos de interesse declarados?
- [ ] Aprovacao etica mencionada?

### 4. Criar arquivos

- `paper/manuscript.md` com a estrutura
- `paper/references.bib` vazio
- `paper/figures/` diretorio para figuras
- `paper/tables/` diretorio para tabelas
