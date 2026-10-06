# STARD-AI, CLAIM e DECIDE-AI

Os três cobrem IA diagnóstica em fases diferentes: **STARD-AI** para acurácia contra um
padrão de referência, **CLAIM** para modelos de imagem, **DECIDE-AI** para a primeira
avaliação clínica ao vivo, com humano no loop.

---

## STARD-AI

**Sounderajah V et al. Nat Med 2025;31(10):3283-3289.** doi:10.1038/s41591-025-03953-8.
Extensão do STARD 2015 para estudos de acurácia diagnóstica centrados em IA. Consenso
Delphi com mais de 240 participantes. Ênfase declarada em descrição transparente do
conjunto de dados, validação rigorosa, e consideração explícita de viés, generalização e
equidade.

Usar quando o objeto é **acurácia contra um padrão de referência**, sensibilidade,
especificidade, VPP, VPN, e não risco predito. Se o modelo produz probabilidade de um
evento futuro, o guideline é TRIPOD+AI.

### O que o Methods precisa carregar

- **Padrão de referência**, o que é, como foi aplicado, por quem, e se foi aplicado a
  todos os participantes independentemente do resultado do índice. Verificação parcial ou
  diferencial precisa ser declarada e quantificada.
- **Cegamento**, quem leu o índice sabia o resultado da referência, e vice-versa.
- **Teste índice**, versão do modelo, congelamento dos pesos antes do teste, limiar
  pré-especificado ou derivado, e em que dado foi derivado.
- **Dados**, proveniência de cada conjunto, período, equipamentos e sítios, e o que
  separa treino, ajuste e teste. Sobreposição de pacientes entre conjuntos é falha grave.
- **Amostragem**, consecutiva, aleatória ou por conveniência. Coorte enriquecida muda a
  prevalência e portanto os valores preditivos: dizer e discutir.
- **Comparador humano**, quando o estudo alega equivalência ou superioridade a
  clínicos: quantos, experiência, condições de leitura, e se leram o mesmo material.
- **Casos indeterminados, falhas e exclusões técnicas**, quantos e como entraram no
  denominador. Excluir imagem de má qualidade infla a acurácia.
- **Subgrupos**, desempenho estratificado, com atenção a equipamento, sítio e
  características demográficas.

### Results

Tabela 2×2 completa, sensibilidade e especificidade com IC, prevalência na amostra e a
prevalência esperada em uso, valores preditivos calculados na prevalência de uso.
Diagrama de fluxo dos participantes.

---

## CLAIM

Checklist para modelos de IA em **imagem** médica. Usar como camada adicional sobre
TRIPOD+AI (se o modelo é preditivo) ou STARD-AI (se é acurácia). Sozinho, cobre pouco do
desenho clínico.

O que o CLAIM acrescenta e os outros não cobrem com esse detalhe:

- **Aquisição**, modalidade, equipamento, fabricante, parâmetros de aquisição, protocolo,
  uso de contraste, e a variação disso entre sítios.
- **Pré-processamento**, reamostragem, normalização de intensidade, registro,
  segmentação, recorte, e se algum passo usou informação do desfecho.
- **Ground truth**, como foi estabelecido: leitor único, consenso, adjudicação,
  patologia, seguimento. Número de anotadores, qualificação, e concordância entre eles.
- **Aumento de dados**, quais transformações, aplicadas a que conjunto.
- **Arquitetura**, camadas, pesos pré-treinados e de onde vieram, transfer learning.
- **Interpretabilidade**, mapas de saliência quando apresentados: como foram gerados e
  qual sua limitação declarada. Mapa de saliência não é explicação de mecanismo.

---

## DECIDE-AI

**Vasey B et al. Nat Med 2022;28:924-933.** Reporte da **avaliação clínica em estágio
inicial** de sistemas de apoio à decisão movidos a IA, a fase entre a validação offline e
o ensaio randomizado. Se o estudo tem clínico usando o sistema em pacientes reais, o
guideline é este, mesmo que não seja randomizado.

Eixos que só o DECIDE-AI cobre:

- **Interação humano-IA**, como o resultado é apresentado, em que ponto do fluxo, e o
  que o clínico pode fazer com ele. Concordância entre clínico e sistema, e o que aconteceu
  nas discordâncias.
- **Treinamento dos usuários**, o que receberam antes de usar, e por quanto tempo usaram.
- **Modificações durante o estudo**, o sistema mudou no meio? Ajuste de limiar, retreino,
  mudança de interface. Declarar e datar.
- **Segurança**, eventos adversos, quase-erros, uso indevido, e o mecanismo de
  monitoramento.
- **Fatores humanos**, carga de trabalho, confiança, automation bias, tempo por caso.
- **Implementação**, integração ao sistema de informação, latência, falhas técnicas e
  indisponibilidade.

DECIDE-AI é complementar, não substituto: o modelo por trás continua devendo TRIPOD+AI ou
STARD-AI.
