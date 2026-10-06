---
name: ic
description: >
  Calcula o tamanho de uma amostra estatisticamente confiável para estimar uma
  proporção (taxa de erro, discordância, prevalência, adesão) com intervalo de
  confiança, conduzindo um Q&A curto e devolvendo a amostra e o cálculo passo a
  passo, SEM escrever nem rodar código (aritmética feita e mostrada na resposta).
  Use SEMPRE que o usuário pedir "/ic", "calcula a amostra", "tamanho de amostra",
  "quantos preciso sortear", "qual o n", "amostra pra auditoria", "amostra
  estatisticamente confiável", "calcula o n com wilson", "qual o IC dessa taxa",
  "qual a margem de erro", ou descrever a intenção de dimensionar uma amostra ou
  calcular o IC de uma proporção observada, mesmo informal. Dois modos: DIMENSIONAR
  (pergunta objetivo, N, p, margem, confiança, perda, estratos e calcula n com
  correção finita, inflação por perda e precisão de Wilson) e ANALISAR (recebe
  avaliáveis e discordantes e devolve a taxa com IC de Wilson). Mostra sempre as
  substituições. NÃO confundir com /papers nem /abstract.
---

# Skill: /ic: Amostra Confiável e Intervalo de Confiança (sem código)

Dimensiona uma amostra para estimar uma proporção com confiança estatística, ou calcula o IC de uma proporção já observada. Conduz um Q&A enxuto, faz a conta na própria resposta e mostra cada substituição. O resultado é a amostra em si mais a explicação de como foi calculada.

---

## Regra absoluta: sem código

NUNCA escrever, gerar ou rodar Python (nem qualquer outra linguagem). Toda a aritmética é feita à mão e exibida na resposta, com as substituições explícitas. O valor da skill é justamente entregar a conta legível, que o pesquisador consegue defender numa conversa sem depender de script.

---

## Dois modos

A skill detecta o modo pelo que o usuário trouxe:

- **DIMENSIONAR** (padrão): o usuário quer saber quantos sortear. Falta o n.
- **ANALISAR**: o usuário já tem o resultado da auditoria (nº de avaliáveis e nº de discordantes/eventos) e quer a taxa com IC. Reconhecer por frases como "auditei X e deu Y discordantes", "qual o IC de 56 em 400".

Se o usuário só digitar `/ic` sem contexto, assumir DIMENSIONAR e fazer as perguntas.

---

## MODO DIMENSIONAR

### Perguntas (enxutas, com defaults)

Fazer as perguntas numa única mensagem, já indicando o default entre parênteses, e deixar claro que o usuário pode responder só o que quer mudar. Em celular, oferecer as escolhas-chave (p conservador vs piloto, confiança) como opções tocáveis quando fizer sentido. Não perguntar o que já estiver claro no contexto da conversa.

1. **O que vai estimar e qual a unidade?** (ex.: taxa de discordância de laudos; unidade = laudo/exame/paciente)
2. **Tamanho da população N?** (a contagem total de onde vai sortear; se não souber, tratar como infinita)
3. **Taxa esperada p?** Conservador 0,5 (pior caso, recomendado quando não há piloto confiável) ou um valor de piloto/literatura (ex.: 0,139). **Default: 0,5.**
4. **Margem de erro d aceitável?** **Default: 0,05 (±5 pontos percentuais).**
5. **Confiança?** 90% / 95% / 99%. **Default: 95%.**
6. **Perda esperada?** Fração de unidades inelegíveis, sem imagem, canceladas. **Default: 10%.**
7. **Vai estratificar?** Por leitor, unidade, subtipo ou período. Se sim, cada estrato precisa do próprio n (rodar a conta por estrato). **Default: não, taxa global.**

### Tabela de z por confiança

| Confiança | z |
|---|---|
| 80% | 1,282 |
| 90% | 1,645 |
| 95% | 1,960 |
| 99% | 2,576 |

### Cálculo (mostrar todas as substituições)

**Passo 1. Amostra base (população infinita)**
`n₀ = z²·p(1−p)/d²`
Calcular `z²`, depois `p(1−p)`, depois multiplicar e dividir por `d²`. Arredondar **sempre para cima**.

**Passo 2. Correção para população finita (só se N foi informado)**
`n = n₀/(1 + (n₀−1)/N)`
Arredondar para cima. Se `N ≥ 20×n₀`, dizer explicitamente que a correção é desprezível e que a população é, na prática, infinita (o N confirma a fórmula simples, não muda o número). Se N não foi informado, pular este passo e avisar que o resultado vale para população grande.

**Passo 3. Inflação por perda**
`n_sortear = n/(1 − perda)`
Arredondar para cima. Deixar claro: **n é o número de avaliáveis no fim; n_sortear é quanto puxar no começo.**

