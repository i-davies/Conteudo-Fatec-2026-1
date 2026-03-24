# MLP — Prática

!!! important "Pré-requisito obrigatório"
    Antes de começar, confirme que você rodou o script da Semana 05:
    ```bash
    uv run python scripts/train_feature_engineer.py
    ```
    Você precisa ter os arquivos:

    - `models/transformers.joblib`
    - `data/processed/dataset_features.csv`
    - `data/processed/dataset_clean.csv`

---

## Construindo o Serviço MLP

> **Objetivo:** Criar a classe `MusicMLPClassifier` método a método, entendendo cada componente antes de adicionar o próximo.

### O que vamos construir

O serviço MLP é o **cérebro** do sistema. Ele encapsula toda a lógica da rede neural em uma classe reutilizável, com cinco responsabilidades claras:

| Método | Responsabilidade |
|--------|-----------------|
| `__init__` | Configura os caminhos para salvar/carregar o modelo |
| `train()` | Treina a rede neural com dados de entrada |
| `predict()` | Faz previsões para novas músicas |
| `evaluate()` | Mede a qualidade do modelo em dados de teste |
| `save()` / `load()` | Persiste o modelo treinado em disco para uso na API |

!!! info "Por que separar em métodos?"
    Em sistemas reais, treino e predição acontecem em momentos diferentes. O treino ocorre **uma vez** (ou periodicamente), gera um arquivo `.joblib` e termina. A API depois **carrega** esse arquivo e usa apenas `predict()`, sem nunca re-treinar. Essa separação é o que torna o sistema viável em produção.

---

### O MLPClassifier (scikit-learn)

Antes de implementar, vamos entender rapidamente o algoritmo que será usado.

O `MLPClassifier` é a implementação de rede neural multicamada do scikit-learn. Ele usa:

- **Backpropagation** para ajustar os pesos.
- **Adam** como otimizador padrão.
- **ReLU** como função de ativação padrão nas camadas ocultas.

Os parâmetros mais importantes são:

| Parâmetro | Valor padrão | O que controla |
|-----------|-------------|----------------|
| `hidden_layer_sizes` | `(100,)` | Arquitetura: número de camadas ocultas e neurônios em cada uma |
| `activation` | `'relu'` | Função de ativação das camadas ocultas |
| `solver` | `'adam'` | Otimizador para atualizar os pesos |
| `max_iter` | `200` | Número máximo de épocas de treino |
| `early_stopping` | `False` | Se `True`, para quando a validação não melhora |
| `validation_fraction` | `0.1` | Fração dos dados de treino usada para validação interna |
| `random_state` | `None` | Semente para reprodutibilidade |


### Estrutura do Arquivo

Crie o arquivo `src/services/mlp_classifier.py` com as importações e a estrutura da classe. **Não adicione nenhum método ainda.**

```python
# src/services/mlp_classifier.py
import numpy as np
import pandas as pd
from pathlib import Path
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report


class MusicMLPClassifier:
    """
    Serviço de classificação usando Rede Neural Multicamada (MLP).
    Prevê se uma música será 'Curtida' (1) ou 'Não Curtida' (0).
    """

    def __init__(self, model_dir: str | Path = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.model_dir / "mlp_model.joblib"
        self.model: MLPClassifier | None = None
```

**Teste — abra um terminal Python e verifique se a importação funciona:**

```python
# No terminal: uv run python
from src.services.mlp_classifier import MusicMLPClassifier
clf = MusicMLPClassifier()
print(clf.model_path)   # deve imprimir: models/mlp_model.joblib
print(clf.model)        # deve imprimir: None
```

Antes de continuar, confirme que não há erros de importação.

---

### Train

Adicione o método `train()` à classe:

```python
    def train(
        self,
        X_train: np.ndarray | pd.DataFrame,
        y_train: np.ndarray | pd.Series,
        hidden_layers: tuple = (64, 32),
        max_iter: int = 300,
        random_state: int = 42,
    ) -> "MusicMLPClassifier":
        print(f"[MLP] Treinando rede neural com arquitetura {hidden_layers}...")
        print(f"[MLP] Features: {X_train.shape[1]} | Amostras: {X_train.shape[0]}")

        self.model = MLPClassifier(
            hidden_layer_sizes=hidden_layers,
            max_iter=max_iter,
            random_state=random_state,
            activation="relu",
            solver="adam",
            early_stopping=True,
            validation_fraction=0.1,
            verbose=False,
        )
        self.model.fit(X_train, y_train)
        self.save()
        print(f"[MLP] Treinamento concluído em {self.model.n_iter_} épocas.")
        return self
```

