# Configuração e Perceptron

> Guia prático: Dados, Modelo e API.

---

## 1. Configuração

### Inicialização

Você tem duas opções. Escolha **UMA**.

=== "Opção A: Do Zero"

    1.  Crie a pasta `am-projeto-recomendacao` e abra no VS Code.
    2.  No terminal: `uv init`.
    3.  Instale as dependências:

    ```bash
    uv add pandas matplotlib "fastapi[standard]"
    uv add --dev ipykernel notebook
    ```

=== "Opção B: Repositório"

    1.  Clone o repositório.
    2.  Abra no VS Code.
    3.  Execute `uv sync`.

### Notebooks

!!! important "Kernel do Python"
    Para rodar os notebooks, garanta que o kernel seja o ambiente virtual (`.venv`) do projeto.

    **Se não encontrar:** `uv run ipython kernel install --user --name=am-projeto-kernel`

### Dados

1.  Baixe o [Spotify Dataset (Kaggle)](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset).
2.  Extraia e salve `dataset.csv` em `data/raw/`.

---

## 2. Modelagem (Pydantic)

Precisamos definir os dados (Schemas) para o cálculo.

!!! abstract "O que é Pydantic?"
    Python não força tipos (`int`, `str`). O Pydantic cria **contratos** (Schemas) que validam os dados automaticamente. Se a API receber um texto onde deveria ser número, ela rejeita o pedido.

### Schemas (`src/schemas.py`)

Crie o arquivo com os modelos de entrada e saída.

```python
from pydantic import BaseModel
from typing import Optional

# 1. Características da música (Base do cálculo)
class MusicFeatures(BaseModel):
    energy: float
    loudness: float

# 2. O que o usuário envia (Pedido)
class TrackRequest(BaseModel):
    track_id: Optional[str] = "unknown"
    track_name: str
    artist_name: str
    features: MusicFeatures

# 3. O que a API responde (Resposta)
class TrackResponse(BaseModel):
    track: str
    artist: str
    recommendation: str
    debug_info: dict
```

---

## 3. O Perceptron

### Lógica

!!! info "Fórmula"
    $$ Z = (Energy \times 0.8) + (Normaliz(Loudness) \times 0.2) + 0.1 $$
    
    *   **Se Z >= 0.5**: Festa
    *   **Se Z < 0.5**: Relax

### Implementação (`src/models/perceptron.py`)

Implemente a classe que processa a lógica de decisão.

```python
class Perceptron:
    def __init__(self, weights=None, bias=0.1):
        self.default_weights = {'energy': 0.8, 'loudness': 0.2}
        self.weights = weights if weights else self.default_weights
        self.bias = bias

    def predict(self, energy, loudness):
        # Normalização: (-60dB a 0dB) -> (aprox 0.0 a 1.0)
        loudness_norm = (loudness + 10) / 10
        
        # Cálculo Z
        w_energy = self.weights.get('energy', 0.0)
        w_loudness = self.weights.get('loudness', 0.0)
        linear_output = (energy * w_energy) + (loudness_norm * w_loudness) + self.bias
        
        # Ativação (Degrau)
        prediction = 1 if linear_output >= 0.5 else 0
        
        return {
            "prediction": prediction,
            "activation": linear_output,
            "normalized_loudness": loudness_norm
        }
```

---

## 4. Testes

### Manual (Notebook `02_testes.ipynb`)

Teste se a lógica funciona antes de criar a API.

```python
import sys
import os
sys.path.append(os.path.abspath('..'))
from src.models.perceptron import Perceptron

cerebro = Perceptron()

# Teste Festa (Energy alta, Loudness alto)
print(cerebro.predict(0.9, -4.0)) 
# Esperado: prediction=1

# Teste Relax (Energy baixa, Loudness baixo)
print(cerebro.predict(0.2, -15.0)) 
# Esperado: prediction=0
```

