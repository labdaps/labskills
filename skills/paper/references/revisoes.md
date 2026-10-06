# PRISMA 2020, AMSTAR 2 e CHARMS

**PRISMA 2020**, Page MJ et al. BMJ 2021;372:n71. Checklist de 27 itens para relato de
revisões sistemáticas e meta-análises, mais o PRISMA para abstracts e o novo fluxograma.
Substitui o PRISMA 2009.

**AMSTAR 2**, Shea BJ et al. BMJ 2017;358:j4008. Ferramenta de **avaliação** da qualidade
de revisões sistemáticas. Não é guideline de relato: serve para julgar uma RS alheia (ou
antecipar como a sua será julgada). Tem 16 itens, 7 deles **críticos**, falha em item
crítico derruba a confiança geral independentemente do resto.

**CHARMS**, Moons KGM et al. PLoS Med 2014. Lista de extração de dados para revisões
sistemáticas **de modelos preditivos**. Combinar: PRISMA 2020 para o relato, CHARMS para
a extração, PROBAST+AI para o risco de viés por modelo.

Checklists oficiais: prisma-statement.org e equator-network.org.

---

## PRISMA 2020: o que a skill cobra por seção

### Título e abstract
Identificar como revisão sistemática no título. Abstract seguindo o checklist próprio
(PRISMA 2020 for Abstracts).

### Introdução
Racional à luz do que já se sabe, e objetivos ou perguntas explicitados em PICO (ou PIRD,
para acurácia; ou população/desfecho/modelo, para RS de modelos preditivos).

### Métodos

- **Critérios de elegibilidade** e como os estudos foram agrupados nas sínteses.
- **Fontes de informação**, cada base, plataforma e a **data da última busca**. Buscas
  manuais, listas de referências, preprints e literatura cinzenta declaradas.
- **Estratégia de busca completa**, para cada base, reproduzível, não "termos MeSH
  relacionados a X". Vai em anexo, na íntegra.
- **Seleção**, quantos revisores, independentes ou não, como as discordâncias foram
  resolvidas, e se houve ferramenta de automação.
- **Extração**, mesma coisa, mais a lista de variáveis extraídas e as suposições feitas
  sobre dados ausentes ou pouco claros.
- **Risco de viés**, ferramenta usada, quantos avaliadores, e o processo.
- **Medidas de efeito** e **métodos de síntese**, modelo, estimador de heterogeneidade,
  como a heterogeneidade foi explorada, subgrupos e metarregressão pré-especificados.
  Se a síntese foi narrativa, dizer por que e como foi estruturada.
- **Viés de relato** entre estudos e **avaliação da certeza** (GRADE, quando aplicável).
- **Registro e protocolo**, PROSPERO ou equivalente, número, e qualquer desvio do
  protocolo com justificativa. Revisão não registrada precisa dizer que não foi.

### Resultados
Fluxograma PRISMA 2020 com os números de cada etapa, incluindo registros removidos por
automação; características dos estudos incluídos; risco de viés por estudo; resultados de
cada síntese com IC e medida de heterogeneidade; e os estudos excluídos na leitura de
texto completo, **listados com o motivo**.

### Discussão
Interpretação no contexto da evidência, limitações da evidência e do processo de revisão,
e implicações para prática e pesquisa.

### Outras informações
Financiamento, conflitos, e disponibilidade de dados, código e material da revisão.

---

## AMSTAR 2: os itens críticos

São os que derrubam a revisão. Ao escrever uma RS, garantir estes:

1. **Protocolo registrado a priori**, com desvios justificados.
2. **Busca adequada**, pelo menos duas bases, estratégia completa, restrições
   justificadas, busca recente.
3. **Justificativa das exclusões**, lista de estudos excluídos em texto completo com
   motivo.
4. **Risco de viés avaliado adequadamente** nos estudos individuais.
5. **Métodos de meta-análise apropriados** ao dado combinado.
6. **Risco de viés considerado na interpretação** dos resultados.
7. **Viés de publicação investigado** e discutido.

Os outros nove itens (PICO explícito, seleção e extração em duplicata, características
dos estudos, fontes de financiamento dos incluídos, heterogeneidade explicada, conflitos
dos autores da revisão) são não críticos, mas contam para o julgamento global.

---

## RS de modelos preditivos: combinação

Ordem prática:

1. PRISMA 2020 estrutura o manuscrito.
2. CHARMS define o que extrair de cada modelo: fonte de dados, participantes, desfecho,
   preditores candidatos e finais, tamanho amostral e eventos, dados faltantes, método de
   modelagem, desempenho (discriminação **e** calibração), validação, e resultados de
   interpretação.
3. PROBAST+AI julga cada modelo, parte de desenvolvimento ou de avaliação conforme o
   caso.

Reportar calibração é onde essas revisões mais encontram ausência: se a maioria dos
estudos incluídos não a reporta, isso é achado, não nota de rodapé.
