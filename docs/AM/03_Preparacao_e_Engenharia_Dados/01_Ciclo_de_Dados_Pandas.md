# O Ciclo de Dados (Pandas)

> Explorando o pipeline de ETL.

---

## Conceitos Chave

!!! info "Objetivos"
    * Entender os princípios de ETL e a importância da qualidade dos dados.
    * Conhecer estratégias para tratamento de valores nulos, outliers e análise de correlação.

### O que é ETL?

ETL significa **Extract, Transform, Load**. É o processo padrão de preparação de dados para projetos de Machine Learning:

* **Extract**: Carregar os dados brutos (CSV, JSON, banco de dados).
* **Transform**: Limpar, normalizar e tratar anomalias.
* **Load**: Salvar ou disponibilizar os dados transformados.

### Garbage In, Garbage Out

A regra de ouro do Aprendizado de Máquina: **se os dados de entrada são ruins, a saída final também será**. Um algoritmo fantástico treinado com dados ruins e sujos resultará na geração de predições ruins.

### Valores Nulos (Missings)

Campos vazios no dataset. Algumas estratégias comuns para tratar problemas assim:

* **Remover**: Descartar a linha inteira do registro (ideal quando o volume de dados é grande).
* **Preencher com mediana/média**: Forma simples de suprir a falta para dados numéricos.
* **Preencher com valor padrão**: Como classificar sob a descrição "desconhecido" para campos textuais com o mesmo erro.

### Outliers (Valores Discrepantes)

Valores que fogem muito do padrão normal dos dados ou comportamento. Por exemplo: uma música com `tempo = 0` ou até `loudness = 0 dB`.

??? tip "Método IQR (Interquartile Range)"
    Para detectar outliers de forma eficiente na estatística visual, podemos usar quartis:
    
    * **Q1** = percentil 25%
    * **Q3** = percentil 75%
    * **IQR** = Q3 - Q1
    * **Limite inferior** = Q1 - 1.5 * IQR
    * **Limite superior** = Q3 + 1.5 * IQR

    No geral, tudo detectado fora desses limites costuma ser visto e modelado como um **outlier**.

### Correlação

A correlação ajuda a entender como o comportamento de uma variável "arrasta" outra. Ela é medida em uma escala de **-1 a +1**:

* **Correlação Positiva (+1)**: As variáveis caminham juntas. Se uma aumenta, a outra também aumenta.
    - *Exemplo*: Em geral, quanto maior a **Loudness** (volume), maior tende a ser a **Energy** da música.
* **Sem Correlação (0)**: As variáveis são independentes. O que acontece com uma não afeta a outra.
    - *Exemplo*: A **Duração** da música não costuma ter relação direta com o fato dela ser **Instrumental** ou não.
* **Correlação Negativa (-1)**: As variáveis são inversas. Se uma aumenta, a outra diminui.
    - *Exemplo*: Geralmente, quanto mais **Acousticness** (acústica) tem uma música, menor é a sua **Energy**.

??? info "Por que isso importa?"
    No Aprendizado de Máquina, identificar correlações fortes nos ajuda a entender quais características (features) são mais importantes para o modelo e quais podem ser redundantes por dizerem a "mesma coisa".

### O Ciclo Contínuo (Feedback Loop)

O pipeline de Limpeza e ETL não serve apenas para o dataset inicial. Em sistemas reais, o processo é contínuo e dinâmico:

1. **Novos Dados**: O usuário escuta novas músicas "na última hora".
2. **Injeção via API**: Esses dados brutos chegam pelo endpoint `/library/upload`.
3. **Limpeza em Tempo Real**: O `DataCleaner` garante que essa "música nova" não tenha nulos ou outliers que quebrariam o modelo.
4. **Recomendação Atualizada**: Os dados limpos alimentam o algoritmo, que agora pode recomendar algo baseado no gosto *atualizado* do usuário.

!!! tip "O Ciclo Vivo"
    No futuro deste projeto, utilizaremos essa mesma estrutura para permitir que o sistema se adapte ao comportamento do usuário em tempo real, transformando um modelo estático em um sistema inteligente e "vivo".


---

## Módulo de Limpeza (`DataCleaner`)

Este módulo abrange as funções necessárias utilizadas no curso para gerenciar e adequar as características do projeto.

### Estrutura Base

Comece criando o diretório `src/services/` (com um `__init__.py` vazio), e crie um novo arquivo `data_cleaner.py`:

??? example "Importação"
    ```python
    import pandas as pd
    import numpy as np
    from pathlib import Path
    from io import BytesIO
    ```

### Carregando Dados

Nossa classe precisa ser hábil a ler a entrada de diferentes direções.

??? example "Código Padrão"
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
    Repare no uso do declarador `@classmethod` nesses escopos acima, em Python eles viabilizam um comportamento no escopo da classe em vez da instância do objeto: são utilizados aqui funcionando como opções ou "construtores alternativos" fornecendo e instanciando um `DataCleaner` através de métodos de entrada diversificados.

### Diagnóstico de Anomalias (Relatório de Saúde)

O método `diagnose()` examinará os dados e produzirá um log mapeando a saúde do arquivo recebido:

??? example "Diagnóstico Geral"
    ```python
        def diagnose(self) -> dict:
            df = self.df
            report = {}

            report["total_rows"] = int(len(df))
            report["total_columns"] = int(len(df.columns))
            report["duplicate_rows"] = int(df.duplicated().sum())

            # Relatório por coluna para iterar e apontar faltantes
            columns_report = []
            for col in df.columns:
                missing = int(df[col].isna().sum())
                columns_report.append({
                    "name": col,
                    "dtype": str(df[col].dtype),
                    "missing_count": missing,
                    "missing_pct": round(missing / len(df) * 100, 2),
                    "unique_count": int(df[col].nunique()),
                    "sample_values": df[col].dropna().head(3).tolist(),
                })
            report["columns"] = columns_report
            # Próxima etapa (cálculo IQR)...
    ```

