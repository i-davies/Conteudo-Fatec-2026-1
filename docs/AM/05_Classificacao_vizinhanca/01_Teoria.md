# Classificação por Vizinhança (KNN)

"Diga-me com quem andas e te direi quem és."

Nas semanas anteriores (Semanas 06 e 07), exploramos Redes Neurais (MLP) para prever se uma música seria curtida ou não. Agora vamos conhecer um algoritmo com outra filosofia: o K-Nearest Neighbors (KNN), ou K-Vizinhos Mais Próximos.

---

## O que é o KNN

O KNN é um dos algoritmos mais simples e intuitivos de Machine Learning. Diferente da MLP, que aprende pesos e padrões abstratos, o KNN trabalha por proximidade.

### Aprendizado preguiçoso (lazy learning)

No KNN, não há uma fase pesada de treino para ajustar milhares de parâmetros. O algoritmo basicamente memoriza os dados de treinamento e decide na hora da predição.

- MLP (eager learner): aprende as regras antes e responde rápido depois.
- KNN (lazy learner): consulta os exemplos mais parecidos na hora de responder.

!!! important "Mudança de foco"
    Na MLP, a pergunta era: "o usuário vai gostar desta música?".
    No KNN, a pergunta pode ser: "quais músicas são mais parecidas com esta?".
    Essa lógica é a base de muitos sistemas de recomendação.

---

## Quando usar KNN

Use KNN quando:

- A interpretabilidade é importante.
- O dataset é pequeno ou médio.
- O problema depende de similaridade entre exemplos.

Em recomendação musical, se duas músicas são parecidas em danceability, energy, valence e tempo, elas tendem a ser boas candidatas para recomendação entre si.

---

## KNN versus MLP

| Característica | MLP | KNN |
|---|---|---|
| Filosofia | Aprende pesos | Procura vizinhos |
| Treinamento | Mais lento | Rápido (memorização) |
| Predição | Rápida | Mais lenta (cálculo de distâncias) |
| Explicabilidade | Menor | Maior |
| Memória | Guarda pesos | Guarda dados |

---

## Intuição do algoritmo

Imagine que você está na cantina sem saber o que pedir:

- Você observa as pessoas mais próximas.
- Se a maioria está comendo pizza, você tende a escolher pizza.

Isso é KNN.

- Com K = 1, decide pelo vizinho mais próximo.
- Com K = 3 ou K = 5, decide por votação da maioria.

!!! tip "Regra prática"
    K muito baixo tende a ser sensível a ruído.
    K muito alto tende a ignorar detalhes locais.
    Em geral, começamos testando K ímpares como 3, 5 e 7.

---

## Distância e proximidade

O coração do KNN é a distância entre pontos no espaço de features.

### Distância Euclidiana

$$
  d_{euclidiana} = \sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2}
$$

Interpreta a menor distância em linha reta entre dois pontos.

### Aplicação do Teorema de Pitágoras no KNN

No plano cartesiano, podemos ver dois pontos como os vértices de um triângulo retângulo:

- Cateto horizontal: $\Delta x = x_1 - x_2$
- Cateto vertical: $\Delta y = y_1 - y_2$
- Hipotenusa: distância reta entre os pontos

Pelo Teorema de Pitágoras:

$$
    h^2 = (\Delta x)^2 + (\Delta y)^2
$$

Logo:

$$
    h = \sqrt{(\Delta x)^2 + (\Delta y)^2}
$$

Essa hipotenusa $h$ é exatamente a distância euclidiana usada no KNN para medir proximidade.

Exemplo rápido:

- Ponto A = (1, 2)
- Ponto B = (4, 6)
- $\Delta x = 4 - 1 = 3$
- $\Delta y = 6 - 2 = 4$
- $d = \sqrt{3^2 + 4^2} = \sqrt{9 + 16} = \sqrt{25} = 5$

### Distância Manhattan