!!! info "O que `early_stopping=True` faz internamente?"
    O scikit-learn separa automaticamente `validation_fraction` (10%) dos dados de treino como um mini conjunto de validação. A cada época, ele mede a acurácia nesse subconjunto. Se a acurácia **não melhorar** por 10 épocas consecutivas (`n_iter_no_change=10`), o treino para, evitando que a rede continue ajustando pesos para dados que já "decorou".

!!! info "O que `self.model.n_iter_` contém?"
    Após o `fit()`, o atributo `n_iter_` registra em quantas épocas o treinamento realmente terminou. Se `early_stopping=True` for ativado, esse número será menor que `max_iter`.

---

### Save e load

Adicione os dois métodos de persistência **logo após o `train()`:**

```python
    def save(self):
        """Salva o modelo treinado em disco usando joblib."""
        joblib.dump(self.model, self.model_path)
        print(f"[MLP] Modelo salvo em: {self.model_path}")

    def load(self):
        """Carrega o modelo salvo do disco."""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Modelo não encontrado em: {self.model_path}. "
                "Rode 'uv run python scripts/train_mlp.py' primeiro."
            )
        self.model = joblib.load(self.model_path)
        print(f"[MLP] Modelo carregado de: {self.model_path}")
```


!!! info "O que o save() persiste?"
    O arquivo `.joblib` contém o objeto `MLPClassifier` completo: **todos os pesos** das camadas, a arquitetura, os hiperparâmetros e os atributos aprendidos (como `n_iter_`, `classes_`). É tudo que a API precisa para fazer previsões sem re-treinar.

---

### Predict

Adicione o método `predict()`:

```python
    def predict(self, X: np.ndarray | pd.DataFrame) -> dict:
        """
        Faz previsão para novas amostras.

        Retorna dict com:
        - 'predictions': lista de 0/1
        - 'probabilities': probabilidade da classe positiva (liked=1)
        - 'labels': texto legível ('Curtida' ou 'Não Curtida')
        """
        if self.model is None:
            self.load()

        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        prob_liked = probabilities[:, 1]

        labels = ["Curtida" if p == 1 else "Não Curtida" for p in predictions]

        return {
            "predictions": predictions.tolist(),
            "probabilities": prob_liked.tolist(),
            "labels": labels,
        }
```

!!! info "predict() vs predict_proba() — qual a diferença?"

    | Método | O que retorna | Exemplo |
    |--------|--------------|---------|
    | `predict(X)` | A classe vencedora (0 ou 1) | `[1, 0, 1]` |
    | `predict_proba(X)` | A probabilidade de cada classe | `[[0.02, 0.98], [0.87, 0.13], ...]` |

    O `predict_proba()` retorna duas colunas: `[:, 0]` é a probabilidade da classe 0 ("Não Curtida") e `[:, 1]` é a probabilidade da classe 1 ("Curtida"). Usamos apenas `[:, 1]` porque é a informação mais útil para o usuário.

---

### Evaluate

Adicione o último método:

```python
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        """
        Avalia o modelo no conjunto de teste.

        Retorna dict com:
        - 'accuracy': acurácia (float entre 0 e 1)
        - 'report': classification_report completo (string)
        """
        if self.model is None:
            self.load()

        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        report = classification_report(
            y_test, y_pred, target_names=["Não Curtida", "Curtida"]
        )

        return {"accuracy": acc, "report": report}
```

!!! info "O que o classification_report mostra?"
    O `classification_report` exibe quatro métricas por classe: **precision**, **recall**, **f1-score** e **support** (quantidade de amostras). A linha `macro avg` é a média simples entre as classes; `weighted avg` pondera pelo `support`.

    ```
                  precision    recall  f1-score   support
     Não Curtida       1.00      1.00      1.00      9032
         Curtida       1.00      1.00      1.00      8916
    ```

---

### Exploração

1. O que aconteceria se `early_stopping=False` e `max_iter=300`? A rede treinaria por exatamente 300 épocas.
2. Se você mudar `hidden_layers` de `(64, 32)` para `(128, 64, 32)`, o que muda na arquitetura?

---

## Treinando a Rede Neural

> **Objetivo:** Criar o script de treinamento bloco a bloco, entender cada decisão e interpretar os resultados.

### O Pipeline de Treinamento

O script de treino executa um **pipeline linear** de cinco passos:

```
[1] Verificar pré-requisitos
        │
[2] Carregar dataset de features (X)
        │
[3] Criar o label 'liked' (Y)
        │
[4] Dividir em Treino / Teste
        │
[5] Treinar a MLP e avaliar
```

