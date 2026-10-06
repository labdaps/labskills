# O que reportar de desempenho

Ler sempre que o manuscrito envolver um modelo.

Regra central: **discriminação sozinha não descreve um modelo clínico.** Um modelo pode
ordenar pacientes perfeitamente e, ainda assim, atribuir probabilidades erradas o
bastante para induzir a decisão errada em qualquer limiar. Manuscrito que reporta só
AUROC é o padrão da área e é o que o revisor metodológico corta primeiro.

Os três eixos, e todos os três entram: **discriminação, calibração, utilidade clínica.**

---

## 1. Discriminação

- **AUROC / c-statistic**, com IC95%. Método do IC declarado (DeLong, bootstrap).
- **AUPRC** quando o desfecho é raro, a AUROC é otimista sob desbalanceamento e a AUPRC
  depende da prevalência, então reportar a prevalência junto, sempre.
- Sensibilidade, especificidade, VPP e VPN **só fazem sentido com o limiar declarado** e
  o critério pela qual ele foi escolhido. VPP e VPN dependem da prevalência: se a coorte
  foi enriquecida, recalcular para a prevalência de uso.
- Não reportar acurácia global em desfecho desbalanceado.

## 2. Calibração

O eixo que decide se a probabilidade pode ser usada. Reportar, em ordem crescente de
informação (Van Calster et al. descrevem essa hierarquia):

- **Gráfico de calibração**, obrigatório. Curva suavizada (loess ou spline) com banda de
  incerteza, distribuição das probabilidades preditas ao longo do eixo (histograma ou
  rug), e a diagonal. Binning em decis esconde miscalibração local; se usar, usar junto
  com a curva suavizada, não no lugar dela.
- **Calibração no grande (intercepto de calibração)**, viés sistemático da média predita.
- **Slope de calibração**, 1,0 é o ideal; < 1 indica sobreajuste (predições extremas
  demais), > 1 indica encolhimento excessivo.
- **ICI / E-max / E-90**, erro absoluto médio e extremo entre predito e observado.
  Preferíveis ao **ECE**, que depende do binning e pode mascarar erro dentro do bin.
- **Brier score** e sua decomposição, quando útil como medida global.

Se houve reamostragem para desbalanceamento (SMOTE, undersampling) ou peso de classe, a
saída **está descalibrada por construção**: dizer isso e reportar a recalibração aplicada
(Platt, isotônica, ajuste do intercepto pela prevalência de base) e a calibração depois
dela. Este é um dos achados de revisão mais recorrentes em ML clínico.

## 3. Utilidade clínica

- **Decision curve analysis** (Vickers e Elkin), net benefit ao longo da faixa de limiares
  clinicamente plausíveis, contra "tratar todos" e "tratar nenhum" e contra o comparador
  existente. É o que responde "e daí?".
- Justificar a **faixa de limiares** pela decisão clínica real, não pela conveniência.
- Quando cabível: número de intervenções por evento evitado, e o custo relativo implícito
  do limiar escolhido.

---

## Validação: nomear pelo que é

- **Interna**, bootstrap com correção de otimismo, ou validação cruzada aninhada (com
  todo o pipeline, incluindo seleção de variáveis e tuning, dentro do loop). Divisão
  simples treino/teste no mesmo dado é validação interna fraca: chamar assim.
- **Interna-externa**, leave-one-cluster-out por sítio ou período, dentro do mesmo
  conjunto.
- **Externa temporal**, período posterior, mesma fonte.
- **Externa geográfica / institucional**, outra fonte, outra população.

Chamar de "validação externa" um hold-out aleatório do mesmo dado é o erro de nomenclatura
que mais rápido derruba a credibilidade do manuscrito. Se a validação é interna, o abstract
diz interna.

Reportar também: **otimismo** (diferença entre aparente e corrigido) e o desempenho na
validação externa lado a lado com o de desenvolvimento.

---

## Equidade e desempenho em subgrupos

Terreno de pesquisa do usuário, tratar com o rigor que ele espera, e não como parágrafo
de cortesia.

- **Pré-especificar** os subgrupos e dizer que foram pré-especificados. Subgrupo escolhido
  depois de ver o resultado é exploratório e se declara como tal.
- Reportar **discriminação e calibração dentro de cada subgrupo**, com IC e com o N e o
  número de eventos do subgrupo. Subgrupo pequeno gera IC largo: mostrar o IC impede
  conclusão sobre ruído.
- Nomear a métrica de equidade usada e o que ela assume: paridade demográfica,
  igualdade de oportunidade (TPR), odds equalizadas, **calibração dentro de grupos**, ou
  **multicalibração**. As definições são mutuamente incompatíveis sob prevalências
  distintas (resultado de impossibilidade): escolher, justificar pela decisão clínica, e
  declarar o trade-off. Manuscrito que reporta uma métrica de fairness sem dizer o que ela
  assume convida o revisor a apontar exatamente isso.
- Discutir a **origem** da disparidade encontrada: diferença de prevalência real,
  qualidade de medição desigual, viés de rótulo, sub-representação amostral. Cada uma pede
  mitigação diferente.
- Variável sensível usada como preditor, omitida, ou usada só na avaliação: dizer qual, e
  a razão. Omitir não neutraliza, os proxies permanecem.

---

## Tamanho amostral

Justificar pelas fórmulas de **Riley et al.** para modelos preditivos (critérios de
encolhimento, otimismo em R² e precisão do risco médio), não por "10 eventos por variável".
Reportar o número de eventos, o número de candidatos a preditor **antes** da seleção, e a
razão entre eles. Quando a amostra é a que existia, dizer isso e reportar a precisão
efetivamente alcançada, não simular um cálculo prospectivo que não houve.

## Incerteza

Todo ponto estimado com IC. Preferir IC a valor-p em desempenho de modelo. Comparação
entre modelos no mesmo dado exige teste pareado (bootstrap sobre a diferença), não
comparação de ICs sobrepostos.