Para mapear e identificar excessos fora da curva normal como outliers pelo IQR:

??? example "Aferindo Outliers pela Quantile"
    ```python
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
    ```

### Pipeline Prática

O método responsável para unificar os processos será o novo `clean()` efetuando as transformações necessárias para finalizar as validações.

??? example "Processo de Limpeza"
    ```python
        def clean(self, save_path=None) -> pd.DataFrame:
            df = self.df.copy()

            # 1. Remover coluna de índice duplicado, caso ela interfira.
            if "Unnamed: 0" in df.columns:
                df = df.drop(columns=["Unnamed: 0"])

            # 2. Remover completas duplicatas visíveis por track_id.
            if "track_id" in df.columns:
                df = df.drop_duplicates(subset=["track_id"], keep="first")

            # 3. Tratar os retornos textuais em colunas nulas.
            df = df.dropna(subset=["track_name", "artists"])
            
            # 4. Tratar nulos numéricos transformando a partir da "Media Centralizada".
            for col in df.select_dtypes(include=[np.number]).columns:
                df[col] = df[col].fillna(df[col].median())

            # 5. Normalizar escalas (exemplo loudness 0 a 1)
            if "loudness" in df.columns:
                loud_min, loud_max = df["loudness"].min(), df["loudness"].max()
                df["loudness_norm"] = (df["loudness"] - loud_min) / (loud_max - loud_min)

            # 6. Gravar caso a base salve algum histórico.
            if save_path:
                df.to_csv(save_path, index=False)

            self.df = df
            return df
    ```

### Entendendo a Métrica Final (Health Score)

O `health_score` vai figurar como um consolidado resumível para a avaliação da "sanidade vital" nos dados. Como um número de aprovação acadêmica entre 0 a 100 baseado na:
* **Completude (peso=40)**: Quão cheios e preenchidos estão os valores analisáveis.
* **Unicidade (peso=30)**: Quão baixas são as clonagens e repetições indevidas nas tabelas.
* **Consistência (peso=30)**: Medida comparativa pela porcentagem e não detecção de elementos listados em Outlier.

---

## Contratos Pydantic (`src/schemas.py`)

A seguir declararemos ao sistema e a API modelos adequados na arquitetura Rest, baseados nas validações descritas para o fluxo ETL e as repostas exigidas no `Pydantic`:

??? example "Código Schemas"
    ```python
    class LibraryUploadResponse(BaseModel):
        """Resposta do upload de biblioteca de músicas."""
        total_received: int
        total_valid: int
        total_invalid: int
        invalid_rows: list[dict]
        sample: list[dict]

    class DataAuditResponse(BaseModel):
        """Relatório completo de auditoria/saúde de um dataset."""
        total_rows: int
        total_columns: int
        duplicate_rows: int
        columns: list[dict] # ColumnReport aqui internamente
        outliers: list[dict] # OutlierReport 
        numeric_summary: dict
        correlations: dict
        health_score: float
    ```

---

## Novos Endpoints

A recepção destas chamadas utilizará portas designadas e lógicas independentes que a equipe deve plugar:

### Recepção do Dataset (`api/v1/library.py`)

No upload do CSV o arquivo de dados deve repassar pelo mínimo: `track_name`, `artists`, `energy`, `loudness`.

??? example "Rota de Validação Inicial"
    ```python
    from fastapi import APIRouter, UploadFile, File, HTTPException
    from src.services.data_cleaner import DataCleaner

    router = APIRouter()

    @router.post("/library/upload")
    async def upload_library(file: UploadFile = File(...)):
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Apenas CSV aceito.")

        content = await file.read()
        cleaner = DataCleaner.from_bytes(content)

        return cleaner.validate_library_upload()
    ```

### Auditoria Completa (`api/v1/data_audit.py`)

E o relator final englobará a classe responsável que emite os status finais de IQR, Outliers e a nota principal.

??? example "Rota de Diagnósticos e Correlacionamento"
    ```python
    @router.post("/data/audit")
    async def audit_data(file: UploadFile = File(...)):
        content = await file.read()
        cleaner = DataCleaner.from_bytes(content)
        return cleaner.diagnose()
    ```

### Router Index (`api/v1/router.py`)

Lembrando de compilar e declarar a injeção nas instâncias ` FastAPI Router`:

??? example "Configuração dos Roteadores Injetados da Semana Atual"
    ```python
    from src.api.v1 import recommendation, library, data_audit

    api_router.include_router(library.router, tags=["library"])
    api_router.include_router(data_audit.router, tags=["data-audit"])
    ```

---

## O Aplicador Limpo (`scripts/clean_dataset.py`)

O código para rodar sem dependências e ter o arquivo processado pelo script CLI manual pode ser embutido como um arquivo de Python padrão que chame suas regras ou utilize o gestor atual "uv":

```bash
uv run python scripts/clean_dataset.py
```

Passos que se executaram no projeto base:

* Carregar o dado na subpasta referenciada `data/raw/dataset.csv`.
* Mostrar um descritivo rápido de colunas e anomalias do estágio primário.
* Desencadear os transformadores (O método `clean`).
* Gravar e gerar subproduto seguro e limpo em `data/processed/dataset_clean.csv`.
* Mostrar a evolução log de melhora de Health Score.