Crie o arquivo `scripts/train_mlp.py` **vazio** e vá adicionando cada bloco a seguir.

---

### Cabeçalho e verificação de pré-requisitos

```python
# scripts/train_mlp.py
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.services.mlp_classifier import MusicMLPClassifier


def main():
    features_path = project_root / "data" / "processed" / "dataset_features.csv"
    clean_path    = project_root / "data" / "processed" / "dataset_clean.csv"

    print("=" * 60)
    print("  [MLP] Treinamento da Rede Neural")
    print("=" * 60)

    if not features_path.exists():
        print(f"\n[ERRO] Arquivo não encontrado: {features_path}")
        print("DICA: Rode 'uv run python scripts/train_feature_engineer.py' primeiro.")
        return

    if not clean_path.exists():
        print(f"\n[ERRO] Arquivo não encontrado: {clean_path}")
        return

    print("\n[OK] Pré-requisitos verificados.")
```

**Execute agora** para confirmar que os arquivos existem:

```bash
uv run python scripts/train_mlp.py
```

Você deve ver `[OK] Pré-requisitos verificados.` Se aparecer `[ERRO]`, volte à Semana 05 antes de continuar.

---

### Carregando os dados

Adicione **dentro da função `main()`**, após a verificação:

```python
    # --- 1. Carregar features ---
    print("\n[1/5] Carregando dataset de features...")
    X = pd.read_csv(features_path)
    print(f"       Shape: {X.shape}")
    print(f"       Primeiras colunas: {list(X.columns[:5])}...")
```

**Execute e observe a saída.** Você deve ver algo como:

```
[1/5] Carregando dataset de features...
       Shape: (89740, 117)
       Primeiras colunas: ['tempo', 'popularity', 'danceability', 'energy', ...]
```

!!! info "Por que 117 colunas?"
    O `FeatureEngineer` (Semana 05) aplicou **normalização** nas features numéricas e **one-hot encoding** nos gêneros. Cada gênero virou uma coluna binária — de ~10 features originais para 117 features numéricas.

---

### Criando o label

O label `liked` é o que a rede vai aprender a prever. Adicione:

```python
    # --- 2. Criar o label (Y) ---
    print("\n[2/5] Criando label 'liked'...")
    df_clean = pd.read_csv(clean_path)

    mediana = df_clean["popularity"].median()
    y = (df_clean["popularity"] > mediana).astype(int)

    print(f"       Mediana de popularity: {mediana}")
    print(f"       Curtidas (1): {y.sum()} | Não Curtidas (0): {len(y) - y.sum()}")

    # Garantir alinhamento entre X e y
    min_len = min(len(X), len(y))
    X = X.iloc[:min_len]
    y = y.iloc[:min_len]
```

**Execute e veja a distribuição dos labels.** A saída deve mostrar uma divisão próxima de 50/50 (porque usamos a mediana como corte).

Aqui, **threshold** significa apenas **valor de corte**: acima da mediana vira 1, abaixo ou igual vira 0.

!!! info "Por que usar a mediana como corte?"
    A mediana divide o dataset exatamente ao meio: metade das músicas terá `popularity` acima dela (label 1) e metade abaixo (label 0). Isso gera um dataset **balanceado**, o que facilita o aprendizado da MLP. Se usássemos um valor fixo (ex: `popularity > 70`), provavelmente teríamos muito menos músicas "curtidas" que "não curtidas".

!!! warning "Por que isso é uma simplificação?"
    Em produção, `liked` viria de dados reais: cliques, tempo de escuta, itens adicionados à playlist. A popularity já está nas features, então a MLP terá uma "dica direta" para acertar — o que explica a alta acurácia que veremos no próximo passo.

---

### Divisão treino e teste

```python
    # --- 3. Divisão Treino / Teste ---
    print("\n[3/5] Dividindo em Treino (80%) e Teste (20%)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )
    print(f"       Treino: {X_train.shape[0]} amostras")
    print(f"       Teste:  {X_test.shape[0]} amostras")
```

**Execute e confirme os tamanhos.**

!!! info "O que `stratify=y` faz?"
    Sem `stratify`, a divisão é aleatória. Com `stratify=y`, o scikit-learn garante que a **proporção de classes** (50% curtidas e 50% não curtidas) seja mantida tanto no treino quanto no teste. Isso é essencial para uma avaliação justa.

---

### Treino, avaliação e finalização

Adicione o treino e a avaliação. Depois, adicione o bloco `if __name__` no final do arquivo:

```python
    # --- 4. Treinar ---
    print("\n[4/5] Treinando a Rede Neural MLP...")
    mlp = MusicMLPClassifier()
    mlp.train(X_train, y_train, hidden_layers=(64, 32), max_iter=300)

    # --- 5. Avaliar ---
    print("\n[5/5] Avaliando no conjunto de teste...")
    results = mlp.evaluate(X_test, y_test)

    print(f"\n{'=' * 60}")
    print(f"  RESULTADO FINAL")
    print(f"{'=' * 60}")
    print(f"  Acurácia: {results['accuracy']:.2%}")
    print(f"\n{results['report']}")
    print(f"\n[OK] Modelo salvo em: models/mlp_model.joblib")


if __name__ == "__main__":
    main()
```

**Execute o script completo:**

```bash
uv run python scripts/train_mlp.py
```

!!! important "Por que 99.79% de acurácia?"
    A acurácia é alta porque o label `liked` foi criado **a partir de** `popularity`, que já está nas features. A MLP basicamente aprendeu a regra que nós mesmos criamos. Em produção, com labels vindos de comportamento real do usuário, a acurácia seria menor (70–90%).

    Isso **não invalida o exercício** — o objetivo é aprender o **fluxo completo** do pipeline de ML: engenharia de features → label → treino → avaliação → API.

---

### Exploração

1. Teste arquitetura menor: no `scripts/train_mlp.py`, troque `hidden_layers=(64, 32)` por `hidden_layers=(10,)`, rode `uv run python scripts/train_mlp.py` e compare a acurácia final.
2. Teste poucas épocas: no mesmo trecho, troque `max_iter=300` por `max_iter=5`, rode novamente e observe `n_iter_` e a acurácia.
3. Teste outro valor de corte do label:
    No bloco de criação do `y`, troque
    `y = (df_clean["popularity"] > mediana).astype(int)`
    por
    `y = (df_clean["popularity"] > 70).astype(int)`.
    Depois rode `uv run python scripts/train_mlp.py` e compare a linha `Curtidas (1) | Não Curtidas (0)` com a versão anterior.

---

## Integração com a API

> **Objetivo:** Expor a MLP como endpoint HTTP e testá-la no Swagger UI.

A API não faz nada novo: apenas orquestra as peças que você já construiu nas semanas anteriores.

---

### Schemas de entrada e saída

Crie o arquivo `src/api/v1/mlp.py`. Comece **apenas com os schemas**:

```python
# src/api/v1/mlp.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import pandas as pd
from pydantic import BaseModel

from src.services.feature_engineer import FeatureEngineer
from src.services.mlp_classifier import MusicMLPClassifier

router = APIRouter()


class MLPTrackInput(BaseModel):
    """Dados de entrada de uma música para predição."""
    track_name: str
    track_genre: str
    tempo: float
    popularity: float
    danceability: float = 0.5
    energy: float = 0.5


class MLPTrackResult(BaseModel):
    """Resultado da predição para uma única música."""
    track_name: str
    prediction: str
    probability: float
    debug: dict


class MLPPredictRequest(BaseModel):
    """Corpo da requisição: uma ou mais músicas."""
    tracks: List[MLPTrackInput]


class MLPPredictResponse(BaseModel):
    """Resposta completa da predição."""
    results: List[MLPTrackResult]
    total: int
    summary: dict
```

---

### Dependências

Adicione as funções de dependência **abaixo dos schemas**. Elas carregam os modelos do disco quando a API começa:

```python
def get_feature_engineer() -> FeatureEngineer:
    fe = FeatureEngineer()
    if not fe.transformer_path.exists():
        dummy = pd.DataFrame([
            {"tempo": 120.0, "popularity": 50.0, "danceability": 0.5,
             "energy": 0.5, "track_genre": "pop"},
            {"tempo": 80.0, "popularity": 10.0, "danceability": 0.3,
             "energy": 0.2, "track_genre": "rock"},
        ])
        fe.fit(dummy, ["tempo", "popularity", "danceability", "energy"], ["track_genre"])
    else:
        fe.load()
    return fe


def get_mlp_model() -> MusicMLPClassifier:
    mlp = MusicMLPClassifier()
    mlp.load()
    return mlp
```

!!! info "O que é uma dependência no FastAPI?"
    O mecanismo `Depends()` do FastAPI executa a função de dependência **antes** do endpoint. Cada requisição recebe uma instância fresca do modelo (ou carregada do cache do sistema operacional). Isso é equivalente à injeção de dependência em frameworks como Spring (Java) ou NestJS (TypeScript).

