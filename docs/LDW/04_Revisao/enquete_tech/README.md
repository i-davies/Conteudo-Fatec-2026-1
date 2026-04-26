# Enquete Tech (Revisao 03 + 04)

Projeto completo da revisao com:

- Flask + Pydantic no backend
- Persistencia com Flask-SQLAlchemy
- Migrations com Alembic
- Seed para carga inicial
- Frontend Flet

## Como executar

```bash
uv sync
uv run alembic upgrade head
uv run seed.py
uv run backend.py
```

Em outro terminal:

```bash
uv run frontend.py
```

A API roda em `http://localhost:5000`.
