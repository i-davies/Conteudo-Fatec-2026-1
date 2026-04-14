# Revisao: Engenharia de Atributos com Scikit-Learn

Agora que os dados estao limpos, vamos transformar tudo para um formato adequado ao modelo.
Esta etapa foca em duas ideias centrais: escalonamento numerico e codificacao de categorias.

---

## Objetivo da Revisao

Ao final, voce deve dominar:

- quando usar MinMaxScaler
- quando usar OneHotEncoder
- por que fit e transform nao sao a mesma coisa
- como salvar e carregar o transformador para manter consistencia

---

## Ordem Didatica

Use os notebooks finais da trilha:

- `03_revisao_onehot_scaler.ipynb`: aplica MinMaxScaler e OneHotEncoder em um exemplo pequeno
- `04_revisao_fit_transform.ipynb`: mostra um mini fluxo de treino e uso em producao

!!! important "Ponto Critico"
    Em producao, a API deve reutilizar o mesmo transformador ja treinado.
    Nao devemos recalcular fit a cada requisicao.

---

## Fit e Transform de Forma Simples

Pense desta forma:

- `fit`: aprende regras do conjunto de treino
- `transform`: aplica as regras aprendidas em novos dados

Se o sistema fizer `fit` toda hora, os limites mudam e as entradas ficam inconsistentes.

??? tip "Analogia Rapida"
    O fit e como criar uma regua padrao.
    O transform e usar sempre essa mesma regua para medir novos itens.

---

## Resultado Esperado

Ao terminar os notebooks, voce deve observar:

- colunas numericas em escala comparavel (0 a 1)
- colunas categoricas convertidas para formato binario
- matriz final pronta para alimentar um modelo de classificacao

---

## Exercicios de Fixacao

<quiz>
Qual problema o MinMaxScaler ajuda a resolver?

* [ ] Criar categorias textuais automaticamente.
* [x] Colocar variaveis numericas em escala comparavel.
* [ ] Remover todas as colunas categoricas do dataset.
</quiz>

<quiz>
Por que usamos OneHotEncoder em categorias como tipo de entrega ou forma de pagamento?

* [ ] Para transformar texto em uma escala ordinal fixa.
* [x] Para evitar ordem artificial entre categorias.
* [ ] Para substituir todas as colunas por uma unica media.
</quiz>

<quiz>
Qual pratica esta correta para APIs em producao?

* [ ] Executar fit em toda nova requisicao.
* [ ] Ignorar o transformador salvo para evitar I/O.
* [x] Carregar o transformador treinado e aplicar apenas transform.
</quiz>
