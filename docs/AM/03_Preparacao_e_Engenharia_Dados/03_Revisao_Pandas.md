# Revisao: Preparacao de Dados com Pandas

Esta revisao isola os conceitos da etapa de ETL em uma sequencia de notebooks pequenos.
A ideia aqui e praticar com exemplos simples e diretos, sem sobrecarga de codigo.

---

## Objetivo da Revisao

Ao final da trilha, voce deve conseguir:

- identificar dados faltantes e duplicados
- tratar nulos com regras simples
- detectar outliers com IQR
- gerar uma base limpa pronta para engenharia de atributos

---

## Estrutura dos Notebooks

Dentro da pasta `revisao_dados`, use os notebooks nesta ordem:

- `01_revisao_ciclo_dados.ipynb`: ciclo completo de leitura, diagnostico e limpeza
- `03_revisao_onehot_scaler.ipynb`: normalizacao e codificacao de categorias
- `04_revisao_fit_transform.ipynb`: diferenca entre fit e transform com pipeline simples

!!! info "Dica de Aula"
    Execute uma celula por vez e sempre observe a saida antes de continuar.
    O objetivo e entender o motivo de cada transformacao.

---

## Fluxo Simples de ETL

No primeiro notebook, siga este roteiro:

- carregar um DataFrame pequeno com erros propositalmente inseridos
- medir nulos, duplicatas e estatisticas basicas
- aplicar limpeza com regras didaticas
- validar a qualidade final do DataFrame

??? tip "Regra de Ouro"
    Dados bons geram modelos melhores. Um modelo simples com base limpa costuma performar melhor do que um modelo complexo com base suja.

---

## Pratica Recomendada

Repita os passos alterando manualmente alguns valores:

- adicione um novo valor nulo e veja o impacto no relatorio
- aumente um valor extremo de `tempo` e veja se o IQR detecta
- troque categorias em `tipo_entrega` e observe o efeito no encoding

---

## Exercicios de Fixacao

<quiz>
Qual objetivo principal da etapa de preparacao de dados antes do modelo?

* [ ] Aumentar a quantidade de codigo no projeto.
* [x] Garantir consistencia e qualidade dos dados de entrada.
* [ ] Eliminar completamente a necessidade de avaliacao de resultados.
</quiz>

<quiz>
Quando encontramos valores nulos em colunas numericas, uma estrategia simples de sala e:

* [ ] Multiplicar todos os valores por zero.
* [x] Preencher com mediana ou media, conforme o contexto.
* [ ] Converter a coluna para texto e ignorar os nulos.
</quiz>

<quiz>
No contexto desta revisao, para que usamos o IQR?

* [ ] Para ordenar colunas alfabeticamente.
* [ ] Para criar novos endpoints automaticamente.
* [x] Para detectar valores muito distantes do comportamento central dos dados.
</quiz>
