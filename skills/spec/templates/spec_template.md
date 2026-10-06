# TITULO DO EXPERIMENTO

> Documento para NOME DO LEITOR, que precisa CONSEGUIR O QUE DEPOIS DE LER.
> Escrito a partir de `pipeline.py` e da execucao registrada em `run.log`, em DATA.
> Nenhum numero aqui foi digitado a mao: todos saem das tabelas em `results/`.

## 1. A pergunta e a decisao

**O que se prediz.** Uma frase.

**Para quem.** A coorte, em uma frase, com o numero.

**Em que momento.** O instante do cuidado em que a predicao aconteceria na vida real. Esta frase
e a mais importante do documento, porque e ela que define o que pode e o que nao pode ser
preditor.

**Que decisao isso informa.** O que muda na conduta se o modelo funcionar. Se nao muda nada, o
trabalho e descritivo, e tudo bem, mas isso precisa estar escrito.

## 2. As regras do experimento

Estes sao os parametros que definem o pipeline. Mudar qualquer um muda o resultado, e por isso
cada um tem um porque. Esta tabela e o "spec": para rodar diferente, muda aqui e roda de novo.

| parametro | valor | por que esse valor |
|---|---|---|
| | | |

### O que foi excluido das variaveis, e por que

| grupo | quantas | motivo |
|---|---|---|
| | | |

### O que foi mantido apesar de parecer suspeito

| variavel | por que ela pode ficar |
|---|---|
| | | |

## 3. O passo a passo

Uma subsecao por etapa, na ordem em que roda. Cada uma responde tres perguntas, e a terceira e a
que a banca pergunta.

### Etapa N: nome

**O que faz.** Descricao operacional, curta.

**Por que existe.** O problema que ela resolve.

**O que aconteceria sem ela.** O estrago concreto, com numero quando houver. Esta e a resposta
para "por que voce fez assim?".

## 4. O que foi testado, e o que o teste pega

Nao basta dizer que foi validado. Para cada verificacao:

| verificacao | o que ela pegaria | o que ela nao pega |
|---|---|---|
| | | |

**Bugs encontrados no caminho.** Liste. Um teste que nunca encontrou nada e um teste que ninguem
sabe se funciona. Bug encontrado e a evidencia de que a verificacao serve.

## 5. Os numeros

Direto das tabelas de `results/`, com intervalo de confianca onde existir.

| | |
|---|---|

**Como ler.** Uma frase por numero importante, dizendo o que ele significa e o que ele nao
significa.

## 6. O que este trabalho nao prova

Escrito como frase que a pessoa pode falar em voz alta na apresentacao.

1. **Limitacao.** Por que, e o que seria preciso para resolver.

## 7. Como rodar de novo, e como mudar

```bash
python pipeline.py > run.log 2>&1
python gerar_notebook.py
python executar_notebook.py
python montar_relatorio.py
python montar_pacote.py
```

**Para mudar o experimento**, mexa na tabela da secao 2 e rode de novo. Exemplos do que e uma
linha de mudanca:

- acrescentar um modelo: entra em `modelos_base` e em `GRADES`
- mudar o desfecho: `ALVO`
- mais repeticoes da validacao cruzada: `N_REPEATS`
- outro criterio de limiar: `SENS_ALVO`

## 8. Perguntas que a banca faz, e onde esta a resposta

| pergunta | secao |
|---|---|
| Por que essa coorte e nao a coorte inteira? | |
| Por que esse desfecho? | |
| Por que esse algoritmo, e por que nao o mais simples? | |
| Como voce sabe que nao tem vazamento? | |
| Por que eu deveria acreditar nesse numero? | |
| O que esse trabalho nao prova? | |
