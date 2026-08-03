---
name: graph-lab
description: Modela um experimento de machine learning em saúde como grafo dirigido antes de rodar qualquer código, no formato de projeto do laboratório (7 fases, de dados a submissão). Cada etapa do pipeline vira um nó com métrica de sucesso mensurável, dependências viram arestas sólidas e efeitos colaterais entre métricas (imputação degradando calibração, balanceamento degradando probabilidade, seleção de features degradando interpretabilidade) viram arestas tracejadas auditadas antes da execução. Use SEMPRE que o usuário pedir "/graph-lab", "modela esse experimento como grafo", "planeja o pipeline antes de rodar", "grafo do experimento", "monta o task-graph do projeto", "inicializa o experimento", ou ao começar um projeto preditivo novo com DataSUS, coorte hospitalar, prontuário ou base pública de saúde. Acionar PROATIVAMENTE antes de treinar o primeiro modelo de um projeto e antes de rodar um ciclo de experimentos, quando houver métricas em tensão (discriminação vs. calibração, desempenho vs. equidade entre subgrupos, ganho de AUC vs. validade externa).
---

# Skill: graph-lab

Modela um experimento de ML em saúde como grafo dirigido antes da execução, seguindo as fases de projeto do laboratório: dados, features, modelagem, explicabilidade, validação, redação e submissão.

Um experimento clínico tem métricas em tensão o tempo todo. Imputar missing melhora a AUC e piora a calibração. Balancear a classe rara melhora a sensibilidade e destrói a probabilidade prevista, que é justamente o que o clínico usa. Cortar features aumenta o desempenho e derruba a interpretabilidade que sustenta o parecer médico. Quem otimiza uma métrica por vez, em loop, não enxerga isso: só vê o número que persegue, e descobre o estrago na revisão do artigo ou, pior, na validação externa.

O grafo torna esses efeitos visíveis ANTES de rodar: toda etapa declara o que ela degrada, e o conflito aparece na auditoria, não no reviewer 2.

**Regra central: nenhum modelo treinado antes do AUDIT aprovado.**

**Segunda regra: nenhuma rodada termina sem a página HTML em `graphs/`.** O Mermaid serve para a máquina validar ciclos, a página serve para a pessoa entender o que cada nó mediu. Ver a fase RENDER.

## Quando NÃO usar

Se a tarefa for pontual (recalcular uma métrica, refazer uma figura, rodar um modelo já definido em dado já limpo), diga que o grafo é overhead e execute direto. Estrutura teatral em tarefa simples só gasta tempo do laboratório.

## Onde vivem os artefatos

| Artefato | Onde | Por quê |
|---|---|---|
| `task-graph.md` | raiz do repositório do experimento | é a fonte da verdade da rodada, e todo update de status acontece nele |
| `graphs/task-graph.html` | repositório do experimento, versionado | é entregável, precisa sobreviver ao fim da sessão |
| CSV de métricas, figuras, modelos | repositório do experimento | são os números daquela rodada |
| aprendizado de ferramenta e método | hub de método do laboratório | é o que outro experimento, com outro dado, consegue reusar |

Na dúvida sobre onde registrar algo, pergunte: isso serve para um experimento de outro domínio? Se a resposta depende dos números desta rodada, fica no projeto.

**Dado bruto nunca entra no repositório**, nem no privado. O grafo referencia o caminho do dado, jamais o conteúdo.

## Formato canônico de nó

```
[id] descrição | métrica: como medir que está pronto | entregável: o quê
```

Exemplo: `[N7] treinar modelos candidatos | métrica: AUC OOF com IC95% por bootstrap para os 4 modelos, curva de calibração gerada | entregável: results/cv_metrics.csv e models/*.pkl`

Métrica de sucesso não é "modelo treinado". É o número que decide se o nó está pronto, com a incerteza junto. Nó sem métrica mensurável não entra no grafo: reescreva até ter.

## Sintaxe das arestas (bloco Mermaid `graph TD`)

| Sintaxe | Tipo | Significado |
|---|---|---|
| `A --> B` | `depends_on` | B depende de A; A executa antes |
| `A -.->\|"−métrica"\| B` | `impacts(−)` | executar A degrada uma métrica de B |
| `A -.->\|"+métrica"\| B` | `impacts(+)` | executar A melhora uma métrica de B |

Só as arestas sólidas entram no cálculo de ciclo e ordem topológica. As tracejadas não ordenam execução, mas obrigam auditoria.

