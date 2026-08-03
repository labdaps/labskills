# Nós padrão de um experimento de ML em saúde

Esqueleto das 7 fases do ciclo de projeto do laboratório, com a métrica de sucesso típica de cada nó. Use como ponto de partida no DECOMPOSE: pode nó que não se aplica, divida nó grande, acrescente o que é do seu desenho.

A métrica listada aqui é o padrão mínimo. Se o seu desenho pede outra, troque, mas mantenha a regra: a métrica precisa ser um número verificável, com incerteza quando fizer sentido, não um estado ("feito", "pronto", "rodado").

## Fase 1: dados e pré-processamento

| Nó | Métrica de sucesso típica |
|---|---|
| ingestão do dado bruto | N de linhas e colunas conferido contra a fonte, dicionário de variáveis escrito, hash do arquivo registrado |
| limpeza e tipagem | zero coluna com tipo ambíguo, faixas implausíveis listadas e decididas uma a uma |
| definição operacional do desfecho | regra escrita que qualquer pessoa aplica e chega ao mesmo N de casos, prevalência reportada |
| análise descritiva (Table 1) | Table 1 completa por grupo de desfecho, com N, percentual de missing e teste apropriado |
| tratamento de missing | percentual por variável antes e depois, mecanismo assumido declarado, estratégia justificada |
| definição da janela temporal | data de início e fim, e a justificativa de por que nada fora dela entra |

## Fase 2: feature engineering e seleção

| Nó | Métrica de sucesso típica |
|---|---|
| features derivadas | lista de features com a regra de cálculo e o momento em que cada uma fica disponível |
| encoding de categóricas | cardinalidade final por variável, estratégia declarada, nenhuma categoria vazando desfecho |
| seleção de features | N de features antes e depois, critério explícito, e o efeito da poda medido na métrica principal |

## Fase 3: modelagem e benchmarking

| Nó | Métrica de sucesso típica |
|---|---|
| baseline | o número que qualquer modelo precisa bater: escore clínico já usado, regressão logística simples, ou prevalência |
| modelos candidatos | lista fechada de famílias, com a justificativa de por que cada uma entra |
| tuning de hiperparâmetros | espaço de busca declarado, N de iterações, partição usada para tunar, distinta da de teste |
| cross-validation | métrica principal OOF com IC95%, esquema de partição declarado, e o que define a unidade do fold |
| comparação de performance | tabela com todos os modelos e a baseline, mesma métrica, mesma partição, com IC |

## Fase 4: explicabilidade e interpretação

| Nó | Métrica de sucesso típica |
|---|---|
| SHAP e importância | ranking das variáveis com a direção do efeito, e as divergências do esperado clinicamente marcadas |
| partial dependence | curvas das principais variáveis, com a faixa de dado onde há suporte amostral |
| análise de subgrupos | métrica principal por subgrupo relevante (sexo, faixa etária, região, raça/cor), com IC e N por célula |

## Fase 5: validação e análises complementares

| Nó | Métrica de sucesso típica |
|---|---|
| calibração | slope e intercepto, Brier, curva de calibração; e se houve recalibração, o antes e o depois |
| validação externa | métrica principal na coorte externa com IC, e a queda em relação à interna declarada sem maquiagem |
| análise de sensibilidade | resultado sob as decisões alternativas de missing, ponto de corte e recorte da coorte |
| utilidade clínica | decision curve ou o par sensibilidade/especificidade no ponto de corte que a prática usaria |

## Fase 6: redação

| Nó | Métrica de sucesso típica |
|---|---|
| métodos | qualquer pessoa reproduz a partir do texto, e o reporting guideline está preenchido item a item |
| resultados, tabelas e figuras | todo número do texto tem origem rastreável num arquivo de resultado |
| discussão | limitações reais listadas, incluindo as que apareceram na auditoria de efeitos colaterais |
| abstract | números do abstract batem com os da tabela principal |
| revisão de coautores | comentários endereçados um a um, com resposta escrita |

## Fase 7: submissão

| Nó | Métrica de sucesso típica |
|---|---|
| checklist do reporting guideline | preenchido, com o número da página de cada item |
| figuras no formato do periódico | resolução e formato conferidos contra as instruções |
| código público | repositório sem dado real, sem credencial, com README que reproduz o pipeline |
| declaração de disponibilidade de dados | escrita e coerente com o que de fato pode ser compartilhado |
| submissão | protocolo de submissão registrado |

## Efeitos colaterais típicos em experimento de saúde

Este é o catálogo que dá valor ao grafo. Percorra a lista no CONNECT: para cada item que se aplica ao seu desenho, desenhe a aresta tracejada e leve para o AUDIT.

| Ação | Degrada | Por quê | Mitigação usual |
|---|---|---|---|
| imputação de missing | calibração, representatividade de subgrupo | a distribuição imputada não é a real, e o missing raramente é aleatório entre grupos | reportar resultado com e sem imputação, e o missing por subgrupo |
| balanceamento de classe (SMOTE, undersampling, class weights) | calibração da probabilidade | a prevalência artificial desloca toda a probabilidade prevista | recalibrar após o balanceamento e reportar Brier antes e depois |
| exclusão de linhas com missing | equidade entre subgrupos, validade externa | quem tem mais missing costuma ser quem tem menos acesso, e some da amostra | comparar quem entrou e quem saiu, no mínimo em idade, sexo e região |
| seleção agressiva de features | interpretabilidade clínica, validade externa | o modelo fica dependente de variáveis instáveis entre serviços | manter um modelo enxuto e clinicamente plausível como comparador |
| tuning intensivo na mesma partição | generalização, validação externa | o hiperparâmetro aprende a partição, não o fenômeno | partição de tuning separada da de teste, e reportar as duas |
| ampliação da janela temporal | risco de leakage, comparabilidade entre períodos | prática clínica e codificação mudam ao longo do tempo | validação temporal, e resultado por período |
| troca para modelo mais complexo | interpretabilidade, custo de implantação | ganho de AUC pequeno costuma não pagar a perda de leitura clínica | reportar o ganho contra a baseline com IC, e decidir explicitamente |
| escolha do ponto de corte por Youden | utilidade clínica no cenário real | o corte ótimo estatístico ignora o custo assimétrico de errar | reportar o corte junto do custo clínico de falso negativo e falso positivo |
| agregação de subgrupos pequenos | equidade | o grupo pequeno some dentro da média e o viés fica invisível | reportar N por célula e não esconder subgrupo com IC largo |
| uso de variável registrada após o desfecho | tudo | é leakage, e infla a métrica de forma indistinguível de sucesso | checklist anti-leakage no AUDIT, antes da modelagem |
