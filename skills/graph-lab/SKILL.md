---
name: graph-lab
description: Modela uma tarefa complexa como grafo dirigido antes de executar qualquer coisa: cada etapa vira nó com métrica de sucesso mensurável, dependências viram arestas sólidas e efeitos colaterais entre métricas viram arestas tracejadas, auditadas antes da execução. Dois perfis: geral, para engenharia (refatoração, migração, infraestrutura), e saúde/ML, obrigatório quando a tarefa treina modelo, com as 7 fases de projeto do laboratório, checklist anti-leakage e regra de dados. Substitui a graph-init. Use SEMPRE que o usuário pedir "/graph-lab", "modela como grafo", "grafo do experimento", "planeja o pipeline antes de rodar", "decompõe antes de executar", "monta o task-graph", "inicializa o experimento". Acionar PROATIVAMENTE antes de executar tarefa com 3 ou mais subtarefas interdependentes ou com métricas em tensão (discriminação vs. calibração, desempenho vs. legibilidade, custo vs. cobertura), e sempre antes de treinar o primeiro modelo de um projeto ou rodar um ciclo de experimentos.
---

# Skill: graph-lab

Modela uma tarefa como grafo dirigido antes da execução. Cada etapa vira nó com métrica de sucesso, dependências viram arestas, e o que uma etapa degrada em outra fica declarado antes de rodar, não descoberto depois.

Toda tarefa real tem métricas em tensão: acelerar um endpoint pode quebrar testes, cortar custo pode degradar cobertura. Um loop que otimiza uma métrica por vez só vê o número que persegue. O grafo torna o efeito colateral visível na auditoria, não em produção.

**Regra central: nada executado antes do AUDIT aprovado.** Nenhuma linha de código no perfil geral, nenhum modelo treinado no perfil saúde/ML.

**Segunda regra: nenhuma rodada termina sem a página HTML em `graphs/`.** O Mermaid serve para a máquina validar ciclos, a página serve para a pessoa entender o que cada nó mediu. Ver a fase RENDER.

## Perfis

| Perfil | Quando | O que usa |
|---|---|---|
| geral | engenharia: refatoração, migração, infraestrutura, pipeline de dados sem modelo | o núcleo: nós com métrica, arestas, AUDIT de ciclo e de efeito negativo, ordem de execução, página HTML |
| saúde/ML | a tarefa treina, ajusta ou avalia modelo preditivo | o núcleo mais a identificação do desfecho, o esqueleto de 7 fases do laboratório (`references/nos-padrao.md`), o checklist anti-leakage e a regra de dados |

**Quando a tarefa treina modelo, o perfil saúde/ML é obrigatório**, mesmo que ela pareça de engenharia (um refactor que re-treina, uma migração que muda o pré-processamento). O checklist anti-leakage e a regra de dados são itens do AUDIT desse perfil e não podem ser pulados: vazamento descoberto na redação custa o experimento inteiro. Declare o perfil no topo do `task-graph.md`.

O perfil saúde/ML segue as fases de projeto do laboratório: dados, features, modelagem, explicabilidade, validação, redação e submissão. Um experimento clínico tem métricas em tensão o tempo todo. Imputar missing melhora a AUC e piora a calibração. Balancear a classe rara melhora a sensibilidade e destrói a probabilidade prevista, que é justamente o que o clínico usa. Cortar features aumenta o desempenho e derruba a interpretabilidade que sustenta o parecer médico. Quem otimiza uma métrica por vez, em loop, descobre o estrago na revisão do artigo ou, pior, na validação externa. Com o grafo, o conflito aparece na auditoria, não no reviewer 2.

Esta skill absorveu o modo geral da antiga `graph-init`. Se as duas estiverem instaladas em `~/.claude/skills/`, mantenha só esta: juntas, disparam gatilhos concorrentes.

## Quando NÃO usar

