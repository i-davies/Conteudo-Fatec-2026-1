# Interface com Flet

> Guia prático: construir a primeira versão funcional da interface do aluno com Flet, conectada ao backend real do MergeSkills.

**Objetivo:** transformar a lógica Python em uma UI multiplataforma, com estado simples, consumo de API e navegação entre telas.

!!! note "Recapitulação"
    Já temos backend com motor de progresso persistente.
    Agora vamos construir a interface que o aluno usará para consumir o conteúdo.

---

## O que é Flet?

O **Flet** é um framework que permite construir aplicativos interativos para Web, Desktop e Mobile usando apenas **Python**. 

### Por que usar Flet no MergeSkills?
- **Zero HTML/CSS/JS**: Você foca na lógica e o Flet cuida da renderização.
- **Baseado em Flutter**: A performance e o visual são de nível nativo (usa a engine do Google).
- **Reativo**: A UI se atualiza automaticamente quando o estado dos dados muda.
- **Multiplataforma**: O mesmo código roda no navegador, no Windows ou no Android.

### Conceitos Fundamentais
1. **Page**: A janela principal ou aba do navegador.
2. **Controls (Widgets)**: Botões, textos, listas, colunas (o que você vê na tela).
3. **Event Handlers**: Funções chamadas quando o usuário interage (ex: `on_click`).
4. **Layout**: Uso de `ft.Column`, `ft.Row` e `ft.Container` para organizar os elementos.

---

## Preparação do Ambiente

Para esta aula, precisamos que todo o ecossistema do MergeSkills esteja rodando. Pequenas falhas no backend impedirão o frontend de funcionar.

### Subir Banco de Dados e Backend
Abra um terminal na raiz do projeto:

```bash
# Iniciar o Postgres via Docker
docker-compose up -d

# Entrar na pasta do backend e rodar o servidor
cd apps/backend
uv sync
uv run alembic upgrade head
uv run python src/scripts/seed.py  # Garante que temos cursos e usuários
uv run flask --app src/app run --debug --port 5000
```

!!! important
    Mantenha esse terminal aberto. A API deve estar acessível em `http://localhost:5000/apidocs`.

### Iniciar o Projeto Frontend

!!! caution "Atenção com terminais ativos no VS Code"
    Se você abrir um novo terminal e ele já mostrar `(.venv)` no início da linha,
    ele pode estar herdando o ambiente do backend.

    Digite `deactivate` para sair de qualquer venv antes de rodar os comandos abaixo.
    Queremos um terminal limpo (sem o prefixo da venv) para criar o novo projeto do zero.

Abra um **segundo terminal** e crie o ambiente e a estrutura de pastas:

```bash
# Criar e entrar na pasta (se já não estiver nela)
# Criar a pasta apps/frontend
cd apps/frontend

# Inicializar o projeto com uv
uv init --app

# Instalar as dependências necessárias
uv add flet httpx

# Criar estrutura de subpastas do src
# Criar src/components src/views
```

---

## Primeiro Código: Hello World

Antes de mergulhar na arquitetura, crie um arquivo temporário `hello.py` em `apps/frontend/` para ver o Flet funcionando:

```python
import flet as ft

def main(page: ft.Page):
    # Configuração da Página
    page.title = "Olá, Flet!"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Criando o Controle
    lbl_ola = ft.Text("Olá, MergeSkills!", size=40, weight="bold", color="blue")

    def on_click(e):
        lbl_ola.value = "Botão Clicado!"
        page.update() # ESSENCIAL: Avisa o Flet que algo mudou na tela

    btn = ft.Button("Clique aqui", on_click=on_click)

    # Adicionar na tela
    page.add(lbl_ola, btn)

ft.run(main)
```

**Rodar:** `uv run flet run --web hello.py`

---

## Estrutura do Projeto

Agora que vimos o básico, vamos organizar o frontend seguindo padrões profissionais de separação de responsabilidades.

```text
apps/frontend/
├── main.py             # Arquivo de entrada (Navegação Central)
├── pyproject.toml
└── src/
    ├── api.py          # Lógica de comunicação com o backend (httpx)
    ├── state.py        # Estado global (Usuário, Curso atual, etc)
    ├── components/     # Elementos visuais reutilizáveis (NavBar, Cards)
    └── views/          # "Páginas" completas (Catálogo, Questões)
```

---

## Contrato da API

Nosso frontend vai conversar exclusivamente com o backend no endereço `http://localhost:5000/api`.

| Método | Endpoint | Função na UI |
| :--- | :--- | :--- |
| `GET` | `/courses` | Mostrar lista inicial de cursos |
| `GET` | `/courses/{id}/lessons` | Mostrar as lições ao clicar em um curso |
| `GET` | `/lessons/{id}/questions` | Buscar as perguntas de uma lição |
| `POST` | `/progress` | Enviar resposta do aluno e receber feedback |

