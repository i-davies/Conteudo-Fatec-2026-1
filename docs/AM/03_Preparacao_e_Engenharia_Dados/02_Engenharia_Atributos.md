# Engenharia de Atributos

Na semana anterior, limpamos o dataset do Spotify com o `DataCleaner`: removemos nulos, tratamos outliers e até normalizamos o `loudness` manualmente. O resultado foi um `dataset_clean.csv` confiável.

Agora damos o próximo passo: **preparar esses dados para que um modelo de Machine Learning possa consumi-los**. Máquinas não leem texto como "Rock" ou "Pop" — elas leem números. E não basta qualquer número: as escalas precisam ser consistentes e reproduzíveis. É aqui que entra o **Scikit-Learn**.

---

## Sugestão de Ordem para a Aula

1. **Conceitos**: Discuta por que a normalização manual não escala e o problema de codificar categorias como `1, 2, 3`.
2. **Dependências**: Instale `scikit-learn` e `joblib`, apresentando as ferramentas.
3. **Serviço (`FeatureEngineer`)**: Implemente a classe em etapas, explicando cada bloco.
4. **Endpoint e Registro**: Crie a rota `/preprocess` e registre no router.
5. **Laboratório**: Testes progressivos no Swagger UI — do básico ao limite.
6. **Script de Treino Real**: Execute com o `dataset_clean.csv` e compare o resultado com o dummy.

---

## Conceitos Chave

!!! info "Objetivos"
    * Entender por que normalização e codificação de categorias são obrigatórias para modelos de ML.
    * Conhecer a diferença entre `fit()` e `transform()` e por que ela importa.
    * Preparar os artefatos (`transformers.joblib` e `dataset_features.csv`) que serão usados nas próximas semanas.

### Da Normalização Manual ao Pipeline

Na semana passada, normalizamos o `loudness` com uma fórmula direta no `DataCleaner`:

```python
df["loudness_norm"] = (df["loudness"] - loud_min) / (loud_max - loud_min)
```

Funciona, mas tem um problema: **os limites (`loud_min`, `loud_max`) são recalculados a cada vez**. Se amanhã chegar uma música nova com um `loudness` diferente, os limites mudam e todos os valores antigos ficam inconsistentes.

A solução profissional é usar um **Pipeline do Scikit-Learn**: um objeto que *aprende* os limites uma única vez e os *aplica* de forma idêntica para sempre.

### Normalização (Min-Max Scaling)

As máquinas são sensíveis a escalas. O `tempo` (60–180 BPM) não pode ter mais "peso" que `energy` (0–1) só porque o número é maior.

$$x_{norm} = \frac{x - x_{min}}{x_{max} - x_{min}}$$

O `MinMaxScaler` do Scikit-Learn aplica exatamente essa fórmula, mas memoriza `x_min` e `x_max` do dataset de treino para reusar depois.

### One-Hot Encoding (OHE)

Não podemos usar $1, 2, 3$ para Rock, Pop e Jazz. O modelo interpretaria que Jazz ($3$) é "maior" que Rock ($1$), introduzindo uma ordem que não existe.

O **One-Hot Encoding** cria uma coluna binária ($0$ ou $1$) para cada categoria, tornando-as independentes:

| Gênero | `genre_Rock` | `genre_Pop` | `genre_Jazz` |
| :--- | :---: | :---: | :---: |
| Rock | 1 | 0 | 0 |
| Pop | 0 | 1 | 0 |
| Jazz | 0 | 0 | 1 |

### O que é um Tensor? (A Analogia da Planilha)

Se a palavra "Tensor" parece assustadora, pense nela como uma **planilha**:

- **Vetor (1D):** Uma única linha — os dados de uma música.
- **Matriz (2D):** A planilha inteira — **linhas** são músicas e **colunas** são atributos.

Quando o endpoint retorna `transformed_shape: [1, 6]`, significa: **1 música** com **6 atributos numéricos**. Se você enviar 10 músicas, o shape será `[10, 6]`. Modelos de ML esperam exatamente esse formato.