Se a tarefa for pontual, de 1 a 2 passos, sem dependência cruzada nem métrica em tensão (recalcular uma métrica, refazer uma figura, rodar um modelo já definido em dado já limpo), diga que o grafo é overhead e execute direto, sem gerar `task-graph.md`. Estrutura teatral em tarefa simples só gasta tempo do laboratório.

## Onde vivem os artefatos

| Artefato | Onde | Por quê |
|---|---|---|
| `task-graph.md` | raiz do repositório do projeto | é a fonte da verdade da rodada, e todo update de status acontece nele |
| `graphs/task-graph.html` | repositório do projeto, versionado, sempre o mesmo caminho | é a página publicada, e o caminho fixo preserva a URL |
| `graphs/<INICIAIS>-v<N>-<AAAA-MM-DD>.html` e `graphs/README.md` | repositório do projeto, versionados | snapshot de cada rodada e o índice deles: mostram quando e por que a conclusão mudou |
| entregáveis dos nós (código, CSV de métricas, figuras, modelos) | repositório do projeto | são os números daquela rodada |
| aprendizado de ferramenta e método | `docs/aprendizados-pipeline-agentes.md` do ai-lab-hub | é o que outro experimento, com outro dado, consegue reusar |

Na dúvida sobre onde registrar algo, pergunte: isso serve para um experimento de outro domínio? Se a resposta depende dos números desta rodada, fica no projeto.

**Dado bruto nunca entra no repositório**, nem no privado. O grafo referencia o caminho do dado, jamais o conteúdo.

## Formato canônico de nó

```
[id] descrição | métrica: como medir que está pronto | entregável: o quê
```

Exemplos:

- geral: `[N3] migrar endpoints de leitura | métrica: 100% dos GET async, suíte verde | entregável: handlers async em routes/read.py`
- saúde/ML: `[N7] treinar modelos candidatos | métrica: AUC OOF com IC95% por bootstrap para os 4 modelos, curva de calibração gerada | entregável: results/cv_metrics.csv e models/*.pkl`

Métrica de sucesso não é "modelo treinado" nem "código migrado". É o número que decide se o nó está pronto, com a incerteza junto quando houver. Nó sem métrica mensurável não entra no grafo: reescreva até ter.

## Sintaxe das arestas (bloco Mermaid `graph TD`)

| Sintaxe | Tipo | Significado |
|---|---|---|
| `A --> B` | `depends_on` | B depende de A; A executa antes |
| `A -.->\|"−métrica"\| B` | `impacts(−)` | executar A degrada uma métrica de B |
| `A -.->\|"+métrica"\| B` | `impacts(+)` | executar A melhora uma métrica de B |

Só as arestas sólidas entram no cálculo de ciclo e ordem topológica. As tracejadas não ordenam execução, mas obrigam auditoria.

Prefira a forma do template: cada nó declarado numa linha, com o rótulo entre aspas, e cada aresta noutra, ligando ids puros. O validador também aceita cadeia (`A --> B --> C`), `&` (`A & B --> C`), `:::classe`, `==>`, `---` e `-- texto -->` como dependência; qualquer linha com seta que ele não consiga transformar em aresta sai com exit 2, em vez de ser ignorada.

## As cinco fases (sempre nesta ordem)

### 1. DECOMPOSE

Gere o `task-graph.md` na raiz do projeto a partir de `templates/task-graph.template.md` e transforme a tarefa em nós no formato canônico. Cada nó tem id, descrição, métrica de sucesso e entregável. No perfil geral, apague as seções do template marcadas como só saúde/ML; `examples/example-refactor.md` mostra um grafo geral preenchido.

No perfil saúde/ML, parta do esqueleto de 7 fases em `references/nos-padrao.md`, que é o mesmo ciclo de projeto do hub do laboratório: dados e pré-processamento, feature engineering, modelagem e benchmarking, explicabilidade, validação e análises complementares, redação, submissão.

Não copie o esqueleto inteiro. Ele é ponto de partida:

- **Pode nó fora**: sem coorte externa, o nó de validação externa vira `n/a` declarado, não um nó pendente eterno.
- **Divida nó grande**: "modelagem" com 4 famílias de modelo e tuning vira mais de um nó, porque as métricas de sucesso são diferentes.
- **Acrescente o que é do seu desenho**: análise de sobrevivência, competing risks, janela temporal, coorte multicêntrica, aprendizado federado.

Declare no topo do `task-graph.md` o tipo de desfecho (classificação, regressão, sobrevivência, séries temporais, visão, NLP), porque ele muda a métrica de sucesso de quase todo nó.

### 2. CONNECT

Ligue as dependências reais de input e output: um nó depende de outro quando consome o arquivo que o outro produz. Não invente dependência por conveniência de narrativa.

Depois, o que importa de verdade: para cada nó pergunte **executar isto degrada ou melhora a métrica de qual outro nó?** No perfil geral, um nó "reduzir latência" pode ter `impacts(−)` em "cobertura de testes". No perfil saúde/ML, percorra `references/nos-padrao.md`, seção "Efeitos colaterais típicos em experimento de saúde".

Os que mais aparecem em projeto clínico:

- imputação de missing `impacts(−)` calibração e representatividade de subgrupo
- balanceamento de classe (SMOTE, undersampling, class weights) `impacts(−)` calibração das probabilidades; não balancear é o padrão (`ml-checkpoints`, CP5)
- seleção agressiva de features `impacts(−)` interpretabilidade clínica e validade externa
- tuning intensivo na mesma partição `impacts(−)` generalização e validação externa
- exclusão de linhas com missing `impacts(−)` equidade entre subgrupos e validade externa
- ampliação da janela temporal de coleta `impacts(−)` risco de leakage e comparabilidade entre períodos

Preencha o bloco Mermaid e a tabela de nós no `task-graph.md`.

### 3. AUDIT (portão obrigatório: bloqueia EXECUTE)

Antes de rodar qualquer coisa, os itens do perfil precisam passar: 1 e 2 em qualquer perfil, e também 3 e 4 no perfil saúde/ML.

1. **Ciclos e ordem.** Rode `python3 <pasta-desta-skill>/scripts/validate_graph.py task-graph.md` (use `python` no Windows). A pasta da skill é `~/.claude/skills/graph-lab/` quando instalada pelo `install.sh`. Exit 1 significa ciclo: o grafo é inválido, volte ao CONNECT. Exit 2 aponta a linha do Mermaid que o script não conseguiu transformar em aresta: corrija a linha antes de seguir, porque aresta ignorada esconde ciclo. O script também imprime a ordem topológica, que vai para a seção "Ordem de execução". Sem ambiente para rodar Python, faça a checagem de ciclo à mão, por DFS.
2. **Efeitos colaterais negativos.** Liste todo nó que recebe `impacts(−)`. Cada um precisa de uma das duas saídas, registrada na tabela: **mitigação explícita** (uma ação concreta, por exemplo "recalibrar com Platt no conjunto de validação após o SMOTE, e reportar Brier antes e depois") ou **aceite consciente**, dito pelo usuário em texto. Sem uma das duas, EXECUTE fica bloqueado.
3. **Checklist anti-leakage (saúde/ML, obrigatório).** Nenhum nó de modelagem começa antes disso, porque leakage descoberto na redação custa o experimento inteiro. A norma de cada item, com as opções que os dados permitem, está na skill `ml-checkpoints` (CP1 a CP5):
   - a variável de desfecho, ou proxy dela, não está entre as preditoras
   - nenhuma variável é registrada depois do momento da predição
   - imputação, encoding, escalonamento e seleção de features são aprendidos **dentro** do fold de treino, nunca no dado completo
   - a divisão respeita a unidade real de dependência (paciente, hospital, período), não a linha
   - em série temporal, a validação é temporal, e nenhuma janela futura alimenta o passado
4. **Regra de dados (saúde/ML, obrigatório).** Confirme que o dado bruto está fora do repositório, que o `.gitignore` cobre os diretórios de dado e que o repositório público, se existir, só recebe dado sintético.

