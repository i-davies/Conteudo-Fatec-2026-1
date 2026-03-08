# Persistência de Dados

> **Objetivo:** Substituir os dados mockados (em memória) por um banco de dados PostgreSQL real usando **SQLAlchemy** como ORM. Configurar **Alembic** para versionamento do schema (migrations) e conectar tanto a um banco **local (Docker)** quanto ao **Supabase (nuvem)**.

!!! note "Recapitulação das Aulas Anteriores"
    Criamos a API com Flask, organizamos em Blueprints, adicionamos Swagger e validação com Pydantic. O problema: os dados vivem em variáveis Python, se reiniciar o servidor, tudo se perde. Hoje vamos resolver isso conectando a um banco de dados real.

---

## ORM e SQLAlchemy

### O que é um ORM?

**ORM** (Object-Relational Mapping) é uma técnica que permite manipular tabelas do banco de dados como se fossem **classes Python**. Em vez de escrever SQL diretamente, você trabalha com objetos.

| Aspecto | SQL Puro | ORM (SQLAlchemy) |
| :--- | :--- | :--- |
| **Criar tabela** | `CREATE TABLE courses (...)` | `class Course(db.Model): ...` |
| **Inserir** | `INSERT INTO courses VALUES (...)` | `db.session.add(Course(...))` |
| **Buscar** | `SELECT * FROM courses` | `Course.query.all()` |
| **Filtrar** | `SELECT * FROM courses WHERE id = 1` | `Course.query.get(1)` |

**Vantagens do ORM:**
- Código mais Pythonic e seguro (sem SQL injection)
- Funciona com qualquer banco (PostgreSQL, MySQL, SQLite) — muda só a URL de conexão
- Validação automática de tipos e relacionamentos

### O que são Migrations?

Migrations são **scripts versionados** que descrevem mudanças no schema do banco. Funciona como um controle de versão (Git) para a estrutura das tabelas.

| Sem Migrations | Com Migrations (Alembic) |
| :--- | :--- |
| `DROP TABLE` e recria tudo | Scripts versionados (`001_criar_tabelas.py`) |
| Perde dados a cada mudança | Aplica apenas o que mudou |
| Cada dev configura manualmente | `alembic upgrade head` sincroniza tudo |

### Flask-SQLAlchemy + Alembic

- **Flask-SQLAlchemy** — integração do SQLAlchemy com o Flask
- **Alembic** — ferramenta oficial de migrations do SQLAlchemy
- **psycopg2** — driver Python para PostgreSQL

---

## Setup do Banco Local com Docker

Antes de escrever código, vamos garantir que o PostgreSQL está rodando localmente.

### Docker Compose

O nosso `docker-compose.yml` já configura um PostgreSQL local. Confirme que ele está assim:

```yaml
services:
  db:
    image: postgres:15-alpine
    container_name: mergeskills-db
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: mergeskills
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### Subindo o Banco

```bash
docker-compose up -d
```

Verifique se está rodando:
```bash
docker ps
```

Deve aparecer `mergeskills-db` com status `Up`.

!!! tip "Troubleshooting de Porta"
    Se a porta 5432 já estiver em uso, pare qualquer PostgreSQL local que esteja rodando ou mude a porta no docker-compose.

---

## Instalando as Dependências

No terminal, na pasta `apps/backend`:

```bash
cd apps/backend
uv add flask-sqlalchemy psycopg2-binary alembic
```

Isso adiciona ao `pyproject.toml`:
```toml
dependencies = [
    "flask>=3.0.0",
    "flasgger>=0.9.7",
    "python-dotenv>=1.0.0",
    "pydantic>=2.12.5",
    "flask-sqlalchemy>=3.1.1",   # ORM
    "psycopg2-binary>=2.9.11",   # Driver PostgreSQL
    "alembic>=1.15.0",           # Migrations
]
```

---

## Configurando a Conexão com o Banco

### Arquivo `.env`

Crie o arquivo `apps/backend/.env` com a URL de conexão do banco local:

```env
# Local (Docker Compose)
DATABASE_URL=postgresql://devuser:devpassword@localhost:5432/mergeskills
```

**Anatomia da URL:**
```
postgresql://USUARIO:SENHA@HOST:PORTA/NOME_DO_BANCO
```

!!! important "Proteja suas Credenciais"
    O `.env` **nunca** deve ser commitado no Git (já está no `.gitignore`). Crie também um `.env.example` como referência para outros devs:
    
    ```env
    # Local (Docker Compose)
    DATABASE_URL=postgresql://devuser:devpassword@localhost:5432/mergeskills
    
    # Supabase (Connection Pooler - Transaction Mode)
    # DATABASE_URL=postgresql://postgres.SEU_PROJECT_REF:SUA_SENHA@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
    ```

### Módulo `database.py`

Crie o arquivo `apps/backend/src/database.py`:

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """
    Configura e inicializa o SQLAlchemy com o Flask app.
    Lê a DATABASE_URL das variáveis de ambiente.
    """
    import os

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL não configurada! "
            "Defina no arquivo .env (local) ou nas variáveis de ambiente (Supabase)."
        )

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
```

**Explicando:**

- `db = SQLAlchemy()` — cria a instância global do ORM (sem app ainda)
- `init_db(app)` — conecta o ORM ao Flask usando a `DATABASE_URL` do `.env`
- `SQLALCHEMY_TRACK_MODIFICATIONS = False` — desativa um recurso de performance que não precisamos

??? tip "Por que separar em um arquivo `database.py`?"
    Para evitar imports circulares. Os models precisam do `db`, e o `app.py` precisa dos models. Com o `database.py` separado, todos importam do mesmo lugar.

---

## Criando os Models

Agora vamos traduzir nossas tabelas em classes Python. Crie `apps/backend/src/models.py`:

```python
from database import db
from sqlalchemy.dialects.postgresql import JSONB


class Course(db.Model):
    """Modelo SQLAlchemy para a tabela de Cursos."""

    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    icon = db.Column(db.String)
    color = db.Column(db.String)
    total_lessons = db.Column(db.Integer)

    # Relacionamento: um curso tem várias lições
    lessons = db.relationship('Lesson', backref='course', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'total_lessons': self.total_lessons,
        }


class Lesson(db.Model):
    """Modelo SQLAlchemy para a tabela de Aulas/Lições."""

    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    order = db.Column(db.Integer)

    # Relacionamento: uma lição tem várias perguntas
    questions = db.relationship('Question', backref='lesson', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'order': self.order,
        }


class Question(db.Model):
    """Modelo SQLAlchemy para a tabela de Perguntas."""

    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    question = db.Column(db.String, nullable=False)
    code = db.Column(db.String)
    options = db.Column(JSONB)
    correct_answer = db.Column(db.Integer)
    order = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'question': self.question,
            'code': self.code,
            'options': self.options,
            'correct_answer': self.correct_answer,
            'order': self.order,
        }
```

**Conceitos importantes:**

| Conceito | O que faz | Exemplo |
| :--- | :--- | :--- |
| `__tablename__` | Nome da tabela no banco | `'courses'` |
| `db.Column(db.Integer, primary_key=True)` | Coluna inteira, chave primária | `id` |
| `db.Column(db.String, nullable=False)` | Texto obrigatório | `title` |
| `db.ForeignKey('courses.id')` | Chave estrangeira | `course_id` |
| `db.relationship(...)` | Liga as tabelas no Python | `lessons = ...` |
| `JSONB` | Tipo especial do PostgreSQL (JSON) | `options` |
| `to_dict()` | Converte o objeto para dicionário | Para o `jsonify()` |