---

## Fit vs. Transform: O Segredo da Consistência

!!! abstract "O Conceito Central desta Semana"
    Entender a diferença entre `fit()` e `transform()` é o que separa um código de pesquisa de um sistema em produção.

| Método | O que faz | Quando usar |
| :--- | :--- | :--- |
| `fit()` | Aprende os parâmetros (mínimo, máximo, categorias) do dataset | **Somente no treinamento** |
| `transform()` | Aplica os parâmetros aprendidos em dados novos | Treinamento **e** produção |
| `fit_transform()` | Faz os dois de uma vez | Somente na primeira execução de treino |

**Exemplo:** O `fit()` descobre que `tempo` vai de 60 a 180. Depois, o `transform()` recebe uma música com `tempo = 120` e calcula: $(120 - 60) / (180 - 60) = 0.5$.

!!! important "Nunca use `fit()` na API"
    Se a API chamar `fit()` a cada requisição, os limites mudam com cada nova música e o modelo recebe dados em escalas inconsistentes. A API deve apenas `load()` o que foi aprendido e chamar `transform()`.

---

## A Memória do Pipeline: o arquivo `.joblib`

Após o `fit()`, os parâmetros aprendidos são salvos em `models/transformers.joblib`.

Pense nele como um **save de jogo**: o estado do transformador (limites, categorias) é congelado naquele momento. Quando a API sobe, ela carrega esse save com `load()` e garante que toda nova música seja vista **sob a mesma ótica** dos dados de treino — mesmo que o servidor tenha sido reiniciado.

??? tip "Treinamento vs. Produção: onde o dado vai parar?"
    - **No treinamento:** O `dataset_clean.csv` passa pelo `fit_transform()` e gera o `dataset_features.csv`. O modelo de ML estudará apenas esse arquivo numérico.
    - **Na produção (API):** A transformação acontece em memória. O dado entra como texto, vira número, passa pelo modelo e o resultado é devolvido. O arquivo `dataset_features.csv` não é gerado nem salvo.

---

## Instalando as Dependências

```bash
uv add scikit-learn joblib
```

- **scikit-learn**: Biblioteca padrão da indústria para pipelines e algoritmos de ML.
- **joblib**: Serializa objetos Python (como o pipeline treinado) em arquivos binários.

Verifique a instalação antes de continuar:

```bash
uv run python -c "import sklearn, joblib; print(sklearn.__version__, joblib.__version__)"
```

---

## Criando o Serviço `FeatureEngineer`

Crie o arquivo `src/services/feature_engineer.py`. Vamos construí-lo em partes.

### Importações e estrutura da classe

Comece com as importações e o `__init__`. O construtor define onde o arquivo `.joblib` será salvo e inicializa os atributos internos como `None` — eles só serão preenchidos após um `fit()` ou `load()`.

```python
import pandas as pd
from pathlib import Path
import joblib
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

class FeatureEngineer:
    def __init__(self, model_dir: str | Path = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.transformer_path = self.model_dir / "transformers.joblib"
        self.pipeline = None
        self.feature_names = None
```

O `model_dir` padrão é `"models/"` na raiz do projeto. O `mkdir(parents=True, exist_ok=True)` garante que a pasta seja criada automaticamente se não existir.

### Construindo o pipeline interno

O `_build_pipeline` cria um `ColumnTransformer` — o componente que aplica transformações **diferentes por coluna**. Colunas numéricas recebem `MinMaxScaler`; colunas categóricas recebem `OneHotEncoder`.

```python
    def _build_pipeline(self, numeric_features: list[str], categorical_features: list[str]):
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", MinMaxScaler(), numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
            ]
        )
        return Pipeline(steps=[("preprocessor", preprocessor)])
```

