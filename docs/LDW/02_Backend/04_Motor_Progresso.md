# Motor de Progresso

>**Objetivo:** Substituir o progresso em memória (`USER_PROGRESS`) por persistência real no banco de dados. Criar tabelas para **usuários**, **tentativas de resposta** e **progresso por lição**. Implementar lógica de validação de respostas com histórico, funcionalidade de "refazer" e progresso salvo permanentemente.

!!! note "Recapitulação da Aula 04"
    Conectamos a API ao PostgreSQL e refatoramos as rotas de cursos, lições e perguntas para usar SQLAlchemy.
    O problema que ficou: o progresso do aluno (`USER_PROGRESS`) ainda vive em memória. Se reiniciar o servidor,
    o progresso some. Nesta aula vamos resolver isso.

---

## Motor de Progresso

### O Problema

Na Aula passada, substituímos os dados mockados de cursos, lições e perguntas pelo banco de dados real. Porém, na rota de progresso (`progress.py`) ainda temos:

```python
# Memória VOLÁTIL de Progresso
USER_PROGRESS: Dict[int, Dict[int, bool]] = {}
```

**Problemas dessa abordagem:**

- Reiniciar o servidor = perder tudo
- Sem histórico de tentativas (só salva acertos)
- Sem conceito de "usuário" no banco
- Impossível saber se uma lição inteira foi concluída

### O que Vamos Construir

Um **Motor de Progresso** que:

1. **Registra cada tentativa** — acertos e erros, com timestamp
2. **Detecta conclusão de lição** — quando todas as perguntas têm pelo menos 1 acerto
3. **Permite "refazer"** — reseta tentativas de uma lição e recomeça
4. **Persiste tudo no banco** — reiniciar o servidor não perde nada

### Novos Modelos de Dados

| Tabela | Propósito | Relacionamento |
| :--- | :--- | :--- |
| `users` | Cadastro simples do aluno | Tem vários `question_attempts` e `lesson_progress` |
| `question_attempts` | Cada tentativa de resposta | Pertence a um `user` e uma `question` |
| `lesson_progress` | Status de conclusão da lição | Pertence a um `user` e uma `lesson` |

### Timestamps no Banco

O campo `timestamp` usa `server_default=db.func.now()`, que significa:

- O **PostgreSQL** gera a data/hora automaticamente no momento do INSERT
- Não precisamos enviar a data pelo Python, o banco cuida disso
- Garante consistência mesmo com fusos horários diferentes

### Lógica de Conclusão Automática

Quando um aluno acerta uma pergunta, o motor verifica se **todas** as perguntas da lição têm pelo menos uma resposta correta. Se sim, marca automaticamente a lição como concluída:

```
Aluno responde pergunta 3
  → Buscar todas as perguntas da lição
  → Para cada pergunta, verificar: existe tentativa correta?
  → Se TODAS têm acerto → criar/atualizar LessonProgress(is_completed=True)
```

---

## Novos Models

### Adicionando ao `models.py`

Abra `apps/backend/src/models.py` e adicione os 3 novos modelos **ao final do arquivo**, depois da classe `Question`:

```python
class User(db.Model):
    """Modelo SQLAlchemy para a tabela de Usuários (Alunos)."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)

    # Relacionamentos
    attempts = db.relationship('QuestionAttempt', backref='user', lazy=True)
    progress = db.relationship('LessonProgress', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
        }


class QuestionAttempt(db.Model):
    """Modelo SQLAlchemy para registrar cada tentativa de resposta."""

    __tablename__ = 'question_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_option = db.Column(db.Integer, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'selected_option': self.selected_option,
            'is_correct': self.is_correct,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


class LessonProgress(db.Model):
    """Modelo SQLAlchemy para registrar o progresso em cada lição."""

    __tablename__ = 'lesson_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
```

**Conceitos novos:**

| Conceito | O que faz | Exemplo |
| :--- | :--- | :--- |
| `unique=True` | Impede valores duplicados na coluna | `username` |
| `server_default=db.func.now()` | O banco gera a data automaticamente | `timestamp` |
| `lazy=True` | Carrega os relacionamentos só quando acessar | `attempts`, `progress` |
| `.isoformat()` | Converte `datetime` do Python para string ISO 8601 | `"2026-03-15T14:30:00"` |

!!! tip "`lazy=True` vs `lazy='dynamic'`"
    Com `lazy=True`, o SQLAlchemy carrega todos os registros de uma vez quando você acessa `user.attempts`.
    Com `lazy='dynamic'`, ele retorna uma Query que você pode filtrar. Aqui usamos `True` por simplicidade,
    porque os alunos terão poucas tentativas.

