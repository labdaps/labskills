# Como escrever cada seção

Ler sempre, em qualquer sub-comando que produza texto.

Princípio geral: o manuscrito é um argumento, não um relatório de atividades. Cada seção
tem uma função no argumento, e texto que não cumpre a função da sua seção enfraquece o
todo mesmo estando correto.

**Registro.** Voz ativa, primeira pessoa do plural onde couber ("nós desenvolvemos" e não
"foi desenvolvido"), a maioria dos journals biomédicos hoje prefere e é mais honesto
sobre quem decidiu o quê. Tempo verbal: passado para o que foi feito e encontrado,
presente para o que é conhecido e para o que os resultados significam. Frases curtas.
Sem advérbio de ênfase ("notavelmente", "surpreendentemente"), o dado carrega a ênfase.

**O que nunca escrever:** "para o melhor do nosso conhecimento, o primeiro estudo a..."
(quase sempre falso e sempre irrelevante); "resultados promissores"; "mais estudos são
necessários" sem dizer quais; "o modelo demonstrou excelente desempenho" com AUROC de
0,78; qualquer superlativo sem comparador.

---

## Título

Uma linha, declarativa ou descritiva. Precisa conter: desenho, desfecho, população, e o
método quando ele é o ponto. Título com achado ("Modelo de aprendizado de máquina supera
o escore de Framingham...") é aceito por poucos journals e cobra evidência forte.

Preparar também: **running title** (≤ 50 caracteres, o journal pede) e 3 a 6
**palavras-chave**, preferindo termos MeSH.

## Abstract

Estruturado, no formato do journal-alvo. Escrever **por último**. O abstract é o que 95%
dos leitores lerão inteiro, então ele carrega o número principal, não a promessa.
Cobrir o checklist de abstracts do guideline (ver o arquivo do guideline). Nada entra no
abstract que não esteja no corpo.

## Introduction

Três a quatro parágrafos. A estrutura que funciona:

1. **O problema clínico**, magnitude e consequência da decisão, com dado e referência.
2. **O que já existe**, os modelos, escores ou práticas atuais, nomeados. Não "vários
   estudos exploraram": dizer quais e o que fizeram.
3. **A lacuna**, o que especificamente falta, decorrendo do parágrafo anterior. A lacuna
   precisa ser consequência do que foi dito, não uma asserção nova.
4. **O objetivo**, uma ou duas frases, no mesmo vocabulário que os resultados usarão.

Não antecipar resultados na introdução (salvo se o journal pedir). Não fazer revisão de
literatura extensa: isso é outro tipo de artigo.

## Methods

A seção que decide se o manuscrito sobrevive à revisão metodológica. Critério de
suficiência: **um pesquisador competente, com acesso aos mesmos dados, reproduziria o
estudo lendo só esta seção.** Se não, falta algo.

Ordem que funciona para modelo preditivo: desenho e fonte de dados → participantes e
momento zero → desfecho → preditores → tamanho amostral → dados faltantes → modelagem →
validação → medidas de desempenho → análise de subgrupos e equidade → ética e ciência
aberta.

Escrever no passado, com decisões atribuídas ("optamos por..., porque..."). Toda escolha
metodológica não óbvia leva a razão junto, é isso que impede o revisor de assumir que foi
arbitrária. Detalhe que não cabe vai para material suplementar, com referência cruzada
explícita.

## Results

Segue a ordem do Methods. Sem interpretação, interpretação é a Discussion, e misturar as
duas é o modo mais fácil de parecer que o dado diz mais do que diz.

- Começar pelo fluxo de participantes e pelas características da amostra.
- Todo número com medida de incerteza. Todo percentual com o denominador.
- Não repetir na prosa o que a tabela já mostra: o texto destaca o padrão, a tabela
  carrega os valores.
- Resultado negativo ou pior que o esperado entra com o mesmo destaque do positivo.
- Análises não pré-especificadas são declaradas como exploratórias, no lugar onde
  aparecem.

## Discussion

Cinco movimentos, nesta ordem:

1. **Achado principal** em uma ou duas frases, sem repetir números já dados.
2. **Comparação com a literatura**, com os trabalhos nomeados na introdução. Onde
  converge, onde diverge, e a hipótese para a divergência.
3. **Explicação**, por que o resultado saiu assim. Mecanismo clínico, propriedade do
  dado, característica do método.
4. **Limitações**, de desenho, de dado, de validação, de generalização. Cada uma com a
  direção provável do efeito ("o que provavelmente infla ou desinfla nossa estimativa").
  Limitação sem direção é limitação decorativa. Não terminar a lista com uma frase que
  neutralize tudo.
5. **Implicações**, o que muda para quem, e o que precisaria acontecer antes do uso.
  Concreto: qual validação, em qual população, com qual monitoramento.

Conclusão de um parágrafo, limitada ao que os dados suportam, sem CTA e sem "mais
pesquisas são necessárias" genérico.

## Declarações

Bloco padrão a incluir sempre, ajustando ao journal:

- Contribuições dos autores (CRediT)
- Financiamento, com número do processo
- Conflitos de interesse (todos os autores, ou declarar ausência)
- Aprovação ética, nome do comitê e **número do parecer**; consentimento ou dispensa
- Disponibilidade de dados, onde, sob que condição, ou por que não
- Disponibilidade de código, repositório e versão, ou por que não
- Disponibilidade do modelo, separada das duas anteriores
- **Uso de IA**, no padrão ICMJE: qual ferramenta, para quê, e que os autores revisaram
  e assumem responsabilidade pelo conteúdo. A ferramenta não é autora.
- Agradecimentos

## Tabelas e figuras

- Tabela 1: características da amostra, com dados faltantes por variável e número de
  eventos. Desenvolvimento e validação lado a lado quando houver ambos.
- Toda tabela e figura autoexplicativa: legenda que permite entender sem o corpo do texto,
  todas as siglas expandidas no rodapé, unidades declaradas.
- Legendas de tabela acima da tabela; legendas de figura ao final do manuscrito, na seção
  própria, com as figuras em arquivo separado (o padrão da maioria dos journals).
- Figura de calibração é obrigatória em manuscrito de modelo preditivo. Ver
  `metricas.md`. Para gerar no padrão editorial, usar `/paper-png`.

## Referências

Vancouver numerada por ordem de aparição, salvo instrução do journal. Toda referência com
DOI ou PMID verificado, ver a regra de integridade 2 no SKILL.md. Preferir fonte
primária: se a afirmação vem de uma revisão, citar a revisão pelo que ela é, não o estudo
que ela cita e que não foi lido.