!!! info "O fallback do `get_feature_engineer`"
    Se por algum motivo o `transformers.joblib` não existir (ex.: primeiro boot em produção), a função cria um transformador mínimo apenas para não quebrar a API. Isso é um **graceful degradation** — a API responde (com qualidade reduzida) em vez de travar.

---

### Endpoint

Adicione o endpoint **após as dependências**:

```python
@router.post("/model/mlp/predict", response_model=MLPPredictResponse)
def mlp_predict(
    request: MLPPredictRequest,
    fe: FeatureEngineer = Depends(get_feature_engineer),
    mlp: MusicMLPClassifier = Depends(get_mlp_model),
):
    """Prevê se uma ou mais músicas serão 'Curtidas' ou 'Não Curtidas'."""
    try:
        df = pd.DataFrame([t.model_dump() for t in request.tracks])
        df_features = fe.transform(df)
        result = mlp.predict(df_features)

        results = []
        liked_count = 0

        for i, track in enumerate(request.tracks):
            pred_val = result["predictions"][i]
            if pred_val == 1:
                liked_count += 1

            results.append(MLPTrackResult(
                track_name=track.track_name,
                prediction=result["labels"][i],
                probability=round(result["probabilities"][i], 4),
                debug={
                    "raw_prediction": pred_val,
                    "features_used": df_features.columns.tolist(),
                },
            ))

        return MLPPredictResponse(
            results=results,
            total=len(results),
            summary={"curtidas": liked_count, "nao_curtidas": len(results) - liked_count},
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Modelo não encontrado. Rode 'train_mlp.py' primeiro. Erro: {e}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

!!! info "Por que `503` e não `500`?"
    O código `503 Service Unavailable` indica que o serviço está temporariamente indisponível (o modelo não foi treinado ainda). O código `500 Internal Server Error` indica um erro genérico e inesperado. Usar o código correto facilita o diagnóstico pelo cliente.

---

### Registro no router

Abra `src/api/v1/router.py` e adicione as duas linhas indicadas:

```python
# Importe o novo módulo no topo
from src.api.v1 import recommendation, library, data_audit, feature_engineering, mlp

# ...rotas existentes...

# Adicione no final
api_router.include_router(mlp.router, tags=["mlp-neural-network"])
```

---

### Testando no Swagger UI

Inicie o servidor:

```bash
uv run fastapi dev
```

Acesse `http://127.0.0.1:8000/docs` e localize o endpoint `POST /api/v1/model/mlp/predict`.

**Teste 1 — Música popular:**

```json
{
  "tracks": [
    {
      "track_name": "In the End",
      "track_genre": "rock",
      "tempo": 105.0,
      "popularity": 88,
      "danceability": 0.6,
      "energy": 0.8
    }
  ]
}
```

**Teste 2 — Música pouco conhecida:**

```json
{
  "tracks": [
    {
      "track_name": "Música Obscura",
      "track_genre": "ambient",
      "tempo": 70.0,
      "popularity": 5,
      "danceability": 0.2,
      "energy": 0.1
    }
  ]
}
```

**Teste 3 — Batch com 3 músicas:**

```json
{
  "tracks": [
    {
      "track_name": "Bohemian Rhapsody",
      "track_genre": "rock",
      "tempo": 144.0,
      "popularity": 95,
      "danceability": 0.4,
      "energy": 0.7
    },
    {
      "track_name": "Música Desconhecida",
      "track_genre": "ambient",
      "tempo": 70.0,
      "popularity": 5,
      "danceability": 0.2,
      "energy": 0.1
    },
    {
      "track_name": "Funk da Galera",
      "track_genre": "funk",
      "tempo": 130.0,
      "popularity": 60,
      "danceability": 0.9,
      "energy": 0.9
    }
  ]
}
```

Observe o campo `summary` na resposta: ele mostra o total de curtidas e não curtidas no batch.

---

### Desafios de Exploração

1. **O ponto de virada:** Envie a mesma música com `popularity` crescendo de 10 em 10 (10, 20, 30...). Em qual valor a predição muda de "Não Curtida" para "Curtida"? Esse valor se aproxima da mediana usada no treino?

2. **Gênero importa?** Envie a mesma música (mesmo `tempo`, `popularity`, `danceability` e `energy`) mas com `track_genre` diferentes. A predição muda? Isso faz sentido dado como o label foi criado?

3. **O Engenheiro de Redes:** Altere `hidden_layers` para `(10,)` (uma camada, 10 neurônios) e re-treine. A acurácia muda? Por quê?