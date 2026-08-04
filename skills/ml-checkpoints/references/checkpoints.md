# Catálogo de checkpoints

Cada checkpoint traz as opções, o critério que decide o status de cada uma e o que a escolha custa adiante. Os limiares citados são os que o `scripts/diagnose_data.py` aplica, e estão declarados como constantes no topo do script: mudá-los é legítimo, desde que a mudança entre no registro de decisões.

Convenção de status: **VIÁVEL** (os dados permitem), **DESACONSELHADO** (permitem, mas há um motivo medido para não usar), **BLOQUEADO** (os dados impedem, não oferecer).

## O que o diagnóstico mede

| Medida | Para que serve |
|---|---|
| N de linhas, colunas, duplicatas | dimensiona o que é viável de holdout e de modelo |
| tipo do desfecho | binário, multiclasse ou contínuo muda métrica e modelo |
| prevalência e razão de desbalanceamento | decide CP5 e a métrica principal do CP8 |
| missing por coluna | decide CP3 coluna a coluna, não em bloco |
| cardinalidade | decide o encoding do CP4 |
| sentinelas (9, 99, 999) | valor implausível para a escala da variável, repetido o suficiente para ser código, não o número 9 em qualquer lugar |
| numéricas que são código | código de município, CID numérico, tipo de estabelecimento lidos como quantidade |
| repetição por identificador | elimina o split aleatório do CP2 |
| colunas de data | habilita o split temporal do CP2 |
| AUC univariada alta | suspeita de vazamento, parada obrigatória |
| casos da classe rara por feature | decide CP6 e CP7 |

Sobre os falsos positivos: uma variável inteira com poucos valores distintos aparece como "possível código" mesmo quando é quantidade legítima, como idade. É de propósito. O custo de perguntar é uma pergunta; o custo de tratar código de município como número é um modelo que aprende que o município 200 é maior que o 100.

## CP1: desfecho e unidade de análise

Antes de qualquer estratégia, três respostas que mudam todo o resto:

- **Qual é a definição operacional do desfecho.** Não o nome da coluna, a regra. Óbito em qual janela, readmissão em quantos dias, contado a partir de quando.
- **Qual é a unidade de análise.** Paciente, internação, exame, município, mês. A unidade define o que não pode se repetir entre treino e teste.
- **Qual é o momento da predição.** O que se sabe naquele instante, na prática. Toda variável registrada depois desse momento é vazamento, por mais correlacionada que seja.

Se o diagnóstico apontou suspeita de vazamento, resolva aqui, uma coluna por vez: ela existe no momento da predição ou não.

## CP2: separação dos dados

| Opção | VIÁVEL quando | Custo |
|---|---|---|
| holdout aleatório estratificado | sem repetição por identificador e N confortável | com N pequeno, o resultado muda a cada semente |
| validação cruzada repetida ou aninhada | sempre | custo computacional; obrigatória com classe rara pequena |
| split por grupo (StratifiedGroupKFold) | há identificador que repete | folds ficam desbalanceados quando os grupos têm tamanhos muito diferentes |
| split temporal | há coluna de data | reduz o treino, e é o único jeito de medir se o modelo envelhece |
| validação externa | há coorte de outro serviço ou período | quase sempre derruba a métrica, e é exatamente por isso que vale |

**Bloqueio duro:** identificador que repete elimina o split aleatório por linha. Com o mesmo paciente nos dois lados, o modelo decora a pessoa e a métrica sobe sem que ele tenha aprendido nada transferível.

O split temporal responde uma pergunta que o aleatório não responde: o modelo treinado em 2021 ainda vale em 2024. Prática clínica, codificação e perfil de paciente mudam, e a validação aleatória esconde isso ao misturar os períodos.

## CP3: dados faltantes

Decida coluna a coluna, por faixa de missing:

| Faixa | Encaminhamento usual |
|---|---|
| acima de 40% | descartar, ou manter só o indicador de presença |
| entre 5% e 40% | imputar com indicador de missing |
| abaixo de 5% | imputação simples resolve |

| Opção | VIÁVEL quando | Custo |
|---|---|---|
| modelo nativo a NaN | sempre | prende a família de modelo: trocar reabre este checkpoint |
| imputação simples com indicador | há missing nas faixas média ou baixa | desloca a distribuição, e a calibração sente |
| imputação múltipla (MICE) | missing intermediário com variáveis correlacionadas | custo alto e relato mais complicado no artigo |
| descartar coluna | há coluna acima de 40% | perde informação que pode ser justamente a que faltava |
| descartar linhas (complete case) | quase nunca | quem tem mais missing costuma ser quem tem menos acesso, e a exclusão vira viés de seleção |
| tratar sentinelas | há valor implausível repetido | precisa vir antes de qualquer imputação, senão a média é calculada com 999 dentro |

**A pergunta que decide:** o missing é diferente entre os grupos de desfecho, ou entre subgrupos como sexo, raça/cor e região. Se for, ele carrega informação, o indicador deixa de ser opcional e a exclusão de linhas passa a ser uma decisão sobre quem sai do estudo.

## CP4: pré-processamento

