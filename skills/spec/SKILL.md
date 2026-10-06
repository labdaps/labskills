---
name: spec
description: Documenta um pipeline do laboratorio como especificacao legivel por quem nao escreveu o codigo, no espirito de spec driven development, e entrega o documento onde ele precisa chegar. Extrai o esqueleto do proprio codigo e do log da execucao, nunca de memoria, e transforma em texto que o colaborador consegue ler, defender numa banca e alterar para rodar de novo: cada regra, por que ela existe, o que quebra sem ela, o que foi testado, quais numeros sairam e o que nao se pode concluir. Termina publicando como artifact, gerando docx, versionando no repositorio ou redigindo o email, sempre mostrando o rascunho antes de enviar. Use SEMPRE que o usuario pedir "/spec", "documenta esse pipeline", "explica o passo a passo do que a gente fez", "escreve pra fulano entender", "manda um email explicando o experimento", "a orientanda precisa saber explicar isso", "faz a documentacao do experimento", "qual foi o spec desse codigo", "prepara isso pra banca", ou quando alguem for apresentar, defender ou reusar um pipeline que outra pessoa escreveu. Acionar PROATIVAMENTE ao terminar um experimento que outra pessoa vai precisar explicar.
---

# Skill: spec

Transforma um pipeline em documento que a pessoa que vai apresentar consegue defender.

O problema que ela resolve: o codigo roda, os numeros saem, e a pessoa que precisa explicar na
banca nao escreveu nenhuma linha. Ela sabe o resultado e nao sabe por que cada decisao foi
tomada, entao nao consegue responder "por que voce usou Boruta?" nem "por que 622 e nao 775?".

**Regra central: nada entra no documento que nao exista no codigo ou no log.** O esqueleto sai
do `extrair_spec.py`, que le o pipeline com o parser do Python e a saida da execucao. Se um
passo nao esta no codigo, ele nao vira paragrafo. Se um numero nao esta no log, ele nao vira
tabela. E o que impede o documento de descolar do pipeline na primeira alteracao.

**Segunda regra: o documento e escrito para quem vai apresentar, nao para quem escreveu.** Quem
escreveu ja sabe. O teste de qualidade e uma pergunta: se a banca perguntar "por que", a resposta
esta no documento?

## Fluxo

### 1. Extrair o esqueleto

```bash
python extrair_spec.py > spec_esqueleto.md      # na raiz do projeto
```

Sai de la, verificavel:

| bloco | de onde vem | para que serve no documento |
|---|---|---|
| etapas na ordem | cabecalhos das celulas markdown do `pipeline.py` | vira a espinha do passo a passo |
| parametros de decisao | constantes em caixa alta, com o comentario da linha | vira a tabela de regras, e e o que a pessoa pode mudar |
| regras em lista | `VAZAMENTO_*`, `LIMITES_PLAUSIVEIS`, `MANTIDAS_COM_JUSTIFICATIVA` | vira a secao de o que saiu e por que |
| pecas e o que resolvem | docstring de cada classe e funcao | vira a explicacao de cada etapa |
| execucao | `run.log`, erros e bloco RESUMO | e o lastro: prova que rodou e com que numeros |
| artefatos | `results/`, tabelas com contagem de linhas e figuras com legenda | vira a lista de evidencias |
| buracos | figura sem legenda, funcao sem docstring, log ausente | e a lista de o que corrigir ANTES de escrever |

Se o extrator apontar buraco, conserte no codigo primeiro. Documento que explica o que o codigo
nao faz e pior que documento nenhum.

### 2. Escolher o leitor

Antes de escrever, defina em uma linha quem le e o que essa pessoa precisa conseguir fazer
depois de ler. Muda tudo:

- **orientanda que vai defender**: precisa do porque de cada decisao e das ressalvas, com as
  frases prontas para responder a banca.
- **coautor clinico**: precisa do desenho, do que o numero significa clinicamente e do que nao
  se pode concluir. Nao precisa de nome de funcao.
- **revisor ou banca**: precisa do metodo reproduzivel, das premissas e das limitacoes.
- **outro pesquisador do lab que vai reusar**: precisa de como mudar e rodar de novo.

### 3. Escrever

Estrutura em `templates/spec_template.md`. As secoes que nunca saem:

1. **A pergunta e a decisao.** O que se prediz, para quem, em que momento, e que decisao clinica
   o resultado informa. Uma frase cada.
2. **As regras.** A tabela de parametros, cada um com o porque. Esta e a parte "spec": quem le
   consegue dizer "quero 10 repeticoes em vez de 5" e sabe exatamente o que muda.
3. **O passo a passo.** Uma secao por etapa, na ordem em que roda. Cada uma responde tres
   perguntas, nesta ordem: o que faz, por que existe, e **o que aconteceria sem ela**. A terceira
   e a que ensina, e e a que a banca pergunta.
4. **O que foi testado e como se sabe que funcionou.** Nao "foi validado", e sim qual verificacao
   rodou, o que ela teria pego, e o que ela nao pega. Bug encontrado no caminho entra aqui: e a
   prova de que a verificacao serve para alguma coisa.
5. **Os numeros.** Direto das tabelas de `results/`, com intervalo de confianca quando existir.
6. **O que nao se pode concluir.** Tamanho de amostra, ausencia de validacao externa, confusao
   residual, comparacao entre coortes diferentes. Escrito como frase que a pessoa pode falar.
7. **Como rodar de novo e como mudar.** Comandos e o que cada parametro faz.

Escreva em portugues direto, sem jargao que o leitor nao precise. Nome de funcao so aparece
quando a pessoa vai precisar procurar no arquivo.

### 4. Entregar

Escolha pelo destino, e pergunte se nao estiver claro:

| destino | como | quando |
|---|---|---|
| artifact HTML | carregue `artifact-design`, publique com `downloads` | leitura, compartilhar link, imprimir em PDF |
| `.docx` | skill `docx` | o leitor vai comentar e editar com controle de alteracoes |
| email | rascunho no chat, envio pela ferramenta de email que o usuario tiver | a pessoa precisa receber e responder |
| repositorio | `DOCUMENTACAO.md` na raiz | e o lastro do codigo, versionado junto |

**Email nunca sai sem confirmacao.** Mostre o rascunho inteiro, com destinatario e assunto, e
espere o "pode mandar". Isso vale mesmo quando o pedido original ja dizia "manda um email": o
pedido autoriza escrever, o envio e um segundo passo.

O corpo do email nao e o documento inteiro. E o convite para ler: o que foi feito em um
paragrafo, o resultado em uma frase, as duas ou tres coisas que a pessoa precisa saber para
apresentar, e o link. O documento completo vai anexo ou linkado.

## O teste do documento

Antes de entregar, responda como se fosse a banca:

- Por que essa coorte e nao a coorte inteira?
- Por que esse desfecho?
- Por que esse algoritmo, e por que nao o mais simples?
- Como voce sabe que nao tem vazamento?
- Por que eu deveria acreditar nesse numero?
- O que esse trabalho nao prova?

Se alguma resposta nao estiver no documento, ele nao esta pronto.

## Referencias

- `scripts/extrair_spec.py`: extrai o esqueleto verificavel do pipeline e da execucao
- `templates/spec_template.md`: a estrutura do documento