---

## Migration

### Criando a Migration 002

Crie o arquivo `apps/backend/migrations/versions/002_motor_progresso.py`:

```python
"""Criar tabelas users, question_attempts e lesson_progress

Revision ID: 002
Revises: 001
Create Date: 2026-03-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String, unique=True, nullable=False),
    )

    op.create_table(
        'question_attempts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer,
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_id', sa.Integer,
                  sa.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('selected_option', sa.Integer, nullable=False),
        sa.Column('is_correct', sa.Boolean, default=False),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        'lesson_progress',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer,
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('lesson_id', sa.Integer,
                  sa.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_completed', sa.Boolean, default=False),
        sa.Column('completed_at', sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table('lesson_progress')
    op.drop_table('question_attempts')
    op.drop_table('users')
```

**Pontos importantes:**

- `down_revision = '001'` — indica que esta migration depende da `001_criar_tabelas`
- `ondelete='CASCADE'` — se deletar um User, todas as suas tentativas e progressos são deletados automaticamente
- A ordem de criação importa: `users` primeiro, porque as outras tabelas referenciam `users.id`
- Na `downgrade()`, a ordem é inversa: deleta primeiro as tabelas que têm FKs

### Atualizando o `env.py` do Alembic

Edite `apps/backend/migrations/env.py` e atualize a linha de imports dos models:

```python
# Antes:
from models import Course, Lesson, Question 

# Depois:
from models import Course, Lesson, Question, User, QuestionAttempt, LessonProgress 
```

### Aplicando a Migration

```bash
cd apps/backend
uv run alembic upgrade head
```

Deve aparecer:
```
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, Criar tabelas users, question_attempts e lesson_progress
```

!!! tip
    Se der erro, verifique se a migration `001` já foi aplicada (`uv run alembic current`).
    Se não, aplique ambas: `uv run alembic upgrade head` roda todas as pendentes.

---

## Atualizando os Schemas

### Novos Schemas Pydantic

Substitua o conteúdo de `apps/backend/src/schemas/progress_schema.py`:

```python
from typing import Optional
from pydantic import BaseModel, Field


class SubmitAnswerSchema(BaseModel):
    """
    Schema de ENTRADA (validação) para submissão de respostas.
    Diferente dos outros schemas, este valida dados que CHEGAM na API.
    """
    user_id: int
    question_id: int
    selected_option: int = Field(ge=0)  # ge = greater or equal (>=0)


class AnswerResultSchema(BaseModel):
    """
    Schema de SAÍDA para o resultado de uma submissão.
    """
    is_correct: bool
    correct_answer: int
    message: str


class ResetProgressSchema(BaseModel):
    """
    Schema de ENTRADA para resetar o progresso de uma lição.
    Permite ao aluno "refazer" uma lição do zero.
    """
    user_id: int
    lesson_id: int


class AttemptSchema(BaseModel):
    """
    Schema de SAÍDA para uma tentativa individual.
    """
    id: int
    user_id: int
    question_id: int
    selected_option: int
    is_correct: bool
    timestamp: Optional[str] = None


class LessonProgressSchema(BaseModel):
    """
    Schema de SAÍDA para o progresso de uma lição.
    """
    id: int
    user_id: int
    lesson_id: int
    is_completed: bool
    completed_at: Optional[str] = None


class UserHistorySchema(BaseModel):
    """
    Schema de SAÍDA para o histórico completo do aluno.
    """
    user_id: int
    completed_lessons: list[dict]
    recent_attempts: list[dict]
    total_score: int


class ProgressResponseSchema(BaseModel):
    """
    Schema de SAÍDA para o progresso do usuário (compatibilidade).
    """
    user_id: int
    completed_questions: list[int]
    total_score: int
```

**O que mudou:**

| Schema | Tipo | Propósito |
| :--- | :--- | :--- |
| `SubmitAnswerSchema` | Entrada | Já existia — valida a submissão |
| `AnswerResultSchema` | Saída | **NOVO** — retorna se acertou + resposta correta |
| `ResetProgressSchema` | Entrada | **NOVO** — valida o pedido de reset |
| `AttemptSchema` | Saída | **NOVO** — serializa uma tentativa |
| `LessonProgressSchema` | Saída | **NOVO** — serializa progresso da lição |
| `UserHistorySchema` | Saída | **NOVO** — histórico completo |

!!! note
    O `AnswerResultSchema` agora retorna `correct_answer` junto com o resultado.
    Na versão anterior, o aluno não sabia qual era a resposta certa quando errava.