Primeiro, **confirme quais numéricas são código**. Depois:

| Opção | VIÁVEL quando | Custo |
|---|---|---|
| one-hot | categóricas com cardinalidade até uma dezena e meia | acima disso a matriz explode e a árvore perde eficiência |
| categóricas nativas (CatBoost, LightGBM) | há cardinalidade média ou alta | prende a família de modelo |
| target encoding | cardinalidade alta e nada mais serve | só dentro do fold; é a fonte de vazamento mais comum |
| escalonamento | condicional à família do CP6 | irrelevante para árvore, obrigatório para linear, SVM e KNN |
| tratamento de outlier | valor implausível clinicamente | cortar cauda pode remover justamente o caso grave que se quer prever |

Outlier em saúde merece cuidado: pressão de 300 pode ser erro de digitação ou o paciente que vai morrer. A decisão é clínica, não estatística.

## CP5: desbalanceamento

| Opção | VIÁVEL quando | Custo |
|---|---|---|
| não balancear, ajustar o corte | sempre, e é o padrão em modelo de risco | exige explicar que acurácia alta não significa nada aqui |
| class_weight balanceado | razão acima de 20 para 1 | mexe na probabilidade, menos que reamostrar |
| SMOTE ou reamostragem | raramente | prevalência artificial desloca toda a probabilidade prevista, e obriga recalibrar |

Desbalanceamento não é um problema a corrigir por reflexo. Desfecho raro é raro no mundo, e a probabilidade prevista precisa refletir isso. Quem usa o modelo na ponta lê "risco de 8%", não "classe positiva".

Se houver reamostragem, ela acontece **dentro do fold de treino**, nunca antes do split, e o CP9 deixa de ser opcional.

## CP6: modelos candidatos

| Opção | VIÁVEL quando | Custo |
|---|---|---|
| baseline (logística ou escore clínico) | sempre, é obrigatória | nenhum; sem ela não há como julgar o resto |
| gradient boosting | N a partir de algumas centenas | menos legível, e o ganho costuma ser menor do que se espera |
| linear regularizado | sempre, e preferível com poucos casos por feature | perde interação não linear |
| rede neural tabular | dezenas de milhares de linhas | em dado tabular de saúde raramente compensa |

**A baseline não é formalidade.** Se o boosting ganha 0,01 de AUC da logística, com IC sobreposto, a resposta certa é a logística: ela é lida, auditada e implantada.

Casos da classe rara por feature abaixo de 10 é o sinal clássico de sobreajuste em modelo clínico. Com esse número baixo, modelo simples e menos features não é conservadorismo, é o que sobrevive à validação externa.

## CP7: seleção de features

| Opção | VIÁVEL quando | Custo |
|---|---|---|
| manter todas | há casos da classe rara suficientes por feature | com poucos casos, sobreajusta |
| conhecimento clínico | sempre | exige um clínico na decisão, e é o critério que melhor sobrevive à validação externa |
| importância dentro do fold | sempre, se for dentro do fold | fora do fold é vazamento silencioso |
| eliminação recursiva (RFE) | N confortável | instável em amostra pequena: a lista muda a cada semente |

## CP8: métrica principal e ponto de corte

| Opção | VIÁVEL quando | Custo |
|---|---|---|
| AUPRC | prevalência abaixo de 10% | menos familiar para o leitor clínico, exige explicar |
| AUROC | prevalência não extrema | com desfecho raro, parece ótima mesmo com muitos falsos positivos |
| sensibilidade em especificidade fixa | há ponto de operação definido pelo serviço | precisa do serviço para definir |
| decision curve analysis | sempre | responde a pergunta do gestor: usar o modelo é melhor que tratar todos ou ninguém |

Escolha **uma** métrica principal antes de rodar. Escolher depois, entre as que saíram, é selecionar o resultado.

O ponto de corte vem do custo clínico, não do Youden. Errar um falso negativo em triagem de sepse e errar um falso positivo em indicação cirúrgica não custam a mesma coisa.

## CP9: calibração

| Opção | VIÁVEL quando | Custo |
|---|---|---|
| só reportar | sempre, é o mínimo | não corrige nada |
| Platt (sigmoid) | sempre, e primeira escolha com amostra pequena | assume forma sigmoide do desvio |
| isotônica | milhares de linhas | sobreajusta a curva com amostra pequena |

Reporte slope, intercepto e Brier. Modelo de risco clínico com AUROC alta e calibração ruim entrega o ranking certo e o número errado, e é o número que vai para a conduta.

## CP10: interpretabilidade

| Opção | VIÁVEL quando | Custo |
|---|---|---|
| SHAP com direção | sempre, é o padrão do laboratório | custo computacional em base grande |
| coeficientes | há baseline linear no relato | só o efeito linear |
| partial dependence | sempre | enganoso fora da faixa com suporte amostral |
| importância por permutação | sem variáveis muito correlacionadas ou de alta cardinalidade | distribui crédito de forma enganosa quando há correlação |

Marque visualmente as variáveis cuja direção contraria o esperado clinicamente. É o que transforma uma tabela de números numa pergunta que o clínico consegue responder, e às vezes é assim que o vazamento aparece.
