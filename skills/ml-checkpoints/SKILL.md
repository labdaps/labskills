---
name: ml-checkpoints
description: Conduz o desenvolvimento de um pipeline preditivo em saúde por checkpoints interativos, um de cada vez, perguntando qual caminho seguir e oferecendo apenas as estratégias que os dados carregados permitem. Roda um diagnóstico da base (missing, cardinalidade, sentinelas, desbalanceamento, repetição de paciente, suspeita de vazamento) e usa esses números para montar as opções de cada decisão: separação dos dados, tratamento de faltantes, pré-processamento, desbalanceamento, modelos candidatos, seleção de features, métrica principal, calibração e interpretabilidade, até a predição final. Cada escolha fica registrada com o motivo. Use SEMPRE que o usuário pedir "/ml-checkpoints", "me guia no pipeline", "vamos passo a passo no modelo", "que estratégia uso para separar os dados", "como trato o missing aqui", "qual modelo uso para esses dados", "qual métrica escolher", "me ajuda a montar o modelo com esses dados", "checkpoints do pipeline", ou quando alguém chegar com uma base e não souber qual decisão tomar em alguma etapa da modelagem. Acionar também quando o usuário estiver em dúvida entre duas estratégias concretas (holdout ou validação cruzada, SMOTE ou class_weight, AUROC ou AUPRC, one-hot ou target encoding).
---

# Skill: ml-checkpoints

Conduz o pipeline preditivo por checkpoints. Em cada um, você pergunta o caminho, oferece só o que os dados permitem, registra a escolha com o motivo e segue.

A skill existe porque a decisão errada em ML de saúde quase nunca é a do modelo. É separar por linha quando o mesmo paciente tem três internações, imputar sem indicador uma variável que falta mais em quem tem menos acesso, usar AUROC com desfecho de 3%, ou tratar código de município como quantidade. Nenhum desses erros aparece na métrica: todos aparecem na validação externa, quando já não dá para voltar.

Por isso a regra que organiza tudo: **as opções de cada checkpoint saem do diagnóstico da base, não de um menu fixo.** Se os dados bloqueiam uma estratégia, ela não é oferecida.

## Fluxo

```
CP0 diagnóstico -> CP1 desfecho -> CP2 separação -> CP3 faltantes -> CP4 pré-processamento
 -> CP5 desbalanceamento -> CP6 modelos -> CP7 features -> CP8 métrica -> CP9 calibração
 -> CP10 interpretabilidade -> CP11 predição e empacotamento
```

Um checkpoint por vez. Não adiante decisão futura nem peça tudo de uma vez: o valor está em cada escolha chegar com o número que a sustenta.

## CP0: diagnóstico (sempre primeiro, sem perguntar antes)

Peça o caminho da base e a coluna do desfecho, e rode:

```bash
python <pasta-desta-skill>/scripts/diagnose_data.py <arquivo> --target <desfecho> [--id <coluna>] [--date <coluna>]
```

A pasta da skill é `~/.claude/skills/ml-checkpoints/` quando instalada pelo `install.sh`. Aceita CSV, TSV, Parquet e Excel. Com `--json`, devolve o mesmo diagnóstico em formato de máquina.

O que ele mede e por que cada coisa importa está em `references/checkpoints.md`. O essencial: N e colunas, tipo e prevalência do desfecho, missing por coluna, cardinalidade, sentinelas de saúde (9, 99, 999) distinguidas de código legítimo, colunas numéricas que na verdade são código, repetição por identificador, colunas de data e suspeita de vazamento por AUC univariada.

Apresente ao usuário só o que exige decisão, não o relatório inteiro. E leve a sério o que aparecer:

- **Suspeita de vazamento é parada obrigatória.** Uma variável com AUC univariada acima de 0,95 quase sempre é consequência do desfecho, não preditora. Resolva antes do CP1.
- **Missing no próprio desfecho** muda a definição da coorte, não é problema de imputação.
- **Repetição por identificador** já elimina o split aleatório, e isso precisa ser dito no CP2 com o número de linhas por grupo.

## Como conduzir cada checkpoint

1. **Nunca ofereça opção marcada BLOQUEADO** pelo diagnóstico. Ela não é uma escolha ruim, é uma escolha que os dados impedem. Se o usuário pedir mesmo assim, mostre o número que a bloqueia e peça confirmação explícita antes de registrar como aceite consciente.
2. **Duas a quatro opções**, cada uma com o que ela custa. A recomendada vem primeiro, marcada, e o motivo é sempre um número medido na base, nunca "é boa prática".
3. **Registre a decisão em `pipeline-decisions.md` assim que ela for tomada**, a partir de `templates/pipeline-decisions.template.md`. Esse arquivo vira a seção de Métodos do artigo: se a decisão não estiver escrita com o motivo, ela não existe daqui a três meses.
4. **Propague a restrição.** Toda escolha fecha portas adiante, e isso precisa ser dito na hora, não descoberto depois.