**Passo 4. Precisão real por Wilson no n obtido**
Reportar a meia-largura do IC de Wilson que esse n entrega, na taxa esperada p e, se p não for 0,5, também no pior caso (p=0,5). Fórmula no bloco ANALISAR. Isso responde "que precisão esse n compra".

**Modo validação contra limiar** (se o objetivo for aprovar/reprovar contra um limiar L em vez de só estimar): dimensionar de forma que o limite superior do IC fique abaixo de L. Na prática, escolher d tal que `p_esperado + d ≤ L`, e seguir os mesmos passos. Explicar a regra de decisão (aprova se o limite superior do IC < L).

---

## MODO ANALISAR (IC de Wilson)

Entradas: `n` = nº de avaliáveis, `k` = nº de discordantes/eventos. `p̂ = k/n`.

Com `z` da confiança escolhida (default 95% → 1,96):

```
denom        = 1 + z²/n
centro       = (p̂ + z²/(2n)) / denom
meia-largura = z·√( p̂(1−p̂)/n + z²/(4n²) ) / denom
IC           = centro ± meia-largura
```

Mostrar cada substituição numérica. Reportar: taxa observada `p̂`, o IC `[inferior; superior]`, e a meia-largura em pontos percentuais. Se houver uma margem prometida ou um limiar, dizer se o IC cabe nela (a precisão real bateu o prometido?) ou se o limite superior ficou abaixo do limiar (aprovado?).

Usar **sempre Wilson, nunca Wald**. Wald quebra com proporção pequena ou n por estrato baixo.

---

## Arredondamento e formatação

- Tamanho de amostra: arredondar **sempre para cima** (não dá pra auditar meio laudo).
- Números em pt-BR: vírgula decimal e ponto de milhar (ex.: 119.232; 0,139; ±3,4 pp).
- Proporções com 3 casas, margens em pontos percentuais (pp) com 1 casa.
- Sem travessão em texto português. Usar vírgula, dois-pontos ou ponto.

---

## Formato de saída

**1. Resposta direta (no topo, 1 a 2 linhas).**
Ex.: "Sortear 427 ao acaso dos 119.232 para terminar com ~385 avaliáveis. Precisão: ±4,9 pp no pior caso, ±3,4 pp na taxa esperada (95% Wilson)."

**2. Definições usadas** (tabela compacta com N, objetivo, p, d, z, perda).

**3. Cálculo passo a passo** (as substituições dos passos 1 a 4).

**4. Como executar.**
- Sortear aleatoriamente do marco amostral (a lista enumerável dos N), com seed registrada, para o sorteio ser reprodutível e ter valor probatório.
- Auditar, contar discordantes.
- Reportar a taxa com IC de Wilson 95%.
- Estratificar só se quiser taxa por leitor/unidade.

Em modo ANALISAR, a saída é a taxa observada, o IC de Wilson e a interpretação (cabe na margem? aprova no limiar?).

---

## Exemplo completo (referência de qualidade)

Entrada: estimar taxa de discordância de laudos de CRC; N = 119.232 TC de abdome; sem piloto confiável; margem 5 pp; 95%; perda 10%.

Cálculo:
- z = 1,96; z² = 3,8416
- p = 0,5 (conservador) → p(1−p) = 0,25
- n₀ = 3,8416 × 0,25 / 0,05² = 0,9604 / 0,0025 = 384,16 → 385
- FPC: 385 / (1 + 384/119.232) = 385 / 1,00322 = 383,8 → 384 (N ≥ 20×n₀, correção desprezível, população praticamente infinita)
- inflação 10%: 384 / 0,9 = 426,7 → 427
- precisão Wilson em 400 avaliáveis: ±4,9 pp no pior caso (p=0,5); ±3,4 pp se a taxa observada for ~0,139

Resposta: sortear 427, esperar ~385 avaliáveis, reportar com IC de Wilson. O número "400" que circulava bate com o n conservador, então é defensável, e agora se sabe de onde veio.

---

## Armadilhas a evitar

- **Não escolher d de trás pra frente.** O d é definido pela precisão necessária, antes da conta. Margens "estranhas" (3,7%, 3,4%) costumam ser sinal de n forçado para cair num número redondo.
- **N grande não justifica n grande.** Acima de ~20 mil, a população é praticamente infinita: o n depende de p, d e confiança, não do tamanho da população.
- **p = 0,5 é o pior caso.** Se houver piloto confiável com p longe de 0,5, usar o piloto reduz bastante o n (e isso é legítimo, desde que declarado).
- **n é avaliáveis, não sorteados.** Sempre inflar pela perda esperada.
- **Sorteio sem seed registrada não é auditável.** Reforçar reprodutibilidade.
- **Wilson, nunca Wald.**