## As cinco fases (sempre nesta ordem)

### 1. DECOMPOSE

Parta do esqueleto de 7 fases em `references/nos-padrao.md`, que é o mesmo ciclo de projeto do hub do laboratório: dados e pré-processamento, feature engineering, modelagem e benchmarking, explicabilidade, validação e análises complementares, redação, submissão.

Não copie o esqueleto inteiro. Ele é ponto de partida:

- **Pode nó fora**: sem coorte externa, o nó de validação externa vira `n/a` declarado, não um nó pendente eterno.
- **Divida nó grande**: "modelagem" com 4 famílias de modelo e tuning vira mais de um nó, porque as métricas de sucesso são diferentes.
- **Acrescente o que é do seu desenho**: análise de sobrevivência, competing risks, janela temporal, coorte multicêntrica, aprendizado federado.

Declare no topo do `task-graph.md` o tipo de desfecho (classificação, regressão, sobrevivência, séries temporais, visão, NLP), porque ele muda a métrica de sucesso de quase todo nó.

### 2. CONNECT

Ligue as dependências reais de input e output: um nó depende de outro quando consome o arquivo que o outro produz. Não invente dependência por conveniência de narrativa.

Depois, o que importa de verdade: percorra `references/nos-padrao.md`, seção "Efeitos colaterais típicos em experimento de saúde", e para cada nó pergunte **executar isto degrada a métrica de qual outro nó?**

Os que mais aparecem em projeto clínico:

- imputação de missing `impacts(−)` calibração e representatividade de subgrupo
- balanceamento de classe (SMOTE, undersampling, class weights) `impacts(−)` calibração das probabilidades
- seleção agressiva de features `impacts(−)` interpretabilidade clínica e validade externa
- tuning intensivo na mesma partição `impacts(−)` generalização e validação externa
- exclusão de linhas com missing `impacts(−)` equidade entre subgrupos e validade externa
- ampliação da janela temporal de coleta `impacts(−)` risco de leakage e comparabilidade entre períodos

Preencha o bloco Mermaid e a tabela de nós no `task-graph.md`.

### 3. AUDIT (portão obrigatório: bloqueia EXECUTE)

Antes de rodar qualquer coisa, os quatro itens precisam passar:

1. **Ciclos e ordem.** Rode `python scripts/validate_graph.py task-graph.md`. Exit 1 significa ciclo: o grafo é inválido, volte ao CONNECT. O script também imprime a ordem topológica, que vai para a seção "Ordem de execução".
2. **Efeitos colaterais negativos.** Liste todo nó que recebe `impacts(−)`. Cada um precisa de uma das duas saídas, registrada na tabela: **mitigação explícita** (uma ação concreta, por exemplo "recalibrar com Platt no conjunto de validação após o SMOTE, e reportar Brier antes e depois") ou **aceite consciente**, dito pelo usuário em texto. Sem uma das duas, EXECUTE fica bloqueado.
3. **Checklist anti-leakage.** Nenhum nó de modelagem começa antes disso, porque leakage descoberto na redação custa o experimento inteiro:
   - a variável de desfecho, ou proxy dela, não está entre as preditoras
   - nenhuma variável é registrada depois do momento da predição
   - imputação, encoding, escalonamento e seleção de features são aprendidos **dentro** do fold de treino, nunca no dado completo
   - a divisão respeita a unidade real de dependência (paciente, hospital, período), não a linha
   - em série temporal, a validação é temporal, e nenhuma janela futura alimenta o passado
4. **Regra de dados.** Confirme que o dado bruto está fora do repositório, que o `.gitignore` cobre os diretórios de dado e que o repositório público, se existir, só recebe dado sintético.

Só declare "AUDIT aprovado" com os quatro itens fechados.

### 4. EXECUTE

Siga a ordem topológica. Para cada nó: marque `in_progress` ao começar, verifique a métrica de sucesso ao terminar, e só então marque `done`. Nunca comece um nó cujas dependências não estejam `done`.

**Regra de replanejamento.** Se durante a execução aparecer dependência ou efeito colateral não mapeado, PARE. Volte ao grafo, acrescente o nó ou a aresta, re-rode o AUDIT no subgrafo afetado e registre no "Log de replanejamento" com data. Resolver inline e seguir é o que transforma um efeito invisível hoje em resultado irreprodutível daqui a três meses.

