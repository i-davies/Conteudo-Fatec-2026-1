# Revisão: KNN - K-Vizinhos Mais Próximos

Esta revisão consolida os conceitos de classificação por vizinhança vistos em aula,
com exemplos simples e diretos ao ponto.
>
> Projeto utilizado: [Revisão](https://github.com/i-davies/revisao_perceptron).
---

## Objetivo da Revisão

Ao final, você deve conseguir:

- calcular a distância euclidiana entre dois pontos
- entender como o KNN usa distância para votar e classificar
- treinar e usar `KNeighborsClassifier` do scikit-learn
- entender por que normalizar os dados é obrigatório no KNN
- usar `NearestNeighbors` para recomendação por similaridade
- salvar e carregar um modelo treinado com `joblib`

---

## Ambiente

Continue usando o mesmo ambiente dos notebooks anteriores.

Se precisar instalar as dependências:

```bash
uv add scikit-learn pandas joblib
```

Crie uma pasta chamada `revisao_knn/` e abra os notebooks dentro dela.

!!! info "Dica"
    Execute uma célula por vez e observe o que cada etapa produz.
    O objetivo é entender o fluxo, não memorizar código.

---

## O Que Muda em Relação à MLP

A MLP aprende pesos durante o treino e aplica uma função matemática para decidir.

O KNN não aprende nada durante o treino: ele apenas memoriza os dados.
Na predição, calcula a distância para todos os pontos e vota.

??? tip "Analogia"
    A MLP é como um especialista que estudou muito e responde de memória.
    O KNN é como alguém que olha ao redor e pergunta: "quem está mais perto de mim?"

---

## Estrutura dos Notebooks

**`revisao_knn.ipynb`**

- Distância euclidiana calculada na mão
- KNN manual: ordenar por distância e votar
- `KNeighborsClassifier` do scikit-learn
- Testando K = 1, 3 e 5 no mesmo exemplo

**`revisao_knn_recomendacao.ipynb`** 

- Por que a falta de normalização quebra o KNN
- `StandardScaler` para colocar features na mesma escala
- Pipeline completo: scaler + modelo + save + load
- `NearestNeighbors` para recomendação por similaridade
