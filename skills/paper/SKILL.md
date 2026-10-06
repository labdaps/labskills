---
name: paper
description: >
  Escreve, monta e audita manuscritos científicos de IA em saúde no padrão-ouro de reporte da área (TRIPOD+AI, PROBAST+AI, TRIPOD-LLM, STARD-AI, CLAIM, DECIDE-AI, CONSORT-AI, SPIRIT-AI, PRISMA 2020, AMSTAR 2), entregando o manuscrito em .docx pronto para submissão. Sub-comandos: `/paper draft` (uma seção), `/paper full` (manuscrito completo), `/paper check` (audita contra o checklist), mais `/paper abstract`, `/paper cover` e `/paper rebuttal`. Use SEMPRE que pedir "/paper", "escreve o paper", "monta o manuscrito", "escreve a seção de métodos", "rascunha a introdução", "monta o abstract do artigo", "prepara pra submissão", "checa se está no TRIPOD", "revisa contra o checklist", "cover letter pro editor", "responde o revisor", "transforma esses resultados em paper", mesmo informal e sem citar o guideline. Também acionar ao enviar resultado de modelo ou rascunho com intenção de virar artigo. Diferente da /artigo (pipeline em 7 fases, da busca de evidências à submissão), a /paper entrega os checklists dos guidelines em references/ e o gerador do .docx. NÃO confundir com /papers, /abstract e /paper-review (papers alheios), /red (revisão em vermelho) nem /paper-png (figuras).
---

# Skill /paper: escrever manuscrito no padrão-ouro da área

O valor desta skill não está em produzir prosa acadêmica: o Claude já faz isso. Está em
**não deixar passar o que o revisor metodológico vai cobrar**, calibração reportada,
tamanho amostral justificado, validação externa nomeada pelo que é, fairness
estratificada, dados e código declarados. Um manuscrito fluente que omite a curva de
calibração é rejeitado mais rápido do que um manuscrito seco que a inclui.

O usuário é doutorando em epidemiologia e publica em IA clínica. Não explicar o que é
AUROC, o que é TRIPOD, nem o que é revisão por pares.

---

## Regras de integridade (valem em todos os sub-comandos)

Estas não são recomendações. São o que separa a skill de um gerador de texto plausível.

1. **Nunca inventar número.** Nenhum N, IC, valor-p, AUROC, hazard ratio, percentual ou
   data sai desta skill se não veio do usuário, de um arquivo que ele forneceu ou de uma
   fonte que a skill leu. Onde faltar, escrever o marcador `[FALTA: AUROC com IC95% na
   coorte de validação externa]` no corpo do texto. Marcador visível é um pedido de
   dado; número inventado é fraude e passa despercebido na revisão.
2. **Nunca inventar referência.** Toda citação precisa ter DOI ou PMID verificado, usar
   o MCP do PubMed ou web search antes de citar. Se o usuário afirma "há evidência de X",
   a skill busca a fonte; não encontrando, escreve `[FALTA: referência para X]`.
3. **Nunca escrever afirmação de significância, superioridade ou generalização sem o
   dado que a sustenta.** "O modelo superou o Framingham" só existe se houver a
   comparação com medida de incerteza.
4. **Separar o que é do usuário do que é da skill.** Ao entregar, listar em três a seis
   linhas quais decisões interpretativas a skill tomou (enquadramento da lacuna, escolha
   do comparador na discussão, ordem do argumento) para ele aceitar ou derrubar.
5. **Declarar o uso de IA.** Todo manuscrito gerado leva, na seção de declarações, a
   frase de uso de ferramenta de IA no padrão ICMJE, a ferramenta não é autora, e a
   responsabilidade pelo conteúdo é dos autores. Não remover isso por conta própria.
6. **Não maquiar limitação.** Se o desenho tem validação só interna, a discussão diz
   isso na voz ativa. Limitação enterrada em subordinada é o que o revisor 2 acha.

---

## Passo 1: Identificar o desenho e travar o guideline

Antes de escrever qualquer linha, determinar o desenho do estudo. Se não estiver óbvio
no material, perguntar, sempre com botões (ferramenta AskUserQuestion), nunca em prosa.