---

## Refatorando as Rotas de Progresso

Vamos substituir completamente o `progress.py`.

### O que Muda

| Antes (Aula 04) | Depois (Aula 05) |
| :--- | :--- |
| `USER_PROGRESS` em memória | `QuestionAttempt` no banco |
| Só registra acertos | Registra acertos **e** erros |
| Sem histórico | Histórico completo com timestamps |
| Sem "refazer" | Endpoint de reset por lição |
| Sem detecção de conclusão | Marca lição como concluída automaticamente |

### Novo `progress.py`

Substitua **todo** o conteúdo de `apps/backend/src/routes/progress.py`:

```python
from typing import Union, Tuple
from flask import Blueprint, jsonify, request, Response
from pydantic import ValidationError
from database import db
from models import Question, QuestionAttempt, LessonProgress, User
from schemas.progress_schema import (
    SubmitAnswerSchema,
    AnswerResultSchema,
    ResetProgressSchema,
    AttemptSchema,
    LessonProgressSchema,
    UserHistorySchema,
)

progress_bp = Blueprint('progress', __name__)


@progress_bp.route('/', methods=['POST'])
def submit_answer() -> Union[Response, Tuple[Response, int]]:
    """
    Submete uma resposta e registra a tentativa no banco
    ---
    tags:
      - Progresso
    parameters:
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/SubmitAnswer'
    responses:
      200:
        description: Resultado da submissão
        schema:
          $ref: '#/definitions/AnswerResult'
      400:
        description: Dados inválidos (erro de validação)
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Pergunta não encontrada
        schema:
          $ref: '#/definitions/Error'
    """
    # Validação com Pydantic
    try:
        data = SubmitAnswerSchema(**request.json)
    except ValidationError as err:
        return jsonify({"errors": err.errors()}), 400

    user_id: int = data.user_id
    question_id: int = data.question_id
    selected_option: int = data.selected_option

    # Busca a pergunta no banco de dados
    question = Question.query.get(question_id)
    if not question:
        return jsonify({"error": "Pergunta não encontrada"}), 404

    # Verifica se o usuário existe
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    # Verifica a resposta
    is_correct = (selected_option == question.correct_answer)

    # Registra a tentativa no banco (PERSISTENTE!)
    attempt = QuestionAttempt(
        user_id=user_id,
        question_id=question_id,
        selected_option=selected_option,
        is_correct=is_correct,
    )
    db.session.add(attempt)
    db.session.commit()

    # Verifica se a lição foi concluída (todas as perguntas certas)
    lesson_id = question.lesson_id
    lesson_questions = Question.query.filter_by(lesson_id=lesson_id).all()

    all_correct = True
    for q in lesson_questions:
        has_correct = QuestionAttempt.query.filter_by(
            user_id=user_id,
            question_id=q.id,
            is_correct=True,
        ).first() is not None

        if not has_correct:
            all_correct = False
            break

    if all_correct:
        # Atualiza ou cria o registro de progresso da lição
        progress = LessonProgress.query.filter_by(
            user_id=user_id, lesson_id=lesson_id
        ).first()

        if not progress:
            progress = LessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_completed=True,
                completed_at=db.func.now(),
            )
            db.session.add(progress)
        else:
            if not progress.is_completed:
                progress.is_completed = True
                progress.completed_at = db.func.now()

        db.session.commit()

    result = AnswerResultSchema(
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        message="Resposta correta!" if is_correct else "Tente novamente.",
    ).model_dump()

    return jsonify(result)
```

**Explicando a lógica principal:**

1. **Validação** → `SubmitAnswerSchema(**request.json)` valida os dados de entrada
2. **Busca** → Verifica se a pergunta e o usuário existem no banco
3. **Comparação** → `selected_option == question.correct_answer`
4. **Registro** → Cria um `QuestionAttempt` com `is_correct` e timestamp automático
5. **Auto-conclusão** → Verifica se todas as perguntas da lição foram acertadas

!!! important
    Diferente da versão em memória, agora registramos **todas as tentativas**, não apenas os acertos.
    Isso permite saber quantas vezes o aluno errou antes de acertar, um dado valioso para análise de dificuldade.

### Endpoint de Reset (Refazer)

Adicione **abaixo** da rota anterior, no mesmo arquivo:

```python
@progress_bp.route('/reset', methods=['POST'])
def reset_progress() -> Union[Response, Tuple[Response, int]]:
    """
    Reseta o progresso de uma lição (permite "refazer")
    ---
    tags:
      - Progresso
    parameters:
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/ResetProgress'
    responses:
      200:
        description: Progresso resetado com sucesso
      400:
        description: Dados inválidos
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        data = ResetProgressSchema(**request.json)
    except ValidationError as err:
        return jsonify({"errors": err.errors()}), 400

    user_id = data.user_id
    lesson_id = data.lesson_id

    # Busca todas as perguntas da lição
    questions = Question.query.filter_by(lesson_id=lesson_id).all()
    question_ids = [q.id for q in questions]

    # Deleta tentativas dessas perguntas para este usuário
    if question_ids:
        QuestionAttempt.query.filter(
            QuestionAttempt.user_id == user_id,
            QuestionAttempt.question_id.in_(question_ids),
        ).delete(synchronize_session=False)

    # Reseta o progresso da lição
    LessonProgress.query.filter_by(
        user_id=user_id, lesson_id=lesson_id
    ).delete()

    db.session.commit()

    return jsonify({"message": "Progresso resetado com sucesso!"})
```

**Explicando a lógica de reset:**

1. Encontra todas as perguntas da lição
2. Deleta as tentativas (`QuestionAttempt`) dessas perguntas para o usuário
3. Deleta o `LessonProgress` da lição
4. O aluno pode recomeçar do zero

!!! tip
    O `synchronize_session=False` é necessário quando usamos `.delete()` com `.in_()` no SQLAlchemy.
    Sem ele, pode dar erro de sincronização de sessão.

### Endpoint de Histórico

Adicione **abaixo** da rota anterior:

```python
@progress_bp.route('/history/<int:user_id>', methods=['GET'])
def get_history(user_id: int) -> Response:
    """
    Retorna o histórico completo do aluno
    ---
    tags:
      - Progresso
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID do usuário
    responses:
      200:
        description: Histórico do aluno
        schema:
          $ref: '#/definitions/UserHistory'
    """
    # Lições completadas
    completed = LessonProgress.query.filter_by(
        user_id=user_id, is_completed=True
    ).all()

    # Últimas 10 tentativas (mais recentes primeiro)
    recent = QuestionAttempt.query.filter_by(
        user_id=user_id
    ).order_by(QuestionAttempt.timestamp.desc()).limit(10).all()

    result = UserHistorySchema(
        user_id=user_id,
        completed_lessons=[p.to_dict() for p in completed],
        recent_attempts=[a.to_dict() for a in recent],
        total_score=len(completed),
    ).model_dump()

    return jsonify(result)
```

**O que este endpoint retorna:**

- Lista de lições completadas (com data de conclusão)
- Últimas 10 tentativas (acertos e erros, com timestamp)
- Total de lições concluídas

---

## Atualizando o Swagger e Seed

### Novas Definitions no `app.py`

Atualize as importações e definitions no `apps/backend/src/app.py`:

```python
    from schemas.progress_schema import (
        SubmitAnswerSchema,
        AnswerResultSchema,
        ResetProgressSchema,
        UserHistorySchema,
        ProgressResponseSchema,
    )

    swagger_template = {
        "tags": [
            {"name": "Health"},
            {"name": "Cursos"},
            {"name": "Aulas"},
            {"name": "Perguntas"},
            {"name": "Progresso"}
        ],
        "definitions": {
            "Course": CourseSchema.model_json_schema(),
            "Lesson": LessonSchema.model_json_schema(),
            "Question": QuestionSchema.model_json_schema(),
            "QuestionId": QuestionIdSchema.model_json_schema(),
            "SubmitAnswer": SubmitAnswerSchema.model_json_schema(),
            "AnswerResult": AnswerResultSchema.model_json_schema(),
            "ResetProgress": ResetProgressSchema.model_json_schema(),
            "UserHistory": UserHistorySchema.model_json_schema(),
            "UserProgress": ProgressResponseSchema.model_json_schema(),
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                }
            }
        }
    }
```

### Atualizando o Seed

Precisamos popular pelo menos um usuário de teste para que o progresso funcione.

**No `apps/backend/src/scripts/seed.py`**, adicione:

1. O import do `User`:
```python
from models import Course, Lesson, Question, User
```

2. A lista de usuários (antes dos cursos):
```python
USERS = [
    {"id": 1, "username": "aluno_teste"},
    {"id": 2, "username": "aluno_02"},
]
```

3. No `seed()`, insira os usuários **antes** dos cursos:
```python
        for u in USERS:
            db.session.add(User(**u))
        print(f"  {len(USERS)} usuários inseridos")
```

