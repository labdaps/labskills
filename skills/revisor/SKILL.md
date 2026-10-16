---
name: revisor
description: Revisão pré-submissão de alto nível de manuscrito de predição clínica ou ML em saúde, na lente do LABDAPS (tempo zero, vazamento, validação com incerteza, calibração, equidade e multicalibração, utilidade clínica, TRIPOD+AI e PROBAST+AI), com números recalculados em python, auditoria de referências e entrega por bloqueadores, maiores e menores com a correção concreta. Use em "/revisor", "revisa esse paper", "revisão pré-submissão", "faz o papel do revisor 2", "o que o revisor vai pedir". NÃO confundir com /peer-review (nota por dimensão e decisão editorial simulada), /paper check (conformidade com checklist de reporte) nem /paper-review (leitura crítica de artigo de terceiros).
---

# /revisor: revisão pré-submissão na perspectiva LABDAPS

Objetivo: agir como o **Revisor 2 mais competente e exigente** que o manuscrito vai encontrar, antes que ele o encontre. A lente é a do LABDAPS/FSP-USP: modelos preditivos clínicos com dados do mundo real (SUS, registros, operadoras), com obsessão por tempo zero, vazamento, calibração, incerteza, equidade/multicalibração e utilidade clínica. Elogio só quando ajuda a decidir o que manter. Toda crítica vem com a correção concreta.

Se o paper não for de predição/ML (ex.: revisão sistemática, estudo etiológico), aplicar as passadas gerais (A e H a L) e trocar o checklist pelo adequado (PRISMA, STROBE, CONSORT, RECORD).

## 1. Obter o texto completo

- **Google Docs**: a leitura da página no navegador não funciona (o editor desenha em canvas). Use o conector do Google Docs da sessão com o ID da URL. A saída é grande e costuma ir para arquivo: extraia com python (`paragraph.elements[].textRun.content` + tabelas célula a célula) para um .txt temporário e leia inteiro. Se `commentsIncluded` for útil (ver o que coautores já apontaram), leia os comentários também.
- PDF/DOCX: skill de leitura correspondente. Nunca revise a partir de trecho parcial.
- Leia TUDO, inclusive página de rosto, declarações, referências e apêndice: é lá que moram os erros baratos que derrubam credibilidade.

## 2. Contexto antes de criticar

Identifique: revista-alvo (geralmente na página de rosto), tipo de artigo, se é primeira submissão ou resubmissão ("versão limpa", "revised"). Se a revista não estiver clara e mudar o veredito, pergunte com AskUserQuestion (botões). Busque na web as instruções aos autores da revista (limite de palavras do abstract e do texto, estrutura, nº de figuras/tabelas, estilo de referência) e compare com contagens reais feitas em python.

## 3. As passadas (fazer todas, nesta ordem)

**A. Pergunta → desenho → conclusão.** O objetivo, o desfecho primário, o título, o abstract e a conclusão dizem a mesma coisa? Qual análise é primária e qual é secundária, e isso é consistente no texto todo (inclusive legendas e apêndice)? A conclusão extrapola os resultados ("demonstrates", "clinically useful") sem validação externa?

**B. Auditoria de vazamento e tempo zero.** Defina o tempo zero e o uso pretendido. Para cada preditor: estava disponível naquele momento, para todos, no mundo real? Procure proxies que reintroduzem uma variável excluída (unidade/hospital ≈ serviço de radioterapia; origem do encaminhamento; "tratamento anterior"; campos administrativos de financiamento; códigos que só existem depois do desfecho). Verifique se pré-processamento, imputação, seleção de variáveis, tuning, calibração e escolha de limiar foram feitos só no treino/fold. Desfecho: como foi apurado (linkage)? Óbitos fora da área de cobertura viram "vivos" → erro de classificação do desfecho.

**C. Validação e incerteza.** Split único é o ponto fraco mais comum. Exigir IC95% (bootstrap) para TODAS as métricas, e validação interna robusta (bootstrap com correção de otimismo, CV repetida, ou splits repetidos). Procurar validações "internas-externas" que os próprios dados permitem e os autores não fizeram: **split temporal** (período de diagnóstico) e **leave-one-hospital/região-out**. Tamanho amostral: cobrar cálculo formal de Riley (pmsampsize) em vez de só EPV. Comparações entre algoritmos sem incerteza não sustentam "nenhum é melhor" nem "X é melhor".

**D. Calibração primeiro.** Calibração-in-the-large, slope, curva suavizada, ICI/E50/E90, Brier e Brier skill score, antes e depois de recalibração, com o recalibrador ajustado fora do teste. Pesos de classe distorcem probabilidades: cobrar que o tuning use métrica própria de probabilidade (log-loss/Brier/AUC), não F1@0,5. Em sobrevida: calibração no horizonte (ex.: 5 anos) para TODOS os modelos, não só o "melhor"; checar se o erro cresce com o tempo (sinal de não-proporcionalidade). IBS: horizonte de integração declarado.