!!! info "Por que `handle_unknown='ignore'`?"
    Se o `fit()` aprendeu os gêneros "Rock" e "Pop", e depois a API receber "K-Pop", o OHE não lança erro — ele simplesmente retorna `0` em todas as colunas de gênero. Sem esse parâmetro, a API quebraria ao encontrar qualquer categoria nova.

### O método `fit()` — o momento do aprendizado

O `fit()` é onde o pipeline "estuda" o dataset. Após aprender, ele extrai os nomes das colunas geradas pelo OHE (ex: `track_genre_Rock`, `track_genre_Pop`) e salva tudo no `.joblib`.

```python
    def fit(self, df: pd.DataFrame, numeric_features: list[str], categorical_features: list[str]):
        """Aprende as escalas e categorias dos dados e salva o pipeline."""
        self.pipeline = self._build_pipeline(numeric_features, categorical_features)
        self.pipeline.fit(df)
        cat_encoder = self.pipeline.named_steps["preprocessor"].named_transformers_["cat"]
        cat_features = cat_encoder.get_feature_names_out(categorical_features).tolist()
        self.feature_names = numeric_features + cat_features
        self.save()
        return self
```

!!! important "Nunca chame `fit()` na API"
    Chamar `fit()` por requisição recalcula os limites e categorias a cada música recebida. Com dados diferentes chegando constantemente, as escalas ficam instáveis e o modelo passa a receber entradas inconsistentes. A API deve apenas `load()` e `transform()`.

### O método `transform()` — aplicando o aprendizado

O `transform()` converte qualquer `DataFrame` usando os parâmetros que foram aprendidos. Se por algum motivo o pipeline não estiver em memória, ele carrega automaticamente do arquivo.

```python
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica a transformação salva em novos dados."""
        if self.pipeline is None:
            self.load()
        transformed_data = self.pipeline.transform(df)
        return pd.DataFrame(transformed_data, columns=self.feature_names)
```

O resultado é devolvido como `DataFrame` com os nomes de coluna corretos — não como um array sem identificação.

### Persistência: `save()` e `load()`

O `.joblib` é o "save de jogo" do pipeline. `save()` congela o estado atual; `load()` restaura exatamente esse estado mais tarde.

```python
    def save(self):
        joblib.dump({"pipeline": self.pipeline, "feature_names": self.feature_names}, self.transformer_path)

    def load(self):
        state = joblib.load(self.transformer_path)
        self.pipeline = state["pipeline"]
        self.feature_names = state["feature_names"]
```

??? tip "Treinamento vs. produção: onde o dado vai parar?"
    - **No treinamento:** O `dataset_clean.csv` passa pelo `fit_transform()` e gera o `dataset_features.csv`. O modelo de ML estudará apenas esse arquivo numérico.
    - **Na produção (API):** A transformação acontece em memória. O dado entra como texto, vira número, passa pelo modelo e o resultado é devolvido. Nenhum arquivo intermediário é salvo.

---

## Criando o Endpoint `/preprocess`

Crie o arquivo `src/api/v1/feature_engineering.py`. Vamos construí-lo em partes.

### Os schemas de entrada

Antes do endpoint, precisamos definir o contrato de dados. `RawTrack` representa uma música crua (texto + números brutos) e `PreprocessRequest` é o envelope que a API recebe.

```python
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import pandas as pd
from src.services.feature_engineer import FeatureEngineer
from pydantic import BaseModel

router = APIRouter()

class RawTrack(BaseModel):
    track_name: str
    track_genre: str
    tempo: float
    popularity: float

class PreprocessRequest(BaseModel):
    tracks: List[RawTrack]
```

Repare que `track_name` é incluído para identificação, mas **não entra na transformação numérica** — o pipeline usará apenas `tempo`, `popularity` e `track_genre`.

### A dependência `get_feature_engineer()` e o Autofit

Esse bloco é responsável por entregar um `FeatureEngineer` pronto para uso ao endpoint. Ele contém um **Autofit** com dados `dummy`: se o arquivo `.joblib` não existir ainda (ex: primeiro dia de aula, antes do treino real), a API treina com dois exemplos mínimos para não quebrar.