Só declare "AUDIT aprovado" com todos os itens do perfil fechados.

### 4. EXECUTE

Siga a ordem topológica. Para cada nó: marque `in_progress` ao começar, verifique a métrica de sucesso ao terminar, e só então marque `done`. Nunca comece um nó cujas dependências não estejam `done`.

**Regra de replanejamento.** Se durante a execução aparecer dependência ou efeito colateral não mapeado, PARE. Volte ao grafo, acrescente o nó ou a aresta, re-rode o AUDIT no subgrafo afetado e registre no "Log de replanejamento" com data. Resolver inline e seguir é o que transforma um efeito invisível hoje em resultado irreprodutível daqui a três meses.

**Resultado negativo é resultado.** Se o modelo não bate a baseline, o nó está `done` com achado negativo, não `pending` esperando um número melhor. Registre e siga: o grafo existe para impedir que a rodada seja reescrita até parecer que deu certo.

### 5. RENDER (obrigatório ao final de cada rodada)

Ao fim de cada rodada, gere a página HTML e grave duas cópias idênticas, versionadas no repositório do projeto, nunca no diretório temporário da sessão:

- **`graphs/task-graph.html`**, com nome estável: sempre o mesmo caminho. É a página que se publica, e republicar sempre a partir dela preserva a URL de quem já recebeu o link. Se a página já foi publicada em outra sessão, reaproveite a URL existente ao republicar.
- **`graphs/<INICIAIS>-v<N>-<AAAA-MM-DD>.html`**, o snapshot da rodada, cópia byte a byte da estável. INICIAIS são as iniciais do projeto em maiúsculas, tiradas do nome do repositório (`transfer-learning-iacov-br` vira `TLI`); N começa em 1 e sobe uma vez por rodada; a data é a do fechamento da rodada.

`graphs/README.md` é o índice dos snapshots: a URL publicada da página estável no topo e uma linha por versão.

```
| versão | data | arquivo | o que mudou em relação à anterior |
|---|---|---|---|
| v2 | AAAA-MM-DD | TLI-v2-AAAA-MM-DD.html | nó de calibração entrou por replanejamento; a manchete passou a ser a calibração |
```

**Snapshot de rodada anterior nunca é editado.** Ele é o registro do que a página dizia naquela data, e é o que mostra quando e por que a conclusão mudou. Correção de texto ou de cor antes de a rodada fechar reescreve a estável e o snapshot da rodada juntos, para que continuem idênticos. O `task-graph.md`, com o Mermaid, continua sendo a fonte que o validador confere; a página é derivada dele e dos entregáveis dos nós.

Conteúdo, nesta ordem:

1. **O resultado principal em destaque no topo**, antes de qualquer gráfico, inclusive (principalmente) quando for negativo.
2. **O grafo desenhado**, com estado de cada nó em cor, dependências sólidas, efeitos colaterais tracejados com o sinal distinguido, e marcação visual nos nós que entraram por replanejamento.
3. **Tabela nó a nó com o resultado medido**, não com a descrição do que o nó deveria fazer.
4. **Os gráficos das métricas que estavam em tensão**, com intervalo de confiança e a linha de referência que separa resultado de ruído (a baseline, o acaso, o escore clínico já usado na prática).
5. **O que o entregável final usa por dentro**, não só como ele se sai. No perfil saúde/ML é a importância SHAP do modelo final com a direção de cada variável, e marcação visual nas variáveis cuja direção contraria o esperado clinicamente. Sem essa seção a página mostra desempenho e esconde conteúdo, que é exatamente o que a pessoa de domínio precisa ler para dar parecer.
6. **Os achados que exigem decisão de outra pessoa**, cada um com o número que o sustenta.
7. **O que ficou pendente e por quê**, com o motivo real do bloqueio.

