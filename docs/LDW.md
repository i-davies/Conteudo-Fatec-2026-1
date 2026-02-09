# LDW

> Material didático para a aula de LDW usando o projeto como guia.  
> Projeto utilizado : [ldw-primeiro-projeto](https://github.com/i-davies/ldw-primeiro-projeto).

---

## Slides

<div style="position: relative; width: 100%; height: 0; padding-top: 56.2500%;
 padding-bottom: 0; box-shadow: 0 2px 8px 0 rgba(63,69,81,0.16); margin-top: 1.6em; margin-bottom: 0.9em; overflow: hidden;
 border-radius: 8px; will-change: transform;">
  <iframe loading="lazy" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0; border: none; padding: 0;margin: 0;"
    src="https://www.canva.com/design/DAHAgYe3_Pw/GUjG7sWT4fzWrU9WREEokA/view?embed" allowfullscreen="allowfullscreen" allow="fullscreen">
  </iframe>
</div>
<a href="https:&#x2F;&#x2F;www.canva.com&#x2F;design&#x2F;DAHAgYe3_Pw&#x2F;GUjG7sWT4fzWrU9WREEokA&#x2F;view?utm_content=DAHAgYe3_Pw&amp;utm_campaign=designshare&amp;utm_medium=embeds&amp;utm_source=link" target="_blank" rel="noopener">01</a> de Icaro Davies

## UV

!!! info "Objetivos"
    - Entender o que é um ambiente virtual
    - Usar o UV para criar projeto, instalar dependências e executar scripts

!!! abstract "Conceitos-chave"
    - **Ambiente virtual**: isola pacotes por projeto
    - **uv init**: cria o projeto base
    - **uv add**: adiciona dependências no `pyproject.toml`
    - **uv run**: executa comandos dentro do ambiente sem ativar

> **Passo a passo (exemplo)**
```bash
uv init
uv add flask
uv run python -V
```

> **Boas práticas**
- Versione `pyproject.toml` e `uv.lock`
- Use `uv run` para evitar ativação manual

---

## Python

!!! info "Objetivos"
    - Reforçar funções, classes e type hints

!!! abstract "Conteúdo trabalhado"
    - Funções simples
    - Tipagem básica com `type hints`
    - Classes e métodos

> **Exemplo curto (type hints)**
```python
def adicionar_item(carrinho: dict[str, float], item: str, preco: float) -> None:
    carrinho[item] = preco
```

---

## Back-end API

!!! info "Objetivos"
    - Criar API simples com Flask
    - Documentar endpoints com Swagger (Flasgger)

!!! abstract "Endpoints básicos"
    - `GET /items`
    - `POST /items`
    - `DELETE /items/<id>`

> **Exemplo de execução**
```bash
uv run python app.py
```

> **Swagger UI**
- URL: `http://127.0.0.1:5000/apidocs/`

---

## Front-end

!!! abstract "Flet"
    - Interface declarativa com componentes
    - Exemplo de formulário com botão

!!! abstract "Jinja2"
    - Renderização server-side
    - Templates com variáveis, loops e condicionais

---

## Banco de dados

!!! info "Objetivos"
    - Subir PostgreSQL com Docker
    - Entender variáveis de ambiente de conexão

> **Comandos básicos**
```bash
docker compose up --build
docker compose down
```

---

## Ambiente

!!! info "Objetivos"
    - Subir backend + frontend + PostgreSQL + Redis
    - Padronizar execução

> **Comandos**
```bash
docker compose up --build
docker compose down
```

---

## Exercícios de fixação

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


## Prática

Crie um projeto com UV + Flask e Swagger + Jinja2 ou Flet
