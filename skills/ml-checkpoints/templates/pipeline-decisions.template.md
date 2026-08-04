# Decisões do pipeline: {{nome-do-projeto}}

> Gerado pela skill `ml-checkpoints`. Cada linha é uma decisão tomada com o
> número que a sustentou. Este arquivo é o rascunho da seção de Métodos:
> decisão sem motivo escrito não sobrevive a três meses.

## Base

| Campo | Valor |
|---|---|
| Arquivo | {{caminho relativo, nunca o conteúdo}} |
| Linhas x colunas | {{N x M}} |
| Desfecho | {{coluna}} |
| Definição operacional | {{a regra que qualquer pessoa aplica e chega ao mesmo N}} |
| Tipo | {{binário, multiclasse, contínuo, tempo até evento}} |
| Prevalência | {{% e N da classe rara}} |
| Unidade de análise | {{paciente, internação, exame, município, mês}} |
| Momento da predição | {{o que já se sabe nesse instante}} |
| Data do diagnóstico | {{data}} |

## Achados do CP0 que exigiram decisão

| Achado | Coluna | Encaminhamento |
|---|---|---|
| {{suspeita de vazamento, missing alto, sentinela, código numérico}} | {{coluna}} | {{o que foi feito e por quê}} |

## Decisões

| CP | Decisão tomada | Motivo medido | Alternativa descartada | Restrição que impõe |
|----|----------------|---------------|------------------------|---------------------|
| CP1 | {{...}} | {{...}} | {{...}} | {{...}} |
| CP2 | {{...}} | {{...}} | {{...}} | {{...}} |
| CP3 | {{...}} | {{...}} | {{...}} | {{...}} |
| CP4 | {{...}} | {{...}} | {{...}} | {{...}} |
| CP5 | {{...}} | {{...}} | {{...}} | {{...}} |
| CP6 | {{...}} | {{...}} | {{...}} | {{...}} |
| CP7 | {{...}} | {{...}} | {{...}} | {{...}} |
| CP8 | {{...}} | {{...}} | {{...}} | {{...}} |
| CP9 | {{...}} | {{...}} | {{...}} | {{...}} |
| CP10 | {{...}} | {{...}} | {{...}} | {{...}} |

## Aceites conscientes

<!-- opção que o diagnóstico bloqueou ou desaconselhou e o usuário escolheu mesmo assim -->

| CP | Opção | Número que a desaconselhava | Justificativa do usuário | Data |
|----|-------|------------------------------|--------------------------|------|
| {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

## Checkpoints reabertos

<!-- toda vez que uma escolha posterior invalidou uma anterior -->

| CP reaberto | O que mudou | Por causa de qual decisão | Data |
|-------------|-------------|---------------------------|------|
| {{...}} | {{...}} | {{...}} | {{...}} |

## Resultado

| Item | Valor |
|---|---|
| Baseline | {{modelo e métrica principal com IC}} |
| Modelo final | {{modelo e métrica principal com IC}} |
| Ganho sobre a baseline | {{diferença com IC; se o IC cruza zero, diga isso}} |
| Calibração | {{slope, intercepto, Brier antes e depois}} |
| Ponto de corte | {{valor e o custo clínico que o justifica}} |
| Variáveis com direção inesperada no SHAP | {{lista, ou "nenhuma"}} |

## Pendências

- {{o que ficou sem decidir e o que destrava}}
