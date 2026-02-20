# Flask e Documentação

> Guia prático: Estruturar uma API profissional utilizando Flask, organizando o código em Blueprints, simulando armazenamento de dados e documentando endpoints automaticamente com OpenAPI (Swagger).

---

## Teoria

### Estrutura e Modularização
Em vez de um único arquivo gigante, adotaremos uma arquitetura profissional baseada em **Blueprints**.

**Estrutura do Projeto:**
```plaintext
apps/backend/src/
├── app.py           # Entrypoint (Placa-mãe) - Inicializa o Flask e Swagger.
└── routes/          # Blueprints (Componentes) - Módulos isolados (Ex: courses, questions).
```

### O que é um Blueprint? (vs Next.js)

!!! abstract "Conceito de Blueprint"
    Um Blueprint é um conjunto de rotas reutilizável. Ele não roda sozinho, precisa ser registrado no `app.py`.

**Comparação para quem vem do Next.js:**

| Característica | Next.js (App Router) | Flask (Blueprints) |
| :--- | :--- | :--- |
| **Roteamento** | **File-system**: A pasta define a rota (`app/users/page.js`). | **Explícito**: Você define no código (`@bp.route`). |
| **Configuração** | **Implícita**: "Convention over Configuration". | **Explícita**: Você decide URL, prefixo e nome ao registrar. |
| **Prefixo** | Fixo pela estrutura de pastas. | Flexível (`url_prefix='/api/v1'`). |

> **Resumo:** Se o `app.py` é a **placa-mãe**, os Blueprints são os **componentes** (Placa de Vídeo, Memória) que você conecta nela para dar funcionalidade.

### Outros Conceitos

- **Mocking (Estado em Memória):** Usaremos variáveis globais para simular um banco de dados temporariamente.

### Documentação com Docstrings e Swagger

O Flutter/Next.js costuma usar arquivos separados para documentação. No Python, usamos as **Docstrings** (comentários de múltiplas linhas logo abaixo da definição da função) para documentar e, ao mesmo tempo, gerar o Swagger.

!!! tip "O que o Swagger valida?"
    Ao definir `type: integer` em um parâmetro, o Swagger UI bloqueia o envio se você digitar um texto. Isso ajuda a testar a API sem precisar de um frontend pronto!

**Anatomia da Docstring (YAML):**

- `tags`: Agrupa os endpoints no painel do Swagger (ex: "Cursos", "Perguntas").
- `parameters`: Define o que a API espera.
    - `in: path`: O valor vem da URL (ex: `/id`).
    - `type/required`: Define o tipo de dado e se o campo é obrigatório.
- `responses`: Lista os possíveis retornos (200 para sucesso, 404 para erro).
- `schema`: Define o "formato" dos dados que a API devolve (ex: uma lista de objetos com `id`).

---

## Prática: Setup

1.  Crie a pasta do projeto:
    ```bash
    mkdir ldw-merge-skills
    cd ldw-merge-skills
    uv init
    ```

2.  Backend:
    ```bash
    mkdir apps\backend\src\routes
    cd apps\backend
    uv init
    uv add flask flasgger python-dotenv
    ```

??? tip "Troubleshooting: Configurando o Pylance no VS Code"

    Se os erros de Type Hint não estiverem aparecendo no seu VS Code ou sua IDE estiver confusa com Flask, siga estes passos para configurar o **Pylance** (o servidor de linguagem Python oficial da Microsoft):

    1. **Instale as Extensões:** Certifique-se de que a extensão "Python" e a "Pylance" estão instaladas e ativas no VS Code.
    2. **Ative a Análise de Tipo (Type Checking):**
       - Abra as configurações do VS Code (`Ctrl` + `,`).
       - Pesquise por `python.analysis.typeCheckingMode`.
       - Mude o valor de `off` (padrão) para `basic`. O modo `basic` já é suficiente para mostrar sublinhados vermelhos de erros de retorno ou argumentos incorretos.
    3. **Selecione o Interpretador Correto:**
       - Aperte `Ctrl` + `Shift` + `P`.
       - Digite `Python: Select Interpreter` e pressione Enter.
       - Escolha o ambiente da sua pasta (`.venv`) criado pelo `uv`. Se o VS Code estiver usando o Python global do sistema, ele não terá acesso aos pacotes baixados na pasta.

    !!! note "Por que a IDE (às vezes) não reclama?"
        Por padrão, como o Python usa tipagem dinâmica, o Pylance no VS Code adota uma postura "flexível" para não gritar erro com quem está só querendo codar rápido (mantendo o modo `off`). Você precisa dizer "Eu ligo para tipagem agora!" ativando o modo `basic` ou `strict`. Além disso, para que a extensão entenda certas bibliotecas (como o Flask), ela às vezes demanda stubs de tipos (`types-Flask`, etc), caso contrário considera apenas os seus próprios códigos, sem reclamar das lógicas de biblioteca.

---

## Prática: Implementação

