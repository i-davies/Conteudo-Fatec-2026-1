# Navegação, perguntas e feedback

> Continuação direta da aula anterior. Aqui vamos evoluir a primeira versão do app para uma interface completa, com navegação entre telas, reaproveitamento de componentes e fluxo de resposta integrado ao backend.

---

## O que vamos construir nesta etapa

Ao final deste documento, o app será capaz de:

- Exibir os cursos em uma interface mais organizada.
- Navegar da lista de cursos para a lista de lições.
- Carregar as perguntas de uma lição uma a uma.
- Permitir ao aluno escolher uma alternativa.
- Enviar a resposta para a API e mostrar feedback visual.
- Encerrar a lição e limpar o estado da navegação.

---

## Resultado esperado da estrutura

Depois das alterações desta etapa, a pasta do frontend ficará assim:

```text
apps/frontend/
├── main.py
├── pyproject.toml
└── src/
    ├── api.py
    ├── state.py
    ├── components/
    │   ├── __init__.py
    │   ├── app_bar.py
    │   ├── cards.py
    │   ├── dialogs.py
    │   └── layout.py
    └── views/
        ├── __init__.py
        ├── courses.py
        ├── lessons.py
        └── questions.py
```

!!! tip "Leitura do fluxo"
    Pense no projeto em três camadas:

    - `api.py` conversa com o backend.
    - `state.py` guarda o estado atual da navegação.
    - `views/` e `components/` desenham a interface.

    O `main.py` fica no centro dessa orquestração.

---

## Ajustando o estado global

Na aula anterior, o estado já guardava o curso atual e o índice da pergunta. Agora precisamos deixá-lo pronto para um fluxo mais completo, com lista de lições, cache das perguntas e limpeza correta ao voltar de tela.

Substitua o conteúdo de `apps/frontend/src/state.py` por:

```python
class AppState:
    def __init__(self) -> None:
        self.user_id = 1

        self.courses: list[dict] = []
        self.lessons: list[dict] = []

        self.current_course: dict | None = None
        self.current_lesson: dict | None = None

        self.current_question_ids: list[int] = []
        self.current_questions_map: dict[int, dict] = {}
        self.current_question_index = 0
        self.selected_option: int | None = None

    def reset_lesson_state(self) -> None:
        """Limpa o estado ao sair ou terminar uma lição."""
        self.current_lesson = None
        self.current_question_ids = []
        self.current_questions_map = {}
        self.current_question_index = 0
        self.selected_option = None

    def reset_course_state(self) -> None:
        """Limpa o estado ao voltar para a lista de cursos."""
        self.current_course = None
        self.lessons = []
        self.reset_lesson_state()


state = AppState()
```

### O que mudou em relação à etapa anterior

- `lessons` agora guarda as lições do curso selecionado.
- `current_question_ids` mantém apenas os identificadores das perguntas.
- `current_questions_map` funciona como um cache local.
- `reset_lesson_state()` ficou responsável por limpar toda a navegação interna da lição.

??? tip "Por que usar um único objeto de estado?"
    Ao criar `state = AppState()` no final do arquivo, todo o frontend passa a compartilhar a mesma instância.
    Isso simplifica a navegação, porque cada tela acessa o mesmo estado em memória.

---

## Reforçando a camada de API

Na primeira versão, a camada HTTP já fazia o básico. Agora vamos deixá-la mais segura para uso em interface gráfica: com timeout menor, validação de tipo e mensagens de erro padronizadas.

Substitua o conteúdo de `apps/frontend/src/api.py` por:

```python
import os

import httpx

API_URL = os.environ.get("API_URL", "http://localhost:5000/api")

REQUEST_TIMEOUT = 1.2
CONNECT_TIMEOUT = 0.35


def _request_json(method: str, path: str, json_data: dict | None = None) -> dict | list:
    """Faz a requisição e devolve o JSON já convertido."""
    try:
        response = httpx.request(
            method=method,
            url=f"{API_URL}{path}",
            json=json_data,
            timeout=httpx.Timeout(REQUEST_TIMEOUT, connect=CONNECT_TIMEOUT),
        )
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        raise RuntimeError("Não foi possível recuperar dados do servidor.") from exc


def get_courses() -> list[dict]:
    payload = _request_json("GET", "/courses/")
    return payload if isinstance(payload, list) else []


def get_lessons(course_id: int) -> list[dict]:
    payload = _request_json("GET", f"/courses/{course_id}/lessons")
    return payload if isinstance(payload, list) else []


def get_lesson_question_ids(lesson_id: int) -> list[int]:
    payload = _request_json("GET", f"/lessons/{lesson_id}/questions")
    if isinstance(payload, list):
        return [int(item["id"]) for item in payload]
    return []


def get_question_details(question_id: int) -> dict:
    payload = _request_json("GET", f"/questions/{question_id}")
    return payload if isinstance(payload, dict) else {}


def submit_answer(user_id: int, question_id: int, selected_option: int) -> dict:
    payload = _request_json(
        "POST",
        "/progress/",
        json_data={
            "user_id": user_id,
            "question_id": question_id,
            "selected_option": selected_option,
        },
    )
    return payload if isinstance(payload, dict) else {}
```

!!! tip "Por que reduzir o timeout?"
    Esperar muitos segundos por uma resposta gera a sensação de travamento.
    Como o app depende de chamadas curtas, faz sentido falhar rápido e avisar o usuário.

---

## Criando componentes reutilizáveis

Até aqui, a interface ainda está muito acoplada ao `main.py`. O próximo passo é extrair peças visuais que podem ser reutilizadas em várias telas.

### Layout base da página

Crie `apps/frontend/src/components/layout.py`:

```python
import flet as ft

MAX_WIDTH = 1040


def wrap_page(content: ft.Control) -> ft.Control:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(content=content, width=MAX_WIDTH, expand=False),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        ),
        bgcolor="#FFFFFF",
        padding=ft.Padding.only(top=20, right=16, bottom=20, left=16),
        expand=True,
    )
```

Esse envelope mantém a interface centralizada e evita que o conteúdo fique largo demais em telas grandes.

### Barra de navegação reutilizável

Crie `apps/frontend/src/components/app_bar.py`:

```python
import flet as ft


def build_app_bar(
    title: str,
    subtitle: str | None = None,
    show_back: bool = False,
    on_back=None,
) -> ft.Control:
    left_controls: list[ft.Control] = []

    if show_back and on_back is not None:
        left_controls.append(
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color="#111111",
                on_click=on_back,
            )
        )

    text_column = [
        ft.Text(title, size=20, weight=ft.FontWeight.W_700, color="#111111"),
    ]

    if subtitle:
        text_column.append(ft.Text(subtitle, size=12, color="#71717A"))

    left_controls.append(ft.Column(controls=text_column, spacing=2, expand=True))

    return ft.Container(
        content=ft.Row(
            controls=left_controls,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=8, vertical=8),
    )
```

### Cards de curso, lição e alternativa

Crie `apps/frontend/src/components/cards.py` com os helpers de hover e os três builders:

```python
import flet as ft


def _is_hovered(data) -> bool:
    if isinstance(data, bool):
        return data
    return str(data).lower() == "true"


def _set_option_hover_state(option_tile: ft.Container, selected_option: int | None, is_hovered: bool) -> None:
    option_index = option_tile.data
    if selected_option == option_index:
        return

    option_tile.bgcolor = "#F9FAFB" if is_hovered else "#FFFFFF"
    option_tile.border = ft.Border.all(1, "#D4D4D8" if is_hovered else "#E4E4E7")
    option_tile.update()


def _set_list_card_hover_state(card: ft.Container, is_hovered: bool) -> None:
    card.bgcolor = "#FAFAFA" if is_hovered else "#FFFFFF"
    card.border = ft.Border.all(1, "#D4D4D8" if is_hovered else "#E4E4E7")
    card.update()


def build_course_card(course: dict, on_click) -> ft.Control:
    card = ft.Container(
        bgcolor="#FFFFFF",
        border=ft.Border.all(1, "#E4E4E7"),
        border_radius=10,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.ListTile(
            title=ft.Text(course["title"], size=16, weight=ft.FontWeight.W_600, color="#111111"),
            subtitle=ft.Text(course.get("description") or "Sem descrição.", size=12, color="#71717A"),
            trailing=ft.Text(f"{course.get('total_lessons', 0)} aulas", size=12, color="#71717A"),
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=14),
            hover_color=ft.Colors.TRANSPARENT,
            splash_color=ft.Colors.TRANSPARENT,
            mouse_cursor=ft.MouseCursor.CLICK,
            data=course,
            on_click=lambda e: on_click(e.control.data),
        ),
    )
    card.on_hover = lambda e, c=card: _set_list_card_hover_state(c, _is_hovered(e.data))
    return card


def build_lesson_card(lesson: dict, on_click) -> ft.Control:
    order = lesson.get("order", "-")
    card = ft.Container(
        bgcolor="#FFFFFF",
        border=ft.Border.all(1, "#E4E4E7"),
        border_radius=10,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.ListTile(
            leading=ft.Container(
                content=ft.Text(str(order), size=13, weight=ft.FontWeight.W_700, color="#111111"),
                bgcolor="#F4F4F5",
                border_radius=99,
                padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            ),
            title=ft.Text(lesson["title"], size=15, weight=ft.FontWeight.W_600, color="#111111"),
            subtitle=ft.Text(lesson.get("description") or "Sem descrição.", size=12, color="#71717A"),
            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color="#71717A", size=18),
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=14),
            hover_color=ft.Colors.TRANSPARENT,
            splash_color=ft.Colors.TRANSPARENT,
            mouse_cursor=ft.MouseCursor.CLICK,
            data=lesson,
            on_click=lambda e: on_click(e.control.data),
        ),
    )
    card.on_hover = lambda e, c=card: _set_list_card_hover_state(c, _is_hovered(e.data))
    return card


def build_option_tile(
    text: str,
    index: int,
    selected_option: int | None,
    on_select,
) -> ft.Control:
    is_selected = selected_option == index

    option_tile = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                chr(65 + index),
                                size=12,
                                weight=ft.FontWeight.W_700,
                                color="#111111" if is_selected else "#111111",
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    width=30,
                    height=30,
                    bgcolor="#FFFFFF" if is_selected else "#F4F4F5",
                    border_radius=99,
                ),
                ft.Text(
                    text,
                    size=14,
                    color="#FFFFFF" if is_selected else "#111111",
                    expand=True,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#111111" if is_selected else "#FFFFFF",
        border=ft.Border.all(1, "#111111" if is_selected else "#E4E4E7"),
        border_radius=10,
        padding=ft.Padding.symmetric(horizontal=12, vertical=12),
        animate=ft.Animation(110, ft.AnimationCurve.EASE_OUT),
        ink=False,
        data=index,
        on_click=lambda e: on_select(e.control.data),
    )
    option_tile.on_hover = lambda e, t=option_tile: _set_option_hover_state(t, selected_option, _is_hovered(e.data))
    return option_tile
```

!!! tip "O papel do atributo data"
    Repare que os cards carregam o próprio dicionário em `data`.
    Isso permite recuperar o curso ou a lição clicada sem depender de variáveis externas no momento do clique.

---

## Atualizando a tela de cursos

Na primeira aula, a listagem de cursos foi construída de forma mais simples. Agora ela pode ser substituída por uma versão alinhada ao novo conjunto de componentes.

Substitua o conteúdo de `apps/frontend/src/views/courses.py` por:

```python
import flet as ft

from src.components.cards import build_course_card
from src.components.layout import wrap_page


def build_courses_view(courses: list[dict], on_course_click) -> ft.Control:
    cards = [build_course_card(course, on_course_click) for course in courses]

    if not cards:
        cards = [
            ft.Container(
                content=ft.Text("Nenhum curso encontrado.", color="#71717A"),
                padding=ft.Padding.only(top=12),
            )
        ]

    return wrap_page(
        ft.Column(
            controls=[
                ft.Text("MergeSkills", size=28, weight=ft.FontWeight.W_700, color="#111111"),
                ft.Text("Escolha um curso para começar.", size=13, color="#71717A"),
                ft.Container(height=8),
                ft.Column(controls=cards, spacing=10, scroll=ft.ScrollMode.AUTO, expand=True),
            ],
            spacing=0,
            expand=True,
        )
    )
```

---

## Criando a tela de lições

Agora que a view de cursos já está mais consistente, o próximo passo é responder ao clique do usuário e abrir as lições do curso selecionado.

Crie `apps/frontend/src/views/lessons.py`:

```python
import flet as ft

from src.components.app_bar import build_app_bar
from src.components.cards import build_lesson_card
from src.components.layout import wrap_page


def build_lessons_view(course: dict, lessons: list[dict], on_back, on_lesson_click) -> ft.Control:
    lesson_cards = [build_lesson_card(lesson, on_lesson_click) for lesson in lessons]

    if not lesson_cards:
        lesson_cards = [
            ft.Container(
                content=ft.Text("Nenhuma lição encontrada.", color="#71717A"),
                padding=ft.Padding.only(top=12),
            )
        ]

    return wrap_page(
        ft.Column(
            controls=[
                build_app_bar(
                    title=course["title"],
                    subtitle="Lições do curso",
                    show_back=True,
                    on_back=on_back,
                ),
                ft.Container(height=8),
                ft.Column(controls=lesson_cards, spacing=10, scroll=ft.ScrollMode.AUTO, expand=True),
            ],
            spacing=0,
            expand=True,
        )
    )
```

---

## Criando a tela de perguntas

Essa parte concentra a lógica mais importante da interface: mostrar a pergunta atual, destacar a alternativa escolhida e habilitar o envio da resposta.

Crie `apps/frontend/src/views/questions.py`:

```python
import flet as ft

from src.components.app_bar import build_app_bar
from src.components.cards import build_option_tile
from src.components.layout import wrap_page


def build_question_view(
    current_course: dict,
    current_lesson: dict,
    question: dict,
    question_number: int,
    total_questions: int,
    selected_option: int | None,
    on_back,
    on_select_option,
    on_submit,
) -> ft.Control:
    options = question.get("options", [])
    option_tiles = [
        build_option_tile(
            text=option,
            index=index,
            selected_option=selected_option,
            on_select=on_select_option,
        )
        for index, option in enumerate(options)
    ]

    submit_button = ft.FilledButton(
        content=ft.Text("Enviar resposta"),
        style=ft.ButtonStyle(
            bgcolor={"": "#111111" if selected_option is not None else "#E4E4E7"},
            color={"": "#FFFFFF" if selected_option is not None else "#A1A1AA"},
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        disabled=selected_option is None,
        on_click=lambda e: on_submit(),
    )

    body_controls: list[ft.Control] = [
        ft.Container(
            content=ft.Text(question.get("question", "Pergunta indisponível."), size=16, color="#111111"),
            bgcolor="#FFFFFF",
            border=ft.Border.all(1, "#E4E4E7"),
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=14, vertical=14),
        )
    ]

    if question.get("code"):
        body_controls.append(
            ft.Container(
                content=ft.Text(question["code"], size=12, font_family="Consolas", color="#111111"),
                bgcolor="#FAFAFA",
                border=ft.Border.all(1, "#E4E4E7"),
                border_radius=10,
                padding=ft.Padding.symmetric(horizontal=12, vertical=12),
            )
        )

    body_controls.extend(
        [
            ft.Text("Alternativas", size=13, weight=ft.FontWeight.W_600, color="#111111"),
            ft.Column(controls=option_tiles, spacing=10),
            ft.Row(controls=[submit_button], alignment=ft.MainAxisAlignment.END),
        ]
    )

    return wrap_page(
        ft.Column(
            controls=[
                build_app_bar(
                    title=current_lesson["title"],
                    subtitle=f"Questão {question_number} de {total_questions}",
                    show_back=True,
                    on_back=on_back,
                ),
                ft.Container(height=8),
                ft.Column(controls=body_controls, spacing=12, scroll=ft.ScrollMode.AUTO, expand=True),
            ],
            spacing=0,
            expand=True,
        )
    )


def build_completion_view(on_finish) -> ft.Control:
    return wrap_page(
        ft.Column(
            controls=[
                ft.Container(expand=True),
                ft.Text("Lição concluída", size=28, weight=ft.FontWeight.W_700, color="#111111"),
                ft.Text("Bom trabalho. Vamos para a próxima.", size=13, color="#71717A"),
                ft.Container(height=12),
                ft.FilledButton(
                    content=ft.Text("Voltar para lições"),
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    on_click=on_finish,
                ),
                ft.Container(expand=True),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,
            expand=True,
        )
    )
```

