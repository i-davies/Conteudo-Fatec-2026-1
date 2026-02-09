# LDW

> Material didático para a aula de LDW usando o projeto como guia.  
> Projeto utilizado : [ldw-primeiro-projeto](https://github.com/i-davies/ldw-primeiro-projeto).

---

## 01 — UV (ambiente e dependências)

### Objetivos
- Entender o que é um ambiente virtual
- Usar o UV para criar projeto, instalar dependências e executar scripts

### Conceitos-chave
- **Ambiente virtual**: isola pacotes por projeto
- **uv init**: cria o projeto base
- **uv add**: adiciona dependências no `pyproject.toml`
- **uv run**: executa comandos dentro do ambiente sem ativar

### Passo a passo (exemplo)
```bash
uv init
uv add flask
uv run python -V
```

### Boas práticas
- Versione `pyproject.toml` e `uv.lock`
- Use `uv run` para evitar ativação manual

---

## 02 — Python (fundamentos)

### Objetivos
- Reforçar funções, classes e type hints

### Conteúdo trabalhado
- Funções simples
- Tipagem básica com `type hints`
- Classes e métodos

### Exemplo curto (type hints)
```python
def adicionar_item(carrinho: dict[str, float], item: str, preco: float) -> None:
    carrinho[item] = preco
```

---

## 03 — Back-end API (Flask + Swagger)

### Objetivos
- Criar API simples com Flask
- Documentar endpoints com Swagger (Flasgger)

### Endpoints básicos
- `GET /items`
- `POST /items`
- `DELETE /items/<id>`

### Exemplo de execução
```bash
uv run python app.py
```

### Swagger UI
- URL: `http://127.0.0.1:5000/apidocs/`

---

## 04 — Front-end (Flet e Jinja2)

### Flet
- Interface declarativa com componentes
- Exemplo de formulário com botão

### Jinja2
- Renderização server-side
- Templates com variáveis, loops e condicionais

---

## 05 — Banco de dados (PostgreSQL + Docker)

### Objetivos
- Subir PostgreSQL com Docker
- Entender variáveis de ambiente de conexão

### Comandos básicos
```bash
docker compose up --build
docker compose down
```

---

## 06 — Ambiente (Docker Compose completo)

### Objetivos
- Subir backend + frontend + PostgreSQL + Redis
- Padronizar execução

### Comandos
```bash
docker compose up --build
docker compose down
```

---

# Exercícios de fixação

> Responda às questões abaixo para consolidar os conceitos aprendidos nos módulos anteriores.

<quiz>
Qual comando cria a estrutura básica de um projeto com UV?
- [ ] `uv run`
- [x] `uv init`
- [ ] `uv add`
</quiz>

<quiz>
Qual comando adiciona uma dependência ao `pyproject.toml`?
- [ ] `uv sync`
- [x] `uv add`
- [ ] `uv venv`
</quiz>

<quiz>
No Flask, qual endpoint é utilizado para criar um novo recurso?
- [ ] `GET /items`
- [x] `POST /items`
- [ ] `DELETE /items/<id>`
</quiz>

<quiz>
Qual tecnologia renderiza HTML no servidor?
- [ ] Flet
- [x] Jinja2
- [ ] Swagger UI
</quiz>

<quiz>
Qual comando sobe todos os serviços definidos no Docker Compose?
- [x] `docker compose up --build`
- [ ] `docker run`
- [ ] `docker build`
</quiz>

<quiz>
No Flet, o que faz `page.update()`?
- [ ] Cria uma nova página HTML
- [x] Atualiza a interface após mudança de estado
- [ ] Reinicia o app
</quiz>

<!-- mkdocs-quiz results -->
