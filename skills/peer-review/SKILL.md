---
name: peer-review
description: Simula revisao por pares de um manuscrito cientifico proprio, como se fosse um revisor anonimo de journal. Avalia 8 dimensoes (Titulo/Abstract, Introducao, Metodos, Resultados, Discussao, Conclusoes, Referencias, Escrita), atribui nota 1-5 a cada uma, lista revisoes prioritarias e emite decisao editorial (Aceito / Revisoes menores / Revisoes maiores / Rejeitar). Diferente de paper-review, que le artigos externos: peer-review e para voce revisar o seu proprio manuscrito antes de submeter. Triggers on /peer-review, "faz peer review do meu artigo", "revisa meu manuscrito como revisor", "simula revisao editorial", "o que um revisor diria do meu paper", "avalia meu manuscrito para submissao".
---

# Skill: peer-review

Avalia um manuscrito cientifico proprio simulando o papel de um revisor anonimo de journal. Gera relatorio estruturado com notas, pontos fortes, pontos fracos, sugestoes de revisao e decisao editorial final.

## Quando usar

- `/peer-review` ou `/peer-review caminho/do/arquivo.md`
- "faz peer review do meu artigo"
- "revisa meu manuscrito como revisor de journal"
- "simula revisao editorial do paper"
- "o que um revisor diria do meu manuscrito"
- Antes de submeter: para identificar falhas antes que os revisores oficiais identifiquem

Diferenca de /paper-review: aquela skill le e critica artigos externos. Esta avalia o seu proprio manuscrito no papel de revisor.

## Entrada

- Caminho para o manuscrito (`.md`, `.tex`, `.docx`). Se nao fornecido, usa `main.md` no diretorio atual.
- Ler o arquivo completo antes de comecar qualquer avaliacao.

## Passos

### 1. Leitura integral

Ler o manuscrito por inteiro. Identificar tipo de estudo, guideline de reporting seguida (IMRAD, GUILD, STROBE, TRIPOD+AI, etc.) e journal alvo, se mencionado.

### 2. Avaliacao por dimensao

Avaliar cada dimensao com nota de 1 (insuficiente) a 5 (excelente), apontar pontos fortes especificos, pontos fracos especificos e sugestoes concretas de revisao.

**Dimensoes:**

1. **Titulo e Abstract** -- titulo preciso? abstract estruturado (objetivo, metodos, resultados, conclusao)?
2. **Introducao** -- contexto suficiente, lacuna identificada, objetivo claro e decorrente da lacuna?
3. **Metodos** -- reproducibilidade, guideline de reporting seguida, analise estatistica apropriada?
4. **Resultados** -- completos, consistentes com os metodos, tabelas e figuras bem descritas?
5. **Discussao** -- interpreta (nao apenas reafirma) resultados, contextualiza na literatura, limitacoes honestas?
6. **Conclusoes** -- suportadas pelos dados, sem extrapolacao indevida?
7. **Referencias** -- completas, sem placeholders ou DOIs pendentes, formato consistente?
8. **Qualidade de escrita** -- clareza, gramatica, terminologia consistente ao longo do texto?

### 3. Lista de acoes prioritarias

Listar de 5 a 10 revisoes obrigatorias em ordem de prioridade, da mais urgente a menos urgente. Ser concreto: "Reescrever X fazendo Y", nao apenas "Melhorar X".

### 4. Decisao editorial

Emitir uma das quatro decisoes padrao de journal:

- **Aceito** -- pronto para publicacao sem alteracoes
- **Revisoes menores** -- correcoes simples sem necessidade de nova rodada de revisao
- **Revisoes maiores** -- problemas substanciais que exigem nova rodada de revisao
- **Rejeitar** -- problemas fundamentais que nao sao corrigiveis sem reescrever o manuscrito

Acompanhar com 2 a 3 frases justificando a decisao.

## Formato do output

Relatorio em Markdown com esta estrutura exata:

```
# Peer Review -- [Titulo do paper]
**Data:** YYYY-MM-DD  |  **Revisor:** Anonimo

## Resumo para o autor
[3 a 5 frases: contribuicao principal, pontos mais fortes, problemas mais criticos]

## Notas por dimensao
| Dimensao          | Nota (1-5) |
|:------------------|:----------:|
| Titulo e Abstract | X          |
| Introducao        | X          |
| Metodos           | X          |
| Resultados        | X          |
| Discussao         | X          |
| Conclusoes        | X          |
| Referencias       | X          |
| Qualidade escrita | X          |
| **Geral**         | **X.X**    |

## Avaliacao detalhada
### 1. Titulo e Abstract -- X/5
**Pontos fortes:** ...
**Pontos fracos:** ...
**Sugestoes:** ...

[repetir para cada dimensao]

## Lista de acoes prioritarias
1. ...
2. ...

## Decisao editorial
**Recomendacao:** [Aceito / Revisoes menores / Revisoes maiores / Rejeitar]
**Justificativa:** ...
```

## Orientacoes de tom

Ser direto e construtivo. Para cada problema identificado: dizer o que esta errado, por que e um problema e como corrigir. Reconhecer explicitamente o que esta funcionando bem -- o autor precisa saber o que preservar, nao so o que mudar. Evitar linguagem vaga ("a discussao poderia melhorar"): dizer sempre como e por que melhorar.
