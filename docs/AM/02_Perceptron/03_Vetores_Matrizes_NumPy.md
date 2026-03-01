# Vetores, Matrizes e NumPy

Este guia mostra como evoluímos nosso Perceptron "engessado" (variáveis soltas) para uma versão que usa **vetores** e **NumPy**, capaz de processar **várias músicas de uma vez**.

---

## Recapitulando: O Problema

### Onde paramos

Na semana passada, criamos um Perceptron que decide "Festa" ou "Relax":

```python
def predict(self, energy, loudness):
    loudness_norm = (loudness + 10) / 10
    z = (energy * w_energy) + (loudness_norm * w_loudness) + bias
    return 1 if z >= 0.5 else 0
```

Funciona! Mas tem um problema...

### E se quisermos mais features?

O Spotify nos dá **12 métricas** por música. Se quisermos usar 4 delas:

```python
# Código não escalável
def predict(self, energy, loudness, danceability, tempo):
    z = (energy * w1) + (loudness * w2) + (danceability * w3) + (tempo * w4) + bias
```

E se forem 12? Ou 100? Variáveis soltas **não escalam**.

### A solução: Vetores

Em vez de `x1, x2, x3...`, agrupamos tudo numa **lista ordenada**:

```python
# Um vetor de entradas
X = [energy, loudness_norm]

# Um vetor de pesos
W = [0.8, 0.2]
```

A conta vira um **produto escalar**: multiplica par com par e soma tudo.

??? tip "O que é Produto Escalar?"
    É uma forma de calcular o "total" entre dois grupos de números. Em vez de fazer várias contas separadas, multiplicamos os pares correspondentes e somamos tudo no final.

    **Exemplo Simples:**
    Entradas (X): `[2, 3]`
    Pesos (W): `[10, 5]`

    * Multiplica os primeiros: `2 * 10 = 20`
    * Multiplica os segundos: `3 * 5 = 15`
    * Soma tudo: `20 + 15 = 35`

    O resultado do produto escalar entre X e W é **35**. No Perceptron, usamos isso para calcular a influência de todas as entradas de uma vez.




```
z = (X[0] * W[0]) + (X[1] * W[1]) + bias
```

Ou, em notação matemática: `z = X · W + b`

---

## De Variáveis Soltas para Vetores

### O que muda no código?

Vamos comparar o "antes" e o "depois":

```diff
  # ANTES (Semana 02) — variáveis soltas, cálculo manual
- z = (energy * w_energy) + (loudness_norm * w_loudness) + bias

  # DEPOIS (Semana 03) — vetores + produto escalar
+ X = np.array([energy, loudness_norm])
+ z = np.dot(X, self.weights) + self.bias
```

A fórmula é **a mesma**. Mas agora, se quisermos 4, 10 ou 100 features, **não mudamos nada** — só aumentamos o tamanho dos vetores.

### Por que NumPy e não um Loop?

Python puro é lento para contas com listas:

```python
# Lento — Python faz uma operação por vez
total = 0
for i in range(len(X)):
    total += X[i] * W[i]
```

O **NumPy** usa código em C por baixo dos panos — faz a conta **toda de uma vez**:

```python
# Rápido — NumPy faz tudo de uma vez (vetorização)
total = np.dot(X, W)
```

---

## Refatorando o Perceptron com NumPy

### Criando o novo modelo

**Passo 1**: Crie o arquivo `src/models/perceptron_numpy.py`.

**Passo 2**: Defina a classe. Observe como os pesos agora são um `np.array` em vez de um dicionário:

??? tip "O que é `np.array`?"
    Pense no `np.array` como uma "super lista". Ao contrário das listas comuns do Python, o array do NumPy foi feito exclusivamente para matemática. Ele guarda os números de forma organizada na memória, o que permite que o computador faça contas com milhares de itens muito mais rápido.


```python
import numpy as np


class PerceptronNumpy:
    """
    Perceptron refatorado com NumPy (Semana 03).
    Mesma lógica, mas com vetores e produto escalar.
    """

    def __init__(self, weights=None, bias=0.1):
        # Pesos padrão: [energy, loudness]
        # Mesmos valores da semana anterior, agora como vetor NumPy
        default_weights = [0.8, 0.2]

        if weights is not None:
            self.weights = np.array(weights, dtype=float)
        else:
            self.weights = np.array(default_weights, dtype=float)

        self.bias = bias
```

**Passo 3**: O método `predict` — mesma lógica, agora com `np.dot`:

??? tip "O que é `np.dot`?"
    É a função do NumPy que faz o **Produto Escalar** que vimos anteriormente. Em vez de você escrever um `for` para multiplicar e somar cada peso, o `np.dot(X, W)` faz todo esse trabalho pesado em uma única linha de código.


```python
    def _normalizar_loudness(self, loudness):
        """Normaliza loudness de dB (-60..0) para escala comparável."""
        return (loudness + 10) / 10

    def predict(self, energy, loudness):
        """
        Antes:  z = (energy * w1) + (loudness_norm * w2) + bias
        Agora:  z = np.dot(X, W) + bias
        """
        loudness_norm = self._normalizar_loudness(loudness)

        # Monta o vetor de entradas
        X = np.array([energy, loudness_norm])

        # Produto escalar: substitui a soma manual
        z = np.dot(X, self.weights) + self.bias

        prediction = 1 if z >= 0.5 else 0

        return {
            "prediction": prediction,
            "activation": float(z),
            "normalized_loudness": float(loudness_norm),
        }
```

*Teste: deve dar o **mesmo resultado** que o Perceptron da semana passada!*

### Predição em Lote (Batch)

Agora a parte nova. Em vez de classificar **uma** música, classificamos **várias de uma vez**.

A ideia: se cada música é um **vetor** (uma linha), várias músicas formam uma **matriz** (várias linhas).

!!! info "Como o computador enxerga o Lote (Batch)"
    Em vez de processar uma música por vez, o NumPy recebe a "tabela" inteira e aplica os pesos em um único passo:

    | Músicas (Matriz) | Pesos (W) | Bias (b) | Resultados (Z) |
    | :--- | :---: | :---: | :--- |
    | `[ 0.90,  0.60 ]` | | | → **0.93** (Festa) |
    | `[ 0.20, -0.50 ]` | **x [ 0.8, 0.2 ]** | **+ 0.1** | → **0.16** (Relax) |
    | `[ 0.85,  0.70 ]` | | | → **0.92** (Festa) |

    O `np.dot` faz todo esse trabalho matemático de uma só vez, o que é muito mais rápido do que fazer um loop `for`.


`np.dot` com uma **matriz** calcula **todas as ativações de uma vez**, sem loop!

**Passo 4**: O método `predict_batch`:

```python
    def predict_batch(self, lista_de_musicas):
        """
        Predição para VÁRIAS músicas de uma vez.
        Cada item é [energy, loudness].
        """
        X = np.array(lista_de_musicas, dtype=float)

        # Normaliza a coluna de loudness (coluna 1)
        X[:, 1] = (X[:, 1] + 10) / 10

        # Multiplicação Matriz-Vetor: UMA linha faz o trabalho de N iterações!
        Z = np.dot(X, self.weights) + self.bias

        # Função de ativação vetorizada (sem loop!)
        predictions = (Z >= 0.5).astype(int)

        # Monta a lista de resultados
        return {
            "prediction": predictions,
            "activation": Z,
            "normalized_loudness": X[:, 1],
        }
```

---

## Schemas para o Batch

Precisamos de novos schemas para aceitar **uma lista de músicas** na API.

**Passo 1**: Abra `src/schemas.py` e adicione **abaixo** dos schemas existentes:

```python
# Schemas para Batch (Semana 03)
# Reutiliza MusicFeatures (mesmas 2 features: energy + loudness)

class BatchTrackItem(BaseModel):
    """Uma música dentro de um lote (batch)."""
    track_name: str
    artist_name: str
    features: MusicFeatures   # Reutiliza o que já existe!


class TrackBatchRequest(BaseModel):
    """Requisição com várias músicas de uma vez."""
    tracks: list[BatchTrackItem]


class TrackBatchResponse(BaseModel):
    """Resposta com o resultado de todas as músicas."""
    results: list[TrackResponse]
    total: int
    summary: dict
```

*Observe: reutilizamos o `MusicFeatures` e `TrackResponse` que já existiam!*

---

## Endpoint de Batch na API

### Atualizando a rota

**Passo 1**: Atualize os imports em `src/api/v1/recommendation.py`:

```python
from src.schemas import (
    TrackRequest, TrackResponse,
    TrackBatchRequest, TrackBatchResponse,
)
from src.models.perceptron_numpy import PerceptronNumpy
```

**Passo 2**: Adicione a injeção de dependência:

```python
@lru_cache
def get_perceptron_numpy() -> PerceptronNumpy:
    return PerceptronNumpy()
```

**Passo 3**: Crie o endpoint:

```python
@router.post("/recommend/predict-batch", response_model=TrackBatchResponse)
def predict_batch(request: TrackBatchRequest, model: PerceptronNumpy = Depends(get_perceptron_numpy)):
    """Predição para VÁRIAS músicas de uma vez (Perceptron NumPy)."""

    # 1. Monta a matriz: cada linha é [energy, loudness]
    features_matrix = [
        [t.features.energy, t.features.loudness]
        for t in request.tracks
    ]

    # 2. Predição em lote via NumPy (np.dot, sem loop)
    batch_results = model.predict_batch(features_matrix)

    # 3. Monta a resposta
    results = []
    festa_count = 0


    # Extrai os arrays resultantes do dicionário
    predictions = batch_results["prediction"].tolist()
    activations = batch_results["activation"].tolist()
    loudnesses = batch_results["normalized_loudness"].tolist()

    for i, track in enumerate(request.tracks):
        pred_val = predictions[i]
        mood = "Festa/Agitada" if pred_val == 1 else "Relax/Calma"
        if pred_val == 1:
            festa_count += 1
            
        debug_info = {
            "prediction": pred_val,
            "activation": activations[i],
            "normalized_loudness": loudnesses[i]
        }
            
        results.append({
            "track": track.track_name,
            "artist": track.artist_name,
            "recommendation": mood,
            "debug_info": debug_info,
        })

    total = len(results)
    return {
        "results": results,
        "total": total,
        "summary": {"festa": festa_count, "relax": total - festa_count},
    }
```

---

## Testando

### Subindo o servidor

```bash
uv run fastapi dev
```

### Testando o endpoint individual

Abra `http://127.0.0.1:8000/docs` → `POST /api/v1/recommend/predict`:

```json
{
  "track_name": "Mr. Brightside",
  "artist_name": "The Killers",
  "features": {
    "energy": 0.93,
    "loudness": -3.76
  }
}
```

*Deve retornar "Festa/Agitada", exatamente como antes.*

### Testando o Batch

`POST /api/v1/recommend/predict-batch`:

```json
{
  "tracks": [
    {
      "track_name": "Mr. Brightside",
      "artist_name": "The Killers",
      "features": {"energy": 0.93, "loudness": -3.76}
    },
    {
      "track_name": "Chasing Cars",
      "artist_name": "Boyce Avenue",
      "features": {"energy": 0.33, "loudness": -8.9}
    },
    {
      "track_name": "Para Reiki: Gotas de Agua",
      "artist_name": "Artista",
      "features": {"energy": 0.92, "loudness": -32.79}
    }
  ]
}
```

**Resultado esperado:**
- "Mr. Brightside" → **Festa/Agitada**
- "Chasing Cars" → **Relax/Calma**
- "Gotas de Agua" → **Relax/Calma** (a pegadinha! Energy alta mas loudness muito baixo)

---

## Exercício de Fixação: Loop vs NumPy

??? example "Meça a diferença de performance!"

    Abra o notebook `notebooks/03_perceptron_numpy.ipynb` e siga os passos abaixo:

    **Passo 1**: Gere músicas aleatórias:

    ```python
    import numpy as np
    import time
    import sys, os
    sys.path.append(os.path.abspath('..'))

    from src.models.perceptron import Perceptron
    from src.models.perceptron_numpy import PerceptronNumpy

    np.random.seed(42)
    N = 10_000

    energy = np.random.uniform(0, 1, N)
    loudness = np.random.uniform(-60, 0, N)
    ```

    **Passo 2**: Meça o loop Python:

    ```python
    modelo_antigo = Perceptron()

    inicio = time.time()
    for i in range(N):
        modelo_antigo.predict(energy=energy[i], loudness=loudness[i])
    fim = time.time()

    print(f"Loop Python ({N} músicas): {fim - inicio:.4f}s")
    ```

    **Passo 3**: Meça o NumPy:

    ```python
    modelo_numpy = PerceptronNumpy()

    # Monta a matriz (N, 2): cada linha é [energy, loudness]
    X = np.column_stack([energy, loudness])

    inicio = time.time()
    modelo_numpy.predict_batch(X)
    fim = time.time()

    print(f"NumPy Batch  ({N} músicas): {fim - inicio:.4f}s")
    ```

    ---

    ### Perguntas para Reflexão

    1. Qual foi a diferença de tempo?
    2. Se aumentarmos para 100.000 músicas, a diferença cresce ou diminui?
    3. Por que o NumPy é mais rápido fazendo a "mesma" operação?

---

**Parabéns!** Você refatorou o Perceptron de variáveis soltas para vetores NumPy e criou um endpoint que processa lotes inteiros de músicas de uma vez.