### Desafio
Teste com músicas reais para ver se o modelo acerta:

*   **The Killers - Mr. Brightside**: (Energy: 0.93, Loudness: -3.76) -> ?
*   **Boyce Avenue - Chasing Cars**: (Energy: 0.33, Loudness: -8.9) -> ?
*   **Para Reiki**: (Energy: 0.92, Loudness: -32.8) -> ?

---

## 5. API (FastAPI)

Vamos expor o modelo como um serviço web.

### Endpoint (`recommendation.py`)

Crie `src/api/v1/recommendation.py`.

```python
from fastapi import APIRouter, Depends
from functools import lru_cache
from src.schemas import TrackRequest, TrackResponse
from src.models.perceptron import Perceptron

router = APIRouter()

@lru_cache
def get_perceptron():
    return Perceptron()

@router.post("/recommend/predict", response_model=TrackResponse)
def predict_track(request: TrackRequest, model: Perceptron = Depends(get_perceptron)):
    result = model.predict(request.features.energy, request.features.loudness)
    mood = "Festa/Agitada" if result["prediction"] == 1 else "Relax/Calma"
    
    return {
        "track": request.track_name,
        "artist": request.artist_name,
        "recommendation": mood,
        "debug_info": result
    }
```

### Router (`src/api/v1/router.py`)

```python
from fastapi import APIRouter
from src.api.v1 import recommendation

api_router = APIRouter()
api_router.include_router(recommendation.router, tags=["recomendacao"])
```

### Main (`src/main.py`)

```python
from fastapi import FastAPI
from src.api.v1.router import api_router

app = FastAPI(title="API de Recomendação")
app.include_router(api_router, prefix="/api/v1")
```

---

## 6. Execução

### Rodar Server

```bash
uv run fastapi dev
```

### Testar (Swagger)

Acesse `http://127.0.0.1:8000/docs`. POST em `/recommend/predict` com:

```json
{
  "track_name": "Teste",
  "artist_name": "DJ",
  "features": { "energy": 0.95, "loudness": -3.0 }
}
```

---

## 7. Exercícios de Fixação

### Calibrando o Modelo

??? example "Exercício de Fixação: Músicas 'Enganosas'"

    Chegou a hora de você ajustar o "cérebro" do seu modelo.

    **O Problema**
    
    Algumas músicas estão sendo classificadas incorretamente. Lembram daquela análise que fizemos no notebook `01_intro_dados.ipynb`?
    
    Nós filtramos músicas com **Alta Energia (> 0.8)** mas **Volume Baixo (< -10dB)**:
    ```python
    excecoes = df[(df['energy'] > 0.8) & (df['loudness'] < -10)]
    ```
    
    Essas músicas (como "Meeresrauschen", sons de chuva/natureza) confundem nosso modelo atual, que confia demais na Energia (`0.8`). Precisamos equilibrar isso dando mais importância ao "peso" do som (Loudness).

    **Sua Missão**: Encontrar os pesos ideais para equilibrar `Energy` e `Loudness`.

    ---

    === "Opção A: Pelo Notebook (Rápido)"
    
        1.  Abra o notebook `02_testes_perceptron.ipynb`.
        2.  Instancie o Perceptron passando novos pesos:
        
        ```python
        # Tentativa 1 (Atual)
        cerebro = Perceptron(weights={'energy': 0.8, 'loudness': 0.2})
        
        # Tentativa 2 (Ajuste aqui!)
        c_tuning = Perceptron(weights={'energy': ?, 'loudness': ?})
        ```

    === "Opção B: Direto na API (Definitivo)"
    
        1.  Vá até `src/api/v1/recommendation.py`.
        2.  Encontre a função `get_perceptron`.
        3.  Altere o dicionário de pesos:
        
        ```python
        return Perceptron(weights={'energy': ?, 'loudness': ?}, bias=0.1)
        ```
        4.  Teste a mesma música no Swagger UI. O resultado mudou?
