# O Ciclo de Dados

Este guia detalha como construímos o pipeline de ETL (Extract, Transform, Load) para limpar e analisar o dataset do Spotify. Ao final, o aluno terá:

* Um módulo reutilizável de limpeza de dados (`DataCleaner`)
* Dois novos endpoints na API: upload de biblioteca e auditoria de dados
* Um dataset limpo e pronto para alimentar modelos de ML

---

## Conceitos Chave

!!! info "Objetivos"
    * Entender os princípios de ETL e a importância da qualidade dos dados.
    * Conhecer estratégias para tratamento de valores nulos, outliers e análise de correlação.

### O que é ETL?

ETL significa **Extract, Transform, Load**. É o processo padrão de preparação de dados para projetos de Machine Learning:

1. **Extract**: Carregar os dados brutos (CSV, JSON, banco de dados).
2. **Transform**: Limpar, normalizar e tratar anomalias.
3. **Load**: Salvar ou disponibilizar os dados transformados.

### Garbage In, Garbage Out

A regra de ouro do Aprendizado de Máquina: **se os dados de entrada são ruins, a saída final também será**. Um algoritmo fantástico treinado com dados ruins e sujos resultará na geração de predições ruins.

### Valores Nulos (Missings)

Campos vazios no dataset. Algumas estratégias comuns para tratar problemas assim:

* **Remover**: Descartar a linha inteira do registro (ideal quando o volume de dados é grande).
* **Preencher com mediana/média**: Forma simples de suprir a falta para dados numéricos.
* **Preencher com valor padrão**: Como classificar sob a descrição "desconhecido" para campos textuais com o mesmo erro.

### Outliers (Valores Discrepantes)

Valores que fogem muito do padrão normal dos dados ou comportamento. Por exemplo: uma música com `tempo = 0` ou até `loudness = 0 dB`.

??? tip "O que é o IQR (Interquartile Range)?"
    O **IQR** (Intervalo Interquartil) é a diferença entre o terceiro quartil (Q3) e o primeiro quartil (Q1) de um conjunto de dados. Ele representa a **faixa onde estão concentrados os 50% centrais** dos valores, descartando os extremos.

    * **Q1** (1o Quartil) = percentil 25% - abaixo desse valor estão 25% dos dados.
    * **Q3** (3o Quartil) = percentil 75% - abaixo desse valor estão 75% dos dados.
    * **IQR** = Q3 - Q1 - a "largura" da faixa central.

??? tip "Por que usar o IQR para detectar outliers?"
    Diferente da **média** e do **desvio padrão**, o IQR **não é influenciado por valores extremos**. Se um dataset de músicas tiver uma faixa com `loudness = 999 dB` por erro, a média e o desvio padrão seriam distorcidos por esse valor absurdo, mas o IQR permaneceria estável, pois ele olha apenas para a faixa central dos dados.

??? tip "Por que o fator 1.5?"
    A fórmula clássica para definir os limites de um outlier é:

    * **Limite inferior** = Q1 - 1.5 * IQR
    * **Limite superior** = Q3 + 1.5 * IQR

    Tudo que estiver **fora** desses limites é considerado um **outlier**.

### Correlação

A correlação ajuda a entender como o comportamento de uma variável "arrasta" outra. Ela é medida em uma escala de **-1 a +1**:

* **Correlação Positiva (+1)**: As variáveis caminham juntas. Se uma aumenta, a outra também aumenta.
* **Sem Correlação (0)**: As variáveis são independentes. O que acontece com uma não afeta a outra.
* **Correlação Negativa (-1)**: As variáveis são inversas. Se uma aumenta, a outra diminui.

### O Ciclo Contínuo (Feedback Loop)

O pipeline de Limpeza e ETL não serve apenas para o dataset inicial. Em sistemas reais, o processo é contínuo e dinâmico:

1. **Novos Dados**: O usuário escuta novas músicas "na última hora".
2. **Injeção via API**: Esses dados brutos chegam pelo endpoint `/library/upload`.
3. **Limpeza em Tempo Real**: O `DataCleaner` garante que essa "música nova" não tenha nulos ou outliers que quebrariam o modelo.
4. **Recomendação Atualizada**: Os dados limpos alimentam o algoritmo, que agora pode recomendar algo baseado no gosto *atualizado* do usuário.

!!! tip "O Ciclo Vivo"
    No futuro deste projeto, utilizaremos essa mesma estrutura para permitir que o sistema se adapte ao comportamento do usuário em tempo real, transformando um modelo estático em um sistema inteligente e "vivo".

---

## O Módulo de Limpeza (`src/services/data_cleaner.py`)

Vamos criar uma classe `DataCleaner` que encapsula todo o pipeline ETL.

### 1.1. Estrutura do Arquivo

Crie o diretório `src/services/` (com `__init__.py` vazio) e o arquivo `data_cleaner.py`:

??? example "Importações e Constantes"
    ```python
    import pandas as pd
    import numpy as np
    from pathlib import Path
    from io import BytesIO

    # Colunas numéricas do dataset Spotify que usaremos para análise
    SPOTIFY_NUMERIC_COLS = [
        "popularity", "duration_ms", "danceability", "energy",
        "loudness", "speechiness", "acousticness", "instrumentalness",
        "liveness", "valence", "tempo",
    ]

    # Colunas obrigatórias para o upload de biblioteca
    REQUIRED_LIBRARY_COLS = ["track_name", "artists", "energy", "loudness"]
    ```

### 1.2. Carregando Dados

Nossa classe precisa ser hábil a ler a entrada de diferentes direções.

??? example "Construtores Alternativos"
    ```python
    class DataCleaner:
        def __init__(self, df: pd.DataFrame | None = None):
            self.df = df

        @classmethod
        def from_csv(cls, path: str | Path, **kwargs) -> "DataCleaner":
            """Carrega dados de um arquivo CSV no disco."""
            df = pd.read_csv(path, **kwargs)
            return cls(df=df)

        @classmethod
        def from_bytes(cls, content: bytes, file_type: str = "csv") -> "DataCleaner":
            """Carrega dados a partir de bytes (usado pelo endpoint de upload)."""
            buffer = BytesIO(content)
            if file_type == "json":
                df = pd.read_json(buffer)
            else:
                df = pd.read_csv(buffer)
            return cls(df=df)
    ```

!!! abstract "Explicação Técnica"
    Repare no uso do `@classmethod`: em Python, eles permitem comportamentos no escopo da classe (e não da instância), funcionando como construtores alternativos para criar um `DataCleaner` a partir de múltiplas fontes.

### 1.3. Diagnóstico (Relatório de Saúde)

O método `diagnose()` analisa o DataFrame e gera um relatório completo:

??? example "Diagnóstico Geral"
    ```python
    def diagnose(self) -> dict:
        df = self.df
        report = {}

        report["total_rows"] = int(len(df))
        report["total_columns"] = int(len(df.columns))
        report["duplicate_rows"] = int(df.duplicated().sum())

        # Relatório por coluna
        columns_report = []
        for col in df.columns:
            missing = int(df[col].isna().sum())
            total = len(df)
            sample_values = df[col].dropna().head(3).tolist()
            sample_values = [v.item() if hasattr(v, "item") else v for v in sample_values]

            columns_report.append({
                "name": col,
                "dtype": str(df[col].dtype),
                "missing_count": missing,
                "missing_pct": round(missing / total * 100, 2) if total > 0 else 0,
                "unique_count": int(df[col].nunique()),
                "sample_values": sample_values,
            })
        report["columns"] = columns_report

        # Detecção de Outliers (IQR)
        outliers_report = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        for col in numeric_cols:
            q1 = float(df[col].quantile(0.25))
            q3 = float(df[col].quantile(0.75))
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            n_outliers = int(((df[col] < lower) | (df[col] > upper)).sum())
            total_notna = int(df[col].notna().sum())

            outliers_report.append({
                "column": col,
                "total_outliers": n_outliers,
                "outlier_pct": round(n_outliers / total_notna * 100, 2) if total_notna > 0 else 0,
                "lower_bound": round(lower, 4),
                "upper_bound": round(upper, 4),
            })
        report["outliers"] = outliers_report

        # Estatísticas e correlações
        if numeric_cols:
            report["numeric_summary"] = df[numeric_cols].describe().round(4).to_dict()
            if len(numeric_cols) >= 2:
                report["correlations"] = df[numeric_cols].corr().round(4).to_dict()
            else:
                report["correlations"] = {}
        else:
            report["numeric_summary"] = {}
            report["correlations"] = {}

        report["health_score"] = self._calculate_health_score(report)
        return report
    ```

