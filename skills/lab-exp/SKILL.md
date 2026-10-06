---
name: lab-exp
description: Roda um experimento preditivo clinico de ponta a ponta no padrao do laboratorio, da auditoria de vazamento ate o zip e o repositorio privado. Comeca sempre pela auditoria que decide se o experimento faz sentido (momento da predicao, censura disfarcada de desfecho, variavel que sozinha da AUC alta demais), depois monta o pipeline com Boruta dentro do fold, sete modelos com regra de desempate declarada antes, limiar fora da amostra, IC por bootstrap e calibracao, e entrega notebook do Colab, notebook executado com as saidas, relatorio HTML de arquivo unico, results com figuras e tabelas, zip de compartilhamento e repo privado. Use SEMPRE que o usuario pedir "/lab-exp", "roda esse experimento", "monta o pipeline desse dado", "novo experimento do lab", "refaz esse notebook direito", "esse modelo tem vazamento?", "prepara isso pra dissertacao", ou enviar um notebook de aluno, um banco de coorte hospitalar ou uma pergunta preditiva clinica para transformar em experimento. Acionar PROATIVAMENTE quando alguem mandar um notebook de predicao clinica com AUC alta e pedir opiniao, porque o primeiro passo e a auditoria de vazamento.
---

# Skill: lab-exp

Experimento preditivo clinico completo, no padrao que o laboratorio ja validou.

A skill existe porque o erro caro nesses projetos nunca e o algoritmo. E o dado: uma coluna que
so existe depois do desfecho, um paciente censurado rotulado como sobrevivente, uma metrica
otimizada que nao e a que importa. Modelo errado custa 0.02 de AUC. Vazamento custa 0.19, e so
aparece na validacao externa, ou no reviewer 2, ou nunca.

**Regra central: nenhum modelo treinado antes da auditoria da fase 1 estar respondida por
escrito.**

**Segunda regra: nenhum numero e digitado a mao.** Todo valor no README e no relatorio sai de
uma tabela em `results/`, que sai de uma execucao registrada em `run.log`. Numero que muda, muda
por reexecucao.

## Quando NAO usar

Recalcular uma metrica, refazer uma figura, rodar um modelo ja definido em dado ja limpo: faca
direto, sem a estrutura. O ritual em tarefa pequena so gasta tempo.

## Fase 1: auditoria, antes de qualquer modelo

Tres perguntas. Responda por escrito, com numero, antes de escrever o pipeline. Se qualquer uma
ficar sem resposta, o experimento nao comeca.

### 1.1 Qual e o momento da predicao?

Escreva o instante do cuidado por extenso: "a alta hospitalar", "a admissao no pronto socorro",
"o momento da indicacao cirurgica". Toda variavel medida depois desse instante e vazamento,
sem excecao e sem negociacao.

Monte a lista explicita, com o motivo de cada coluna, e salve como tabela. Categorias que sempre
aparecem: o desfecho e suas variantes em outras janelas, datas posteriores ao momento,
identificadores, colunas constantes na coorte, e o grupo perigoso, que e a informacao que parece
clinica mas so existe depois (tempo total de antibiotico, tempo de internacao quando o desfecho
e intra-hospitalar, qualquer "tempo ate" que termine depois do momento da predicao).

Variavel que fica apesar de parecer suspeita fica com a justificativa escrita ao lado.

### 1.2 Quem nao teve o evento realmente nao teve?

Esta e a pergunta que mais passa batido. Se o desfecho e "obito em N dias", o paciente com
seguimento de 40 dias e vivo nao e sobrevivente, e desconhecido. Rotular como zero produz um
desfecho que so e coerente se o modelo tambem enxergar o tempo de seguimento, que e exatamente
a variavel que precisa sair. **O rotulo errado e o vazamento se sustentam mutuamente.**

Solucao: censura vira criterio de elegibilidade, nunca preditor. Quem nao completou a janela sai
da coorte. Reporte quantos sairam, porque costuma ser muito (no experimento de endocardite foram
153 de 775, quase 20 por cento) e isso vai para o fluxograma do artigo.

Quem quiser aproveitar os excluidos: analise de sobrevida como sensibilidade, que usa cada um
ate onde foi observado.

### 1.3 Alguma variavel, sozinha, discrimina demais?

AUC univariada de cada candidata sobrevivente. Qualquer uma acima de 0.80 e suspeita de ser
consequencia do desfecho, e nao causa. A lista manual cobre o que se conhece, a auditoria pega
o que passou.

Sinal de que deu ruim: uma variavel com AUC univariada perto de 1.000 e uma tautologia, nao um
achado. Se dentro da coorte elegivel "morreu em 180 dias" e "tem menos de 180 dias de
seguimento" sao a mesma frase, a AUC de 1.000 esta medindo a definicao do desfecho.

### 1.4 Quantifique o estrago, se havia vazamento

Se o experimento e o refazimento de um anterior que vazava, rode tres cenarios na mesma
validacao cruzada e com o mesmo modelo: original com a variavel, original sem ela, e novo com a
coorte corrigida. A distancia entre o primeiro e o terceiro e o ganho artificial, e esse numero
vale mais para o orientador do que qualquer AUC nova.

## Fase 2: montar o pipeline

Copie `"${CLAUDE_SKILL_DIR}/templates/pipeline.py"` para a raiz do projeto como `pipeline.py` e preencha o que esta
marcado. O que ja vem pronto e testado:

| Peca | O que resolve |
|---|---|
| `sem_acento` na carga | nome de coluna com acento quebra dependendo do encoding de leitura |
| `LIMITES_PLAUSIVEIS` | valor impossivel vira missing por faixa, nunca por lista digitada a mao |
| `montar_coorte` | elegibilidade e lista de vazamento num lugar so, devolvendo o fluxograma |
| `PreProcessador` | descarte por missing, imputacao por mediana e indicador de ausencia, tudo dentro do fold |
| `SelecaoBoruta` | Boruta com plano B quando nada e confirmado, para o fold nao ficar sem preditor |
| `rodar_cv` | Boruta uma vez por fold alimentando todos os modelos, mais a estabilidade da selecao |
| `escolher_campeao` | empate ate 0.01 resolvido a favor do modelo mais simples, regra declarada antes |
| `limiar_por_sensibilidade` | limiar fora da amostra, um por modelo |
| `bootstrap_ic` | IC95% em 2000 reamostragens |
| `shap_valores` | explicador certo por tipo de modelo, incluindo o caro do TabPFN |
| `salvar_fig(nome, legenda)` | grava a legenda em `results/legendas.json`, para o relatorio nunca descolar |

Decisoes que ja foram tomadas e nao precisam ser rediscutidas a cada experimento:

- **Seletor e imputacao rodam dentro do fold.** Fora, sao vazamento discreto.
- **Otimizacao por AUC**, nunca por acuracia em desfecho raro. `cross_val_score` sem `scoring`
  usa acuracia e, com 4 por cento de evento, encontra o modelo que acerta "todo mundo vive".
- **A logistica regularizada e obrigatoria na comparacao.** Com poucas dezenas de eventos ela
  costuma ganhar, e o artigo precisa mostrar isso.
- **Ensemble por media de postos**, nunca de probabilidade: com peso de classe, a logistica
  preve risco medio de 0.45 e as arvores 0.045, e a media simples viraria a logistica disfarcada.
- **Um limiar por modelo**, mesmo criterio para todos. Limiar unico compara modelos em pontos de
  operacao diferentes.
- **Calibracao e metrica de primeira classe.** Peso de classe infla o risco predito. Reporte
  Brier e ofereca a versao recalibrada por Platt, ajustada dentro do treino. Se algum risco
  absoluto vai para o texto, ele sai do modelo calibrado.
- **`sem_paralelismo_interno` antes de qualquer busca paralela.** Sem isso, cada processo do
  joblib abre uma thread por nucleo e a busca nao termina.

## Fase 3: rodar e verificar

```bash
python pipeline.py > run.log 2>&1        # a saida inteira fica registrada
```

Se a execucao passa de uns minutos, rode em background e acompanhe por `tail -f run.log`.
Enquanto roda, escreva o template do relatorio, que nao depende dos numeros.

Verificacao real: `EXIT=0` e as tabelas em `results/`. Nunca diga que rodou sem ter o codigo de
saida e o arquivo no disco.

## Fase 4: entregaveis

Nesta ordem, depois de copiar os scripts da skill para a raiz do projeto
(`cp "${CLAUDE_SKILL_DIR}/scripts/"*.py .`):

```bash
python gerar_notebook.py     # pipeline.py -> <pasta>.ipynb, pronto para o Colab
python executar_notebook.py  # roda o notebook e grava <pasta>_executado.ipynb
python montar_relatorio.py   # relatorio_template.html + results/*.png -> relatorio.html
python montar_pacote.py      # requirements.txt com as versoes que rodaram, mais o zip
```

**`executar_notebook.py` e o teste de integracao, nao um passo cosmetico.** Checagem de sintaxe
nao pega tudo: uma primeira celula com `IndentationError` passou por `ast.parse` porque a
checagem ignorava as linhas iniciadas por `!`, e so apareceu na execucao de verdade.

O relatorio vai como artifact publicado, com `capabilities: {downloads: true}`, porque o sandbox
bloqueia download que a propria pagina dispara e um `<a download>` seria botao morto. Carregue a
skill `artifact-design` antes de escrever o template e a `artifact-capabilities` antes de
declarar a capability. Use `"${CLAUDE_SKILL_DIR}/templates/relatorio_template.html"` como ponto de partida.

## Fase 5: repositorio

Criar o repositório privado a partir da pasta existente (`gh repo create --private --source=.`)
e subir o primeiro commit.

**`data/` nunca entra**, nem desidentificado: data de nascimento com data de internacao
reidentifica. Antes do commit, varra os arquivos versionados procurando CPF, data de nascimento,
nome proprio e tabela com uma linha por paciente. `results/` e os logs entram, porque sao a
evidencia do trabalho.

O `CLAUDE.md` do projeto recebe as regras que nao se negociam naquele experimento, para a
proxima sessao nao desfazer o que foi corrigido.

## O que reportar ao terminar

1. O artefato, com o link.
2. Os numeros que decidem: n, eventos, EPV antes e depois do Boruta, AUC do campeao com
   intervalo, e o ganho artificial se havia vazamento.
3. As ressalvas que precisam entrar no texto da dissertacao, com destaque para as que limitam a
   conclusao: tamanho da amostra de teste, ausencia de validacao externa, comparacoes entre
   coortes diferentes.
4. O que ficou fora e por que.

## Referencias

- `references/auditoria.md`: a auditoria da fase 1 com os casos reais ja encontrados
- `templates/pipeline.py`: o pipeline para copiar e preencher
- `templates/relatorio_template.html`: a casca do relatorio
- `scripts/`: os quatro scripts de entrega, generalizados por convencao de pasta