!!! caution "Sem backend, sem dados"
    O frontend em Flet depende da API para renderizar os conteúdos.
    Se o backend estiver offline, as telas podem ficar vazias ou exibir erro.

---

## Implementação Passo a Passo

### O Coração dos Dados: `src/state.py`

Como o Flet é reativo, precisamos de um lugar centralizado para guardar o que está acontecendo na navegação. Crie `apps/frontend/src/state.py`:

```python
class AppState:
    def __init__(self) -> None:
        self.user_id = 1             # Simulando usuário logado
        self.courses: list[dict] = []
        self.current_course: dict | None = None
        self.current_lesson: dict | None = None
        
        # Estado das Perguntas
        self.current_question_ids: list[int] = []
        self.current_questions_map: dict[int, dict] = {}
        self.current_question_index = 0
        self.selected_option: int | None = None

    def reset_lesson_state(self) -> None:
        """Limpa o estado ao sair de uma lição."""
        self.current_lesson = None
        self.current_question_index = 0
        self.selected_option = None

    def reset_course_state(self) -> None:
        """Limpa o estado ao voltar para a lista de cursos."""
        self.current_course = None
        self.reset_lesson_state()

state = AppState()
```

---

### O Mensageiro: `src/api.py`

Aqui vamos usar o `httpx` para falar com o Flask. Crie `apps/frontend/src/api.py`:

```python
import os
import httpx

# URL do ambiente ou usa o padrão localhost
API_URL = os.environ.get("API_URL", "http://localhost:5000/api")

def _request_json(method: str, path: str, json_data: dict | None = None) -> dict | list:
    """Função auxiliar para fazer requisições e tratar erros."""
    try:
        response = httpx.request(
            method=method,
            url=f"{API_URL}{path}",
            json=json_data,
            timeout=5.0
        )
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        print(f"Erro na API ({path}): {exc}")
        raise RuntimeError("Servidor Indisponível")

def get_courses() -> list[dict]:
    return _request_json("GET", "/courses/")

def get_lessons(course_id: int) -> list[dict]:
    return _request_json("GET", f"/courses/{course_id}/lessons")

def get_lesson_question_ids(lesson_id: int) -> list[int]:
    """Retorna apenas os IDs das perguntas da lição."""
    payload = _request_json("GET", f"/lessons/{lesson_id}/questions")
    return [int(item["id"]) for item in payload]

def get_question_details(question_id: int) -> dict:
    return _request_json("GET", f"/questions/{question_id}")

def submit_answer(user_id: int, question_id: int, selected_option: int) -> dict:
    return _request_json(
        "POST", 
        "/progress", 
        json_data={
            "user_id": user_id,
            "question_id": question_id,
            "selected_option": selected_option
        }
    )
```

---

### O Maestro: `main.py`

O `main.py` coordena a troca de telas (navegação). Substitua o conteúdo de `apps/frontend/main.py`:

```python
import flet as ft
from src.api import get_courses, get_lessons, get_lesson_question_ids, get_question_details, submit_answer
from src.state import state
# Importaremos as views que criaremos no próximo passo
# from src.views.courses import build_courses_view
# ...

def main(page: ft.Page):
    page.title = "MergeSkills - Aluno"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 450 # Tamanho de celular para teste
    page.window.height = 800

    def render(view_content: ft.Control):
        """Limpa a tela e desenha o novo conteúdo."""
        page.controls.clear()
        page.add(view_content)
        page.update()

    # --- Funções de Navegação ---
    
    def show_courses():
        state.reset_course_state()
        state.courses = get_courses()
        # Aqui chamaremos a view de cursos
        # render(build_courses_view(state.courses, on_course_click=show_lessons))
        render(ft.Text("Lista de Cursos (Construindo...)"))

    # Inicialização
    show_courses()

ft.run(main)
```

---

### Construindo as Visualizações (Views)

As views são funções que pegam dados e retornam "pedaços" de interface.

#### Crie `apps/frontend/src/views/courses.py`:
```python
import flet as ft

def build_courses_view(courses, on_course_click):
    list_items = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    
    for c in courses:
        list_items.controls.append(
            ft.Container(
                content=ft.ListTile(
                    title=ft.Text(c['title'], weight="bold"),
                    subtitle=ft.Text(c['description']),
                    on_click=lambda e, course=c: on_course_click(course)
                ),
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=10
            )
        )
        
    return ft.Column([
        ft.Text("Catálogo de Cursos", size=25, weight="bold"),
        list_items
    ])
```

---


## Execução e Validação

```bash
# No terminal do frontend
uv run flet run --web -r main.py
```