**No `apps/backend/seed.sql`** (alternativa SQL), adicione **antes** dos cursos:

```sql
-- Limpar dados existentes (ordem importa por causa das FKs)
DELETE FROM lesson_progress;
DELETE FROM question_attempts;
DELETE FROM questions;
DELETE FROM lessons;
DELETE FROM courses;
DELETE FROM users;

-- Usuários de teste
INSERT INTO users (id, username) VALUES
    (1, 'aluno_teste'),
    (2, 'aluno_02');
```

### Reaplicando o Seed

Como agora temos novas tabelas, precisamos resetar e repopular:

```bash
cd apps/backend
uv run alembic downgrade base
uv run alembic upgrade head
uv run python src/scripts/seed.py
```

---

## Testando o Motor de Progresso

### Checklist Completo

1. **Banco rodando:**
   ```bash
   docker-compose up -d
   ```

2. **Migrations aplicadas:**
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

5. **Testes no Swagger** (http://localhost:5000/apidocs):

   **Teste 1 — Resposta correta:**
   ```
   POST /api/progress/
   Body: {"user_id": 1, "question_id": 1, "selected_option": 1}
   Esperado: {"is_correct": true, "correct_answer": 1, "message": "Resposta correta!"}
   ```

   **Teste 2 — Resposta errada:**
   ```
   POST /api/progress/
   Body: {"user_id": 1, "question_id": 1, "selected_option": 0}
   Esperado: {"is_correct": false, "correct_answer": 1, "message": "Tente novamente."}
   ```

   **Teste 3 — Consultar histórico:**
   ```
   GET /api/progress/history/1
   Esperado: ver as tentativas feitas (acertos e erros)
   ```

   **Teste 4 — Persistência (IMPORTANTE!):**
   - Pare o servidor (`Ctrl+C`)
   - Suba novamente: `uv run flask --app src/app run`
    - Consulte `GET /api/progress/history/1` -> Os dados persistiram.

   **Teste 5 — Reset:**
   ```
   POST /api/progress/reset
   Body: {"user_id": 1, "lesson_id": 1}
   Esperado: {"message": "Progresso resetado com sucesso!"}
   ```

   **Teste 6 — Verificar reset:**
   ```
   GET /api/progress/history/1
   Esperado: tentativas da lição 1 sumiram
   ```

### Troubleshooting

| Problema | Solução |
| :--- | :--- |
| `"Usuário não encontrado"` | O seed foi executado? Verifique se existe o user com id=1 |
| `relation "question_attempts" does not exist` | Rode a migration: `uv run alembic upgrade head` |
| `UniqueViolation` no seed | Rode `alembic downgrade base && alembic upgrade head` antes do seed |
| Dados sumiram após restart | Sucesso! Ah, espera... confira se o Docker ainda está rodando |


---

## Exercicio de fixação

**Objetivo:** criar o endpoint `GET /api/progress/stats/<int:lesson_id>/<int:user_id>` para retornar estatísticas do aluno em uma lição específica.

### Resposta Esperada

```json
{
    "lesson_id": 1,
    "user_id": 1,
    "total_questions": 2,
    "correct_answers": 1,
    "wrong_answers": 3,
    "completion_percentage": 50.0,
    "is_completed": false
}
```

### Bloco para Copiar: Schema Necessário

```python
class LessonStatsSchema(BaseModel):
    """
    Schema de SAÍDA para estatísticas de uma lição.
    """
    lesson_id: int
    user_id: int
    total_questions: int
    correct_answers: int
    wrong_answers: int
    completion_percentage: float
    is_completed: bool
```

### Bloco para Copiar: Início da Rota

```python
@progress_bp.route('/stats/<int:lesson_id>/<int:user_id>', methods=['GET'])
def get_lesson_stats(lesson_id: int, user_id: int) -> Response:
    """
    Retorna estatísticas detalhadas de um aluno em uma lição
    ---
    tags:
      - Progresso
    parameters:
      - name: lesson_id
        in: path
        type: integer
        required: true
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Estatísticas da lição
        schema:
          $ref: '#/definitions/LessonStats'
    """
    # 1. Total de perguntas da lição

    # 2. Buscar IDs das perguntas da lição

    # 3. Contar perguntas acertadas (únicas)

    # 4. Contar total de erros (todas as tentativas incorretas)

    # 5. Verificar conclusão

    # 6. Montar resposta
```

!!! tip
    Não esqueça de registrar `"LessonStats": LessonStatsSchema.model_json_schema()`
    nas `definitions` do `swagger_template` no `app.py`.