### O que essa view resolve

- Exibe a pergunta atual com o contador da lição.
- Renderiza as alternativas dinamicamente.
- Habilita o botão de envio apenas quando há uma opção selecionada.
- Exibe uma tela final quando todas as perguntas acabam.

---

## Exibindo erros e feedback com diálogo

Quando a interface depende de API, erros de rede e retornos inesperados precisam ser tratados sem travar a navegação. Vamos isolar esse comportamento em um componente próprio.

Crie `apps/frontend/src/components/dialogs.py`:

```python
import flet as ft


def show_error(page: ft.Page, message: str) -> None:
    snackbar = ft.SnackBar(
        content=ft.Text(message, color="#FFFFFF"),
        bgcolor="#DC2626",
    )
    page.overlay.append(snackbar)
    snackbar.open = True
    page.update()


def show_feedback_dialog(page: ft.Page, is_correct: bool, on_continue) -> None:
    title = "Resposta correta" if is_correct else "Resposta incorreta"
    description = (
        "Boa! Vamos para a próxima."
        if is_correct
        else "Sem problema, tente novamente na próxima."
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title, color="#111111"),
        content=ft.Text(description, color="#52525B"),
        bgcolor="#FFFFFF",
        actions=[
            ft.TextButton(
                "Continuar",
                on_click=lambda e: _close_and_continue(page, dialog, on_continue),
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def _close_and_continue(page: ft.Page, dialog: ft.AlertDialog, on_continue) -> None:
    dialog.open = False
    page.update()
    on_continue()
```

!!! important
    O uso de `page.overlay` evita que o diálogo ou o `SnackBar` desapareçam quando a árvore principal da página é redesenhada pelo `render()`.

---

## Orquestrando tudo no main.py

Agora sim vamos unir estado, API, views e componentes em um único fluxo de navegação.

Substitua o conteúdo de `apps/frontend/main.py` por:

```python
import flet as ft

from src.api import (
    get_courses,
    get_lessons,
    get_lesson_question_ids,
    get_question_details,
    submit_answer,
)
from src.state import state
from src.components.dialogs import show_error, show_feedback_dialog
from src.views.courses import build_courses_view
from src.views.lessons import build_lessons_view
from src.views.questions import build_question_view, build_completion_view

SERVER_UNAVAILABLE_MSG = "Não foi possível recuperar dados do servidor."
ANSWER_SUBMIT_ERROR_MSG = "Não foi possível enviar a resposta."


def main(page: ft.Page) -> None:
    page.title = "MergeSkills"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#FFFFFF"
    page.padding = 0

    page.window.width = 1140
    page.window.height = 800
    page.window.min_width = 360
    page.window.min_height = 640

    loading_title = ft.Text("Carregando...", size=16, weight=ft.FontWeight.W_600, color="#111111")
    loading_subtitle = ft.Text("Aguarde um instante", size=12, color="#52525B")
    loading_overlay = ft.Container(
        visible=False,
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.25, "#FFFFFF"),
        alignment=ft.Alignment(0, 0),
        content=ft.Container(
            bgcolor="#FFFFFF",
            border=ft.Border.all(1, "#E4E4E7"),
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=18, vertical=14),
            content=ft.Row(
                controls=[
                    ft.ProgressRing(width=20, height=20, stroke_width=2),
                    ft.Column(controls=[loading_title, loading_subtitle], spacing=2, tight=True),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
        ),
    )
    page.overlay.append(loading_overlay)

    def show_loading(title: str, subtitle: str = "Aguarde um instante") -> None:
        loading_title.value = title
        loading_subtitle.value = subtitle
        loading_overlay.visible = True
        page.update()

    def hide_loading() -> None:
        if loading_overlay.visible:
            loading_overlay.visible = False
            page.update()

    def render(view: ft.Control) -> None:
        page.controls.clear()
        page.add(view)
        page.update()

    def back_to_courses(e=None) -> None:
        state.reset_course_state()
        show_loading("Carregando cursos")
        try:
            state.courses = get_courses()
            render(build_courses_view(state.courses, on_course_click))
        except Exception:
            show_error(page, SERVER_UNAVAILABLE_MSG)
        finally:
            hide_loading()

    def back_to_lessons(e=None) -> None:
        if not state.current_course:
            back_to_courses()
            return
        state.reset_lesson_state()
        show_loading("Carregando lições")
        try:
            state.lessons = get_lessons(state.current_course["id"])
            render(build_lessons_view(state.current_course, state.lessons, back_to_courses, on_lesson_click))
        except Exception:
            show_error(page, SERVER_UNAVAILABLE_MSG)
        finally:
            hide_loading()

    def go_to_next_question() -> None:
        total = len(state.current_question_ids)
        print(f"[DEBUG] Navegando: questão {state.current_question_index + 1} de {total}")

        if state.current_question_index >= total:
            print("[DEBUG] Lição concluída")
            render(build_completion_view(back_to_lessons))
            return

        current_question_id = state.current_question_ids[state.current_question_index]

        question = state.current_questions_map.get(current_question_id)
        if question is None:
            show_loading("Carregando pergunta")
            try:
                print(f"[DEBUG] Buscando detalhes da questão: {current_question_id}")
                question = get_question_details(current_question_id)
            except Exception as e:
                print(f"[DEBUG] Erro ao buscar questão: {e}")
                show_error(page, SERVER_UNAVAILABLE_MSG)
                return
            finally:
                hide_loading()
            state.current_questions_map[current_question_id] = question

        print(f"[DEBUG] Renderizando questão: {question.get('question', '...')[0:30]}...")

        render(
            build_question_view(
                current_course=state.current_course,
                current_lesson=state.current_lesson,
                question=question,
                question_number=state.current_question_index + 1,
                total_questions=total,
                selected_option=state.selected_option,
                on_back=back_to_lessons,
                on_select_option=on_select_option,
                on_submit=on_submit_answer,
            )
        )

    def on_course_click(course: dict) -> None:
        state.current_course = course
        show_loading("Carregando lições")
        try:
            state.lessons = get_lessons(course["id"])
            render(build_lessons_view(course, state.lessons, back_to_courses, on_lesson_click))
        except Exception:
            show_error(page, SERVER_UNAVAILABLE_MSG)
        finally:
            hide_loading()

    def on_lesson_click(lesson: dict) -> None:
        print(f"[DEBUG] Entrando na lição ID: {lesson['id']} - {lesson['title']}")
        state.reset_lesson_state()
        state.current_lesson = lesson

        show_loading("Carregando perguntas")
        try:
            print(f"[DEBUG] Buscando IDs de questões para lição: {lesson['id']}")
            state.current_question_ids = get_lesson_question_ids(lesson["id"])
            print(f"[DEBUG] IDs recebidos: {state.current_question_ids}")
        except Exception as e:
            print(f"[DEBUG] Erro ao buscar IDs: {e}")
            show_error(page, SERVER_UNAVAILABLE_MSG)
            return
        finally:
            hide_loading()

        if not state.current_question_ids:
            print("[DEBUG] Nenhum ID de questão encontrado na lição.")
            show_error(page, "Essa lição ainda não possui perguntas.")
            return

        go_to_next_question()

    def on_select_option(index: int) -> None:
        state.selected_option = index
        go_to_next_question()

    def on_submit_answer() -> None:
        if state.selected_option is None:
            show_error(page, "Selecione uma opção antes de enviar.")
            return

        question_id = state.current_question_ids[state.current_question_index]
        print(f"[DEBUG] Enviando resposta: questão={question_id}, opção={state.selected_option}")

        show_loading("Enviando resposta")
        try:
            result = submit_answer(
                user_id=state.user_id,
                question_id=question_id,
                selected_option=state.selected_option,
            )
            is_correct = bool(result.get("is_correct", False))
            print(f"[DEBUG] Resultado: is_correct={is_correct}")
        except Exception as e:
            print(f"[DEBUG] Erro ao enviar: {e}")
            show_error(page, ANSWER_SUBMIT_ERROR_MSG)
            return
        finally:
            hide_loading()

        def continue_flow() -> None:
            state.current_question_index += 1
            state.selected_option = None
            go_to_next_question()

        show_feedback_dialog(page, is_correct, continue_flow)

    back_to_courses()


if __name__ == "__main__":
    ft.run(main)
```

