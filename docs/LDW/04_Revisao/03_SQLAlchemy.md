# Revisão de Arquitetura: Camada de Informação Permanente

> Substituindo o armazenamento volátil pela persistência real em Banco de Dados.

Nas etapas anteriores da "Enquete Tech", estruturamos o Flet como interface e blindamos a API com Pydantic. Contudo, se o terminal cair ou o programa for encerrado, o dicionário em memória desaparece completamente.

Para resolver isso, vamos introduzir o **Flask-SQLAlchemy** como ORM e salvar os votos em um arquivo SQLite real no disco.

---


## O Flask-SQLAlchemy como ORM

Em aplicações profissionais, escrever queries SQL cruas (`SELECT * FROM ...`) diretamente no codigo Python dificulta a manutenção e reduz a portabilidade entre diferentes bancos de dados. O **ORM (Object-Relational Mapping)** resolve isso mapeando tabelas do banco para classes Python, permitindo que operemos com objetos ao inves de strings SQL.

### Instalação

Adicione a dependência no ambiente do projeto:

```bash
uv add flask-sqlalchemy
```

---

## Separando a Configuração: `database.py`

Ao invés de colocar toda a configuração do banco diretamente no `backend.py`, vamos isolar essa responsabilidade em um arquivo dedicado chamado `database.py`. Essa separação segue o mesmo padrão utilizado no projeto MergeSkills e traz benefícios claros:

- O `backend.py` fica focado exclusivamente nas **rotas da API**
- Qualquer outro arquivo (como um script de seed) pode importar o banco sem depender do Flask inteiro
- Facilita futuras trocas de banco (de SQLite para PostgreSQL, por exemplo)

Crie o arquivo `database.py` na raiz do projeto:

```python
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Apontando para o arquivo banco.sqlite na mesma pasta do projeto
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'banco.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
```

??? tip "Por que usar SQLite?"
    Para fins de estudo, o SQLite é ideal porque não exige instalação de servidor. O banco inteiro fica em um único arquivo `.sqlite` dentro da pasta do projeto. No ambiente corporativo, a troca para PostgreSQL ou MySQL seria apenas uma mudança na `SQLALCHEMY_DATABASE_URI`.

---

## Definindo o Modelo: `models.py`

O Model descreve a estrutura da tabela usando classes Python. Cada atributo da classe corresponde a uma coluna no banco. Crie o arquivo `models.py`:

```python
from database import db


class TecnologiaModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    votos = db.Column(db.Integer, default=0)

    def to_dict(self):
        """Converte o registro do banco para um dicionário Python (formato JSON)."""
        return {
            "nome": self.nome,
            "votos": self.votos
        }
```


??? info "O que cada coluna faz?"
    - `id`: Chave primária autoincrementada. Cada tecnologia recebe um identificador unico automaticamente.
    - `nome`: Texto de até 50 caracteres, marcado como `unique` para impedir duplicatas e `nullable=False` para exigir preenchimento.
    - `votos`: Contador inteiro que começa em `0` por padrão.

---

## Inicializando o Banco com Dados

Para que a aplicacao funcione sem uma tabela vazia, precisamos criar as tabelas e popular com as tecnologias iniciais. Essa logica precisa ficar no `backend.py` (e nao no `database.py`), porque se o `database.py` importar o `models.py` ao mesmo tempo que o `models.py` importa o `database.py`, teremos uma **importacao circular** e o Python vai travar com erro.

Por isso, o `database.py` permanece puro, contendo apenas a configuracao. O `backend.py` e quem orquestra tudo: importa o banco, importa os modelos, cria as tabelas e popula os dados iniciais.

---

## Refatorando o `backend.py`

Com o banco e os modelos isolados, o `backend.py` precisa de ajustes importantes em relacao a versao que criamos na primeira revisao:

**O que sai do `backend.py`:**