**E. Equidade e multicalibração (nossa assinatura).** Desempenho por subgrupo com IC e n: AUC, calibração-in-the-large, slope, taxa de sinalização, sensibilidade/VPP no limiar. Sugerir auditoria de multicalibração em interseções (idade × raça/cor × escolaridade × região/hospital) e, quando cabível, pós-processamento multicalibrado como análise de sensibilidade. Discutir explicitamente o uso de raça/cor como preditor. Subgrupos com n < ~100 ou poucos eventos: pedir agregação ou só descritivo. Lembrar: calibração média boa ≠ equidade.

**F. Utilidade clínica.** Qual decisão o modelo vai apoiar, para quem, em que ponto do cuidado? DCA só faz sentido com faixa de limiar justificada clinicamente. Limiar por máximo de F1 é arbitrário (ignora VN e custos): sugerir limiar ancorado em DCA/custo, capacidade do serviço ou sensibilidade-alvo. Mostrar tabela de reclassificação/ números por 1.000 pacientes.

**G. Explicabilidade.** O modelo explicado é o modelo relatado/recomendado? SHAP não é efeito causal (os autores devem dizer, e não se contradizer depois). Para modelos lineares (Cox/Coxnet/LR), KernelExplainer é desnecessário: usar coeficientes/HR ou LinearExplainer. Categorias "Unknown" com alta importância = padrão de registro/acesso, não biologia.

**H. Reprodutibilidade e declarações.** Código: release com tag + DOI (Zenodo) correspondente ao paper, nunca "o repositório pode mudar". Dados: declaração coerente (não pode dizer "não disponível" e "disponível sob pedido" sem conciliar). Uso de API externa com dados de pacientes (ex.: TabPFN cloud, LLMs): cobertura pelo CEP/LGPD precisa estar declarada. Versões de pacotes, seeds, hardware.

**I. Conferência numérica (sempre em python).** Recalcular: somas de N e % das tabelas, partições (treino/teste, eventos), prevalências, F1 a partir de precisão/recall, BSS a partir do Brier e da prevalência, spreads e diferenças citadas no texto, reduções percentuais (ex.: IBS vs KM), conversões dias→anos, EPV. Conferir que todo número do abstract aparece igual nos resultados/tabelas. Caçar **placeholders vazios** ("between  and ", "near  and"), afiliações em branco, rótulos de tabela truncados.

**J. Auditoria de referências.** Para cada citação no texto: a referência daquele número sustenta aquela frase? (erro clássico: renumeração deixa [23] apontando para XGBoost numa frase sobre raça/cor). Duplicatas na lista, ordem de aparição (estilo Vancouver), afirmações factuais sem citação ("SEER models achieved C 0.77 a 0.83"), revisão sistemática citada que na verdade é primer/estudo primário. Nunca inventar referência substituta: sugerir o tipo de fonte ou buscar no PubMed MCP e confirmar.

**K. Consistência interna e terminologia.** Mesma sigla para a mesma coisa (HCR/HBR/RHC), mesmos nomes de modelos, numeração de figuras/suplementos batendo com o apêndice, caminhos de arquivo ou termos em português no texto em inglês, limitações citando o número certo (ex.: % de missing do campo certo).

**L. Higiene de submissão.** Resquícios de revisão ("Hence, Therefore", "to: to:", palavras duplicadas), **changelog dentro do manuscrito** ("an earlier version of this analysis...", "previously reported 0.69" sem referência): isso vai para a carta-resposta ou suplemento como análise de sensibilidade, não para o Methods. Abstract e texto dentro do limite da revista.

## 4. Checklists de fundo

TRIPOD+AI (relato) e PROBAST+AI (risco de viés: participantes, preditores, desfecho, análise). Não colar o checklist inteiro na resposta: usar para encontrar lacunas e citar só os itens que falham.

## 5. Formato da entrega (em português, direto)

1. **Veredito em 2 ou 3 linhas**: pronto / pronto com ajustes / precisa de nova análise, e qual a chance realista na revista-alvo.
2. **Bloqueadores** (impedem submissão: placeholders, erros factuais, contradições, problemas éticos/LGPD, referências erradas).
3. **Maiores** (o que o Revisor 2 vai pedir; cada um com: onde → problema → por que importa → correção concreta, com texto pronto quando for reescrita).
4. **Análises adicionais viáveis com os dados que já existem** (priorizadas por ganho/esforço).
5. **Menores e edição** (lista compacta com localização).
6. **O que está forte** (curto, para não ser mexido).

Endereçar por seção + frase-âncora citada (não por número de linha, que muda). Números sempre conferidos. Se o usuário pedir, oferecer: aplicar correções de texto no Google Doc (pelo conector do Google Docs, só após confirmação), gerar prompt de Claude Code (em bloco de código) para as análises novas no repositório, ou rascunhar a carta-resposta.