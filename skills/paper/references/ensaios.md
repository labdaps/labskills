# CONSORT-AI e SPIRIT-AI

**CONSORT-AI**, Liu X, Cruz Rivera S, Moher D, Calvert MJ, Denniston AK. Nat Med
2020;26:1364-1374. Extensão do CONSORT 2010 para **relato** de ensaios clínicos com
intervenção de IA.

**SPIRIT-AI**, Cruz Rivera S et al. Nat Med 2020;26:1351-1363. Extensão do SPIRIT 2013
para **protocolos** de ensaios com IA.

São o mesmo conjunto de preocupações em dois momentos: SPIRIT-AI antes, CONSORT-AI depois.
Escrever o protocolo com SPIRIT-AI facilita o CONSORT-AI, porque força as decisões que o
relato vai cobrar.

---

## Itens de extensão (o que se soma ao CONSORT/SPIRIT padrão)

### Título e abstract
Declarar que a intervenção envolve IA, e qual o tipo de modelo. Ensaio de IA que não diz
isso no título é difícil de encontrar em revisão sistemática.

### Introdução
O uso pretendido do sistema: qual decisão apoia, para qual população, em que ponto do
cuidado, e o que substitui ou acrescenta.

### Métodos: a intervenção

- **Versão do algoritmo**, congelada, e como ela seria identificada por terceiros.
- **Requisitos de entrada e saída**, que dado o sistema exige, em que formato, com que
  qualidade mínima, e o que ele devolve.
- **Cenário de integração**, onde roda, integrado a qual sistema, com que latência.
- **Perfil e treinamento dos usuários**, quem opera, que qualificação, que treinamento
  receberam antes do ensaio.
- **Interação humano-IA**, o output é mandatório, consultivo ou automático? O clínico
  pode sobrepor? Como isso é registrado?
- **Tratamento de entradas fora do escopo**, dado de má qualidade, populações não
  previstas, casos que o sistema recusa: o protocolo diz o que acontece.
- **Análise de erros do sistema**, falhas, indisponibilidade, e como foram registradas e
  analisadas. CONSORT-AI cobra isso como item próprio.
- **Acesso ao código e ao modelo**, nível de disponibilidade e a justificativa quando
  restrito.

### Métodos: desenho
Nada de específico de IA muda no essencial: randomização, alocação, cegamento (dizer quem
foi cego ao braço, o que é difícil quando o sistema é visível na tela), desfecho primário
pré-especificado, cálculo de tamanho amostral, plano de análise estatística e registro do
ensaio.

### Resultados
Fluxograma CONSORT; desempenho do sistema durante o ensaio, não só o desfecho clínico;
falhas e desvios; análise de subgrupos pré-especificada; eventos adversos, incluindo os
atribuíveis à interação com o sistema.

### Discussão
Generalização limitada ao cenário de integração testado. Um sistema validado num fluxo
não é validado em outro.

---

## Armadilhas frequentes

- **Comparador inadequado**, comparar IA + clínico contra clínico sem nada tende a medir
  o efeito de atenção adicional, não do modelo. Definir o cuidado usual com precisão.
- **Cegamento declarado sem ser possível**, se o clínico vê a saída do modelo, ele não é
  cego. Dizer isso e discutir o efeito.
- **Desfecho substituto**, mudança de conduta não é desfecho clínico. Se o primário é
  substituto, justificar e não concluir sobre desfecho duro.
- **Deriva durante o ensaio**, se o modelo ou o dado de entrada mudou ao longo do estudo,
  declarar.
