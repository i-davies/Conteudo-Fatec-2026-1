# Revisão: Redes Neurais com Scikit-Learn

Com os dados limpos e transformados, é hora de colocar o modelo para trabalhar.
Esta revisão mostra de forma direta como treinar e usar uma rede neural simples com o scikit-learn.
>
> Projeto utilizado: [Revisão](https://github.com/i-davies/revisao_perceptron).

---

## Objetivo da Revisão

Ao final, você deve conseguir:

- entender por que o Perceptron não resolve todos os problemas
- treinar um `MLPClassifier` com dados simples
- organizar treino e predição em uma classe reutilizável
- aplicar redes neurais em exemplos tabulares e em imagens
- salvar, carregar e prever em novos dados sem re-treinar a cada requisição

---

## Continuando no Mesmo Repositório

Não é necessário criar um novo projeto. Continue usando a mesma pasta `revisao_perceptron` dos notebooks anteriores.

Instale as dependências novas:

```bash
uv add scikit-learn matplotlib
```

Crie um novo notebook chamado `revisao_mlp.ipynb` dentro da mesma pasta.

!!! info "Dica de Aula"
    Execute uma célula por vez e observe o que cada etapa produz.
    O objetivo é entender o fluxo: treino → salvamento → previsão.

---

## O Que Muda em Relação ao Perceptron

O Perceptron traça uma linha reta para separar os dados.
Quando os dados não cabem em uma linha reta, ele falha.

A rede neural (MLP) resolve isso adicionando camadas intermediárias que aprendem padrões mais complexos, sem a limitação da linha reta.

??? tip "Analogia Rápida"
    O Perceptron é como uma régua: só traça linhas retas.
    A rede neural é como uma borracha de modelar: se adapta a qualquer formato.

---

## Estrutura do Notebook

Use o notebook nesta ordem:

- `revisao_mlp.ipynb` (Parte 1): fluxo básico com dados de crédito (treino, save, load e predict)
- `revisao_mlp.ipynb` (Parte 2): classe `MiniMLPClassifier` para organizar uso no dia a dia
- `revisao_mlp.ipynb` (Parte 3): exemplo tabular real com `load_wine`
- `revisao_mlp.ipynb` (Parte 4): exemplo com imagens usando `load_digits`

---

## Fluxo do Notebook

O notebook segue este roteiro simples:

1. montar uma base pequena de crédito (aprovação/reprovação)
2. treinar o `MLPClassifier` e salvar com `joblib`
3. carregar e prever em novos clientes
4. encapsular a lógica em uma classe `MiniMLPClassifier`
5. aplicar a mesma classe em um dataset tabular real (`load_wine`)
6. aplicar em imagens (`load_digits`) para reconhecer dígitos

---

## Visualizando Imagens do Scikit-Learn

Para datasets que já possuem imagens (como `load_digits`), a visualização é direta:

- carregar com `load_digits()`
- acessar `dataset.images[i]`
- plotar com `plt.imshow(..., cmap="gray")`
- mostrar o rótulo com `dataset.target[i]`

Exemplo mínimo:

```python
from sklearn.datasets import load_digits
import matplotlib.pyplot as plt

dataset = load_digits()
i = 0

plt.imshow(dataset.images[i], cmap="gray")
plt.title(f"Rótulo real: {dataset.target[i]}")
plt.axis("off")
plt.show()
```

Se quiser mostrar várias imagens de uma vez, use `plt.subplots()` e percorra com `for`.

---

## Resultado Esperado

Ao terminar o notebook, você deve observar:

- o modelo treinado e salvo em arquivo
- previsões corretas para clientes novos
- reutilização com classe para cenários diferentes
- acurácia em um caso tabular real (`load_wine`)
- reconhecimento de dígitos em imagens (`load_digits`)
- entendimento de que `fit()` só acontece no treino; depois usamos `predict()`

---

## Exercícios de Fixação

<quiz>
Por que o Perceptron não consegue resolver problemas como o XOR?

* [ ] Porque ele é muito lento para calcular.
* [x] Porque ele só consegue separar dados com uma linha reta.
* [ ] Porque ele não aceita mais de uma entrada.
</quiz>

<quiz>
O que é o `MLPClassifier` do scikit-learn?

* [ ] Uma ferramenta para limpar dados faltantes.
* [ ] Um algoritmo que só funciona com dados categóricos.
* [x] Uma rede neural que aprende padrões não-lineares para classificar dados.
</quiz>

<quiz>
Qual prática está correta ao usar o modelo em produção?

* [ ] Executar `fit()` a cada nova previsão para manter o modelo atualizado.
* [x] Carregar o modelo salvo e usar apenas `predict()` nos novos dados.
* [ ] Ignorar o arquivo salvo e recriar o modelo do zero sempre que necessário.
</quiz>

<quiz>
No exemplo com imagens (`load_digits`), o que a rede neural recebe na entrada?

* [ ] A imagem colorida original em alta resolução.
* [x] Um vetor numérico com os pixels da imagem (8x8 = 64 valores).
* [ ] Apenas o nome textual do dígito ("zero", "um", "dois"...).
</quiz>