!!! note "Relacionamentos e Cascade"
    **`cascade='all, delete-orphan'`** significa: se deletar um Course, todas as Lessons desse curso são deletadas automaticamente. Isso é equivalente ao `ON DELETE CASCADE` do SQL.

---

## Prática: Configurando o Alembic (Migrations)

### Estrutura das Migrations

A pasta de migrations fica em `apps/backend/migrations/` com a seguinte estrutura:

```plaintext
apps/backend/
├── alembic.ini              # Configuração do Alembic
├── migrations/
│   ├── env.py               # Script que conecta Alembic ao SQLAlchemy
│   ├── script.py.mako       # Template para novas migrations
│   └── versions/
│       └── 001_criar_tabelas.py  # Primeira migration
├── src/
│   ├── database.py
│   ├── models.py
│   └── ...
└── .env
```

### Arquivo `alembic.ini`

Crie `apps/backend/alembic.ini`:

```ini
[alembic]
script_location = migrations

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### Arquivo `migrations/env.py`

Este arquivo é o **coração** do Alembic. Ele lê a `DATABASE_URL` e conhece os models:

```python
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Adiciona a pasta src ao path para importar os models
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from dotenv import load_dotenv
load_dotenv()

# Importa os models para que o Alembic conheça as tabelas
from database import db
from models import Course, Lesson, Question  # noqa: F401

# Configuração do Alembic
config = context.config