```python
def get_feature_engineer():
    fe = FeatureEngineer()
    if not fe.transformer_path.exists():
        dummy = pd.DataFrame([
            {"tempo": 120, "popularity": 50, "track_genre": "Pop"},
            {"tempo": 80, "popularity": 10, "track_genre": "Rock"},
        ])
        fe.fit(dummy, ["tempo", "popularity"], ["track_genre"])
    else:
        fe.load()
    return fe
```

!!! abstract "O que o Autofit sabe?"
    Com esses dois registros dummy, o pipeline aprende:
    
    - `tempo`: mínimo = 80, máximo = 120
    - `popularity`: mínimo = 10, máximo = 50
    - Gêneros conhecidos: `Pop` e `Rock`
    
    Qualquer música enviada com esses dois gêneros será transformada corretamente. Gêneros diferentes retornarão `0` em todas as colunas de gênero (por causa do `handle_unknown="ignore"`).

### O endpoint em si

```python
@router.post("/preprocess")
def preprocess_data(request: PreprocessRequest, fe: FeatureEngineer = Depends(get_feature_engineer)):
    try:
        df = pd.DataFrame([t.model_dump() for t in request.tracks])
        df_transformed = fe.transform(df)
        return {
            "transformed_shape": list(df_transformed.shape),
            "features": df_transformed.columns.tolist(),
            "data": df_transformed.to_dict(orient="records"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

O `Depends(get_feature_engineer)` é a **Injeção de Dependência** do FastAPI: o endpoint não cria o `FeatureEngineer` diretamente, ele apenas pede um já pronto. Isso facilita testes e troca de implementação futura.

---

## Registrando o Router

Abra `src/api/v1/router.py` e adicione o novo módulo:

```python
from src.api.v1 import recommendation, library, data_audit, feature_engineering

# ...

api_router.include_router(feature_engineering.router, tags=["feature-engineering"])
```

---

## Laboratório: Testando e Analisando

Suba o servidor:

```bash
uv run fastapi dev
```

Acesse `http://127.0.0.1:8000/docs`. As próximas seções guiam experimentos progressivos — **não vá para o próximo sem analisar o retorno do anterior**.

### Experimento 1 — Uma música conhecida

Envie uma música Rock com valores dentro da escala que o Autofit aprendeu:

```json
{
  "tracks": [
    {
      "track_name": "In the End",
      "track_genre": "Rock",
      "tempo": 105.0,
      "popularity": 88
    }
  ]
}
```

Analise o retorno campo por campo:

- **`transformed_shape`**: Deve ser `[1, 4]` — 1 música, 4 colunas totais (`tempo`, `popularity`, `track_genre_Pop`, `track_genre_Rock`).
- **`features`**: Lista os nomes de cada coluna. Observe que as colunas numéricas vêm primeiro, depois as colunas do OHE com o prefixo `track_genre_`.
- **`data`**: O valor de `track_genre_Rock` deve ser `1.0` e `track_genre_Pop` deve ser `0.0`. Os valores de `tempo` e `popularity` estarão entre `0.0` e `1.0`.

??? tip "Calculando manualmente"
    O Autofit aprendeu `tempo` mínimo = 80 e máximo = 120. Para `tempo = 105`:
    
    $$\frac{105 - 80}{120 - 80} = \frac{25}{40} = 0.625$$
    
    Confira se o valor no retorno bate com essa conta.

### Experimento 2 — Um gênero desconhecido

Envie uma música com um gênero que o Autofit **nunca viu**:

```json
{
  "tracks": [
    {
      "track_name": "Gangnam Style",
      "track_genre": "K-Pop",
      "tempo": 132.0,
      "popularity": 97
    }
  ]
}
```

- A API retornou erro ou respondeu normalmente?
- Olhe os campos `track_genre_Rock` e `track_genre_Pop` no retorno. O que você observa?
- Isso é um problema? Para quem cabe "julgar" que o gênero é inválido?

