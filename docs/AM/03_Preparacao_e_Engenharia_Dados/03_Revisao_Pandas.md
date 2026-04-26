# Revisão: Preparação de Dados com Pandas

Esta revisão isola os conceitos da etapa de ETL em uma sequência de notebooks pequenos.
A ideia aqui é praticar com exemplos simples e diretos, sem sobrecarga de código.
>
> Projeto utilizado: [Revisão](https://github.com/i-davies/revisao_perceptron).

---

## Objetivo da Revisão

Ao final da trilha, você deve conseguir:

- identificar dados faltantes e duplicados
- tratar nulos com regras simples
- detectar outliers com IQR
- gerar uma base limpa pronta para engenharia de atributos

---

## Estrutura dos Notebooks

Dentro da pasta `revisao_dados`, use os notebooks nesta ordem:

- `01_revisao_ciclo_dados.ipynb`: ciclo completo de leitura, diagnóstico e limpeza
- `03_revisao_onehot_scaler.ipynb`: normalização e codificação de categorias
- `04_revisao_fit_transform.ipynb`: diferença entre fit e transform com pipeline simples

!!! info "Dica de Aula"
    Execute uma célula por vez e sempre observe a saída antes de continuar.
    O objetivo é entender o motivo de cada transformação.

---

## Fluxo Simples de ETL

No primeiro notebook, siga este roteiro:

- carregar um DataFrame pequeno com erros propositalmente inseridos
- medir nulos, duplicatas e estatísticas básicas
- aplicar limpeza com regras didáticas
- validar a qualidade final do DataFrame

??? tip "Regra de Ouro"
    Dados bons geram modelos melhores. Um modelo simples com base limpa costuma performar melhor do que um modelo complexo com base suja.

---

## Prática Recomendada

Repita os passos alterando manualmente alguns valores:

- adicione um novo valor nulo e veja o impacto no relatório
- aumente um valor extremo de `tempo` e veja se o IQR detecta
- troque categorias em `tipo_entrega` e observe o efeito no encoding

---

## Exercícios de Fixação

<quiz>
Qual objetivo principal da etapa de preparação de dados antes do modelo?

* [ ] Aumentar a quantidade de código no projeto.
* [x] Garantir consistência e qualidade dos dados de entrada.
* [ ] Eliminar completamente a necessidade de avaliação de resultados.
</quiz>

<quiz>
Quando encontramos valores nulos em colunas numéricas, uma estratégia simples de sala é:

* [ ] Multiplicar todos os valores por zero.
* [x] Preencher com mediana ou média, conforme o contexto.
* [ ] Converter a coluna para texto e ignorar os nulos.
</quiz>

<quiz>
No contexto desta revisão, para que usamos o IQR?

* [ ] Para ordenar colunas alfabeticamente.
* [ ] Para criar novos endpoints automaticamente.
* [x] Para detectar valores muito distantes do comportamento central dos dados.
</quiz>