- A criacao do `app = Flask(__name__)` (agora vive no `database.py`)
- O dicionario `PLACAR` em memoria (substituido pelo banco SQLite)
- Qualquer configuracao de banco de dados

**O que entra no `backend.py`:**

- `from database import app, db` para reutilizar o Flask e o SQLAlchemy ja configurados
- `from models import TecnologiaModel` para acessar a tabela do banco
- As rotas passam a consultar e gravar usando `TecnologiaModel.query` e `db.session.commit()`

O arquivo final fica assim:

```python
# pyright: reportCallIssue=false
from flask import jsonify, request
from pydantic import BaseModel, ValidationError
from database import app, db
from models import TecnologiaModel


class VotoRequest(BaseModel):
    tecnologia: str


@app.route('/api/votos', methods=['GET'])
def buscar_placar():
    tecnologias = TecnologiaModel.query.all()
    banco_formatado = {tech.nome: tech.votos for tech in tecnologias}
    return jsonify(banco_formatado)


@app.route('/api/votar', methods=['POST'])
def registrar_voto():
    try:
        dados_validados = VotoRequest(**request.json)
    except ValidationError:
        return jsonify({"sucesso": False, "mensagem": "Formato invalido"}), 400

    tecnologia_votada = dados_validados.tecnologia

    tech_alvo = TecnologiaModel.query.filter_by(nome=tecnologia_votada).first()

    if tech_alvo:
        tech_alvo.votos += 1
        db.session.commit()
        return jsonify({"sucesso": True, "mensagem": f"Voto para {tecnologia_votada} computado com sucesso!"})

    return jsonify({"sucesso": False, "mensagem": "Tecnologia nao encontrada"}), 404


# Cria as tabelas e popula com dados iniciais na primeira execucao
with app.app_context():
    db.create_all()

    if not TecnologiaModel.query.first():
        tecnologias_iniciais = [
            TecnologiaModel(nome="Flask", votos=0),
            TecnologiaModel(nome="FastAPI", votos=0),
            TecnologiaModel(nome="Flet", votos=0),
        ]
        db.session.add_all(tecnologias_iniciais)
        db.session.commit()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

??? tip "Pylance reclamando de 'No parameter named nome'?"
    Esse e um **falso positivo** comum. O SQLAlchemy gera o construtor da Model de forma dinamica a partir das colunas definidas (`db.Column`). O Pylance/Pyright nao consegue introspectar essa criacao automatica e acha que `nome` e `votos` nao existem como parametros. O codigo funciona perfeitamente. A diretiva `# pyright: reportCallIssue=false` no topo do arquivo silencia esse aviso.

??? info "Por que verificar com `query.first()`?"
    Sem essa verificacao, toda vez que o servidor reiniciasse ele tentaria inserir as mesmas tecnologias novamente, gerando um erro de `UNIQUE constraint` na coluna `nome`. Verificando se ja existe ao menos um registro, garantimos que a carga inicial roda **apenas uma vez**.

??? tip "Estrutura final do projeto"
    Após essa refatoração, a pasta do projeto deve conter:
    ```
    enquete_tech/
    ├── backend.py      # Rotas da API (GET e POST)
    ├── database.py     # Configuracao do Flask + SQLAlchemy
    ├── models.py       # Definicao das tabelas (TecnologiaModel)
    ├── frontend.py     # Interface Flet
    └── pyproject.toml  # Dependencias gerenciadas pelo UV
    ```

Note como o `database.py` ficou **puro**, contendo apenas a configuracao do Flask e do SQLAlchemy. Todo o restante (rotas, seed, create_all) fica no `backend.py`, que e o ponto de entrada da aplicacao. Essa organizacao evita importacoes circulares e segue o padrao utilizado no projeto MergeSkills.

??? warning "Por que não usar `db.py` como nome?"
    O Python pode confundir o arquivo `db.py` do projeto com pacotes internos ou bibliotecas que possuem o mesmo nome, gerando um `ImportError`. Usar `database.py` evita essa ambiguidade por completo.
