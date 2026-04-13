# Revisão de Arquitetura: Backend e Frontend

> Uma visão unificada e simplificada do fluxo de dados em aplicações voltadas à web, consolidadas a partir do uso de Flask e Flet.

Nesta etapa do curso, você já foi exposto a conceitos fundamentais sobre a criação de APIs (Backend) e ao ranqueamento de interfaces de usuário (Frontend). Quando mergulhamos no código da nossa plataforma educacional principal (o MergeSkills), a grande quantidade de arquivos pode ofuscar a simplicidade matemática e lógica do processo.

O objetivo deste material é oferecer um "laboratório purificado". Criaremos uma mini-aplicação do zero com apenas dois arquivos para vermos claramente como de fato um "Cérebro" de dados (Backend) conversa com um componente visual de Tela (Frontend).

---

## O Paradigma do Restaurante

Pense no desenvolvimento Fullstack como a rotina interna de um grande restaurante dinâmico:

* **O Cliente e o Cardápio (Interface / Flet)**: O cliente senta à mesa e visualiza os pratos. Ele toma as decisões (clica em botões) e espera ver o prato chegar à mesa.
* **O Garçom (API / HTTP)**: O garçom anota o pedido, leva até os fundos e volta trazendo a resposta. O cliente não precisa saber fritar o bife; ele delega a ação.
* **A Cozinha (Servidor / Flask)**: É onde ocorre a "Lógica de Negócios" pesada. Ela processa o pedido, queima insumos, deduz do estoque na despensa (Banco de Dados) e embala na bandeja (Formato JSON) enviando aos clientes.

Em vez de criar uma aplicação monolítica, manter a Cozinha completamente apartada das Mesas (Arquitetura Desacoplada) confere agilidade. A nossa API pode entregar os dados para um navegador Web, para um Desktop e para um celular, simultaneamente, sem recompilar a lógica.

---

## A Prática Simplificada: Enquete Tech

Para isolar a lógica, vamos recriar o projeto "Enquete Tech" do zero. Todo o fluxo acontece entre apenas dois arquivos executáveis e utilizaremos o `uv` para gerenciar nosso ambiente e as dependências de forma ágil e segura.

### 1. Preparando o Ambiente com UV

Abra o seu terminal e crie uma nova pasta para o projeto. Em seguida, inicialize a estrutura e instale as bibliotecas necessárias:

```bash
# Cria e acessa o diretório do projeto
mkdir enquete_tech
cd enquete_tech

# Inicializa o projeto vazio
uv init

# Instala as dependências de Backend e Frontend
uv add flask "flet[all]" httpx
```

??? tip "Atenção ao flet[all]"
    Em versões recentes, a equipe do Flet otimizou a biblioteca separando seus componentes. O pacote base `flet` puro atende apenas o Desktop. Quando precisamos rodar no **Modo Web**, instalar `"flet[all]"` é obrigatório, pois garante a instalação do servidor web interno (FastAPI e Uvicorn) que o Flet utiliza para construir a ponte com o seu navegador!

??? tip "Por que utilizar o UV?"
    O `uv` gerencia o seu ambiente virtual automaticamente e é extremamente rápido na instalação de pacotes, garantindo que as dependências do projeto fiquem isoladas e não entrem em conflito com o seu Python global.

### 2. O Cérebro: `backend.py`

Crie um arquivo chamado `backend.py` na raiz do seu novo projeto. O backend expõe duas finalidades puras: a visualização (leitura) e o processamento de incrementos (escrita), armazenando a contagem temporária numa simples matriz em sua memória local volátil.

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

# Banco de dados simulado em memória
PLACAR = {
    "Flask": 0,
    "FastAPI": 0,
    "Flet": 0
}

@app.route('/api/votos', methods=['GET'])
def buscar_placar():
    """Via de regra: GET não altera o sistema, ele apenas consulta dados estritos e entrega o JSON"""
    return jsonify(PLACAR)