### Como esse fluxo funciona

1. `back_to_courses()` carrega os cursos e desenha a tela inicial.
2. `on_course_click()` salva o curso atual e abre a lista de lições.
3. `on_lesson_click()` busca os identificadores das perguntas da lição.
4. `go_to_next_question()` decide se deve abrir a próxima pergunta ou a tela final.
5. `on_select_option()` apenas marca a alternativa e redesenha a tela.
6. `on_submit_answer()` envia a resposta e, após o diálogo, avança o índice.

??? tip "Por que guardar só os IDs primeiro?"
    Buscar primeiro a lista de IDs e carregar o detalhe apenas da pergunta atual reduz tráfego e permite usar cache.
    Isso deixa a navegação mais eficiente, principalmente quando a lição tem várias questões.

    O loading overlay também está integrado nas chamadas de API para manter feedback visual consistente.

---

## Roteiro de validação

Depois de aplicar as alterações, execute:

```bash
cd apps/frontend
uv run flet run main.py
```

Valide o comportamento abaixo:

- A tela inicial mostra os cursos em cards.
- O clique em um curso abre a lista de lições.
- O botão de voltar da barra superior retorna corretamente.
- O clique em uma lição abre a primeira pergunta.
- A alternativa selecionada muda de aparência.
- O botão de envio só fica habilitado após a seleção.
- O diálogo de feedback aparece depois do envio.
- Ao continuar, a próxima pergunta é carregada.
- Ao final da lição, a tela de conclusão aparece.
- O retorno para a lista de lições limpa o estado anterior.

!!! caution "Se algo não funcionar"
    Verifique primeiro se o backend continua ativo em `http://localhost:5000/apidocs`.
    A maior parte dos erros nesta etapa vem de API indisponível, banco sem seed ou rota diferente do esperado.


---

### Ponto de teste do bônus

Execute novamente:

```bash
uv run flet run --web -r main.py
```