Gere os gráficos por código, como SVG a partir de um array de dados. Não embuta PNG do matplotlib: pesa, tem fundo fixo que quebra no tema escuro e não deixa marcar os pontos que aguardam decisão humana.

**O grafo da página é interativo, não uma figura.** Acima de uma dúzia de nós sempre existe aresta cruzando caixa, e a caixa nunca cabe o que o nó mediu. Três interações resolvem: clique abre o detalhe num modal centralizado (estado, métrica, resultado medido, dependências de entrada e saída, efeitos colaterais), arrastar afasta o nó e soltar traz de volta com as arestas acompanhando, e arrastar o fundo percorre o grafo. O detalhe vai em modal e não em painel no rodapé, porque com muitos níveis o painel fica fora da tela justamente ao clicar num nó do topo. Use `<dialog>` nativo com `showModal()`, que já entrega Escape, foco preso e devolução do foco.

A volta ao lugar é obrigatória: a posição por nível topológico **é** a ordem de execução, e reposicionar em definitivo faz o grafo mentir sobre ela.

Armadilhas que costumam quebrar a página: converta o deslocamento do ponteiro pela razão entre a largura do viewBox e a largura renderizada, use `touch-action: none` no nó, distinga clique de arrasto por distância acumulada, respeite `prefers-reduced-motion`, faça a panorâmica por `scrollLeft` e `scrollTop` do visor (e só para mouse), e no handler do fundo desista quando `ev.target.closest(".no")` achar um nó. Atributos de apresentação do SVG (`fill`, `stroke`) não aceitam `var(--token)` de forma confiável: use classes CSS. Use pointer events com `setPointerCapture` e trate `pointercancel`; no `<dialog>`, feche pelo backdrop só depois de comparar as coordenadas do clique com `getBoundingClientRect()`. Cada nó recebe `tabindex="0"`, `role="button"` e `aria-label`, e responde a Enter e Espaço. Diga na legenda o que dá para fazer: interação que ninguém descobre é o mesmo que não existir.

Antes de publicar, confira por script que toda aresta aponta para nó existente, que nenhuma caixa se sobrepõe a outra, que tudo cabe no viewBox e que nenhum rótulo estoura a caixa.

**Honestidade da página.** Os números vêm dos entregáveis dos nós, nunca de memória. Nó `pending` aparece como pendente, não como "em andamento". Se a versão anterior dizia outra coisa, diga o que mudou e por quê, em vez de reescrever a história.

## Ligação com as outras skills do laboratório (perfil saúde/ML)

O grafo é o plano, as outras skills executam os nós. As decisões de método de cada nó seguem a `ml-checkpoints`, que é a norma do laboratório; o porquê de cada regra está em `docs/aprendizados-pipeline-agentes.md`, no ai-lab-hub.

| Nó do grafo | Skill que executa |
|---|---|
| decisão de cada etapa com os dados na mão (separação, faltantes, encoding, balanceamento, métrica, calibração) | `ml-checkpoints` |
| pipeline de treino, CV, calibração | `ml-pipeline` |
| avaliação, ROC, SHAP, subgrupos | `ml-eval-report` |
| desfecho novo no pipeline DataSUS | `datasus-outcome` |
| séries temporais | `ml-timeseries` |
| redação com reporting guideline | `artigo`, `paper-scaffold` |
| revisão antes de submeter | `peer-review` |

## Referências

- `templates/task-graph.template.md`: esqueleto do artefato de estado, com as seções só saúde/ML marcadas
- `references/nos-padrao.md`: as 7 fases com nós e métricas de sucesso típicas, mais o catálogo de efeitos colaterais (perfil saúde/ML)
- `examples/example-refactor.md`: grafo do perfil geral preenchido (migração de endpoints síncronos para async)
- `scripts/validate_graph.py`: detecta ciclo e imprime ordem topológica (stdlib pura). É a fonte canônica do validador: cópias em outros repositórios devem ser idênticas a ele
- `tests/`: testes do validador, rodados no CI deste repositório; não são instalados em `~/.claude/skills/`