### Criando a Base (`app.py`)

O `app.py` é o coração da nossa aplicação (o "Entrypoint"). É ele quem:

1.  **Inicializa o Flask:** Cria a instância principal da aplicação.
2.  **Configura Extensões:** Como o Swagger (para documentação) e futuramente o Banco de Dados.
3.  **Registra os Blueprints:** Conecta as rotas que criaremos nos outros arquivos.

Crie `apps/backend/src/app.py`:
```python
from flask import Flask
from flasgger import Swagger

def create_app():
    app = Flask(__name__)

    # Configuração do Swagger
    app.config['SWAGGER'] = {
        'title': 'LDW Merge Skills',
        'uiversion': 3
    }
    Swagger(app)

    # Espaço reservado para registrar Blueprints depois

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
```

### Health Check (`health.py`)
Crie `apps/backend/src/routes/health.py`:
*(Código do health.py anterior)*

### Cursos e Aulas (`courses.py` e `lessons.py`)

No REST, o agrupamento lógico diz que um arquivo deve se responsabilizar por gerenciar e rotear URLs a partir de um prefixo base.

1.  As rotas que começam com `/api/courses` ficarão no Blueprint do arquivo `courses.py`. Exemplo: listar todos os cursos (`/`) e listar as aulas do curso (`/<id>/lessons`).
2.  As rotas que começam com `/api/lessons` ficarão no Blueprint do arquivo `lessons.py`. Exemplo: listar as perguntas de uma aula (`/<id>/questions`).

Crie `apps/backend/src/routes/courses.py` e `lessons.py` e adicione esses endpoints conforme essas responsabilidades de URL.

### Perguntas e Relacionamento com Aulas

Seguindo as boas práticas REST, vamos separar a busca de uma pergunta específica da lista de perguntas de uma aula.

**Banco de Perguntas (`questions.py`)**

Crie `apps/backend/src/routes/questions.py`:
```python
from flask import Blueprint, jsonify

questions_bp = Blueprint('questions', __name__)

QUESTIONS_DB = [
    {
        "id": 1,
        "lesson_id": 1,
        "question": "O que é Flask?",
        "options": ["Um microframework Web", "Uma marca de garrafa", "Um banco de dados"],
        "correct_option": 0
    }
]

@questions_bp.route('/<int:question_id>', methods=['GET'])
def get_question_details(question_id):
    """
    Obtém detalhes de uma pergunta
    ---
    tags:
      - Perguntas
    parameters:
      - name: question_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Detalhes da pergunta
        schema:
          type: object
          properties:
            id:
              type: integer
            lesson_id:
              type: integer
            question:
              type: string
            options:
              type: array
              items:
                type: string
            correct_option:
              type: integer
      404:
        description: Pergunta não encontrada
    """
    question = next((q for q in QUESTIONS_DB if q['id'] == question_id), None)
    if question:
        return jsonify(question)
    return jsonify({"error": "Question not found"}), 404
```

**Atualizando as Aulas (`lessons.py`)**

Para listar as perguntas de uma aula, usaremos o próprio blueprint de lessons (já que a rota base será `/api/lessons`):
```python
from typing import Union, Tuple
from flask import Blueprint, jsonify, Response
from routes.questions import QUESTIONS_DB
# ... (outros imports e códigos de lessons) ...
lessons_bp = Blueprint('lessons', __name__)

@lessons_bp.route('/<int:lesson_id>/questions', methods=['GET'])
def get_questions_by_lesson(lesson_id: int) -> Union[Response, Tuple[Response, int]]:
    """
    Lista IDs das perguntas de uma aula
    ---
    tags:
      - Aulas
    parameters:
      - name: lesson_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de IDs de perguntas
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
      404:
        description: Aula não encontrada
    """
    lesson = next((l for l in LESSONS_DB if l['id'] == lesson_id), None)
    if not lesson:
        return jsonify({"error": "Aula não encontrada"}), 404

    questions = [{"id": q['id']} for q in QUESTIONS_DB if q['lesson_id'] == lesson_id]
    return jsonify(questions)
```

### Registro no `app.py` (Parte 1)

Atualize o `create_app` para registrar os blueprints de forma limpa, direta, em suas URLs base.

```python
    from routes.courses import courses_bp
    from routes.lessons import lessons_bp
    from routes.questions import questions_bp
    
    # ...
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    app.register_blueprint(lessons_bp, url_prefix='/api/lessons')
    app.register_blueprint(questions_bp, url_prefix='/api/questions')
```

### O Desafio: Lógica de Progresso (Estado)

Aqui usaremos uma variável global `USER_PROGRESS` para simular o banco. 

!!! warning "Atenção"
    Se reiniciar o servidor, os dados somem.

1. Crie `apps/backend/src/routes/progress.py`:

```python
from flask import Blueprint, request, jsonify
from routes.questions import QUESTIONS_DB

progress_bp = Blueprint('progress', __name__)

# Memória Volátil
USER_PROGRESS = {} 

@progress_bp.route('/', methods=['POST'])
def submit_answer():
    """
    Submete resposta
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
            question_id:
              type: integer
            selected_option:
              type: integer
    responses:
      200:
        description: Feedback da resposta
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
    option = data.get('selected_option')

    # Busca pergunta
    question = next((q for q in QUESTIONS_DB if q['id'] == question_id), None)
    if not question: return jsonify({"error": "404"}), 404

    # Valida
    is_correct = (option == question['correct_option'])
    
    # Salva estado
    if user_id not in USER_PROGRESS: USER_PROGRESS[user_id] = {}
    if is_correct: USER_PROGRESS[user_id][question_id] = True

    return jsonify({"correct": is_correct})
```

2. **Registro Final:** Volte ao `app.py` e registre o novo blueprint:

```python
    from routes.progress import progress_bp
    # ...
    app.register_blueprint(progress_bp, url_prefix='/api/progress')
```

---

## Rodando o Servidor

Para rodar, precisamos apontar para o `app.py` dentro de `src`.

1.  Execute:
    ```bash
    uv run flask --app src/app run
    ```
    *Ou execute o arquivo diretamente:* `uv run python src/app.py`

2.  Acesse:
    - Swagger: `http://localhost:5000/apidocs`

---

## Exercícios de Fixação

??? example "Exercício de Fixação: Consultando o Progresso"

    Chegou a hora de validar e extender a persistência em memória do backend.

    **O Problema**
    
    Até agora os alunos podem enviar respostas para o progresso, mas como ele sabe quantas perguntas já acertou? E o que acontece com as variáveis de memória do backend se o app fechar?

    **Sua Missão**:

    1.  **Rota de Histórico:** Implemente `GET /api/progress/<id>` no `progress.py` que retorne todo o histórico do aluno (ou calcule quantas questões ele acertou). Registre também o retorno no Swagger desta rota na Docstring!
    2.  **Teste de "Persistência":**
        - Submeta uma resposta correta via Swagger.
        - Consulte o histórico enviando um GET na nova rota criada.
        - Derrube o servidor (Ctrl+C no Terminal).
        - Suba ele de volta (`uv run flask --app src/app run`).
        - Consulte o histórico novamente. O que aconteceu? 

---

## Preparação para a Semana 3: Type Hints

Para facilitar a introdução do Pydantic na próxima aula, vamos refatorar nosso backend e incluir **Type Hints** (Dicas de Tipo) do Python.

!!! info "O que são Type Hints?"
    Eles permitem especificar o tipo de dado esperado em variáveis, parâmetros e retornos de funções.

!!! question "Por que usar agora?"
    O Pydantic é inteiramente baseado nessas anotações (ex: `id: int`, `title: str`). Acostumar-se com eles tornará a transição na próxima semana muito mais suave. Além disso, a sua IDE fornecerá um autocompletar mais inteligente e alertas de erro.

**Exemplo Prático (Refatorando `courses.py`):**

*Antes:*
```python
def get_course_by_id(course_id):
```

*Depois:*
```python
from typing import Union, Tuple
from flask import Response

# ...

@courses_bp.route('/<int:course_id>', methods=['GET'])
def get_course_by_id(course_id: int) -> Union[Response, Tuple[Response, int]]:
    # ...

@courses_bp.route('/<int:course_id>/lessons', methods=['GET'])
def get_lessons_by_course(course_id: int) -> Union[Response, Tuple[Response, int]]:
    # ...
```

!!! success "Desafio Final da Aula"
    Refatore os demais arquivos (`progress.py`, `questions.py`, etc) adicionando os imports necessários do pacote `typing` (`List`, `Dict`, `Any`) e as dicas de tipo nas assinaturas dos métodos.

---

??? example "Extra: Organizando as Tags do Swagger no app.py"

    Para garantir que as seções da documentação no painel do Swagger UI apareçam na ordem desejada (ex: Health primeiro, depois Cursos, Aulas, etc), você pode sobrescrever as declarações da docstring adicionando um `template` na inicialização do arquivo base de roteamento.

    No `app.py`:

    ```python
        # ...
        # Swagger Configuration
        app.config['SWAGGER'] = {
            'title': 'MergeSkills API',
            'uiversion': 3,
            'description': 'Student API for LDW Merge Skills project',
            'specs_route': '/apidocs/'
        }

        # Definir a Ordem das Abas
        swagger_template = {
            "tags": [
                {"name": "Health"},
                {"name": "Cursos"},
                {"name": "Aulas"},
                {"name": "Perguntas"},
                {"name": "Progresso"}
            ]
        }
        
        Swagger(app, template=swagger_template)
        # ...
    ```
    
    Certifique-se que em todos os outros arquivos os nomes definidos em `tags: - <Nome>` batam perfeitamente com os registrados no `swagger_template`. O de `health.py`, por exemplo, deve ter `- Health`.
