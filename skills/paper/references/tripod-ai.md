# TRIPOD+AI e TRIPOD-LLM

**TRIPOD+AI**, Collins GS et al. BMJ 2024;385:e078378. doi:10.1136/bmj-2023-078378.
Checklist de 27 itens. Substitui o TRIPOD 2015, que não deve mais ser usado. Vale para
modelos de diagnóstico, prognóstico, monitoramento ou rastreio, com regressão **ou**
machine learning, em qualquer domínio clínico. Há um checklist separado para abstracts.

**TRIPOD-LLM**, Gallifant J et al. Nat Med 2025. Extensão para estudos que desenvolvem,
ajustam (fine-tuning, prompting) ou avaliam modelos de linguagem em saúde.

Checklist oficial: tripod-statement.org e equator-network.org. Buscar a redação e a
numeração oficiais na fonte antes de montar a tabela que vai ao journal, o que segue é
a substância organizada por seção do manuscrito, para escrever e auditar.

---

## Título e abstract

**Título**, precisa deixar explícito que é estudo de modelo de predição, dizer se é
desenvolvimento, validação ou ambos, nomear o desfecho predito e a população-alvo.
Se usou IA/ML, dizer. Título que esconde o desenho atrasa a triagem editorial.

**Abstract**, checklist próprio. Cobrir: objetivo; fonte dos dados e desenho; população
e critérios; desfecho e janela; preditores; método de modelagem; tamanho amostral e
**número de eventos**; tipo de validação (interna, externa temporal, externa geográfica);
**discriminação e calibração, ambas com medida de incerteza**; disponibilidade de dados
e código; e a conclusão limitada ao que os dados suportam.

Abstract que reporta só AUROC é o erro mais frequente da área e sinaliza ao revisor que
a calibração não foi olhada.

---

## Introduction

- **Contexto e justificativa**, por que o modelo é necessário: o problema clínico, a
  decisão que ele apoiaria, e os modelos que já existem para esse desfecho nessa
  população, com o que eles deixam em aberto. Lacuna afirmada sem nomear o que existe é
  lacuna não demonstrada.
- **Objetivos**, desenvolvimento, validação, ou atualização/extensão de modelo
  existente. Dizer qual, explicitamente.

## Methods

### Fonte de dados e desenho
Desenho (coorte, caso-controle aninhado, registro, dados de rotina/EHR), origem, período
de coleta, e se dados de desenvolvimento e validação vieram de fontes distintas. Dados de
rotina exigem dizer para que foram coletados originalmente e o que isso introduz.

### Participantes
Cenário (atenção primária, hospitalar, UTI), critérios de elegibilidade, e o **momento
zero**, em que ponto do cuidado o modelo seria aplicado. Momento zero mal definido é a
principal fonte de vazamento temporal.

### Desfecho
Definição, como foi determinado e por quem, se a determinação foi cega aos preditores,
janela de predição, e se houve mais de uma definição candidata.

### Preditores
Definição de cada um, como e quando foram medidos, disponibilidade no momento zero, e se
a medição foi cega ao desfecho. Preditor que só existe depois do desfecho não é preditor.

### Tamanho amostral
Como foi determinado. Para modelo preditivo, justificar pelas fórmulas de Riley et al.,
não por regra de dedo de 10 EPV. Se a amostra é a que havia, dizer isso e reportar o
poder efetivo, omitir a justificativa é item incompleto.

### Dados faltantes
Quantidade por variável, mecanismo assumido, e como foram tratados. Imputação múltipla
exige dizer o número de imputações, o modelo de imputação, se o desfecho entrou nele, e
como as estimativas foram combinadas. Análise de casos completos exige justificar.

### Métodos analíticos
Tipo de modelo e por quê; pré-processamento; seleção de variáveis e em que ponto (dentro
ou fora do loop de validação); regularização; hiperparâmetros e espaço de busca;
**tratamento de desbalanceamento de classes**, e, se houve reamostragem, o efeito sobre
a calibração e como foi corrigido; procedimento de validação interna (bootstrap com
correção de otimismo, validação cruzada aninhada) e o que exatamente foi reamostrado.

### Equidade e subgrupos
Como a população foi definida e representada; quais subgrupos foram pré-especificados;
como diferenças de desempenho entre grupos foram avaliadas. Ver `metricas.md`.

### Saída do modelo
O que o modelo produz (probabilidade, escore, classe), e se houve limiar, qual, como foi
escolhido, e sob que custo relativo de erro.

### Medidas de desempenho
Quais foram calculadas e por quê, com incerteza. Discriminação e calibração são ambas
obrigatórias. Utilidade clínica (decision curve analysis) é o que separa um manuscrito
competente de um que responde "e daí?".

### Ciência aberta
Financiamento, conflitos, protocolo e registro (se houver), disponibilidade de dados,
disponibilidade de **código**, e disponibilidade do modelo em si, TRIPOD+AI cobra os
três separadamente. "Disponível mediante solicitação razoável" é aceito por poucos
journals e por nenhum revisor metodológico.

### Envolvimento de pacientes e público
Se houve, como. Se não houve, dizer. Item novo no TRIPOD+AI, frequentemente esquecido.

## Results

- **Fluxo de participantes**, número elegível, incluído, excluído e por quê. Diagrama
  de fluxo.
- **Características**, demográficas e clínicas, dados faltantes por variável, e
  **número de eventos**. Comparar desenvolvimento vs validação lado a lado.
- **Especificação do modelo**, o que permite outra pessoa usar o modelo: coeficientes e
  intercepto para regressão; para ML, arquitetura, hiperparâmetros finais e o artefato ou
  o caminho para ele. Modelo não especificado é modelo não reprodutível, e o item cobra
  isso independentemente do método.
- **Desempenho**, com IC. Calibração apresentada graficamente, não só como número.
- **Se houve atualização/extensão**, o que mudou e o desempenho antes e depois.

## Discussion

- **Interpretação**, o desempenho no contexto do objetivo e do que já existe. Comparar
  com os modelos nomeados na introdução.
- **Limitações**, desenho, dados, validação, generalização. Na voz ativa.
- **Usabilidade e implicações**, quem usaria, em que ponto do fluxo, o que ainda falta
  antes do uso clínico, e o que precisaria ser monitorado depois do desdobramento.

---

## TRIPOD-LLM: o que muda

Sobre o esqueleto acima, acrescentar:

- **Identificação do modelo**, nome, versão, data de acesso, provedor, se aberto ou
  proprietário. Modelo proprietário muda entre versões: sem data e versão o estudo não é
  reproduzível.
- **Prompt e configuração**, prompts na íntegra (anexo), estratégia (zero/few-shot,
  chain-of-thought, RAG), temperatura e demais parâmetros de decodificação, e se houve
  fine-tuning, com quais dados.
- **Não determinismo**, número de execuções por item e como a variabilidade entre
  execuções foi reportada. Resultado de execução única precisa ser declarado como tal.
- **Contaminação de dados**, se o benchmark ou os casos podem ter estado no treino, e
  como isso foi endereçado.
- **Avaliação humana**, quem avaliou, qualificação, rubrica, cegamento, concordância
  entre avaliadores.
- **Segurança**, alucinação, recusa, dano potencial, e como foram medidos.
- **Custo e latência**, quando o estudo faz alegação de viabilidade operacional.