$$
  d_{manhattan} = |x_1 - x_2| + |y_1 - y_2|
$$

Interpreta um caminho em "L", como deslocamento em quarteirões.


Interpretação didática:

- Distância Euclidiana: vai em linha reta de A até B.
- Distância Manhattan: anda "em quarteirões", primeiro no eixo X e depois no eixo Y.

Valores do exemplo:

- Euclidiana: $\sqrt{3^2 +4^2} = 5$
- Manhattan: $|3| + |4| = 7$

!!! tip "Custo de processamento"
    No KNN, para cada música consultada, calculamos a distância para vários pontos do dataset.
    Em termos de custo computacional por par de pontos, Euclidiana e Manhattan são parecidas em ordem de grandeza.
    Porém, na prática:

    - Manhattan costuma ser um pouco mais barata: usa subtração, valor absoluto e soma.
    - Euclidiana costuma ser um pouco mais cara: além disso, envolve quadrado e raiz quadrada.
    - No geral, a escolha entre elas é mais sobre qualidade da vizinhança do que ganho grande de velocidade.

| Tipo | Como funciona | Uso comum |
|---|---|---|
| Euclidiana | Linha reta | Padrão na maioria dos casos |
| Manhattan | Soma de deslocamentos absolutos | Casos com eixos muito independentes |

!!! note "Qual métrica usar"
    Na maior parte dos cenários desta disciplina, a distância euclidiana atende bem e será o padrão.

---

## Efeito do valor de K

| Valor de K | Comportamento | Risco |
|---|---|---|
| Muito baixo | Fronteira recortada | **Overfitting** (decora os dados de treino, erra em dados novos) |
| Intermediário | Equilíbrio local/global | Melhor generalização |
| Muito alto | Fronteira simplificada | **Underfitting** (simplifica demais, não captura padrões relevantes) |

!!! tip "Evitar empate"
    Em classificação binária, valores ímpares de K ajudam a reduzir empates na votação.

---

## Importância da normalização

KNN depende diretamente de distância. Se uma feature estiver em escala maior, ela domina a conta.

Exemplo:

- danceability: 0 a 1
- energy: 0 a 1
- tempo: 50 a 250

Sem normalizar, pequenas variações de tempo podem pesar mais que variações relevantes de danceability e energy.

A solução é aplicar `StandardScaler` antes do KNN, colocando as features em escala comparável.

!!! important "Regra para KNN"
    Sempre normalize as features antes de treinar e prever.

---

## KNN no projeto da disciplina

Nesta semana, o KNN entra com duas utilidades:

- Classificação multiclasse: prever gênero musical.
- Recomendação por similaridade: recuperar músicas próximas.

Comparando com o que já construímos:

| Semana | Modelo | Tipo | Pergunta |
|---|---|---|---|
| 06 | MLP classificador | Classificação binária | Curtida ou não? |
| 07 | MLP regressor | Regressão | Qual score? |
| 09 | KNN | Classificação multiclasse e recomendação | Qual gênero? Quais similares? |

---

## Exercícios de fixação

<quiz>
KNN é considerado um algoritmo de aprendizado preguiçoso porque:

* [x] Ele deixa o trabalho pesado para a fase de predição.
* [ ] Ele não usa dados de treino.
* [ ] Ele não funciona para classificação.
</quiz>

<quiz>
Qual afirmação sobre normalização no KNN está correta?

* [x] Sem normalização, features com escala maior podem dominar a distância.
* [ ] A normalização só melhora visualizações e não afeta o modelo.
* [ ] KNN não usa distância, então normalização é opcional.
</quiz>

<quiz>
Sobre o parâmetro K, a alternativa correta é:

* [x] K muito baixo pode overfitar; K muito alto pode underfitar.
* [ ] Quanto maior K, melhor em qualquer dataset.
* [ ] O valor de K não impacta a fronteira de decisão.
</quiz>