| Desenho | Reporte | Risco de viés / qualidade |
|---|---|---|
| Desenvolvimento e/ou validação de modelo preditivo (regressão **ou** ML) | **TRIPOD+AI** (27 itens) | **PROBAST+AI** |
| Estudo que desenvolve, ajusta ou avalia **LLM** em saúde | **TRIPOD-LLM** | PROBAST+AI (parcial) |
| Acurácia diagnóstica de sistema de IA contra referência | **STARD-AI** | QUADAS-2 |
| Modelo de IA em **imagem** médica | **CLAIM** (+ TRIPOD+AI se preditivo) |, |
| Avaliação clínica em estágio inicial de sistema de apoio à decisão (live, com humano no loop) | **DECIDE-AI** |, |
| Ensaio clínico randomizado com intervenção de IA | **CONSORT-AI** | RoB 2 |
| **Protocolo** de ensaio com IA | **SPIRIT-AI** |, |
| Revisão sistemática / meta-análise | **PRISMA 2020** | **AMSTAR 2** (avaliar RS) / ROBIS |
| RS de modelos preditivos | PRISMA 2020 + CHARMS (extração) | PROBAST+AI por modelo |

Regras de combinação que aparecem na prática:

- Modelo preditivo **de imagem** → TRIPOD+AI é o esqueleto, CLAIM entra como camada
  adicional para aquisição, pré-processamento e ground truth.
- Modelo preditivo validado **externamente em ambiente clínico com clínico no loop** →
  TRIPOD+AI para o modelo, DECIDE-AI para a fase de avaliação.
- Estudo de **fairness / calibração em subgrupos** não tem guideline próprio: usa
  TRIPOD+AI (que já traz itens de equidade e de definição da população) e reporta as
  métricas do bloco de fairness em `references/metricas.md`.

Confirmar o guideline com o usuário antes de escrever. Guideline errado significa
reescrever o Methods inteiro depois.

Depois de travado, ler o arquivo correspondente em `"${CLAUDE_SKILL_DIR}/references/"`:

- `references/tripod-ai.md`, TRIPOD+AI e TRIPOD-LLM
- `references/probast-ai.md`, PROBAST+AI (desenvolvimento e avaliação)
- `references/diagnostico.md`, STARD-AI, CLAIM, DECIDE-AI
- `references/ensaios.md`, CONSORT-AI, SPIRIT-AI
- `references/revisoes.md`, PRISMA 2020, AMSTAR 2, CHARMS
- `references/secoes.md`, como escrever cada seção do IMRaD (ler **sempre**)
- `references/metricas.md`, o que reportar de discriminação, calibração, utilidade
  clínica, fairness e incerteza (ler **sempre** que houver modelo)
- `references/anti-ia.md`, padrões de escrita que denunciam texto gerado por IA, em
  inglês e português (ler **sempre** antes de entregar prosa; passar o texto pela lista
  antes de fechar qualquer seção)

Os arquivos de `references/` trazem a substância de cada item organizada por seção do
manuscrito. Para produzir a **tabela de checklist submetida ao journal**, com numeração
e redação oficial dos itens, buscar o checklist na fonte (equator-network.org,
tripod-statement.org ou o próprio artigo do guideline), não reproduzir numeração de
memória.

---

## Passo 2: Inventariar o material antes de escrever

Levantar o que existe e o que falta. Sem isso a skill escreve um manuscrito bonito cheio
de buraco.

Checar: dados e coorte descritos; desfecho e janela de predição definidos; preditores e
momento de disponibilidade; tamanho amostral e eventos por variável; estratégia de dados
faltantes; partição treino/validação/teste; métricas calculadas; validação externa
(temporal, geográfica ou nenhuma); análise de subgrupos; comparador; aprovação ética e
número do parecer; disponibilidade de dados e código.

Se algo central faltar, dizer **antes** de escrever, não descobrir na hora da discussão.

---

## Passo 3: Executar o sub-comando

### `/paper draft [seção]`: rascunhar uma seção

Sem argumento, perguntar qual seção com botões. Escrever a seção completa, na extensão
que ela pede no padrão do journal, seguindo `references/secoes.md` e cobrindo os itens do
guideline que caem naquela seção. Ao final, listar quais itens do checklist a seção
cobriu e quais dependem de dado que ainda falta.

Entrega inline no chat (a seção isolada não vira .docx, salvo pedido).

### `/paper full`: manuscrito completo

Só rodar com material suficiente: resultados numéricos, descrição da coorte e desenho
definido. Sem isso, voltar ao Passo 2.

Ordem de escrita, que não é a ordem de leitura: **Methods → Results → Introduction →
Discussion → Abstract → Título**. Methods e Results ancoram o que o resto pode afirmar;
escrever a introdução antes convida a prometer o que os resultados não entregam.

Entrega em `.docx` no padrão de submissão via `"${CLAUDE_SKILL_DIR}/scripts/build_docx.js"` (ver Passo 4).

