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

Para isolar a lógica, elaboramos o projeto "Enquete Tech", com os arquivos disponíveis anexados junto a esta revisão. Todo o fluxo acontece entre apenas dois arquivos executáveis.

### O Cérebro: `backend.py`

O backend expõe duas finalidades puras: a visualização (leitura) e o processamento de incrementos (escrita), armazenando a contagem temporária numa simples matriz em sua memória local volátil.

```python
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Essencial para permitir requisições seguras partindo do Frontend
CORS(app)

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

??? tip "Por que o CORS (Cross-Origin Resource Sharing)?"
    Os navegadores implementam blocos nativos de segurança que evitam que uma página Web qualquer tente solicitar informações sigilosas de um Backend alocado em um "domínio" diferente sem a devida permissão formal do destino. A biblioteca `flask_cors` cria a credencial explícita na configuração permitindo que a interface se conecte e converse via HTTP.

### A Apresentação: `frontend.py`

O script de UI não é capaz de modificar o placar sozinho, nem guarda os resultados de fato. O Flet simplesmente lê o resultado do Backend e constrói o cenário final.

```python
import flet as ft
import httpx

API_URL = "http://localhost:5000/api"

def main(page: ft.Page):
    page.title = "Enquete Tech"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 50

    texto_titulo = ft.Text("Qual a sua tecnologia favorita?", size=24, weight="bold")
    coluna_placar = ft.Column(spacing=15)

    def carregar_placar():
        """Busca os votos originais consolidados que residem unicamente no Backend (Comunicação de Rede)"""
        try:
            resposta = httpx.get(f"{API_URL}/votos")
            dados = resposta.json()
            
            # Resetamos a tela de matriz visual atual para preencher a tabela realçada
            coluna_placar.controls.clear()
            
            for tecnologia, votos in dados.items():
                linha = ft.Row([
                    ft.Text(f"{tecnologia}: {votos} votos", size=18, expand=True),
                    ft.ElevatedButton("Votar", on_click=lambda e, t=tecnologia: registrar_voto(t))
                ])
                coluna_placar.controls.append(linha)
                
            page.update()
        except Exception:
            coluna_placar.controls.clear()
            coluna_placar.controls.append(ft.Text("Erro ao conectar no banco/backend.", color="red"))
            page.update()

    def registrar_voto(tecnologia):
        """Solicita a mudança estrutural delegando todo o serviço e carga técnica via POST"""
        try:
            httpx.post(f"{API_URL}/votar", json={"tecnologia": tecnologia})
            # A base de Reatividade: Os dados foram alterados no roteador do Backend. Logo, exigimos que a tela reflita isso:
            carregar_placar()
        except Exception:
            page.snack_bar = ft.SnackBar(ft.Text(f"Falha ao votar em {tecnologia}"))
            page.snack_bar.open = True
            page.update()

    # Layout estrutural primário
    page.add(texto_titulo, ft.Divider(), coluna_placar)
    
    # Renderizamos com a primeira carga efetiva
    carregar_placar()

