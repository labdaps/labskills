---
name: journal
description: >
  Seleciona o periódico alvo de um manuscrito cruzando encaixe de escopo, impacto e custo real de
  publicação, com cada dado verificado na fonte do editor e nunca de memória. Entrega uma lista
  curta com o trade-off declarado, não um nome só. Sub-comandos: `/journal` (recomenda alvos para o
  manuscrito atual), `/journal check <revista>` (audita uma revista específica: APC, indexação,
  escopo, sinal de predatória), `/journal fit <revista>` (só o encaixe de escopo, com evidência),
  `/journal free` (só os que não cobram nada) e `/journal compare A vs B`. Use SEMPRE que pedir
  "/journal", "qual revista", "onde submeter", "escolhe o journal", "qual periódico se encaixa",
  "revista sem taxa", "sem APC", "onde publicar isso", "qual journal de alto impacto pra esse
  paper", "essa revista é boa", "essa revista é predatória", "quanto custa publicar nessa
  revista", ou ao terminar um manuscrito e perguntar o destino. NÃO confundir com /paper e
  /paper-tex (que escrevem o manuscrito), /paper cover (carta ao editor), /pubs (registra
  publicação) nem /papers e /abstract (leem papers alheios).
---

# Skill: /journal: escolher onde submeter

O valor desta skill não está em listar revistas de alto fator de impacto: qualquer um faz isso.
Está em **não deixar o usuário submeter para o lugar errado nem pagar o que não precisava**, e as
duas coisas erram pelo mesmo motivo, que é responder de memória sobre um dado que muda todo ano.

O usuário é doutorando em epidemiologia e publica em IA clínica. Não explicar o que é fator de
impacto, quartil, desk reject nem revisão por pares.

---

## Regras de integridade

Estas separam a skill de um chute plausível.

1. **Nunca afirmar valor de APC de memória.** Taxa muda todo ano. Todo número de custo sai de
   busca feita nesta sessão, na página do editor, com a URL citada na entrega. Sem verificar,
   escrever `[NÃO VERIFICADO: APC de <revista>]`.
2. **Nunca confiar em site agregador para custo.** `journalsearches`, `resurchify`,
   `journalmetrics`, `bioxbio`, `askbisht` e similares erram sistematicamente, e o erro tem sempre
   a mesma direção, descrita na armadilha 1 abaixo. Servem no máximo para achar o nome e uma
   estimativa de impacto; para dinheiro, só a página do editor.
3. **Escopo antes de impacto.** Uma revista de fator 8 que rejeita o tema na mesa vale zero. O
   encaixe de escopo é o primeiro filtro, e ele precisa de evidência: um artigo comparável
   publicado nos últimos dois anos, ou a frase do escopo oficial que cobre o desenho.
4. **Impacto sem indexação é ilusão.** Confirmar PubMed/MEDLINE, Scopus e Web of Science antes de
   recomendar. Revista grátis e não indexada não serve para currículo Lattes nem para CAPES.
5. **Grátis e de alto impacto ao mesmo tempo é o pitch clássico de predatória.** Sempre rodar a
   triagem da seção correspondente antes de recomendar qualquer revista que o usuário não conheça.
6. **Entregar de dois a quatro alvos com o trade-off explícito**, nunca um nome só. A decisão entre
   impacto e acesso aberto é do autor, não da skill.

---

## As três armadilhas que fazem esta skill existir

### Armadilha 1: confundir revista híbrida com revista que cobra

**A mais cara das três, e a mais fácil de cair.** Buscador e agregador leem "esta revista tem APC
de USD 1.200" e reportam "esta revista cobra USD 1.200". Errado para revista híbrida.

Os três modelos, e quem paga em cada um:

| Modelo | Publicar custa | Ler custa | Exemplo |
|---|---|---|---|
| Assinatura / híbrida | **nada**, pela rota de assinatura | leitor ou biblioteca paga | maioria de Elsevier, Wiley, Oxford, Springer |
| Gold OA | APC, de USD 1.000 a 6.000 | nada | PLOS, BMC, Frontiers, Scientific Reports |
| Diamond OA | **nada** | nada | Cadernos de Saúde Pública, Eurosurveillance |

Em revista híbrida o APC é **opcional**: paga quem quer que o artigo saia aberto. Quem não paga
publica pela rota de assinatura, sem custo, e o artigo fica atrás de paywall. Isso significa que a
maioria das revistas de alto impacto das áreas do usuário é **grátis para publicar**, e um pedido de
"alto impacto sem taxa" quase sempre se resolve por aí.

Como confirmar que é híbrida, e não gold:
- A página do editor diz "open access option" ou "optional open access", não "all articles are
  published open access".
- A revista **não** está no DOAJ. Estar no DOAJ é sinal de gold ou diamond.
- Sherpa Romeo classifica a política de autoarquivamento, o que só faz sentido em híbrida.

Ao recomendar a rota de assinatura, **dizer o custo não financeiro**: o artigo não sai aberto, e o
autoarquivamento verde costuma ter embargo. Para trabalho com dado público de saúde isso é uma
perda real, e o autor precisa pesar.

### Armadilha 2: escopo que parece encaixar e não encaixa

Fator de impacto alto e APC zero atraem, e o escopo é onde o tiro sai pela culatra. Um exemplo real:
a Eurosurveillance tem fator 8,3 e é diamond, mas publica **doença transmissível com foco na
Europa**. Um manuscrito sobre mortalidade cardiovascular no Brasil é desk reject no primeiro dia.

Antes de colocar uma revista na lista, achar **um artigo comparável publicado nela nos últimos dois
anos**: mesmo desenho, ou mesma região, ou mesmo tipo de dado. Não achando, dizer isso na entrega em
vez de esconder. "Escopo declarado cobre, mas não achei precedente" é uma informação útil; omitir é
como a submissão morre.

Checar também o que a revista **explicitamente não publica**: muitas listam isso no guia de autores,
e é onde aparecem exclusões do tipo "não publicamos estudos de um único centro" ou "não publicamos
análise secundária de dado administrativo".

### Armadilha 3: custo tem mais de uma linha

APC é a linha óbvia. Perguntar também, porque cada uma já derrubou submissão de gente que não
esperava:

- **Taxa de submissão**, cobrada mesmo se rejeitar. Comum em economia e em algumas de finanças.
- **Page charges** e **taxa de figura colorida**, sobrevivência de revista tradicional.
- **Acordo transformativo**: CAPES, USP e outras instituições têm acordo com editor que zera o APC
  para autor correspondente afiliado. Isso muda a resposta inteira. Sempre mandar o usuário conferir
  na biblioteca da instituição antes de descartar uma gold OA por preço.
- **Isenção para país de renda baixa e média**: o Brasil costuma cair em desconto parcial, não em
  isenção total. Não prometer isenção sem ver a política.
- **Page charge por página em revista híbrida.** É o caso que mais engana, porque a revista
  é corretamente descrita como "grátis pela rota de assinatura" e ainda assim cobra. Já
  visto: American Journal of Epidemiology, USD 95 por página, cerca de USD 1.900 num
  artigo de vinte páginas. Sempre abrir o guia de autores e procurar por "page charge",
  "per page" e "colour figure", mesmo depois de confirmar que a revista é híbrida.

---

## Passo 1: levantar o que o manuscrito é

Sem isso a skill recomenda pelo tema e erra o desenho. Ler o manuscrito, ou perguntar, para fixar:

- **Desenho**: coorte, ensaio, modelo preditivo, benchmark metodológico, revisão, série temporal.
- **Contribuição principal**: metodológica ou aplicada. Manuscrito com as duas faces pode ir para
  públicos diferentes e é o caso em que a lista curta mais ajuda.
