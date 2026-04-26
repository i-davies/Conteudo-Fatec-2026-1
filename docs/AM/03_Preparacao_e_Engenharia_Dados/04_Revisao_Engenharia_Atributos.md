# Revisão: Engenharia de Atributos com Scikit-Learn

Agora que os dados estão limpos, vamos transformar tudo para um formato adequado ao modelo.
Esta etapa foca em duas ideias centrais: escalonamento numérico e codificação de categorias.
>
> Projeto utilizado: [Revisão](https://github.com/i-davies/revisao_perceptron).

---

## Objetivo da Revisão

Ao final, você deve dominar:

- quando usar MinMaxScaler
- quando usar OneHotEncoder
- por que fit e transform não são a mesma coisa
- como salvar e carregar o transformador para manter consistência

---

## Ordem Didática

Use os notebooks finais da trilha:

- `03_revisao_onehot_scaler.ipynb`: aplica MinMaxScaler e OneHotEncoder em um exemplo pequeno
- `04_revisao_fit_transform.ipynb`: mostra um mini fluxo de treino e uso em produção

!!! important "Ponto Crítico"
    Em produção, a API deve reutilizar o mesmo transformador já treinado.
    Não devemos recalcular fit a cada requisição.

---

## Fit e Transform de Forma Simples

Pense desta forma:

- `fit`: aprende regras do conjunto de treino
- `transform`: aplica as regras aprendidas em novos dados

Se o sistema fizer `fit` toda hora, os limites mudam e as entradas ficam inconsistentes.

??? tip "Analogia Rápida"
    O fit é como criar uma régua padrão.
    O transform é usar sempre essa mesma régua para medir novos itens.

---

## Resultado Esperado

Ao terminar os notebooks, você deve observar:

- colunas numéricas em escala comparável (0 a 1)
- colunas categóricas convertidas para formato binário
- matriz final pronta para alimentar um modelo de classificação

---

## Exercícios de Fixação

<quiz>
Qual problema o MinMaxScaler ajuda a resolver?

* [ ] Criar categorias textuais automaticamente.
* [x] Colocar variáveis numéricas em escala comparável.
* [ ] Remover todas as colunas categóricas do dataset.
</quiz>

<quiz>
Por que usamos OneHotEncoder em categorias como tipo de entrega ou forma de pagamento?

* [ ] Para transformar texto em uma escala ordinal fixa.
* [x] Para evitar ordem artificial entre categorias.
* [ ] Para substituir todas as colunas por uma única média.
</quiz>

<quiz>
Qual prática está correta para APIs em produção?

* [ ] Executar fit em toda nova requisição.
* [ ] Ignorar o transformador salvo para evitar I/O.
* [x] Carregar o transformador treinado e aplicar apenas transform.
</quiz>