**Resultado negativo é resultado.** Se o modelo não bate a baseline, o nó está `done` com achado negativo, não `pending` esperando um número melhor. Registre e siga: o grafo existe para impedir que a rodada seja reescrita até parecer que deu certo.

### 5. RENDER (obrigatório ao final de cada rodada)

Gere a página HTML em `graphs/task-graph.html`, versionada no repositório do experimento, com nome de arquivo estável. A cada replanejamento, **reescreva o mesmo arquivo e republique o mesmo caminho**, para preservar a URL de quem já recebeu o link. Se a página já foi publicada em outra sessão, reaproveite a URL existente ao republicar.

Conteúdo, nesta ordem:

1. **O resultado principal em destaque no topo**, antes de qualquer gráfico, inclusive (principalmente) quando for negativo.
2. **O grafo desenhado**, com estado de cada nó em cor, dependências sólidas, efeitos colaterais tracejados com o sinal distinguido, e marcação visual nos nós que entraram por replanejamento.
3. **Tabela nó a nó com o resultado medido**, não com a descrição do que o nó deveria fazer.
4. **Os gráficos das métricas que estavam em tensão**, com intervalo de confiança e a linha de referência que separa resultado de ruído (a baseline, o acaso, o escore clínico já usado na prática).
5. **O que o modelo final usa por dentro**: importância SHAP com a direção de cada variável, e marcação visual nas variáveis cuja direção contraria o esperado clinicamente. Sem essa seção a página mostra desempenho e esconde conteúdo, que é exatamente o que a pessoa de domínio precisa ler para dar parecer.
6. **Os achados que exigem decisão de outra pessoa**, cada um com o número que o sustenta.
7. **O que ficou pendente e por quê**, com o motivo real do bloqueio.

Gere os gráficos por código, como SVG a partir de um array de dados. Não embuta PNG do matplotlib: pesa, tem fundo fixo que quebra no tema escuro e não deixa marcar os pontos que aguardam decisão humana.

**O grafo da página é interativo, não uma figura.** Acima de uma dúzia de nós sempre existe aresta cruzando caixa, e a caixa nunca cabe o que o nó mediu. Três interações resolvem: clique abre o detalhe num modal centralizado (estado, métrica, resultado medido, dependências de entrada e saída, efeitos colaterais), arrastar afasta o nó e soltar traz de volta com as arestas acompanhando, e arrastar o fundo percorre o grafo. O detalhe vai em modal e não em painel no rodapé, porque com muitos níveis o painel fica fora da tela justamente ao clicar num nó do topo. Use `<dialog>` nativo com `showModal()`, que já entrega Escape, foco preso e devolução do foco.

A volta ao lugar é obrigatória: a posição por nível topológico **é** a ordem de execução, e reposicionar em definitivo faz o grafo mentir sobre ela.

Armadilhas que costumam quebrar a página: converta o deslocamento do ponteiro pela razão entre a largura do viewBox e a largura renderizada, use `touch-action: none` no nó, distinga clique de arrasto por distância acumulada, respeite `prefers-reduced-motion`, faça a panorâmica por `scrollLeft` e `scrollTop` do visor (e só para mouse), e no handler do fundo desista quando `ev.target.closest(".no")` achar um nó. Atributos de apresentação do SVG (`fill`, `stroke`) não aceitam `var(--token)` de forma confiável: use classes CSS.

**Honestidade da página.** Os números vêm dos entregáveis dos nós, nunca de memória. Nó `pending` aparece como pendente, não como "em andamento". Se a versão anterior dizia outra coisa, diga o que mudou e por quê, em vez de reescrever a história.

## Ligação com as outras skills do laboratório

O grafo é o plano, as outras skills executam os nós:

| Nó do grafo | Skill que executa |
|---|---|
| pipeline de treino, CV, calibração | `ml-pipeline` |
| avaliação, ROC, SHAP, subgrupos | `ml-eval-report` |
| desfecho novo no pipeline DataSUS | `datasus-outcome` |
| séries temporais | `ml-timeseries` |
| redação com reporting guideline | `artigo`, `paper-scaffold` |
| revisão antes de submeter | `peer-review` |

## Referências

- `templates/task-graph.template.md`: esqueleto do artefato de estado
- `references/nos-padrao.md`: as 7 fases com nós e métricas de sucesso típicas, mais o catálogo de efeitos colaterais
- `scripts/validate_graph.py`: detecta ciclo e imprime ordem topológica (stdlib pura)
