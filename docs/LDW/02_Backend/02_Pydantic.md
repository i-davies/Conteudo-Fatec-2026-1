# Design de API e Schemas Pydantic

> **Objetivo:** Completar a implementação do Blueprint de `Progress`, refatorar a API com uma camada de validação usando **Pydantic**, e padronizar todas as respostas dos endpoints.
> Projeto utilizado : [ldw-merge-skills-aula](https://github.com/i-davies/ldw-merge-skills-aula).

!!! note "Recapitulação"
    Na aula anterior, criamos a estrutura base com Blueprints (`app.py`, `health.py`, `courses.py`, `lessons.py` e `questions.py`). Agora vamos:
    - Completar a lógica de progresso (submissão de respostas e histórico).
    - Adicionar Schemas de validação com Pydantic.
    - Padronizar as respostas da API no Swagger.

---

### Criando o Blueprint de Progress (`progress.py`)

Este arquivo implementa a lógica de **submissão de respostas** e **consulta de progresso** do aluno. Usaremos uma variável global `USER_PROGRESS` para simular o banco de dados temporariamente.

!!! note "Estado em Memória (Mocking)"
    Se reiniciar o servidor, os dados se perdem. Isso é proposital — em breve, vamos substituir isso por um banco de dados real com SQLAlchemy. Esse é um ótimo gancho para entender a importância da persistência!

Crie o arquivo `apps/backend/src/routes/progress.py`:

```python
from flask import Blueprint, jsonify, request
from routes.questions import QUESTIONS_DB

progress_bp = Blueprint('progress', __name__)

# Memória VOLÁTIL de Progresso (Simulando banco em memória)
# Estrutura: { "user_id": { "question_id": is_correct } } 
USER_PROGRESS = {}

@progress_bp.route('/', methods=['POST'])
def submit_answer():
    """
    Submete uma resposta e salva o progresso
    ---
    tags:
      - Progresso
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
              example: 1
            question_id:
              type: integer
              example: 1
            selected_option:
              type: integer
              example: 1
    responses:
      200:
        description: Resultado da submissão
        schema:
          type: object
          properties:
            correct:
              type: boolean
            message:
              type: string
    """
    data = request.json
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    selected_option = data.get('selected_option')

    # Validação simples
    if not all([user_id, question_id, selected_option is not None]):
        return jsonify({"error": "Dados incompletos"}), 400

    # Busca a pergunta no "Banco"
    question = next((q for q in QUESTIONS_DB if q['id'] == question_id), None)
    
    if not question:
        return jsonify({"error": "Pergunta não encontrada"}), 404

    # Verifica a resposta
    is_correct = (selected_option == question['correct_option'])
    
    # Salva no "Banco em Memória"
    if user_id not in USER_PROGRESS:
        USER_PROGRESS[user_id] = {}
        
    # Só salva se acertou (lógica simplificada)
    if is_correct:
         USER_PROGRESS[user_id][question_id] = True

    return jsonify({
        "correct": is_correct,
        "message": "Resposta correta!" if is_correct else "Tente novamente."
    })
```

### Registrando no `app.py`

Abra `apps/backend/src/app.py` e adicione o registro do Blueprint de Progress:

```python
    from routes.progress import progress_bp  # ← NOVO
    
    app.register_blueprint(progress_bp, url_prefix='/api/progress')  # ← NOVO
```

### Testando o Progress no Swagger

Rode o servidor:
```bash
cd apps/backend
uv run flask --app src/app run
```

---

## Prática: Adicionando Schemas com Pydantic

Agora que todos os endpoints estão funcionando, vamos adicionar uma **camada de validação e serialização** usando Pydantic.

### Por que Validar Dados?

Até agora, nossos endpoints retornam dicionários Python "crus". Isso traz problemas:

- **Sem garantia de formato:** Um dicionário pode ter campos extras ou faltando.
- **Sem validação de entrada:** Se alguém enviar `"user_id": "abc"` em vez de um número, a API quebra.
- **Documentação inconsistente:** O Swagger mostra uma coisa, mas a API pode devolver outra.

**Schemas** resolvem esses problemas: eles definem um **contrato** do que entra e do que sai da API.

### Pydantic: O que é?

**Pydantic** é a biblioteca Python mais popular para validação de dados. Ela usa **Type Hints nativos do Python** para definir modelos de dados que validam automaticamente.

1. **Serialização:** Converter modelos Python → JSON (saída da API) com `.model_dump()`.
2. **Desserialização:** Converter JSON recebido → modelo Python validado (entrada da API).
3. **Validação:** Automática via Type Hints — se o tipo está errado, o Pydantic rejeita.

**Comparação para quem vem do TypeScript/Zod:**

| Conceito | Zod (TypeScript) | Pydantic (Python) |
| :--- | :--- | :--- |
| **Definição** | `z.object({ name: z.string() })` | `class MyModel(BaseModel): name: str` |
| **Validação** | `schema.parse(data)` | `MyModel(**data)` |
| **Serialização** | Implícita (JSON.stringify) | `model.model_dump()` |
| **Erro** | `.safeParse()` retorna `{ success, error }` | `ValidationError` com `.errors()` |

### Pydantic vs Marshmallow

!!! abstract "Por que Pydantic e não Marshmallow?"
    Ambas são bibliotecas de validação, mas o Pydantic é o padrão moderno. Ele é usado pelo FastAPI, LangChain, e diversas ferramentas de IA. Sua principal vantagem é aproveitar **Type Hints nativos**, tornando o código mais limpo e "Pythonic".

| Aspecto | Marshmallow | Pydantic |
| :--- | :--- | :--- |
| **Sintaxe** | `name = fields.String(required=True)` | `name: str` |
| **Validação** | Na chamada `.load()` | Na **instanciação** do modelo |
| **Type Hints** | Usa sistema próprio (`fields.*`) | Usa **Type Hints nativos** |
| **Performance** | Mais lento (puro Python) | Mais rápido (core em Rust) |
| **JSON Schema** | Manual | `.model_json_schema()` (automático!) |


### Criando os Schemas

A estrutura ficará:
```plaintext
apps/backend/src/
├── app.py
├── routes/
│   └── ...
└── schemas/          ← NOVO
    ├── __init__.py
    ├── course_schema.py
    ├── lesson_schema.py
    ├── question_schema.py
    └── progress_schema.py
```

Adicione o Pydantic ao seu projeto:

```bash
cd apps/backend
uv add pydantic
```


Crie `apps/backend/src/schemas/__init__.py` (vazio) e os arquivos a seguir.

**Course Schema (`course_schema.py`):**
```python
from pydantic import BaseModel

class CourseSchema(BaseModel):
    id: int
    title: str
    description: str
    total_lessons: int
    active: bool = True
```

!!! tip "Simplicidade do Pydantic"
    O tipo Python (`int`, `str`) já é suficiente. Todo campo sem valor padrão é obrigatório automaticamente.

**Lesson Schema (`lesson_schema.py`):**
```python
from pydantic import BaseModel

class LessonSchema(BaseModel):
    id: int
    course_id: int
    title: str
    order: int
```

**Question Schema (`question_schema.py`):**
```python
from pydantic import BaseModel

class QuestionSchema(BaseModel):
    id: int
    lesson_id: int
    question: str
    options: list[str]
    correct_option: int

class QuestionIdSchema(BaseModel):
    id: int
```

**Progress Schema (`progress_schema.py`):**
```python
from pydantic import BaseModel, Field

class SubmitAnswerSchema(BaseModel):
    user_id: int
    question_id: int
    # ge = greater or equal (>=0) - Maior ou igual a 0
    selected_option: int = Field(ge=0)  

class ProgressResponseSchema(BaseModel):
    user_id: int
    completed_questions: list[int]
    total_score: int
```

---

## Prática: Refatorando as Rotas para Usar Schemas

Vamos substituir o `jsonify` direto pelo `model_dump` do Pydantic e usar `$ref` no Swagger para evitar repetição.

### Schema vs Docstring

| Aspecto | Docstring (YAML) | Schema (Pydantic) |
| :--- | :--- | :--- |
| **Propósito** | Documentar no Swagger UI | Validar dados em runtime |
| **Quando age** | Na geração da documentação | No processamento da requisição |
| **Erro** | Swagger mostra info errada | API retorna erro 400 (Bad Request) |

!!! important "Documentação Viva"
    Os dois são complementares! Com Pydantic, podemos gerar as `definitions` do Swagger automaticamente, eliminando duplicação e garantindo que a documentação sempre reflita o código.

### Registrando as Definitions no `app.py`

Atualize o `apps/backend/src/app.py` para incluir os schemas como definições reutilizáveis:

```python
    # ... dentro de create_app()
    from schemas.course_schema import CourseSchema
    from schemas.lesson_schema import LessonSchema
    from schemas.question_schema import QuestionSchema, QuestionIdSchema
    from schemas.progress_schema import SubmitAnswerSchema, ProgressResponseSchema

    swagger_template = {
        "tags": [
            {"name": "Health"}, {"name": "Cursos"}, {"name": "Aulas"}, 
            {"name": "Perguntas"}, {"name": "Progresso"}
        ],
        "definitions": {
            "Course": CourseSchema.model_json_schema(),
            "Lesson": LessonSchema.model_json_schema(),
            "Question": QuestionSchema.model_json_schema(),
            "QuestionId": QuestionIdSchema.model_json_schema(),
            "SubmitAnswer": SubmitAnswerSchema.model_json_schema(),
            "UserProgress": ProgressResponseSchema.model_json_schema(),
            "Error": {
                "type": "object",
                "properties": {"error": {"type": "string"}}
            }
        }
    }
    Swagger(app, template=swagger_template)
```

### Refatorando endpoints (Exemplo: Progress)

Aqui é onde o Pydantic brilha: validando os dados que chegam no **POST**.

```python
from pydantic import ValidationError
from schemas.progress_schema import SubmitAnswerSchema

@progress_bp.route('/', methods=['POST'])
def submit_answer():
    """
    Submete uma resposta
    ---
    tags:
      - Progresso
    parameters:
      - name: body
        in: body
        schema:
          $ref: '#/definitions/SubmitAnswer'
    responses:
      200:
        description: Sucesso
      400:
        description: Erro de validação
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        # Validação automática!
        data = SubmitAnswerSchema(**request.json)
    except ValidationError as err:
        return jsonify({"errors": err.errors()}), 400

    # Acesso via atributo: data.user_id
    # ... resto da lógica
```

---

## Prática: Refatorando as Rotas

Agora que temos as definitions registradas, podemos trocar as docstrings verbosas por `$ref` limpos.

**Cursos (`courses.py`):**
```python
from typing import List, Dict, Any, Union, Tuple
from flask import Blueprint, jsonify, Response
from routes.lessons import LESSONS_DB
from schemas.course_schema import CourseSchema
from schemas.lesson_schema import LessonSchema

courses_bp = Blueprint('courses', __name__)

# Dados Mockados (Simulando Banco de Dados)
COURSES_DB = [...] # Mantendo os dados da aula anterior

@courses_bp.route('/', methods=['GET'])
def get_courses() -> Response:
    """
    Lista todos os cursos
    ---
    tags:
      - Cursos
    responses:
      200:
        schema:
          type: array
          items:
            $ref: '#/definitions/Course'
    """
    result = [CourseSchema(**c).model_dump() for c in COURSES_DB]
    return jsonify(result)

@courses_bp.route('/<int:course_id>', methods=['GET'])
def get_course_by_id(course_id: int) -> Union[Response, Tuple[Response, int]]:
    """
    Obtém detalhes de um curso
    ---
    tags:
      - Cursos
    responses:
      200:
        schema:
          $ref: '#/definitions/Course'
    """
    course = next((c for c in COURSES_DB if c['id'] == course_id), None)
    if course:
        result = CourseSchema(**course).model_dump()
        return jsonify(result)
    return jsonify({"error": "Curso não encontrado"}), 404
```

**Aulas (`lessons.py`):**
```python
from flask import Blueprint, jsonify
from routes.questions import QUESTIONS_DB
from schemas.question_schema import QuestionIdSchema

@lessons_bp.route('/<int:lesson_id>/questions', methods=['GET'])
def get_questions_by_lesson(lesson_id: int):
    """
    Lista IDs das perguntas
    ---
    tags:
      - Aulas
    responses:
      200:
        schema:
          type: array
          items:
            $ref: '#/definitions/QuestionId'
    """
    # ... busca aula ...
    questions = [{"id": q['id']} for q in QUESTIONS_DB if q['lesson_id'] == lesson_id]
    result = [QuestionIdSchema(**q).model_dump() for q in questions]
    return jsonify(result)
```

**Perguntas (`questions.py`):**
```python
from schemas.question_schema import QuestionSchema

@questions_bp.route('/<int:question_id>', methods=['GET'])
def get_question_details(question_id: int):
    """
    Obtém detalhes de uma pergunta
    ---
    tags:
      - Perguntas
    responses:
      200:
        schema:
          $ref: '#/definitions/Question'
    """
    question = next((q for q in QUESTIONS_DB if q['id'] == question_id), None)
    if question:
        result = QuestionSchema(**question).model_dump()
        return jsonify(result)
    return jsonify({"error": "Pergunta não encontrada"}), 404
```

### Validação de Entrada (Progress)

Aqui é onde o Pydantic brilha: validando os dados que chegam no **POST**, não apenas serializando a saída.

```python
from pydantic import ValidationError
from schemas.progress_schema import SubmitAnswerSchema, ProgressResponseSchema

@progress_bp.route('/', methods=['POST'])
def submit_answer() -> Union[Response, Tuple[Response, int]]:
    """
    Submete uma resposta e salva o progresso
    ---
    tags:
      - Progresso
    parameters:
      - name: body
        in: body
        schema:
          $ref: '#/definitions/SubmitAnswer'
    responses:
      200:
        schema:
          $ref: '#/definitions/AnswerResult'
      400:
        schema:
          $ref: '#/definitions/Error'
    """
    # VALIDAÇÃO COM PYDANTIC:
    # 1. Desempacota o JSON nos campos do modelo
    # 2. Valida automaticamente os tipos (int, str, etc)
    try:
        data = SubmitAnswerSchema(**request.json)
    except ValidationError as err:
        return jsonify({"errors": err.errors()}), 400

    # Acesso via atributo: data.user_id
    user_id = data.user_id
    question_id = data.question_id
    selected_option = data.selected_option

    # Lógica de validação da resposta ...
```

!!! success "Novidades do Refactor"
    - Trocamos a validação manual (`if not all(...)`) pelo Schema.
    - Acessamos os campos como **atributos** (`data.user_id`) em vez de chaves.
    - Se o cliente enviar um dado inválido, o Pydantic retorna um erro 400 informativo automaticamente.


---

## Testando as Validações no Swagger

2. **Dados Inválidos:** Envie `user_id: "abc"` e veja o `400 Bad Request` detalhado.
3. **Campos Faltando:** Remova um campo obrigatório e veja a rejeição automática.
4. **Validação de Range:** Tente enviar `selected_option: -1` (bloqueado pelo `ge=0`).

---

## Exercícios de Fixação

??? example "Exercício: Novo Endpoint — Listar Todas as Perguntas"
    Adicione a rota `GET /api/questions/` no `questions.py` que retorne **todas** as perguntas. Use o `QuestionSchema` e `$ref` na docstring.

??? example "Exercício: Validação Customizada com Field"
    No `SubmitAnswerSchema`, adicione uma validação que limite `selected_option` a um máximo de 4 (índice 0 a 4).
---

## Resumo da Aula

| O que fizemos | Arquivo | Conceito |
| :--- | :--- | :--- |
| Completamos o Progress | `progress.py` | Blueprint + Estado em Memória |
| Criamos schemas Pydantic | `schemas/*.py` | `BaseModel` + Type Hints |
| Registramos definitions | `app.py` | `.model_json_schema()` (auto) |
| Refatoramos as docstrings | `courses.py`, etc. | `$ref: '#/definitions/...'` |
| Adicionamos validação | `progress.py` | `ValidationError` + `Field(ge=0)` |
| Testamos validação | Swagger UI | Erros 400 vs 500 |