# Lê a DATABASE_URL do .env
database_url = os.getenv('DATABASE_URL')
if database_url:
    config.set_main_option('sqlalchemy.url', database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData dos models
target_metadata = db.metadata


def run_migrations_offline():
    """Executa migrations sem conectar ao banco (gera SQL)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Executa migrations conectando ao banco."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Primeira Migration

Crie `apps/backend/migrations/versions/001_criar_tabelas.py`:

```python
"""Criar tabelas courses, lessons e questions

Revision ID: 001
Revises: 
Create Date: 2026-03-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('description', sa.String),
        sa.Column('icon', sa.String),
        sa.Column('color', sa.String),
        sa.Column('total_lessons', sa.Integer),
    )

    op.create_table(
        'lessons',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('course_id', sa.Integer,
                  sa.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('description', sa.String),
        sa.Column('order', sa.Integer),
    )

    op.create_table(
        'questions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('lesson_id', sa.Integer,
                  sa.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question', sa.String, nullable=False),
        sa.Column('code', sa.String),
        sa.Column('options', JSONB),
        sa.Column('correct_answer', sa.Integer),
        sa.Column('order', sa.Integer),
    )


def downgrade() -> None:
    op.drop_table('questions')
    op.drop_table('lessons')
    op.drop_table('courses')
```

**Explicando:**

- `upgrade()` — o que fazer ao aplicar a migration (criar tabelas)
- `downgrade()` — o que fazer ao reverter (dropar tabelas, na ordem inversa)
- A **ordem importa**: `courses` primeiro (pois `lessons` referencia `courses.id`)

### Aplicando a Migration

Com o Docker rodando, execute:

```bash
cd apps/backend
uv run alembic upgrade head
```

Deve aparecer algo como:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Criar tabelas courses, lessons e questions
```

??? tip "Comandos úteis do Alembic"
    - `alembic upgrade head` — aplica todas as migrations pendentes
    - `alembic downgrade base` — reverte todas as migrations
    - `alembic current` — mostra a versão atual
    - `alembic history` — lista todas as migrations

---

## Prática: Populando o Banco (Seed)

### Script de Seed com Python

Crie `apps/backend/src/scripts/seed.py`:

```python
import sys
import os

# Adiciona a pasta src ao path
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from database import db
from models import Course, Lesson, Question


COURSES = [
    {
        "id": 1,
        "title": "Python Fundamentos",
        "description": "Aprenda o básico de Python",
        "icon": "python",
        "color": "#306998",
        "total_lessons": 2,
    },
    {
        "id": 2,
        "title": "Flask API Masterclass",
        "description": "Crie APIs profissionais",
        "icon": "flask",
        "color": "#FF5722",
        "total_lessons": 2,
    },
]

LESSONS = [
    {"id": 1, "course_id": 1, "title": "Introdução ao Python",
     "description": "Primeiros passos com Python", "order": 1},
    {"id": 2, "course_id": 1, "title": "Variáveis e Tipos",
     "description": "Tipos de dados em Python", "order": 2},
    {"id": 3, "course_id": 2, "title": "Setup do Ambiente Flask",
     "description": "Configurando o Flask", "order": 1},
    {"id": 4, "course_id": 2, "title": "Blueprints",
     "description": "Organizando rotas com Blueprints", "order": 2},
]

QUESTIONS = [
    {
        "id": 1,
        "lesson_id": 1,
        "question": "O que é Python?",
        "code": None,
        "options": ["Um réptil", "Uma linguagem de programação",
                    "Um editor de texto"],
        "correct_answer": 1,
        "order": 1,
    },
    {
        "id": 2,
        "lesson_id": 1,
        "question": "Qual comando imprime textos?",
        "code": "# Para imprimir 'Olá mundo':\n[BLANK]('Olá mundo')",
        "options": ["echo()", "console.log()", "print()"],
        "correct_answer": 2,
        "order": 2,
    },
]


def seed():
    """Popula o banco de dados com os dados iniciais."""
    app = create_app()

    with app.app_context():
        # Verifica se já existem dados
        if Course.query.first():
            print("Banco já possui dados. Pulando seed.")
            return

        print("Populando banco de dados...")

        for c in COURSES:
            db.session.add(Course(**c))
        print(f"  {len(COURSES)} cursos inseridos")

        for l in LESSONS:
            db.session.add(Lesson(**l))
        print(f"  {len(LESSONS)} lições inseridas")

        for q in QUESTIONS:
            db.session.add(Question(**q))
        print(f"  {len(QUESTIONS)} perguntas inseridas")

        db.session.commit()
        print("Seed concluído com sucesso!")


if __name__ == '__main__':
    seed()
```

Execute:
```bash
uv run python src/scripts/seed.py
```

## Integrando no Flask e Refatorando as Rotas

### Atualizando `app.py`

Adicione a inicialização do banco de dados no `create_app()`:

```python
from flask import Flask
from flasgger import Swagger
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    # ═══════════════════════════════════════════════════════════════
    # Database — Inicializa SQLAlchemy com a DATABASE_URL do .env
    # ═══════════════════════════════════════════════════════════════
    from database import init_db
    init_db(app)

    # Detecta o ambiente pelo conteúdo da DATABASE_URL
    db_url = os.getenv('DATABASE_URL', '')
    env_label = 'Supabase' if 'supabase' in db_url else 'Local (Docker)'

    # Swagger Configuration
    app.config['SWAGGER'] = {
        'title': f'MergeSkills API — {env_label}',
        'uiversion': 3,
        'description': f'API do projeto MergeSkills. Ambiente: **{env_label}**',
        'specs_route': '/apidocs/'
    }

    # ... (resto do código — Swagger template e Blueprints)
```

**O que mudou:**

- `from database import init_db` + `init_db(app)` configura a conexão
- O Swagger agora mostra se está conectado ao banco Local ou Supabase

### Seed SQL (alternativa para Supabase)

Para quem preferir usar o SQL Editor do Supabase, criamos `apps/backend/seed.sql`:

```sql
-- Limpar dados existentes
DELETE FROM questions;
DELETE FROM lessons;
DELETE FROM courses;

-- Cursos
INSERT INTO courses (id, title, description, icon, color, total_lessons) VALUES
    (1, 'Python Fundamentos', 'Aprenda o básico de Python', 'python', '#306998', 2),
    (2, 'Flask API Masterclass', 'Crie APIs profissionais', 'flask', '#FF5722', 2);

-- Lições
INSERT INTO lessons (id, course_id, title, description, "order") VALUES
    (1, 1, 'Introdução ao Python', 'Primeiros passos com Python', 1),
    (2, 1, 'Variáveis e Tipos', 'Tipos de dados em Python', 2),
    (3, 2, 'Setup do Ambiente Flask', 'Configurando o Flask', 1),
    (4, 2, 'Blueprints', 'Organizando rotas com Blueprints', 2);

-- Perguntas
INSERT INTO questions (id, lesson_id, question, code, options, correct_answer, "order") VALUES
    (1, 1, 'O que é Python?', NULL,
        '["Um réptil", "Uma linguagem de programação", "Um editor de texto"]', 1, 1),
    (2, 1, 'Qual comando imprime textos?',
        E'# Para imprimir ''Olá mundo'':\n[BLANK](''Olá mundo'')',
        '["echo()", "console.log()", "print()"]', 2, 2);
```

!!! note "Palavras Reservadas"
    Note que `"order"` está entre aspas duplas no SQL porque `order` é uma palavra reservada do PostgreSQL.

---

### Refatorando as Rotas

O principal: **remover os dados mockados** e usar queries SQLAlchemy.

**Antes (Aula 03) — courses.py com dados em memória:**
```python
COURSES_DB = [
    {"id": 1, "title": "Python Fundamentos", ...},
    {"id": 2, "title": "Flask API Masterclass", ...}
]

# Na rota:
result = [CourseSchema(**c).model_dump() for c in COURSES_DB]
```

**Depois (Aula 04) — courses.py com banco de dados:**
```python
from models import Course, Lesson

# Na rota:
courses = Course.query.all()
result = [CourseSchema(**c.to_dict()).model_dump() for c in courses]
```

Refatore os 4 arquivos de rotas:

**`courses.py`** — Substitua `COURSES_DB` e `LESSONS_DB` por queries:
```python
from models import Course, Lesson
from schemas.course_schema import CourseSchema
from schemas.lesson_schema import LessonSchema

# GET /api/courses
courses = Course.query.all()

# GET /api/courses/<id>
course = Course.query.get(course_id)

# GET /api/courses/<id>/lessons
lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()
```

**`lessons.py`** — Substitua `LESSONS_DB` e `QUESTIONS_DB`:
```python
from models import Lesson, Question

# GET /api/lessons/<id>/questions
lesson = Lesson.query.get(lesson_id)
questions = Question.query.filter_by(lesson_id=lesson_id).order_by(Question.order).all()
```

**`questions.py`** — Substitua `QUESTIONS_DB`:
```python
from models import Question

# GET /api/questions
questions = Question.query.all()

# GET /api/questions/<id>
question = Question.query.get(question_id)
```

**`progress.py`** — Substitua a busca de pergunta:
```python
from models import Question

# Antes: question = next((q for q in QUESTIONS_DB if q['id'] == question_id), None)
# Depois:
question = Question.query.get(question_id)

# Antes: is_correct = (selected_option == question['correct_option'])
# Depois:
is_correct = (selected_option == question.correct_answer)
```

!!! important "Progresso do Aluno"
    O `USER_PROGRESS` (progresso do aluno) **continua em memória** por enquanto. Na Semana 5, vamos persistir isso no banco também.

---

## Testando Localmente

### Checklist Completo

1. **Banco rodando:**
   ```bash
   docker-compose up -d
   ```

2. **Migration aplicada:**
   ```bash
   cd apps/backend
   uv run alembic upgrade head
   ```

3. **Seed executado:**
   ```bash
   uv run python src/scripts/seed.py
   ```

4. **Servidor Flask:**
   ```bash
   uv run flask --app src/app run
   ```

5. **Teste no Swagger** (http://localhost:5000/apidocs):
   - `GET /api/courses` → Deve retornar os cursos do banco
   - `GET /api/courses/1/lessons` → Lições do curso 1
   - `GET /api/questions/1` → Detalhes da pergunta 1
   - `POST /api/progress/` → Submeter uma resposta

6. **Atenção ao título do Swagger:** Deve mostrar `MergeSkills API — Local (Docker)`

### Troubleshooting

| Problema | Solução |
| :--- | :--- |
| `RuntimeError: DATABASE_URL não configurada` | Verifique se o arquivo `.env` existe em `apps/backend/` |
| `connection refused` | O Docker está rodando? `docker-compose up -d` |
| `relation does not exist` | Rode a migration: `uv run alembic upgrade head` |
| Dados vazios nas rotas | Rode o seed: `uv run python src/scripts/seed.py` |

---

## Conectando ao Supabase

Nesta seção, vamos configurar o mesmo código para funcionar com o **Supabase** na nuvem.

### Criando o Projeto no Supabase

1. Acesse [supabase.com](https://supabase.com) e crie uma conta
2. Clique em **New Project**
3. Escolha um nome (ex: `mergeskills`)
4. **Importante:** Anote a senha do banco de dados

### Obtendo a Connection String (Pooler)

1. No dashboard do Supabase, vá em **Settings → Database**
2. Role até **Connection String** e selecione a aba **Transaction (Supavisor)**
3. Copie a URL — ela terá este formato:
   ```
   postgresql://postgres.SEU_PROJECT_REF:SUA_SENHA@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
   ```

??? info "Por que usar o Connection Pooler?"
    O Supabase oferece dois tipos de conexão:
    
    - **Direct** (porta 5432) — Conexão direta ao PostgreSQL. Pode não funcionar em redes restritas (como a rede da faculdade)
    - **Transaction Pooler** (porta 6543) — Passa por um proxy (Supavisor) que gerencia conexões. Funciona em qualquer rede, inclusive a da FATEC
    
    O nosso SQLAlchemy funciona com os dois. Usamos o Pooler para garantir compatibilidade.

### Configurando o `.env`

Edite `apps/backend/.env` e troque a `DATABASE_URL`:

```env
# Comente a linha do Docker:
# DATABASE_URL=postgresql://devuser:devpassword@localhost:5432/mergeskills

# Descomente e configure o Supabase:
DATABASE_URL=postgresql://postgres.abc123:minhasenha@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

### Rodando Migrations no Supabase

O mesmo comando funciona:
```bash
uv run alembic upgrade head
```

Isso cria as tabelas **diretamente no Supabase**, via Connection Pooler.

### Populando o Supabase

**Opção A** — Via script Python:
```bash
uv run python src/scripts/seed.py
```

**Opção B** — Via SQL Editor do Supabase:
1. No Dashboard do Supabase, vá em **SQL Editor**
2. Cole o conteúdo do arquivo `seed.sql`
3. Clique em **Run**

### Testando

Suba o Flask e teste — os dados agora vêm do Supabase:
```bash
uv run flask --app src/app run
```

O Swagger deve mostrar: `MergeSkills API — Supabase`

!!! tip "Voltando ao Local"
    Para **voltar ao banco local**, basta trocar a `DATABASE_URL` no `.env` de volta para a versão Docker. O código não muda — **só a conexão muda**.


---

## Exercícios de Fixação

??? example "Exercícios práticos"

    1. **Adicionar Curso:** Adicione um novo curso ao `seed.py` com pelo menos 2 lições e 1 pergunta cada. Execute o seed novamente (reset: `alembic downgrade base && alembic upgrade head`, depois `seed.py`).
    
    2. **Verificar Supabase:** No Supabase, vá ao **Table Editor** e confira se os dados inseridos pelo seed estão lá.
    
    3. **Discussão:** Compare a experiência de desenvolvimento com banco local (Docker) vs Supabase. Quais as vantagens de cada abordagem?

---
