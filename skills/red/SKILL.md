---
name: red
description: >
  Revisa criticamente qualquer documento (proposta, contrato, lista de perguntas a fornecedor,
  protocolo, projeto, política, texto institucional), aponta o que falta, o que está frágil e
  o que está internamente inconsistente, e devolve o MESMO documento em .docx com as sugestões
  inseridas em vermelho no ponto exato de cada seção. Use SEMPRE que o usuário pedir "/red",
  "revisa esse documento", "revisa e marca em vermelho", "aponta as sugestões no documento",
  "vê se falta algo nesse doc", "critica esse documento", "marca as alterações", "revisa esse
  contrato/proposta/protocolo", "o que falta nesse documento", "faz a revisão crítica disso", 
  mesmo informal e mesmo sem dizer "vermelho". Também acionar quando anexar um documento e
  pedir opinião ou conferência antes de enviar a terceiros. O texto original NUNCA é alterado:
  as sugestões são aditivas. NÃO confundir com /peer-review (nota e decisão editorial sobre o manuscrito)
  nem /paper-review (leitura crítica de artigo alheio).
---

# Skill: /red: Revisão crítica com marcação em vermelho

Entrega dois produtos ao mesmo tempo: o **documento marcado** (.docx com as sugestões
em vermelho, prontas para o autor aceitar ou descartar) e, no chat, os **três a seis
achados que realmente mudam a decisão**.

O valor da skill não está na marcação, está na qualidade da crítica. Marcação bonita
com sugestões genéricas ("considerar revisar este ponto") é pior do que não revisar,
porque consome a atenção do autor sem devolver nada.

---

## Princípios

1. **Nunca alterar o texto original.** Toda sugestão é aditiva. Se houver erro factual,
   aritmético ou de coerência no original, apontar em vermelho, nunca corrigir em
   silêncio. Quem decide o que entra é o autor.
2. **Cada sugestão precisa dizer o que incluir e por quê.** "Falta tratar X" não serve.
   O padrão é: a pergunta ou cláusula pronta para colar, seguida da razão pela qual ela
   importa naquele documento.
3. **Ancorar no ponto exato.** A sugestão vai logo depois do trecho que comenta, não
   numa lista no fim. O autor tem que ler a crítica junto com o que a motivou.
4. **Não inventar sugestão onde o documento está bom.** Seções sólidas passam sem
   marcação. Volume de vermelho não é métrica de qualidade.
5. **Assumir leitor sênior.** Sem preâmbulo, sem elogio de cortesia, sem repetir o que
   o documento já diz.

---

## Passo 1: Obter o documento

Verificar onde o conteúdo realmente está antes de decidir a rota:

- **Arquivo .docx disponível no disco** (anexado ou no projeto): rota preferida. Editar o
  `word/document.xml` do próprio arquivo com `"${CLAUDE_SKILL_DIR}/scripts/red_insert.py"`
  preserva estilos, numeração, cabeçalho, rodapé e classificação (INTERNO/CONFIDENCIAL).
- **Só o texto extraído está no contexto** (acontece: a pasta de uploads às vezes vem
  vazia) → reconstruir o documento com `docx` (npm) reproduzindo a estrutura fielmente
  e inserindo o vermelho. **Avisar o usuário** de que o original não chegou e que o
  arquivo é uma reconstrução, para ele não perder formatação sem saber.
- **PDF** → ler com a skill `pdf-reading` e entregar a revisão em .docx.
- **Texto colado no chat** → mesma coisa, entrega em .docx.

Confirmar o tipo de documento e o destinatário quando não estiver óbvio. Uma lista de
perguntas para um fornecedor, um protocolo assistencial e um artigo científico pedem
lentes diferentes.

---

## Passo 2: A revisão

Ler o documento inteiro antes de escrever qualquer sugestão. Rodar estes eixos:

**1. Lacunas.** O que um documento maduro desse tipo teria e este não tem. É de longe
o eixo mais valioso e o mais fácil de pular.

**2. Consistência interna.** Conferir a aritmética e os números do próprio documento:
múltiplos que não batem, metas que contradizem o que a proposta anexa oferece, unidades
trocadas, prazos incompatíveis entre seções, referências cruzadas a itens inexistentes.
Achado desse tipo costuma ser o mais útil da revisão inteira.

**3. Definições operacionais.** Toda meta, indicador ou critério precisa ser mensurável
sem ambiguidade: qual percentil, qual janela, qual amostra, medido por quem, com qual
rubrica, e o que acontece se não for atingido. Meta sem definição operacional vira
disputa no fechamento.

**4. Baselines móveis.** Se o documento compara contra uma referência que está mudando,
exigir que a versão e a data da referência sejam congeladas por escrito.

**5. Estratificação.** Resultado agregado dentro da meta pode esconder falha sistemática
num subgrupo (região, sotaque, faixa etária, unidade, especialidade, turno). Onde houver
métrica agregada, sugerir o recorte.

**6. Regulatório, jurídico e de responsabilidade.** Costuma ser o bloco inteiramente
ausente. Enquadramento (ANVISA/SaMD, CFM, LGPD, guarda de prontuário), alocação de
responsabilidade, trilha de auditoria que torne a responsabilidade apurável, seguro,
saída e continuidade.