### Experimento 3 — Múltiplas músicas de uma vez

```json
{
  "tracks": [
    { "track_name": "Bohemian Rhapsody", "track_genre": "Rock", "tempo": 72.0, "popularity": 92 },
    { "track_name": "Blinding Lights", "track_genre": "Pop", "tempo": 171.0, "popularity": 99 },
    { "track_name": "HUMBLE.", "track_genre": "K-Pop", "tempo": 150.0, "popularity": 85 }
  ]
}
```

- Qual é o `transformed_shape` agora?
- Observe a segunda música (Pop): `track_genre_Pop` é `1.0` e `track_genre_Rock` é `0.0`?
- Observe a terceira música (K-Pop): como ficaram as colunas de gênero?

### Experimento 4 — Estourando a escala

O Autofit aprendeu que `tempo` máximo é 120. O que acontece se enviarmos um BPM absurdo?

```json
{
  "tracks": [
    {
      "track_name": "Super Fast",
      "track_genre": "Rock",
      "tempo": 1000.0,
      "popularity": 50
    }
  ]
}
```

- O valor normalizado de `tempo` ficou entre `0` e `1` ou ultrapassou esse limite?
- Calcule manualmente: $(1000 - 80) / (120 - 80)$. O resultado confirma o retorno?
- Isso é um bug? O que deveríamos ter feito antes de chegar aqui? (Dica: lembre-se do `DataCleaner`.)

!!! abstract "A conexão entre as semanas"
    A limpeza da semana anterior e a transformação desta semana são complementares. O `DataCleaner` remove outliers **antes** do `fit()` para que a escala aprendida reflita dados reais. Se o treino incluiu `tempo = 1000`, o modelo teria aprendido uma escala distorcida — e músicas normais ficariam comprimidas em uma faixa minúscula perto de `0`.

### Experimento 5 — Apagando a memória

1. Pare o servidor (`Ctrl + C`).
2. Apague o arquivo `models/transformers.joblib`.
3. Suba o servidor novamente.
4. Envie a mesma requisição do Experimento 1.

- O servidor quebrou ou funcionou?
- Olhe o `transformed_shape` — ele ficou igual ao do Experimento 1?
- Abra a pasta `models/` — o arquivo `.joblib` foi recriado?

Isso demonstra que o Autofit é uma **rede de segurança para o laboratório**, não uma substituta do treino real.

---

## Treinando com Dados Reais

Até agora, o pipeline usa os dois exemplos dummy. Para refletir a realidade do dataset do Spotify, precisamos treinar com o `dataset_clean.csv` gerado na semana anterior.

Crie o arquivo `scripts/train_feature_engineer.py`:

### Carregando o dataset e escolhendo colunas

```python
import pandas as pd
from src.services.feature_engineer import FeatureEngineer

df = pd.read_csv("data/processed/dataset_clean.csv")

numeric = ["tempo", "popularity", "danceability", "energy"]
categorical = ["track_genre"]
```

Estamos escolhendo 4 colunas numéricas e 1 categórica. Após o OHE, o número de colunas vai crescer — uma coluna nova para cada gênero único no dataset.

### Executando o fit e verificando o resultado

```python
fe = FeatureEngineer()
fe.fit(df, numeric, categorical)

print(f"Colunas geradas: {fe.feature_names}")
print(f"Total de features: {len(fe.feature_names)}")
```

Execute o script:

```bash
uv run python scripts/train_feature_engineer.py
```

Observe a saída:

- Quantas colunas foram geradas no total?
- Quantos gêneros únicos existem no dataset? (É o total de colunas menos 4.)
- O arquivo `models/transformers.joblib` foi criado ou atualizado?

### Comparando dummy vs. dados reais

Suba o servidor novamente e repita o **Experimento 4** (BPM = 1000).

- O valor normalizado de `tempo` ainda passa de `1.0`?
- Qual é agora o `transformed_shape` para uma única música?
- As colunas `track_genre_K-Pop` aparecem desta vez? (Dica: verifique quantos gêneros o Spotify dataset cobre.)