ft.app(target=main)
```

O isolamento é evidente: A nossa "Enquete Tech" poderia rodar um aplicativo Web com Flet, mas amanhã uma equipe poderia lançar um sistema em Android utilizando Kotlin e consumir o exato mesmo endpoint na porta `5000`, e o `backend.py` nem sequer perceberia a mudança de dispositivos.

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

## Exercícios de Fixação

> Valide o seu entendimento abordando o processo lógico de separação das responsabilidades.

??? example "Verificando o Entendimento"
    **Os questionários não avaliam a escrita pura do código, mas os conceitos arquiteturais fundamentais suportados pelo modelo de desenvolvimento explorado.**

    <quiz>
    A analogia do "Restaurante" aborda as camadas focadas do ambiente Fullstack. O que aconteceria conceitualmente num projeto web tradicional caso tentássemos unir a Cozinha junto à Mesa (Processamento de Banco atrelado à Interface Gráfica no mesmo código fonte) no caso do MergeSkills?

    * [ ] A arquitetura base aumentaria severamente sua performance final de repasse nas nuvens de matrizes JSON interligadas por Blueprints.
    * [x] Perderíamos a escalabilidade técnica e flexibilidade multiplataforma. Ao compilar a interface de um aparelho atrelada totalmente aos acessos críticos e lógicas locais de persistência de dados, quebraríamos a capacidade de fornecer aqueles dados para outros frontends isolados, gerando grandes conflitos diretos nos registros do sistema.
    * [ ] O ambiente seria isolado e o CORS modular fecharia as portas, obrigando a equipe central a estruturar inteiramente os blocos REST e as renderizações de imagens pelo HTTP GET sem nenhuma alteração profunda na estrutura original dos arquivos Flet.
    </quiz>

    <quiz>
    Quando o Flet inicia em tela e precisa mostrar aos alunos o total do placar de enquetes (ou uma listagem ativa complexa de novos Cursos disponíveis na plataforma), qual tipo de método HTTP e padrão informacional o Flet usaria prioritariamente em uma comunicação profissional restrita?

    * [x] Ele formula e despacha amplamente uma solicitação central com o método `GET` na URL do Flask, aguardando que o Backend responda adequadamente com um Payload contendo todos os dados já enpacotados e definidos no padrão limpo de entrega em `JSON`.
    * [ ] Ele formula diretamente um registro `POST` no endpoint HTTP enviando comandos puros em SQL (estruturados via Dicionários Voláteis do próprio Numpy embutido) garantindo assim alterações definitivas automáticas rápidas da memória original do Flask.
    * [ ] O Frontend não utiliza as chamadas do método convencional HTTP para apresentar dados na inicialização de sessão. Ele requer essencialmente uma requisição assíncrona bruta interligada puramente por comandos do Alembic que renderizam a lista visual e formatam as colunas Flet com suporte de CORS ativado.
    </quiz>

    <quiz>
    A principal utilidade de se adotar a formatação de pacotes do modelo `JSON` na transferência de requisições HTTP entre o `backend.py` e o `frontend.py` é essencialmente:

    * [ ] Bloquear invasões estruturadas que simulam acessos nativos, mantendo arquivos Python fortemente compactados baseados exclusivamente em modelos encapsulados restritos nativos da camada base do Postgres.
    * [ ] Forçar a conversão obrigatória das imagens locais do Frontend e traduzi-las instantaneamente para strings hexadecimais legíveis mantendo suporte nativo fixo com os dicionários clássicos nativos originais fechados em redes e sessões no Flet.
    * [x] Atuar com um formato comum e agnóstico como padrão internacional. Ele garante que qualquer elemento e estrutura local da origem (como a lista isolada de dicionários do Python e variáveis primitivas int/float) sejam legíveis do outro lado exato na base do Destino mantendo a fidelidade das informações trocadas.
    </quiz>

    <quiz>
    Na "Enquete Tech" ou mesmo durante as validações ativas de progresso da API no MergeSkills, nós delegamos as solicitações via funções Httpx ativando a reatividade forçada nas telas locais das máquinas locais (ex: `page.update()`). Por que isso é determinante para gerar interações fluidas do aluno com o sistema no Flet?

    * [ ] Porque as bibliotecas Flet interligam automaticamente todas as memórias primárias cruas remotas de qualquer serviço Flask rodando localmente no banco, desativando o botão temporariamente sempre que os acessos puramente restritos são rejeitados de imediato por erros clássicos originais no sistema sem qualquer uso manual de UI puro.
    * [x] Porque sem a ordem ativa de reestruturar visualmente e atualizar formalmente a tela no Flet e nas views após a busca bem-sucedida de rede remota os valores seriam efetivamente processados na nuvem e salvos no servidor remoto mas a UI se manteria fixa em seu estado original anterior, deixando o usuário cego na aplicação sem respostas sensoriais e validações ativas.
    * [ ] Pelo fato isolado central de que toda conexão limpa do método POST HTTP do Frontend atua de maneira assíncrona forçando um redirecionamento forçado fechado e absoluto para Blueprints e endpoints da web centralizados recarregando inteiramente todo o app nativo inicial do zero novamente bloqueando acessos originais clássicos de toda rede em ambientes multiplataformas locais curtos nativos.
    </quiz>

    <quiz>
    Durante nossos testes da plataforma nativa, percebemos que o sistema não guardava os placares se ocorresse o simples reiniciar estrito do terminal do nosso arquivo puramente isolado `backend.py`. Qual das explicações detalha fundamentalmente essa situação estrita do projeto do laboratório básico?

    * [ ] A rota `POST` que processa a contagem de votos da votação possuía erros clássicos lógicos nativos e rejeitava nativamente sempre os arquivos JSON contendo valores inválidos soltos fechados fixos.
    * [x] As modificações dos contadores efetuadas pelo algoritmo agiram ativamente e alteraram uma variável primitiva unificada (`PLACAR`) armazenando na matriz volátil puramente carregada da memória RAM local temporária da execução base da linguagem da aplicação Python.
    * [ ] O frontend falhou integralmente no cruzamento da interface no momento forçado base quando as transações nativas unificadas do método httpx limitavam envios constantes contínuos ao endpoint do estado primário do Swagger e apagavam a memória nativa.
    </quiz>

<!-- mkdocs-quiz results -->

