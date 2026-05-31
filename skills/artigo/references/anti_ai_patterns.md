# Anti-IA patterns: lista expandida

Padroes que denunciam texto gerado por IA. Remover ou reescrever.

## Em ingles

### Verbos suspeitos (IA adora)
- "delve into" -> "examine", "explore", "investigate"
- "navigate" (metaforico) -> "address", "deal with"
- "leverage" -> "use"
- "underscore" -> "show", "highlight"
- "shed light on" -> "reveal", "show"
- "elucidate" -> "explain", "clarify"
- "facilitate" -> "help", "enable"
- "embark on" -> "start", "begin"
- "harness" -> "use"
- "foster" (metaforico) -> "promote", "encourage"

### Adjetivos repetidos demais
- "robust" - usar com moderacao, nao em todo paragrafo
- "comprehensive" - quase sempre desnecessario
- "cutting-edge" -> "current", "recent"
- "game-changing" -> "significant"
- "pivotal" -> "important", "key"
- "groundbreaking" -> "novel", "new"
- "intricate" -> "complex" ou deletar
- "multifaceted" -> "complex" ou deletar
- "seamless" -> deletar
- "novel" em excesso -> deletar uns

### Frases de transicao genericas
- "It is important to note" -> deletar
- "It is worth noting" -> deletar
- "It should be noted" -> deletar
- "Notably," -> deletar
- "Importantly," -> deletar
- "In essence" -> deletar
- "Furthermore," repetido -> alternar com "also", "in addition", ou nada
- "Moreover," repetido -> idem
- "Additionally," repetido -> idem

### Estruturas de paragrafo
- Listas de 3 items sempre terminando "and" -> variar (2 items, 4 items, prosa)
- "Not only X but also Y" usado em excesso -> "X and Y", "X. Y"
- "On one hand... on the other hand" -> reescrever
- Frases comecando todas com "The" -> variar

### Cliches academicos
- "in the realm of" -> "in"
- "in the context of" usado em excesso -> "in", "for"
- "plays a crucial role" -> "is important for"
- "plays a significant role" -> "matters for"
- "a wide range of" -> "many", "various"
- "a plethora of" -> "many"
- "myriad of" -> "many"

### Palavras vazias
- "essentially"
- "fundamentally"
- "ultimately"
- "ostensibly"
- "arguably"
- "indeed" em excesso

### Conclusoes
- "In conclusion," -> deletar (a secao ja se chama Conclusion)
- "To summarize," -> deletar
- "All in all," -> deletar
- "At the end of the day," -> deletar

## Em portugues

### Frases vazias
- "Vale ressaltar" -> deletar
- "Cabe destacar" -> deletar
- "E importante notar" -> deletar
- "Faz-se necessario" -> "precisamos", "e necessario"
- "Ao longo do presente trabalho" -> "neste trabalho"
- "No decorrer da pesquisa" -> "na pesquisa"

### Estruturas
- "No ambito de" -> "em"
- "No contexto de" em excesso -> reescrever
- "Em virtude de" -> "por causa de", "devido a"
- "Tendo em vista que" -> "porque", "ja que"
- "Nao obstante" -> "porem", "mas"
- "Outrossim" -> deletar (formal demais)

### Verbos suspeitos
- "evidenciar" usado demais -> "mostrar", "indicar"
- "elucidar" -> "explicar", "esclarecer"
- "consubstanciar" -> "concretizar" ou reescrever
- "perpassar" -> "passar por", "envolver"

### Pontuacao
- Travessoes (em dash —, en dash –) -> SEMPRE virgula, ponto, ou parenteses
- Aspas tipograficas " " -> retas " "
- Aspas simples tipograficas ' ' -> retas ' '
- Reticencias Unicode -> tres pontos normais ...
- Hifen como separador decorativo em titulos -> dois pontos ou virgula

## Estruturais (nao especificos a palavras)

### Frases longas demais
- Mais de 30-35 palavras: quebrar
- Mais de 2 niveis de subordinacao: simplificar
- Listas embutidas em frases: virar lista de verdade

### Voz passiva em excesso
- Alternar com ativa
- "It was found that X" -> "We found X"
- "X was determined" -> "We determined X" ou "X is"

### Repeticao de inicio de paragrafo
- Nao todos com "The"
- Nao todos com "We"
- Variar: "Among", "After", "When", "Despite", etc.

### Conectores em excesso
- "However" em todo paragrafo
- "Therefore" em todo paragrafo
- Aprenda quando NAO usar conector (frases curtas seguidas funcionam)

## Workflow de revisao anti-IA

1. Ler o paper inteiro em voz alta (mentalmente)
2. Marcar (highlight amarelo) toda frase que "soa de IA"
3. Buscar com regex/grep cada padrao da lista
4. Reescrever priorizando: frases curtas + voz ativa + verbo concreto
5. Pedir para alguem (humano) ler 1-2 paragrafos e dizer se soa natural

## Ferramentas

- GPTZero, Originality.ai: detectores (uteis para auto-checagem mas nao confiar 100%)
- Grammarly: bom para gramatica mas pode introduzir mais padroes IA
- Hemingway Editor: ajuda a quebrar frases longas e simplificar

## Citar Kapoor & Narayanan

Quando discutir leakage e reproducibilidade em ML, sempre citar:
> Kapoor S, Narayanan A. Leakage and the reproducibility crisis in machine-learning-based science. Patterns. 2023;4(9):100804.

Eles documentaram falhas sistematicas em 294 estudos de ML em ciencia. Util como contraponto critico em qualquer paper de IA medica.