### Restrições que uma escolha impõe às seguintes

| Escolha no checkpoint | O que ela obriga depois |
|---|---|
| split por grupo (CP2) | a CV do CP6 usa o mesmo agrupamento, e o tuning também |
| split temporal (CP2) | nenhuma feature pode usar informação posterior ao corte, e o resultado sai por período |
| imputação (CP3) | o imputador é aprendido dentro do fold, e o CP9 reporta calibração com e sem |
| indicador de missing (CP3) | os indicadores entram como features e aparecem no SHAP do CP10 |
| target encoding (CP4) | encoding dentro do fold, obrigatoriamente; fora dele é vazamento |
| SMOTE ou reamostragem (CP5) | CP9 deixa de ser opcional: recalibrar e reportar Brier antes e depois |
| modelo nativo a NaN (CP3, CP6) | trocar de família de modelo reabre o CP3 inteiro |
| família de modelo (CP6) | reabre o CP4: árvore dispensa escalonamento, linear e SVM exigem |
| seleção de features (CP7) | a seleção acontece dentro do fold, e o N de features entra no cálculo de casos por variável |
| ponto de corte (CP8) | o corte é fixado no treino, nunca escolhido olhando o teste |

Quando uma escolha reabre um checkpoint anterior, volte, refaça e anote no registro. Seguir em frente com a decisão velha é o caminho mais curto para um resultado que não reproduz.

## Os checkpoints

O catálogo completo de opções, com o critério que muda o status de cada uma, está em `references/checkpoints.md`. Resumo do que se decide:

| Checkpoint | Decisão |
|---|---|
| CP1 desfecho e unidade | qual coluna é o alvo, qual é a unidade de análise, qual é o momento da predição |
| CP2 separação | holdout, CV repetida ou aninhada, split por grupo, split temporal, validação externa |
| CP3 faltantes | modelo nativo a NaN, imputação simples com indicador, MICE, descarte de coluna, sentinelas |
| CP4 pré-processamento | confirmar códigos numéricos, encoding, escalonamento, outliers |
| CP5 desbalanceamento | não balancear, class_weight, reamostragem |
| CP6 modelos | baseline obrigatória, boosting, linear regularizado, rede neural |
| CP7 features | manter todas, conhecimento clínico, importância dentro do fold, RFE |
| CP8 métrica | AUROC, AUPRC, sensibilidade em especificidade fixa, decision curve, ponto de corte |
| CP9 calibração | só reportar, Platt, isotônica |
| CP10 interpretabilidade | SHAP com direção, coeficientes, partial dependence, permutação |
| CP11 predição | treinar no conjunto final, prever em dado novo, empacotar e registrar |

### CP11: fechar o ciclo

Com todas as decisões tomadas, gere o código do pipeline refletindo exatamente o que foi escolhido, rode, e entregue quatro coisas:

1. **A predição no dado que o usuário quer prever**, com a probabilidade calibrada, não só a classe.
2. **A métrica principal com intervalo de confiança**, comparada com a baseline do CP6. Sem a baseline ao lado, o número não significa nada.
3. **O SHAP com a direção de cada variável**, com as divergências do esperado clinicamente marcadas.
4. **O `pipeline-decisions.md` completo**, que já é o rascunho da seção de Métodos.

Se o modelo não bater a baseline, diga isso na primeira linha. Resultado negativo fecha o ciclo, não reabre a busca por um número melhor.

## Regras que não dependem do checkpoint

- **Todo pré-processamento aprendido dentro do fold.** Imputação, encoding, escalonamento, seleção e balanceamento. Aprender no dado completo infla a métrica de um jeito indistinguível de sucesso.
- **Dado bruto nunca no repositório.** O registro de decisões referencia o caminho, jamais o conteúdo.
- **Nada de escolher o corte olhando o teste.**
- **Métrica sem incerteza não é resultado.** Reporte IC, por bootstrap ou pela variação entre folds.

## Relação com as outras skills do laboratório

Esta skill decide, as outras executam. Ela é o passo a passo interativo; a `graph-lab` é o planejamento do experimento inteiro como grafo antes de começar, e a `ml-pipeline` é a implementação padrão do laboratório.

| Momento | Skill |
|---|---|
| planejar o experimento todo antes de rodar | `graph-lab` |
| decidir cada etapa com os dados na mão | `ml-checkpoints` (esta) |
| implementar treino, CV e calibração | `ml-pipeline` |
| avaliação, ROC, SHAP, subgrupos | `ml-eval-report` |
| desfecho novo no pipeline DataSUS | `datasus-outcome` |
| série temporal | `ml-timeseries` |

## Referências

- `scripts/diagnose_data.py`: o diagnóstico que alimenta as opções (pandas e numpy)
- `references/checkpoints.md`: catálogo de opções por checkpoint, com o critério de cada status
- `templates/pipeline-decisions.template.md`: registro das decisões, que vira a seção de Métodos
