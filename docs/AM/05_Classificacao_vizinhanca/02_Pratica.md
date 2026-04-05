# KNN - Prática

!!! important "Pré-requisito obrigatório"
    Antes de iniciar esta prática, execute:

    ```bash
    uv run python scripts/clean_dataset.py
    ```

    Arquivo esperado:

    - `data/processed/dataset_clean.csv`

---

## Objetivo da prática

Nesta aula prática, você vai:

- Criar o serviço `MusicKNNClassifier`.
- Treinar e avaliar o modelo com diferentes valores de K.
- Expor endpoints de classificação e recomendação por similaridade.

---

## Serviço KNN

Crie o arquivo `src/services/knn_classifier.py`:

```python
import numpy as np
import pandas as pd
from pathlib import Path
import joblib
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report


class MusicKNNClassifier:
    """
    Servico de classificacao por K-Nearest Neighbors (KNN).

    Fluxo:
    - treino: ajusta o scaler e armazena os dados no modelo
    - predicao: normaliza entrada, busca vizinhos e vota
    """

    FEATURE_COLUMNS = [
        "danceability",
        "energy",
        "loudness_norm",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
    ]

    def __init__(self, model_dir: str | Path = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.model_dir / "knn_model.joblib"
        self.model: KNeighborsClassifier | None = None
        self.scaler: StandardScaler | None = None
        self.label_names: list[str] | None = None
        self.metrics: dict | None = None

    def train(
        self,
        X_train: np.ndarray | pd.DataFrame,
        y_train: np.ndarray | pd.Series,
        n_neighbors: int = 5,
        metric: str = "euclidean",
    ) -> "MusicKNNClassifier":
        print(f"[KNN] Configurando classificador com K={n_neighbors}, metrica={metric}...")
        print(f"[KNN] Features: {X_train.shape[1]} | Amostras: {X_train.shape[0]}")

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_train)

        self.model = KNeighborsClassifier(
            n_neighbors=n_neighbors,
            metric=metric,
            weights="distance",
            n_jobs=-1,
        )

        self.model.fit(X_scaled, y_train)

        if hasattr(y_train, "unique"):
            self.label_names = sorted(y_train.unique().tolist())

        self.save()
        return self

    def predict(self, X: np.ndarray | pd.DataFrame) -> dict:
        if self.model is None:
            self.load()

        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        distances, indices = self.model.kneighbors(X_scaled)

        return {
            "predictions": predictions.tolist(),
            "probabilities": probabilities.tolist(),
            "neighbor_distances": distances.tolist(),
            "neighbor_indices": indices.tolist(),
        }

    def find_similar(self, X: np.ndarray | pd.DataFrame, n_similar: int = 5) -> dict:
        if self.model is None:
            self.load()

        X_scaled = self.scaler.transform(X)
        distances, indices = self.model.kneighbors(X_scaled, n_neighbors=n_similar)
        return {"distances": distances.tolist(), "indices": indices.tolist()}

    def evaluate(self, X_test: np.ndarray | pd.DataFrame, y_test: np.ndarray | pd.Series) -> dict:
        if self.model is None:
            self.load()

        X_scaled = self.scaler.transform(X_test)
        y_pred = self.model.predict(X_scaled)

        acc = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, zero_division=0)

        self.metrics = {
            "accuracy": round(acc, 4),
            "k": self.model.n_neighbors,
            "metric": self.model.metric,
        }

        return {"accuracy": acc, "report": report}

    def save(self):
        state = {
            "model": self.model,
            "scaler": self.scaler,
            "label_names": self.label_names,
            "metrics": self.metrics,
        }
        joblib.dump(state, self.model_path)
        print(f"[KNN] Modelo salvo em: {self.model_path}")

    def load(self):
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Modelo KNN nao encontrado em: {self.model_path}. "
                "Rode 'uv run python scripts/train_knn.py' primeiro."
            )
        state = joblib.load(self.model_path)
        self.model = state["model"]
        self.scaler = state["scaler"]
        self.label_names = state.get("label_names")
        self.metrics = state.get("metrics")
```

### Parâmetros essenciais

| Parâmetro | Valor sugerido | Efeito |
|---|---|---|
| `n_neighbors` | `5` | Define quantos vizinhos participam da decisão |
| `metric` | `"euclidean"` | Distância usada para proximidade |
| `weights` | `"distance"` | Vizinho mais próximo vota com mais peso |
| `n_jobs` | `-1` | Usa todos os núcleos disponíveis |

---

## Script de treinamento

Crie o arquivo `scripts/train_knn.py`:

```python
# -*- coding: utf-8 -*-
"""
Treina o classificador KNN para prever genero musical
com base nas features numericas.
"""
import sys
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.services.knn_classifier import MusicKNNClassifier

NUMERIC_FEATURES = [
    "danceability",
    "energy",
    "loudness_norm",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
]

TOP_N_GENRES = 10


def main():
    clean_path = project_root / "data" / "processed" / "dataset_clean.csv"

    print("=" * 60)
    print("  [KNN] Treinamento do Classificador KNN")
    print("=" * 60)

    if not clean_path.exists():
        print(f"\n[ERRO] Dataset limpo nao encontrado em: {clean_path}")
        print("DICA: Rode 'uv run python scripts/clean_dataset.py' primeiro.")
        return

    df = pd.read_csv(clean_path)

    top_genres = df["track_genre"].value_counts().head(TOP_N_GENRES).index.tolist()
    df_filtered = df[df["track_genre"].isin(top_genres)].copy()

    X = df_filtered[NUMERIC_FEATURES].copy()
    y = df_filtered["track_genre"].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\nTeste de K:")
    print(f"{'K':>4s} {'Acuracia':>10s}")
    print("-" * 20)

    k_values = [1, 3, 5, 7, 11, 15, 21]
    best_k = 5
    best_acc = 0

    for k in k_values:
        model = MusicKNNClassifier()
        model.train(X_train, y_train, n_neighbors=k)
        result = model.evaluate(X_test, y_test)
        acc = result["accuracy"]

        if acc > best_acc:
            best_acc = acc
            best_k = k

        print(f"{k:>4d} {acc:>10.4f}")

    print(f"\nMelhor K encontrado: {best_k}")

    knn = MusicKNNClassifier()
    knn.train(X_train, y_train, n_neighbors=best_k)
    final = knn.evaluate(X_test, y_test)

    knn.metrics = {
        "accuracy": round(final["accuracy"], 4),
        "k": best_k,
        "metric": "euclidean",
    }
    knn.save()

    print(f"\nAcuracia final: {final['accuracy']:.2%}")
    print(final["report"])


if __name__ == "__main__":
    main()
```

Execute:

```bash
uv run python scripts/train_knn.py
```

---

## Endpoint da API

Crie o arquivo `src/api/v1/knn.py`:

```python
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import pandas as pd
from pydantic import BaseModel, Field
from pathlib import Path

from src.services.knn_classifier import MusicKNNClassifier

router = APIRouter()


class KNNTrackInput(BaseModel):
    track_name: str
    danceability: float = Field(ge=0, le=1)
    energy: float = Field(ge=0, le=1)
    loudness_norm: float = Field(ge=0, le=1)
    speechiness: float = Field(default=0.05, ge=0, le=1)
    acousticness: float = Field(default=0.5, ge=0, le=1)
    instrumentalness: float = Field(default=0.0, ge=0, le=1)
    liveness: float = Field(default=0.2, ge=0, le=1)
    valence: float = Field(default=0.5, ge=0, le=1)
    tempo: float = Field(default=120.0, ge=0, le=300)


class KNNClassifyRequest(BaseModel):
    tracks: List[KNNTrackInput]


class KNNClassifyResult(BaseModel):
    track_name: str
    predicted_genre: str
    confidence: float
    top_genres: dict
    debug: dict


class KNNClassifyResponse(BaseModel):
    results: List[KNNClassifyResult]
    total: int
    model_info: dict


class SimilarTrackResult(BaseModel):
    track_name: str
    genre: str
    distance: float
    similarity_score: float


class SimilarRequest(BaseModel):
    reference_track: KNNTrackInput
    n_similar: int = Field(default=5, ge=1, le=20)


class SimilarResponse(BaseModel):
    reference: str
    similar_tracks: List[SimilarTrackResult]
    total: int


_dataset_cache = None


def get_knn_model() -> MusicKNNClassifier:
    knn = MusicKNNClassifier()
    knn.load()
    return knn


def get_dataset() -> pd.DataFrame:
    global _dataset_cache
    if _dataset_cache is None:
        dataset_path = Path("data/processed/dataset_clean.csv")
        if dataset_path.exists():
            _dataset_cache = pd.read_csv(dataset_path)
    return _dataset_cache


@router.post("/classify-user", response_model=KNNClassifyResponse)
def classify_user_profile(
    request: KNNClassifyRequest,
    knn: MusicKNNClassifier = Depends(get_knn_model),
):
    try:
        feature_columns = MusicKNNClassifier.FEATURE_COLUMNS

        rows = []
        for t in request.tracks:
            rows.append(
                {
                    "danceability": t.danceability,
                    "energy": t.energy,
                    "loudness_norm": t.loudness_norm,
                    "speechiness": t.speechiness,
                    "acousticness": t.acousticness,
                    "instrumentalness": t.instrumentalness,
                    "liveness": t.liveness,
                    "valence": t.valence,
                    "tempo": t.tempo,
                }
            )

        df = pd.DataFrame(rows, columns=feature_columns)
        result = knn.predict(df)

        response_items = []
        for i, track in enumerate(request.tracks):
            pred_genre = result["predictions"][i]
            proba = result["probabilities"][i]

            if knn.label_names:
                top_genres = {
                    name: round(float(p), 4)
                    for name, p in sorted(
                        zip(knn.label_names, proba),
                        key=lambda x: x[1],
                        reverse=True,
                    )[:5]
                }
                confidence = max(proba)
            else:
                top_genres = {pred_genre: 1.0}
                confidence = 1.0

            response_items.append(
                KNNClassifyResult(
                    track_name=track.track_name,
                    predicted_genre=pred_genre,
                    confidence=round(float(confidence), 4),
                    top_genres=top_genres,
                    debug={
                        "k": knn.model.n_neighbors if knn.model else "N/A",
                        "metric": knn.model.metric if knn.model else "N/A",
                        "neighbor_distances": result["neighbor_distances"][i][:5],
                    },
                )
            )

        model_info = knn.metrics or {"accuracy": "N/A", "k": "N/A"}

        return KNNClassifyResponse(
            results=response_items,
            total=len(response_items),
            model_info=model_info,
        )

    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/recommend/similar", response_model=SimilarResponse)
def find_similar_tracks(
    request: SimilarRequest,
    knn: MusicKNNClassifier = Depends(get_knn_model),
    dataset: pd.DataFrame = Depends(get_dataset),
):
    try:
        feature_columns = MusicKNNClassifier.FEATURE_COLUMNS
        ref = request.reference_track

        ref_data = pd.DataFrame(
            [
                {
                    "danceability": ref.danceability,
                    "energy": ref.energy,
                    "loudness_norm": ref.loudness_norm,
                    "speechiness": ref.speechiness,
                    "acousticness": ref.acousticness,
                    "instrumentalness": ref.instrumentalness,
                    "liveness": ref.liveness,
                    "valence": ref.valence,
                    "tempo": ref.tempo,
                }
            ],
            columns=feature_columns,
        )

        similar = knn.find_similar(ref_data, n_similar=request.n_similar + 1)
        indices = similar["indices"][0]
        distances = similar["distances"][0]

        similar_tracks = []
        for idx, dist in zip(indices, distances):
            if dataset is not None and idx < len(dataset):
                row = dataset.iloc[idx]
                name = str(row.get("track_name", f"Track #{idx}"))
                genre = str(row.get("track_genre", "desconhecido"))
            else:
                name = f"Track #{idx}"
                genre = "desconhecido"

            similarity = round(1.0 / (1.0 + float(dist)), 4)
            similar_tracks.append(
                SimilarTrackResult(
                    track_name=name,
                    genre=genre,
                    distance=round(float(dist), 4),
                    similarity_score=similarity,
                )
            )

        return SimilarResponse(
            reference=ref.track_name,
            similar_tracks=similar_tracks[: request.n_similar],
            total=len(similar_tracks[: request.n_similar]),
        )

    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
```