@app.route('/api/votar', methods=['POST'])
def registrar_voto():
    """Via de regra: POST recebe uma carga de informações novas (Payload JSON) e aciona a alteração interna do servidor"""
    dados = request.json
    tecnologia = dados.get('tecnologia')
    
    if tecnologia in PLACAR:
        PLACAR[tecnologia] += 1
        return jsonify({"sucesso": True, "mensagem": f"Voto para {tecnologia} computado!"})
    
    return jsonify({"sucesso": False, "mensagem": "Tecnologia não encontrada"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

??? tip "Por que a nossa API não usa CORS?"
    Se você já estudou aplicações Web tradicionais (como React ou Angular), deve conhecer os famosos bloqueios de segurança **CORS** (Same-Origin Policy) que ocorrem quando o navegador tenta enviar dados diretamente entre portas diferentes. No entanto, o **Flet atua como *Server-Driven UI***. Mesmo no Modo Web, quando um botão é clicado no navegador, ele apenas comunica o evento via *WebSocket*. Quem de fato formata a requisição e executa o `httpx.post` para a API Flask é o servidor Python (do Flet) rodando no fundo (uma conexão *Server-to-Server*). Dessa forma, a nossa API permanece segura, minimalista e 100% livre da dor de cabeça do `flask-cors`!

### 3. A Apresentação: `frontend.py`

Crie o arquivo `frontend.py` na mesma pasta do seu projeto. O script da Interface de Usuário (UI) não é capaz de modificar o placar sozinho, nem guarda os resultados de fato. O Flet simplesmente lê os dados remotos do Backend e constrói o cenário final na tela.

```python
# pylint: disable=no-member,unexpected-keyword-arg,too-many-function-args
import flet as ft
import httpx

API_URL = "http://localhost:5000/api"

async def main(page: ft.Page):
    page.title = "Enquete Tech"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 50

    texto_titulo = ft.Text("Qual a sua tecnologia favorita?", size=24, weight=ft.FontWeight.BOLD)
    coluna_placar = ft.Column(spacing=15)

    async def carregar_placar():
        """Busca assíncrona para não travar a tela (UI Thread) durante a Comunicação de Rede"""
        try:
            async with httpx.AsyncClient() as client:
                resposta = await client.get(f"{API_URL}/votos")
            dados = resposta.json()
            
            # Resetamos a tela de matriz visual atual para preencher a tabela realçada
            coluna_placar.controls.clear()
            
            for tecnologia, votos in dados.items():
                linha = ft.Row([
                    ft.Text(f"{tecnologia}: {votos} votos", size=18, expand=True),
                    # A injeção em "data" evita os alertas pesados do Pylint sobre variáveis de laços no Lambda
                    ft.Button(content="Votar", data=tecnologia, on_click=registrar_voto)
                ])
                coluna_placar.controls.append(linha)
                
            page.update()
        except Exception:
            coluna_placar.controls.clear()
            coluna_placar.controls.append(ft.Text("Erro ao conectar no banco/backend.", color="red"))
            page.update()

    async def registrar_voto(e):
        """Solicita a mudança estrutural de forma assíncrona garantindo total fluidez do click"""
        tecnologia = e.control.data
        try:
            async with httpx.AsyncClient() as client:
                resposta = await client.post(f"{API_URL}/votar", json={"tecnologia": tecnologia})
            dados = resposta.json()

            if dados.get("sucesso"):
                # Atualiza o placar somente se o voto foi aceito pelo servidor
                await carregar_placar()
            else:
                # Exibe a mensagem de erro retornada pela API
                page.show_dialog(ft.SnackBar(content=ft.Text(dados.get("mensagem", "Erro desconhecido"))))
        except Exception:
            page.show_dialog(ft.SnackBar(content=ft.Text(f"Falha de conexão ao votar em {tecnologia}")))

    # Layout estrutural primário
    page.add(texto_titulo, ft.Divider(), coluna_placar)
    
    # Renderizamos com a primeira carga efetiva
    await carregar_placar()

# Forçamos a interface a ser renderizada estritamente no Navegador (Web Mode)
ft.run(main, view=ft.AppView.WEB_BROWSER)
```

### 4. Executando a Aplicação

Como possuímos uma arquitetura separada, precisamos rodar a "Cozinha" e o "Cardápio" independentemente, abrindo **dois terminais distintos** na mesma pasta do projeto.

**Terminal 1 (Ligando o Backend):**
```bash
uv run backend.py
```
*(Opcional: você pode deixar este terminal minimizado, pois ele apenas registrará as requisições em texto)*

**Terminal 2 (Iniciando o Frontend):**
```bash
uv run frontend.py
```

Ao executar, o Flet será forçado a abrir estritamente no seu Navegador Web. O isolamento em duas vias fica evidente: como a nossa "Enquete Tech" se comunica por WebSockets debaixo dos panos com seu próprio servidor para blindar a API de banco de dados, caso a equipe crie o sistema Mobile amanhã para consumir a porta `5000`, o nosso `backend.py` não tomará conhecimento da mudança.

---
## De/Para: A Enquete vs Plataforma MergeSkills

Para solidificar o raciocínio, preste atenção em como essa estrutura compacta representa as engrenagens principais adotadas em nossa solução robusta do MergeSkills.

| Funcionalidade Prática | Esta Revisão (Enquete Tech) | Projeto Principal (MergeSkills) |
| :--- | :--- | :--- |
| **Ponto Base do Backend** | O servidor simples configurado em `backend.py`. | O registro detalhado no módulo e pacote core gerado no arquivo base `app.py`. |
| **Motor de Consulta (GET)** | A lista enxuta de placares da enquete. | As consultas rigorosas do catálogo, repassando listas massivas de cursos (`/courses`) e aulas ativas disponíveis. |
| **Motor de Escrita (POST)** | O modelo focado de somar um voto limpo (`/api/votar`). | A rota isolada e complexa de avanço e progresso do estudante acionada em conjunto ao responder (`/api/progress`). |
| **O Comunicador Httpx** | O arquivo `frontend.py` possui funções diretas chamando `httpx.get`. | O agrupamento consolidado focado em isolar lógica no arquivo exclusivo de pontes de rede modularizado em `api.py`. |
| **Interface e Reatividade** | A atualização em tempo real chamando `carregar_placar()` após validar as requisições puras e exatas. | O estado centralizado de transição robusto no arquivo `state.py`, mantendo e gerenciando os IDs carregados ativos. |

Note que a lógica raiz e central da comunicação não muda em absoluto. O que se expande dramaticamente é a segmentação modular (separar funções em vários arquivos organizando cada pedaço) e a introdução de camadas de persistência avançada (usando bancos via SQLAlchemy ao invés de variáveis isoladas de memória).

---