**7. Higiene de negociação e de comunicação.** Ordem de revelação de informação, o que o
documento entrega ao outro lado antes da hora, o que deve ficar registrado em ata, e
qual contra-argumento previsível precisa de resposta pronta.

### Lentes por tipo de documento

- **Proposta comercial / contrato / avaliação de fornecedor:** dados e privacidade,
  suboperadores, SLA com consequência, definição do que é faturável, reajuste e teto,
  mudança de controle, solidez do fornecedor, propriedade intelectual, plano de saída.
- **Documento técnico ou de produto:** premissas não declaradas, modo de falha,
  degradação, dependências externas, versionamento, o que acontece quando o componente
  crítico cai.
- **Documento clínico ou assistencial:** população de aplicação, critérios de exclusão,
  sinais de alarme, quem valida, o que fazer quando o protocolo não se aplica,
  rastreabilidade da decisão.
- **Projeto de pesquisa, submissão a edital, paper:** desenho, tamanho de amostra e
  poder, viés de seleção, comparador, desfecho primário definido antes, plano de
  análise, conflito de interesse, o que os avaliadores vão atacar primeiro.
- **Comunicação institucional:** o que uma leitura hostil extrai da frase, o que fica
  implícito e não deveria, e o que promete mais do que se pode entregar.

---

## Passo 3: Marcar

Padrão visual, em vermelho `C00000`:

- **Bloco de sugestões**, título em negrito com barra lateral vermelha
  (`Sugestões de inclusão, 1.1`, `Ajuste sugerido no racional de custo`) seguido dos
  itens. Usar quando há mais de uma sugestão para a mesma seção.
- **Nota inline**, parágrafo único começando com `Sugestão:`. Usar para um comentário
  pontual sobre um indicador ou uma frase específica.
- **Seção final**, quando houver observações que não pertencem a nenhuma seção
  (condução da reunião, ordem de revelação, o que registrar em ata), criar uma seção
  própria no fim, também em vermelho.
- Uma linha em itálico vermelho logo abaixo do título do documento avisando que o
  vermelho são sugestões.

Aplicar com o script:

```bash
python "${CLAUDE_SKILL_DIR}/scripts/red_insert.py" entrada.docx saida.docx --json sugestoes.json
```

O JSON é uma lista de inserções ancoradas em trechos literais do documento
(`anchor` + `title`/`bullets`, ou `anchor` + `note`, ou `at: "end"` para o bloco final).
O script aborta se a âncora casar com zero ou com mais de um parágrafo, nesse caso,
aumentar o trecho até ficar único. O cabeçalho do próprio script tem o formato completo.

Quando o documento tiver que ser reconstruído (original indisponível), montar direto com
`docx` (npm): cor `C00000`, borda esquerda vermelha nos títulos de bloco, mesma
hierarquia de headings do original.

**Se o usuário pedir explicitamente controle de alterações / redline**, aí sim usar
`<w:ins>`/`<w:del>` (tracked changes do OOXML) com `--author` preenchido. O padrão desta skill é marcação em vermelho, não tracked changes: sugestão
de inclusão não é edição do texto alheio.

---

## Passo 4: Conferir antes de entregar

```bash
unzip -tq saida.docx                                    # o pacote OOXML continua íntegro
soffice --headless --convert-to pdf saida.docx          # precisa de LibreOffice (command -v soffice)
pdftoppm -jpeg -r 70 saida.pdf page
```

Abrir as imagens e olhar. Sem LibreOffice na máquina, não fingir que conferiu: entregar
dizendo que a inspeção visual não foi feita. Conferir que o vermelho está no lugar certo, que nada do
original sumiu e que a contagem de parágrafos só cresceu.

---

## Passo 5: Entregar

- Arquivo `<nome_original>_revisado.docx` ao lado do original, entregue com a ferramenta
  SendUserFile.
- No chat, **não repetir o documento**. Escrever os três a seis achados que mais mudam a
  decisão, agrupados por gravidade, cada um em uma ou duas linhas. Se houver um achado
  de consistência interna (número que não bate, meta que contradiz a proposta), ele vem
  primeiro.
- Se alguma sugestão for opinativa ou depender de informação que só o autor tem, dizer
  isso explicitamente em vez de afirmar com falsa confiança.

---

## Calibragem das sugestões

**Ruim:** "Sugestão: considerar incluir aspectos de segurança da informação."

**Bom:** "Sugestão: prazo contratual para comunicação de incidente de segurança
(sugestão: 24h), direito de auditoria e evidências vigentes (ISO 27001, SOC 2 Tipo II,
relatório de pentest)."

**Ruim:** "A meta de latência poderia ser melhor especificada."

**Bom:** "Sugestão: fechar a definição da métrica antes do piloto, qual percentil (p50,
p95 ou p99), medido sob carga de pico e com qual marco (primeiro token ou documento
completo). Uma média de 5s com p95 de 30s é inaceitável na emergência e passa
despercebida se a métrica não for especificada."

A diferença é sempre a mesma: a sugestão boa já está pronta para ser colada no
documento, e explica a consequência de não incluí-la.