- **População e região**, que decidem se revista regional entra.
- **Tipo de dado**: registro administrativo, prontuário, imagem, dado público.
- **Resultado é positivo, nulo ou negativo.** Resultado nulo restringe muito o alvo, e algumas
  revistas dizem explicitamente que aceitam. Isso é informação de seleção, não detalhe.
- **Restrições do autor**: precisa ser aberto, precisa ser rápido, precisa ser Qualis alto,
  precisa ser indexado em X.

Se o usuário não declarou a restrição de custo, **perguntar com botões** antes de buscar: aceita
pagar APC, quer custo zero mesmo que fique fechado, ou quer aberto a custo zero, que restringe a
diamond.

## Passo 2: montar os candidatos

Cruzar três fontes, porque cada uma sozinha enviesa:

1. **Onde o próprio manuscrito cita.** As revistas da lista de referências são, por construção, as
   que publicam o assunto. É a fonte mais barata e a mais subestimada.
2. **Busca por artigo comparável.** Procurar dois ou três artigos com o mesmo desenho e ver onde
   saíram.
3. **Sociedade ou consórcio da área.** Revista oficial de sociedade costuma ter escopo mais
   explícito e público mais certo.

Chegar a seis ou oito candidatos aqui, para o filtro seguinte cortar.

**Manuscrito com duas faces gera duas listas, e a segunda quase sempre é esquecida.**
Trabalho de IA aplicada à saúde cabe tanto na revista da doença quanto na de informática
médica, e os dois conjuntos têm economia completamente diferente. As de informática médica
e IA clínica de maior impacto são majoritariamente **híbridas**, portanto grátis pela rota
de assinatura: JAMIA, Journal of Biomedical Informatics, International Journal of Medical
Informatics, Artificial Intelligence in Medicine, Computer Methods and Programs in
Biomedicine, IEEE Journal of Biomedical and Health Informatics. As que o autor lembra
primeiro costumam ser as gold caras: Lancet Digital Health, npj Digital Medicine, JMIR,
PLOS Digital Health. Quando o usuário pede custo zero, montar a lista das híbridas antes
de descartar a área inteira por preço.

O contrapeso: revista de informática publica o **método**, e revista da doença publica o
**achado epidemiológico**. Rodar a busca de precedente (armadilha 2) separado em cada
bloco, porque é comum a de informática ter impacto maior e nenhum precedente no tema, o
que a torna pior alvo apesar do número.

## Passo 3: verificar cada candidato na fonte

Para cada um, e **só com busca feita nesta sessão**:

| O que verificar | Onde | Cuidado |
|---|---|---|
| Modelo de publicação e APC | página do editor, "open access options" ou "author information" | armadilha 1 |
| Taxa de submissão e page charge | guia de autores | costuma estar no rodapé |
| Fator de impacto e quartil | JCR, Scimago | agregador serve só de estimativa |
| Indexação | PubMed, Scopus, Web of Science | conferir na base, não no site da revista |
| Escopo e exclusões | "aims and scope" e guia de autores | armadilha 2 |
| Precedente | busca por artigo comparável dos últimos dois anos | armadilha 2 |
| Tempo até primeira decisão | site da revista ou relato público | nem toda revista publica |

Página de editor grande costuma devolver 403 para fetch automatizado. Nesse caso, buscar a mesma
informação por outra rota (Sherpa Romeo, DOAJ, página da sociedade, guia de biblioteca
universitária) e **declarar qual rota foi usada**, em vez de reportar como se tivesse lido a fonte
primária.

**O DOAJ resolve a armadilha 1 sem depender do site do editor**, e é consultável por API,
o que permite triar muitos candidatos de uma vez. A regra: revista que se declara open
access e **não** está no DOAJ é híbrida ou de assinatura, portanto grátis para publicar
pela rota fechada; revista **no** DOAJ é gold ou diamond, e o próprio registro diz se cobra
APC e quanto.

```bash
curl -s "https://doaj.org/api/search/journals/issn:1067-5027" | \
  python -c "import sys,json; d=json.load(sys.stdin); print(d.get('total'))"
```