### 1.4. Pipeline de Limpeza

O método `clean()` aplica as transformações necessárias para finalizar as validações:

??? example "Processo de Limpeza"
    ```python
    def clean(self, save_path: str | Path | None = None) -> pd.DataFrame:
        df = self.df.copy()

        # 1. Remover coluna de índice duplicado do CSV original
        if "Unnamed: 0" in df.columns:
            df = df.drop(columns=["Unnamed: 0"])

        # 2. Remover duplicatas
        if "track_id" in df.columns:
            df = df.drop_duplicates(subset=["track_id"], keep="first")
        else:
            df = df.drop_duplicates(keep="first")

        # 3. Tratar valores nulos
        text_critical = [c for c in ["track_name", "artists"] if c in df.columns]
        if text_critical:
            df = df.dropna(subset=text_critical)

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isna().sum() > 0:
                df[col] = df[col].fillna(df[col].median())

        # 4. Normalizar loudness (escala 0-1)
        if "loudness" in df.columns:
            loud_min = df["loudness"].min()
            loud_max = df["loudness"].max()
            if loud_max != loud_min:
                df["loudness_norm"] = ((df["loudness"] - loud_min) / (loud_max - loud_min)).round(6)
            else:
                df["loudness_norm"] = 0.0

        # 5. Salvar (opcional)
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(save_path, index=False)

        self.df = df
        return df
    ```

### 1.5. Health Score

O `health_score` funciona como uma nota de 0 a 100 que resume a qualidade geral do dataset. Ele é composto por tres critérios ponderados:

* **Completude (peso 40%)**: Porcentagem de valores preenchidos (sem nulos) no dataset.
* **Unicidade (peso 30%)**: Porcentagem de registros que não são duplicatas.
* **Consistência (peso 30%)**: Porcentagem de valores numéricos que não foram classificados como outliers.

??? example "Cálculo do Score"
    ```python
    def _calculate_health_score(self, report: dict) -> float:
        total_rows = report["total_rows"]
        total_cols = report["total_columns"]

        if total_rows == 0 or total_cols == 0:
            return 0.0

        # Completude (40 pts)
        total_missing = sum(c["missing_count"] for c in report["columns"])
        total_cells = total_rows * total_cols
        completude = (1 - total_missing / total_cells) * 40

        # Unicidade (30 pts)
        dup = report["duplicate_rows"]
        unicidade = (1 - dup / total_rows) * 30

        # Consistência / Outliers (30 pts)
        if report["outliers"]:
            total_outlier_cells = sum(o["total_outliers"] for o in report["outliers"])
            total_numeric_cells = sum(total_rows for _ in report["outliers"])
            consistencia = (1 - total_outlier_cells / total_numeric_cells) * 30
        else:
            consistencia = 30.0

        score = completude + unicidade + consistencia
        return round(max(0, min(100, score)), 1)
    ```

### 1.6. Validação de Upload de Biblioteca

O método abaixo valida formato e colunas obrigatórias para aceitar apenas dados com qualidade mínima:

??? example "Validação de Upload"
    ```python
    def validate_library_upload(self) -> dict:
        df = self.df
        result = {
            "total_received": len(df), "total_valid": 0, "total_invalid": 0,
            "invalid_rows": [], "sample": []
        }

        # Verificar colunas obrigatórias
        missing_cols = [c for c in REQUIRED_LIBRARY_COLS if c not in df.columns]
        if missing_cols:
            result["invalid_rows"].append({"row": -1, "reason": f"Colunas ausentes: {missing_cols}"})
            result["total_invalid"] = len(df)
            return result

        mask_valid = pd.Series(True, index=df.index)

        # Verificar nulos em colunas obrigatórias
        for col in REQUIRED_LIBRARY_COLS:
            null_mask = df[col].isna()
            if null_mask.any():
                for idx in df[null_mask].index:
                    result["invalid_rows"].append({"row": int(idx), "reason": f"Nulo em '{col}'"})
                mask_valid = mask_valid & ~null_mask

        # Verificar tipos numéricos
        for col in ["energy", "loudness"]:
            if col in df.columns:
                numeric_mask = pd.to_numeric(df[col], errors="coerce").notna()
                invalid = ~numeric_mask & df[col].notna()
                if invalid.any():
                    for idx in df[invalid].index:
                        result["invalid_rows"].append({"row": int(idx), "reason": f"Não numérico em '{col}'"})
                    mask_valid = mask_valid & numeric_mask

        result["total_valid"] = int(mask_valid.sum())
        result["total_invalid"] = int((~mask_valid).sum())

        valid_df = df[mask_valid].head(5)
        sample = valid_df.to_dict(orient="records")
        for record in sample:
            for k, v in record.items():
                if hasattr(v, "item"):
                    record[k] = v.item()
        result["sample"] = sample

        return result
    ```

---

## Novos Schemas (`src/schemas.py`)

Adicione os novos modelos ao arquivo existente:

??? example "Código Schemas"
    ```python
    class LibraryUploadResponse(BaseModel):
        """Resposta do upload de biblioteca de músicas."""
        total_received: int
        total_valid: int
        total_invalid: int
        invalid_rows: list[dict]
        sample: list[dict]

    class ColumnReport(BaseModel):
        """Relatório de saúde de uma coluna."""
        name: str
        dtype: str
        missing_count: int
        missing_pct: float
        unique_count: int
        sample_values: list

    class OutlierReport(BaseModel):
        """Relatório de outliers de uma coluna numérica."""
        column: str
        total_outliers: int
        outlier_pct: float
        lower_bound: float
        upper_bound: float

    class DataAuditResponse(BaseModel):
        """Relatório completo de auditoria/saúde de um dataset."""
        total_rows: int
        total_columns: int
        duplicate_rows: int
        columns: list[ColumnReport]
        outliers: list[OutlierReport]
        numeric_summary: dict
        correlations: dict
        health_score: float
    ```

---

## Endpoint de Upload (`src/api/v1/library.py`)

Endpoint que recebe um CSV com novas músicas e valida os dados:

??? example "Upload de Biblioteca"
    ```python
    from fastapi import APIRouter, UploadFile, File, HTTPException
    from src.schemas import LibraryUploadResponse
    from src.services.data_cleaner import DataCleaner

    router = APIRouter()

    @router.post(
        "/library/upload",
        response_model=LibraryUploadResponse,
        summary="Upload de biblioteca de músicas",
    )
    async def upload_library(file: UploadFile = File(..., description="Arquivo CSV com músicas")):
        # 1. Valida tipo de arquivo
        if not file.filename or not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Apenas arquivos CSV são aceitos.")

        # 2. Lê e processa
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Arquivo vazio.")

        try:
            cleaner = DataCleaner.from_bytes(content, file_type="csv")
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Erro ao processar o CSV: {str(e)}")

        # 3. Valida colunas obrigatórias e retorna resumo
        return cleaner.validate_library_upload()
    ```

O CSV deve conter ao menos: `track_name`, `artists`, `energy`, `loudness`.

---

## Endpoint de Auditoria (`src/api/v1/data_audit.py`)

Endpoint que recebe **qualquer** CSV e retorna um relatório de saúde:

??? example "Auditoria de Dados"
    ```python
    from fastapi import APIRouter, UploadFile, File, HTTPException
    from src.schemas import DataAuditResponse
    from src.services.data_cleaner import DataCleaner

    router = APIRouter()

    @router.post(
        "/data/audit",
        response_model=DataAuditResponse,
        summary="Auditoria de saúde de um dataset",
    )
    async def audit_data(file: UploadFile = File(..., description="Arquivo CSV para auditoria")):
        if not file.filename or not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Apenas arquivos CSV são aceitos.")

        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Arquivo vazio.")

        try:
            cleaner = DataCleaner.from_bytes(content, file_type="csv")
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Erro ao processar o CSV: {str(e)}")

        return cleaner.diagnose()
    ```

O relatório inclui:

* Contagem de nulos por coluna
* Detecção de outliers (IQR)
* Estatísticas descritivas
* Matriz de correlação
* **Health Score** (nota de 0 a 100)

---

## Registrando as Rotas (`src/api/v1/router.py`)

Adicione os novos módulos ao roteador existente:

??? example "Router Index"
    ```python
    from src.api.v1 import recommendation, library, data_audit

    api_router = APIRouter(prefix="/api/v1")

    # ... router de recomendação ...
    api_router.include_router(recommendation.router, tags=["recommendation"])

    # Novos routers
    api_router.include_router(library.router, tags=["library"])
    api_router.include_router(data_audit.router, tags=["data-audit"])
    ```

---

## Script de Limpeza (`scripts/clean_dataset.py`)

Para gerar o dataset limpo de forma reprodutível:

??? example "Script Completo"
    ```python
    import sys
    from pathlib import Path

    # Adiciona a raiz do projeto no path do script
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

    from src.services.data_cleaner import DataCleaner

    def main():
        raw_path = project_root / "data" / "raw" / "dataset.csv"
        clean_path = project_root / "data" / "processed" / "dataset_clean.csv"

        print("=" * 60)
        print("  Pipeline de Limpeza - Dataset Spotify")
        print("=" * 60)

        # 1. Carregar
        print(f"\n[1/3] Carregando dados de: {raw_path}")
        cleaner = DataCleaner.from_csv(raw_path)

        # 2. Diagnóstico Prévio
        print("\n[2/3] Diagnóstico ANTES da limpeza:")
        report = cleaner.diagnose()
        print(f"      Health Score: {report['health_score']}/100")

        # 3. Limpar e salvar
        print("\n[3/3] Executando pipeline de limpeza...")
        cleaner.clean(save_path=clean_path)

        # 4. Diagnóstico final
        print("\n--- Diagnóstico DEPOIS da limpeza ---")
        report_after = cleaner.diagnose()
        print(f"      Health Score: {report_after['health_score']}/100")

    if __name__ == "__main__":
        main()
    ```

Execução:

```bash
uv run python scripts/clean_dataset.py
```

---

## Testando

### Via Swagger UI

1. Certifique-se de que instalou as dependências com `uv`:
   ```bash
   uv sync
   ```
2. Suba o servidor na raiz do projeto:
   ```bash
   uv run fastapi dev main.py
   ```
3. Abra `http://127.0.0.1:8000/docs` no navegador.
4. Teste **POST /api/v1/data/audit** com upload do `dataset.csv` bruto.
5. Teste **POST /api/v1/library/upload** com upload de um CSV pequeno contendo algumas músicas válidas.

### Via Script

```bash
uv run scripts/clean_dataset.py
```

Verifique que o arquivo `data/processed/dataset_clean.csv` foi criado com sucesso.

---

## Exercício de Fixação: Auditando Seus Próprios Dados

1. Crie um arquivo CSV com pelo menos 10 linhas e 5 colunas numéricas.
2. Introduza propositalmente: 3 valores nulos, 2 duplicatas e 1 outlier extremo.
3. Faça upload no endpoint `POST /api/v1/data/audit`.
4. Analise o relatório:
   - O `health_score` reflete os problemas que você criou?
   - Quantos outliers foram detectados?
   - Qual coluna tem mais nulos?
5. Corrija os problemas e faça upload novamente. O score melhorou?



