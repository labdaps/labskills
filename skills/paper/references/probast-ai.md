# PROBAST+AI

**Moons KGM et al. BMJ 2025;388:e082505.** doi:10.1136/bmj-2024-082505. Atualiza o
PROBAST 2019. Vale para modelos com regressão ou IA/ML.

Mudança estrutural em relação ao PROBAST original: **duas partes distintas**.

- **Desenvolvimento de modelo**, 16 questões-sinalizadoras. Avalia **qualidade e
  aplicabilidade**, não risco de viés. A lógica é que um modelo em desenvolvimento não
  tem "viés" contra uma verdade externa: tem qualidade metodológica boa ou ruim.
- **Avaliação de modelo** (validação, teste de desempenho), 18 questões-sinalizadoras.
  Avalia **risco de viés e aplicabilidade**.

Escolher a parte certa antes de aplicar. Manuscrito que desenvolve **e** valida usa as
duas, separadamente.

Redação e numeração oficiais das questões: buscar no artigo do BMJ ou em
probast.org / equator-network.org. O que segue é o que a skill usa para antecipar onde um
avaliador marcaria problema.

---

## Uso dentro da /paper

O PROBAST+AI não é guideline de reporte, é ferramenta de avaliação. Serve aqui em dois
momentos:

1. **Escrevendo** (`/paper full`, `/paper draft`): antecipar o julgamento. Cada domínio
   abaixo aponta o que o Methods precisa dizer para não ser marcado como alto risco.
2. **Auditando** (`/paper check`): rodar como segundo eixo, depois do checklist de
   reporte. Reporte completo e metodologia frágil é rejeição diferente de reporte
   incompleto, vale separar as duas críticas.

---

## Domínio 1: Participantes

Alto risco quando: a fonte de dados não corresponde à população-alvo do uso pretendido;
inclusão ou exclusão introduz seleção relacionada ao desfecho; dados de rotina usados sem
discutir o processo que gerou o registro; caso-controle usado para estimar risco absoluto
sem correção do intercepto.

O que escrever para evitar: cenário, elegibilidade, momento zero, e por que essa
população representa quem usaria o modelo.

## Domínio 2: Preditores

Alto risco quando: preditor não estaria disponível no momento de uso; medição do preditor
influenciada pelo conhecimento do desfecho; definição do preditor difere entre
desenvolvimento e validação; vazamento por variável proxy do desfecho (código de
faturamento, prescrição posterior, contagem de exames).

Vazamento é o achado mais comum em modelo sobre dados de EHR e o mais fácil de esconder
sem querer. Se há qualquer variável derivada de evento posterior ao momento zero, dizer
como foi tratada.

## Domínio 3: Desfecho

Alto risco quando: definição do desfecho não é a mesma para todos os participantes;
determinação do desfecho usou informação do preditor (circularidade); intervalo entre
preditor e desfecho inadequado ou variável sem justificativa; desfecho definido por
consenso sem medida de concordância.

## Domínio 4: Análise

O domínio mais denso e onde a maioria dos modelos de ML é marcada. Alto risco quando:

- número de eventos insuficiente para a complexidade do modelo, sem cálculo amostral;
- dados faltantes tratados por exclusão ou imputação simples sem justificativa;
- seleção de variáveis feita **fora** do loop de validação (usando o conjunto inteiro);
- qualquer decisão, imputação, seleção, escalonamento, tuning, reamostragem, ajustada
  antes da partição, contaminando a estimativa;
- otimismo do desenvolvimento não corrigido (sem bootstrap, sem CV aninhada);
- **calibração não avaliada**, este isolado costuma bastar para alto risco;
- desbalanceamento tratado com reamostragem sem recalibrar a saída;
- limiar escolhido no mesmo conjunto em que o desempenho é reportado;
- complexidade do modelo não justificada frente a um comparador simples;
- ausência de comparador (modelo simples ou escore clínico existente) quando havia um
  disponível.

## Aplicabilidade

Julgar separadamente do viés: mesmo um estudo impecável pode não se aplicar à pergunta.
Verificar se população, preditores e desfecho do estudo correspondem ao contexto de uso
pretendido, e, no caso de modelo desenvolvido em outro sistema de saúde, se as diferenças
de prevalência e de fluxo assistencial foram discutidas.

---

## Saída esperada no `/paper check`

Para cada domínio: julgamento (baixo / alto / pouco claro), a evidência no manuscrito, e
**a frase que muda o julgamento**, o que precisa ser acrescentado ou reanalisado. Domínio
"pouco claro" quase sempre é problema de reporte, não de método: nesse caso, dizer que é
resolvível escrevendo, e o que escrever.