---

## O que geramos para a próxima semana

Ao final desta aula, dois artefatos ficam prontos:

| Artefato | O que é | Para que serve |
| :--- | :--- | :--- |
| `models/transformers.joblib` | O pipeline treinado (limites, categorias) | Traduz qualquer entrada da API para números na mesma escala |
| `data/processed/dataset_features.csv` | O dataset inteiro convertido em números | O "livro de estudos" que o modelo de ML irá consumir |

!!! abstract "Em resumo"
    Esta semana criamos a **linguagem numérica** que o modelo precisa. Na próxima semana, construiremos o **modelo** que usa essa linguagem para recomendar músicas.

---

<quiz>
Por que não podemos usar os números 1, 2 e 3 para representar Rock, Pop e Jazz em um modelo de ML?

* [ ] Porque modelos de ML não aceitam números inteiros.
* [x] Porque o modelo interpretaria uma ordem inexistente entre os gêneros.
* [ ] Porque o Scikit-Learn não suporta valores acima de 1.
</quiz>

<quiz>
Qual método do pipeline deve ser chamado exclusivamente durante o treinamento e nunca na API em produção?

* [ ] `transform()`
* [ ] `load()`
* [x] `fit()`
</quiz>

<quiz>
O que o arquivo `transformers.joblib` armazena?

* [ ] O dataset de músicas convertido em números.
* [ ] Os pesos do modelo de recomendação.
* [x] Os parâmetros aprendidos pelo pipeline (limites de escala e categorias).
</quiz>

<quiz>
Uma música enviada com `tempo = 1000` BPM resulta em um valor normalizado acima de 1.0. Qual é a causa?

* [ ] O endpoint tem um bug de cálculo.
* [x] O transformador usa os limites aprendidos no `fit()`, e 1000 ultrapassa o máximo visto no treino.
* [ ] O `MinMaxScaler` não suporta valores acima de 200.
</quiz>

<quiz>
O que representa o `transformed_shape: [3, 6]` no retorno do endpoint `/preprocess`?

* [ ] 3 atributos e 6 músicas processadas.
* [ ] 3 colunas categóricas e 6 colunas numéricas.
* [x] 3 músicas enviadas, cada uma com 6 atributos numéricos após a transformação.
</quiz>

---

<quiz>
Por que não podemos usar os números 1, 2 e 3 para representar Rock, Pop e Jazz em um modelo de ML?

* [ ] Porque modelos de ML não aceitam números inteiros.
* [x] Porque o modelo interpretaria uma ordem inexistente entre os gêneros.
* [ ] Porque o Scikit-Learn não suporta valores acima de 1.
</quiz>

<quiz>
Qual método do pipeline deve ser chamado exclusivamente durante o treinamento e nunca na API em produção?

* [ ] `transform()`
* [ ] `load()`
* [x] `fit()`
</quiz>

<quiz>
O que o arquivo `transformers.joblib` armazena?

* [ ] O dataset de músicas convertido em números.
* [ ] Os pesos do modelo de recomendação.
* [x] Os parâmetros aprendidos pelo pipeline (limites de escala e categorias).
</quiz>

<quiz>
Uma música enviada com `tempo = 1000` BPM resulta em um valor normalizado acima de 1.0. Qual é a causa?

* [ ] O endpoint tem um bug de cálculo.
* [x] O transformador usa os limites aprendidos no `fit()`, e 1000 ultrapassa o máximo visto no treino.
* [ ] O `MinMaxScaler` não suporta valores acima de 200.
</quiz>

<quiz>
O que representa o `transformed_shape: [3, 6]` no retorno do endpoint `/preprocess`?

* [ ] 3 atributos e 6 músicas processadas.
* [ ] 3 colunas categóricas e 6 colunas numéricas.
* [x] 3 músicas enviadas, cada uma com 6 atributos numéricos após a transformação.
</quiz>