### `/paper check`: auditar rascunho contra o checklist

Recebe .docx, PDF, texto colado ou link. Ler o documento inteiro, então percorrer o
checklist item a item e classificar cada um:

- **Completo**, está no manuscrito, com o dado que o item exige. Citar onde.
- **Parcial**, mencionado, mas sem o que o item pede (ex.: "calibração foi avaliada"
  sem slope, intercepto ou gráfico).
- **Ausente**, não está.
- **Não se aplica**, justificar; item marcado assim sem justificativa é item ausente.

Entregar no chat: contagem por categoria, depois **só os itens Parcial e Ausente**, cada
um com a frase ou tabela pronta para colar e o lugar onde entra. Item completo não gera
comentário, volume de crítica não é métrica.

Rodar também o eixo de risco de viés (PROBAST+AI quando for modelo preditivo): apontar os
domínios que um avaliador marcaria como alto risco e o que no manuscrito muda isso.

Quando o usuário quiser as marcações dentro do próprio documento, fazer handoff para
`/red`, que insere em vermelho no ponto exato.

### `/paper abstract`: abstract estruturado

Seguir o formato do journal-alvo (perguntar se não informado) e o checklist de abstracts
do guideline (TRIPOD+AI tem um específico). Abstract de modelo preditivo precisa carregar:
população e fonte de dados, desfecho, tipo de modelo, tamanho amostral e nº de eventos,
**discriminação e calibração com medida de incerteza**, e se a validação foi interna ou
externa. Abstract que reporta só AUROC é o erro mais comum da área.

### `/paper cover`: cover letter ao editor

Uma página. Por que este journal, o que o estudo acrescenta em uma frase, o achado
principal com o número, declaração de originalidade e não submissão simultânea, conflitos,
e sugestão de revisores se o journal pedir. Sem elogio ao journal, sem resumir o abstract.

### `/paper rebuttal`: resposta a revisor

Uma tabela ou lista com: comentário do revisor na íntegra → resposta → o que mudou no
manuscrito, citando seção e linha. Concordar onde cabe concordar e mudar o texto;
discordar onde há razão metodológica, com a razão explícita e a referência. Nunca
responder "agradecemos o comentário" sem mudança ou argumento. Tom: cordial, curto,
sem defensividade.

### `/paper help`

Listar os sub-comandos e a tabela de guidelines.

---

## Passo 4: Gerar o .docx de submissão

Montar um manifesto JSON e rodar o script da própria skill. Na primeira vez, instalar a lib
`docx` dentro da pasta de scripts da skill (o `package.json` já está lá):

```bash
(cd "${CLAUDE_SKILL_DIR}/scripts" && npm install)
node "${CLAUDE_SKILL_DIR}/scripts/build_docx.js" manifesto.json saida.docx
```

O script produz o layout que a maioria dos journals biomédicos exige: página de rosto
separada, Times New Roman 12, espaçamento duplo, **numeração contínua de linhas**,
número de página, abstract estruturado, palavras-chave, IMRaD, declarações, referências
numeradas em Vancouver e legendas de tabelas e figuras ao final. O schema do manifesto
está no cabeçalho do próprio script.

Depois de gerar, **conferir visualmente** se houver LibreOffice na máquina (`command -v soffice`;
no macOS o binário costuma estar dentro do pacote do LibreOffice em Applications):

```bash
soffice --headless --convert-to pdf saida.docx && pdftoppm -jpeg -r 100 saida.pdf page && ls page-*.jpg
```

Ler as imagens antes de entregar. Sem LibreOffice instalado, não fingir que conferiu:
entregar o .docx dizendo que a inspeção visual não foi feita.

Salvar os arquivos no diretório de trabalho do projeto e mandar para o usuário com a
ferramenta SendUserFile.

Gerar junto, como segundo arquivo, a **tabela de checklist preenchida** (item, onde está
no manuscrito, página/linha), a maioria dos journals exige no upload.

---

## Fechamento

Ao final de qualquer sub-comando, entregar no chat, em no máximo seis linhas:

1. O que ficou faltando de dado (os marcadores `[FALTA: ...]`).
2. As decisões interpretativas que a skill tomou.
3. O item do checklist que mais provavelmente vira pedido de revisor.

E oferecer o próximo passo pertinente: `/paper check` depois de um `full`, `/paper-png`
para as figuras, `/red` para marcar no documento, `/peer-review` para simular a revisão por
pares, `/journal` para escolher o destino.