Resposta `0` significa fora do DOAJ, ou seja, grátis pela assinatura. Resposta positiva
traz `bibjson.apc.has_apc` e `bibjson.apc.max[0].price`, que é valor do editor e não de
agregador, e portanto serve para citar.

Isso tria em segundos, mas **não substitui a checagem de page charge**: híbrida sem APC
ainda pode cobrar por página. Confirmar essa parte no guia de autores, que costuma ser
acessível mesmo quando a página de preços não é.

## Passo 4: triagem de predatória

Rodar sempre em revista que o usuário não conhece, e sempre que a combinação for "alto impacto,
publicação rápida, sem taxa". Sinais, e nenhum isolado condena:

- Não está no DOAJ, sendo que se declara open access.
- Não está no PubMed nem no Scopus, mas anuncia "indexada" de forma vaga.
- Promete decisão em prazo implausível para revisão por pares real.
- Escopo largo demais para uma revista só.
- Convite por email não solicitado, elogiando um artigo anterior do autor.
- Corpo editorial sem afiliação verificável, ou com nomes que não sabem que estão lá.
- Fator de impacto anunciado que não é o do JCR, com nome parecido.

Checar contra DOAJ, COPE, e a lista de Beall onde ainda for aplicável. Achando sinal, dizer qual e
por quê, sem transformar em acusação categórica.

## Passo 5: entregar

Tabela curta, de dois a quatro alvos, ordenada pela recomendação:

| Revista | Encaixe de escopo | Impacto | Custo real para publicar | Aberto? | Risco principal |
|---|---|---|---|---|---|

Depois da tabela, em no máximo seis linhas:

1. **A recomendação e o porquê**, em uma frase que nomeie o critério que decidiu.
2. **O trade-off que o usuário está aceitando** ao seguir a recomendação. Sempre existe um.
3. **A segunda opção e sob qual condição ela vira a primeira.**
4. **O que ficou não verificado**, com o marcador.
5. As URLs consultadas, como links.

Nunca entregar só o primeiro colocado. A escolha entre impacto e acesso aberto, e entre revista
internacional e revista regional que a banca conhece, é do autor.

---

## Sub-comandos

### `/journal`
Fluxo completo dos passos 1 a 5 para o manuscrito em contexto. Sem manuscrito em contexto,
perguntar o desenho e a área antes de buscar.

### `/journal check <revista>`
Auditoria de uma revista só: modelo de publicação, APC com a fonte, taxa de submissão, indexação,
escopo, precedente e triagem de predatória. Entregar o veredito em uma linha no fim.

### `/journal fit <revista>`
Só o encaixe de escopo, com evidência: a frase do escopo oficial que cobre ou não cobre o desenho,
mais um artigo comparável recente, ou a declaração de que não achou.

### `/journal free`
Só os alvos que não custam nada ao autor, separando as duas rotas em blocos distintos, porque elas
não são a mesma coisa: **assinatura ou híbrida**, grátis mas fechado, e **diamond**, grátis e
aberto. Dizer o custo não financeiro de cada bloco.

### `/journal compare A vs B`
Comparação lado a lado nos mesmos eixos do Passo 5, terminando com a condição que decide entre as
duas em vez de um vencedor abstrato.

---

## Fechamento

Ao final de qualquer sub-comando, entregar:

- o que ficou `[NÃO VERIFICADO: ...]` e por quê;
- a decisão que a skill tomou por conta própria e que o usuário pode derrubar;
- o próximo passo pertinente: `/paper cover` para a carta ao editor, `/paper check` ou
  `/paper-tex check` para auditar o manuscrito contra o checklist antes de submeter, `/eng` para
  polir o inglês, `/pubs` para registrar quando sair.

Lembrar o usuário de conferir o acordo transformativo da instituição antes de descartar uma gold OA
por preço: é a checagem de maior retorno por minuto gasto em toda esta skill.
