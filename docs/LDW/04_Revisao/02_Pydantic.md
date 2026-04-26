# Revisão de Arquitetura: Proteção e Pydantic

> Um mergulho na tipagem rigorosa para evitar interações malformadas vindas da interface de usuário.

Na etapa anterior, finalizamos a "Enquete Tech" recebendo os novos votos do Flet puramente pela manipulação bruta do Payload HTTP usando `request.json`. Esse padrão solto do Python introduz riscos críticos no roteamento do backend.

---

## O Problema do Dicionário Solto

Se verificarmos o arquivo `backend.py` atual, temos o seguinte motor de recepção:

```python
@app.route('/api/votar', methods=['POST'])
def registrar_voto():
    dados = request.json
    tecnologia = dados.get('tecnologia')
```

Em um ambiente colaborativo e flexível de desenvolvimento, nada impede que a equipe de Frontend cometa um erro de envio durante uma alteração no código do Flet, passando os dados estruturados erroneamente. 

??? tip "Qual é a falha do Payload sem padronização?"
    Se o Frontend submeter um formato imprevisto, o comando `dados.get('tecnologia')` tentará puxar uma informação de onde ela sequer existe, gerando possíveis quebras de comportamento no sistema Python e retornando erros de Servidor `500` invés de alertas controlados para o usuário. 

Para estruturarmos a aplicação como verdadeiros desenvolvedores em ambientes multiplataforma, usamos **Modelos de Validação Estritos**.

---

## Introdução ao Pydantic

O **Pydantic** é a principal biblioteca moderna do Python para a validação rigorosa de dados. Ao invés de checarmos se uma chave de dicionário existe, nós definimos a moldura exata de como a informação precisa entrar no nosso restaurante, usando classes Python com tipagem.

### Instalação no Ambiente

Para introduzir a validação, precisamos adicionar a dependência oficial na nossa estrutura local ativada na última aula. Abra o terminal onde criamos o projeto e digite o comando de ambiente:

```bash
uv add pydantic
```

### O Molde da Requisição (Schema)

A grande jogada do Pydantic é herdar funções da sua classe base nativa, o `BaseModel`. Nós iremos criar uma blindagem logo no topo do nosso `backend.py`, estipulando formalmente que a ação de votar **exige** a passagem do nome da tecnologia em formato de Texto Puro (`str`).

```python
from pydantic import BaseModel, ValidationError

class VotoRequest(BaseModel):
    tecnologia: str
```

Isso formaliza um Contrato de Interface. Qualquer estrutura JSON despachada na via expressa `POST` e direcionada para a URL `/api/votar` que não traga especificamente o pacote contendo a chave `tecnologia` (com o valor estritamente no padrão texto) será rebatida imediatamente.

---

## Refatorando a Rota do Backend

Agora, conectaremos esse modelo de barreira de entrada dentro do nosso Flask no arquivo nativo da Enquete Tech. Modificamos a rota raiz de gravação para a seguinte arquitetura:

```python
@app.route('/api/votar', methods=['POST'])
def registrar_voto():
    try:
        # A interceptação rigorosa atua aqui centralizada
        dados_validados = VotoRequest(**request.json)
    except ValidationError as e:
        # Resposta orientada e estrutural exigindo correções do componente Front
        return jsonify({"sucesso": False, "mensagem": "Formato inválido do pacote de votação"}), 400

    tecnologia_votada = dados_validados.tecnologia
    
    if tecnologia_votada in PLACAR:
        PLACAR[tecnologia_votada] += 1
        return jsonify({"sucesso": True, "mensagem": f"Voto para {tecnologia_votada} computado!"})
    
    return jsonify({"sucesso": False, "mensagem": "Tecnologia não encontrada nativa na plataforma"}), 404
```

??? info "Por que usar os duplos asteriscos `**` no objeto de request?"
    A nomenclatura `**request.json` faz o desempacotamento dinâmico de dicionários do Python. Ela separa e destrincha todas as chaves JSON repassando chave por chave diretamente como parâmetros individuais na construção da classe validadora.

---

## Testando no VS Code com uma Extensão de Request

Uma forma rápida de validar a API sem depender do frontend é usar a extensão **REST Client** no próprio VS Code.

### Passo a Passo Rápido

1. Instale a extensão `REST Client` (autor: Huachao Mao).
2. Crie um arquivo chamado `teste_api.http` na pasta do projeto.
3. Com o backend rodando em `http://localhost:5000`, execute as requisições clicando em **Send Request** acima de cada bloco.

Exemplo de arquivo `teste_api.http`:

```http
### Buscar placar atual
GET http://localhost:5000/api/votos

### Voto valido
POST http://localhost:5000/api/votar
Content-Type: application/json

{
    "tecnologia": "Flask"
}

### Voto invalido (tecnologia como numero)
POST http://localhost:5000/api/votar
Content-Type: application/json

{
    "tecnologia": 123
}
```

??? tip "O que observar nos testes"
        - No voto valido, a API deve retornar `sucesso: true`.
        - No voto invalido, o Pydantic deve bloquear e retornar `400`.
        - Isso comprova que a validacao da rota esta protegendo o backend contra payload malformado.

Com a implantação dessa barreira restrita, o projeto "Enquete Tech" começa a ganhar traços empresariais, consolidando a ponte comunicacional bloqueando envios nulos e protegendo internamente seus processos transacionais!
