# Auditoria de vazamento e de desfecho

Os casos abaixo sao reais, do laboratorio. Servem como catalogo: quando um dado novo chegar,
procure o analogo aqui antes de modelar.

## Caso 1: o tempo de seguimento dentro do X

**Experimento**: predicao de obito em 180 dias apos alta por endocardite infecciosa.

A coluna `TEMPO_ENTRE_ALTA_ULTIMA_INFORMACAO` mede os dias entre a alta e a ultima noticia que
se teve do paciente. Para quem morreu, essa ultima noticia e o obito. Ela estava entre os
preditores dos quatro modelos.

| medida | valor |
|---|---|
| AUC univariada na coorte completa, 775 pacientes | 0.879 |
| AUC univariada na coorte elegivel, 622 pacientes | 1.000 |
| ganho artificial de AUC do pipeline inteiro | +0.194 |
| folds em que o Boruta a selecionou, quando disponivel | 10/10 |
| fracao da importancia SHAP total que ela sozinha ocupava | 36.1% |

O 1.000 e o sinal mais claro possivel: dentro de quem tem seguimento completo, "morreu em 180
dias" e "tem menos de 180 dias de seguimento" sao a mesma afirmacao. A AUC perfeita estava
medindo a definicao do desfecho, nao um preditor.

**Sintoma generalizavel**: qualquer coluna que comece com "tempo ate" ou "tempo entre" e termine
num evento que pode ser o proprio desfecho.

## Caso 2: censura rotulada como sobrevivencia

Mesmo experimento. 126 pacientes vivos com menos de 180 dias de seguimento e 27 sem data nenhuma
entravam como `OBITO_180DIAS = 0`. Sao censurados: ninguem sabe o que aconteceu com eles.

O ponto que faz esse erro sobreviver a uma revisao: **o rotulo errado so e coerente se o modelo
tambem enxergar o tempo de seguimento**. Os dois erros se sustentam mutuamente, e quem tira so a
variavel deixa o desfecho quebrado, quem so arruma o desfecho deixa o vazamento.

Solucao: elegibilidade. 775 viraram 622, quase 20 por cento da coorte, e isso vai no fluxograma.

**Sintoma generalizavel**: desfecho com janela de tempo ("obito em N dias", "readmissao em 30
dias") sobre coorte com seguimento variavel.

## Caso 3: a metrica que nao e a que importa

`cross_val_score(modelo, X, y, cv=5)` sem `scoring`. O default e acuracia. Num desfecho com 4.5
por cento de evento, a busca de hiperparametros encontrou o modelo que acerta "todo mundo vive".

**Sintoma generalizavel**: qualquer otimizacao sem `scoring` explicito em desfecho raro.

## Caso 4: o limiar escolhido a mao

Limiares diferentes por modelo, 0.04 no Random Forest e 0.1 nos outros, escolhidos ate o numero
ficar bonito. Comparacao entre modelos em pontos de operacao diferentes nao compara nada.

Solucao: criterio unico declarado antes (sensibilidade minima de 80 por cento, por exemplo),
aplicado nas predicoes fora da amostra, um limiar por modelo porque as escalas de probabilidade
nao sao comparaveis entre eles.

**Armadilha de implementacao**: `roc_curve` devolve limiares decrescentes e `tpr` crescente.
O primeiro indice que satisfaz `tpr >= alvo` e o limiar mais alto que serve. Pegar o ultimo
devolve sensibilidade 1 e especificidade 0, que passa despercebido porque a sensibilidade fica
otima.

## Caso 5: confusao por indicacao e tempo imortal

**Experimento**: melhor momento para a cirurgia de troca de valva.

Duas armadilhas que apontam em direcoes opostas, e por isso o efeito liquido e imprevisivel:

- **Confusao por indicacao**: opera-se cedo quem esta instavel. "Cirurgia precoce" carrega a
  gravidade que motivou a pressa, e o modelo ingenuo conclui que operar tarde e melhor.
- **Tempo imortal**: para ser operado no dia 20 e preciso sobreviver 20 dias sem operar. O grupo
  tardio e composto de sobreviventes por construcao, o que faz a cirurgia tardia parecer segura.

Um SHAP dependence plot sobre a variavel de tempo mistura os dois e nao separa nenhum.

Solucoes, em ordem de rigor:

1. **G-computacao**: com o modelo de desfecho, predizer o risco de cada paciente em cada valor
   hipotetico do tempo e tirar a media sobre a coorte. Da a curva risco versus dia padronizada
   pelos confundidores medidos. E o substituto correto do SHAP dependence plot.
2. **Analise landmark**: no dia L, restringir a quem esta vivo e ainda nao operado, e comparar
   quem operou na janela seguinte contra quem nao operou. O tempo imortal some por construcao.
3. **Restricao por indicacao**: comparar so entre quem tinha indicacao cirurgica, porque o
   contraste com quem nunca teve indicacao nao responde a pergunta.

Nenhuma delas remove confusao nao medida. Isso vai nas ressalvas, escrito.

## Checklist rapido

Antes de treinar qualquer coisa:

- [ ] O momento da predicao esta escrito por extenso.
- [ ] Toda coluna removida tem o motivo registrado numa tabela.
- [ ] Toda coluna mantida que parece suspeita tem a justificativa escrita.
- [ ] Quem nao teve o evento foi observado o suficiente para saber disso.
- [ ] Nenhuma candidata tem AUC univariada acima de 0.80 sem explicacao.
- [ ] A metrica de otimizacao esta declarada e nao e acuracia em desfecho raro.
- [ ] Se o desfecho depende de tempo, o desenho lida com tempo imortal.