---

## Registro das rotas

No arquivo `src/api/v1/router.py`, adicione o módulo `knn`:

```python
from src.api.v1 import (
    recommendation,
    library,
    data_audit,
    feature_engineering,
    mlp,
    regression,
    knn,
)

api_router.include_router(knn.router, tags=["knn-classification"])
```

---

## Testes no Swagger

Inicie o servidor:

```bash
uv run fastapi dev
```

Acesse:

- `http://127.0.0.1:8000/docs`

### Teste de classificação

`POST /api/v1/classify-user`

```json
{
  "tracks": [
    {
      "track_name": "Musica Dancante",
      "danceability": 0.85,
      "energy": 0.9,
      "loudness_norm": 0.85,
      "speechiness": 0.05,
      "acousticness": 0.05,
      "instrumentalness": 0.0,
      "liveness": 0.15,
      "valence": 0.8,
      "tempo": 128.0
    }
  ]
}
```

### Teste de recomendação

`POST /api/v1/recommend/similar`

```json
{
  "reference_track": {
    "track_name": "Minha Musica Favorita",
    "danceability": 0.7,
    "energy": 0.6,
    "loudness_norm": 0.7,
    "speechiness": 0.04,
    "acousticness": 0.3,
    "instrumentalness": 0.0,
    "liveness": 0.1,
    "valence": 0.6,
    "tempo": 110.0
  },
  "n_similar": 5
}
```

---

## Boas práticas para a turma

- Teste vários valores de K e compare resultados.
- Avalie também a métrica Manhattan, além da Euclidiana.
- Valide se as recomendações fazem sentido com músicas reais.
- Use o campo `debug` para explicar o comportamento do modelo.

---

## Exercícios de fixação

1. Adicione K = 50 e K = 100 no script de treino e compare a acurácia.
2. Treine com `metric="manhattan"` e compare com `metric="euclidean"`.
3. Envie um exemplo de música com energia alta e valence baixa e analise o gênero previsto.
4. Use o endpoint de recomendação e discuta se os vizinhos retornados fazem sentido musical.
5. Compare o uso de KNN e MLP para um app com 100 milhões de músicas e para uma loja com poucos itens.
