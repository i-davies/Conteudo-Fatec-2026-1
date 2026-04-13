# Revisao de Arquitetura: Migrations e Seeds

> Garantindo a rastreabilidade das tabelas com Alembic e automatizando a carga inicial de dados.

No documento anterior, utilizamos `db.create_all()` dentro do `backend.py` para criar as tabelas do banco. Isso funciona para um projeto simples, mas traz um problema real: e se precisarmos adicionar uma nova coluna ao `TecnologiaModel` (por exemplo, `url`)? O `create_all()` **nao altera tabelas ja existentes**, ele so cria tabelas novas.

Para resolver isso, usamos o **Alembic**, que funciona como um "Git para o banco de dados": ele detecta mudancas nos Models e gera scripts de migracao que atualizam a estrutura do banco de forma controlada.

---

## Configurando o Alembic

### Instalacao

```bash
uv add alembic
```

### Inicializacao

O comando abaixo cria a pasta `migrations/` com toda a estrutura que o Alembic precisa:

```bash
uv run alembic init migrations
```

### Configurando a Conexao

Apos a inicializacao, precisamos ajustar dois arquivos para que o Alembic enxergue nosso banco e nossos Models:

**Arquivo `alembic.ini`** - Atualize a linha `sqlalchemy.url` para apontar para o mesmo banco SQLite do projeto:

```ini
sqlalchemy.url = sqlite:///banco.sqlite
```

**Arquivo `migrations/env.py`** - Importe o `db` e aponte o `target_metadata` para que o Alembic saiba quais tabelas rastrear:

```python
from database import db
from models import TecnologiaModel  # Necessario para o Alembic enxergar a tabela

target_metadata = db.metadata
```

??? info "Por que importar o TecnologiaModel?"
    Mesmo sem usar a variavel diretamente, o `import` faz o Python executar a definicao da classe, registrando a tabela no `db.metadata`. Sem esse import, o Alembic nao detecta nenhuma tabela para migrar.

---

## Gerando e Aplicando Migrations

Com tudo configurado, o fluxo de trabalho segue dois comandos:

```bash
# Gera automaticamente um script de migracao baseado nas diferencas entre os Models e o banco
uv run alembic revision --autogenerate -m "Criacao da Tabela Tecnologia"

# Aplica a migracao, criando/alterando as tabelas no banco
uv run alembic upgrade head
```

??? tip "Upgrade e Downgrade"
    Isso substitui o `db.create_all()` que usamos antes. A vantagem e que cada alteracao fica registrada em um arquivo de versao na pasta `migrations/versions/`. Se algo der errado, voce pode voltar ao estado anterior com `alembic downgrade -1`.

Com o Alembic ativo, voce pode **remover** o bloco `db.create_all()` do `backend.py`, ja que as migrations assumem essa responsabilidade.

---

## Seeds: Populando o Banco com Dados Iniciais

Com o Alembic cuidando da estrutura, o banco comeca vazio. Para popular com dados de teste de forma organizada, criamos um script dedicado chamado `seed.py`:

```python
# pyright: reportCallIssue=false
from database import app, db
from models import TecnologiaModel

with app.app_context():
    tecnologias_iniciais = [
        TecnologiaModel(nome="Flask", votos=0),
        TecnologiaModel(nome="FastAPI", votos=0),
        TecnologiaModel(nome="Flet", votos=0),
    ]

    for tech in tecnologias_iniciais:
        # Evita duplicatas verificando se ja existe no banco
        existente = TecnologiaModel.query.filter_by(nome=tech.nome).first()
        if not existente:
            db.session.add(tech)

    db.session.commit()
    print("Seeds inseridos com sucesso!")
```

Para rodar o seed:

```bash
uv run seed.py
```

??? tip "Estrutura final do projeto"
    Apos adicionar Alembic e Seeds, a pasta do projeto fica assim:
    ```
    enquete_tech/
    ├── backend.py          # Rotas da API
    ├── database.py         # Configuracao do Flask + SQLAlchemy
    ├── models.py           # Definicao das tabelas
    ├── seed.py             # Script de carga inicial de dados
    ├── frontend.py         # Interface Flet
    ├── alembic.ini         # Configuracao do Alembic
    ├── migrations/         # Pasta com os scripts de migracao
    └── pyproject.toml      # Dependencias gerenciadas pelo UV
    ```

Com o Alembic rastreando a estrutura e os Seeds populando os dados, a aplicacao esta pronta para evoluir de forma controlada. O proximo passo logico e empacotar tudo em um container Docker.
