# Revisão: Escalando com Vetores e NumPy

> A segunda parte do guia de revisão. Aqui, saímos das variáveis soltas e usamos o NumPy para avaliar múltiplos clientes de uma só vez, adicionando complexidade ao modelo que construímos previamente.

---

## O Novo Cenário do Banco

No primeiro notebook, nosso código funcionou com **um único** cliente, usando só **duas** informações (Renda e Histórico). 
Mas a vida real é mais complexa: um banco avalia milhares de pessoas por segundo, usando dezenas de informações para cada uma delas.

Se a gente quisesse apenas adicionar mais dois fatores (`idade_score` e `garantia`) mantendo a mesma técnica de antes, o código já começaria a ficar muito grande e repetitivo:
`z = (renda * p1) + (historico * p2) + (idade * p3) + (garantia * p4) + bias`.
Imagine fazer isso para 50 informações num mesmo formulário! Fica insustentável.

Para resolver esse problema e ganhar escala, deixamos as variáveis soltas de lado e usamos **Vetores** (listas numéricas simples) e **Matrizes** (tabelas de dados) usando o **NumPy**.

Assumindo que você ainda está na sua pasta mestre da revisão `revisao_perceptron`, crie um novo notebook chamado `revisao_numpy.ipynb`.

---

### Importando a Biblioteca e Novos Dados

O primeiro passo é importar o NumPy. Em seguida, vamos juntar os quatro pesos do nosso pequeno neurônio em uma única lista e manter o `bias` como um número solitário.

```python
import numpy as np

# Pesos (Weights) agora são um Vetor NumPy agrupado!
# Ordem da matriz: [Renda, Histórico, Idade, Garantia]
pesos = np.array([0.3, 0.8, 0.1, 0.5])

# Bias (Continua sendo apenas um número decimal constante)
bias = -9.0 # O banco ficou ainda mais restrito neste novo setor
```

??? tip "Por que usar arrays do `numpy` em vez de listas nativas do Python?"
    O NumPy compõe os cálculos em linguagem base em C, alocando os arrays de forma linear na memória. Operações com o `np.array` não trazem apenas uma abstração limpa do código ao ler o código, mas o arranjo as torna computacionalmente dezenas de vezes mais rápidas na validação do que uma estrutura iterativa clássica (`for`). 

---

### O Produto Escalar na Prática

Para testar com apenas um cliente usando Vetores, nós não criamos quatro variáveis isoladas. Nós simplesmente agrupamos as notas dele em uma única lista:

* Renda: `7.0`
* Histórico: `8.0`
* Idade_Score: `4.0`
* Garantia: `6.0`

```python
# Dados agrupados de UM cliente (Vetor X)
cliente_teste = np.array([7.0, 8.0, 4.0, 6.0])

# Cálculo da Soma Ponderada (Z) operado de forma simples via Produto Escalar (np.dot)
z = np.dot(cliente_teste, pesos) + bias

# Função Externa
decisao = 1 if z >= 0 else 0
print(f"O valor Z foi {z:.2f} | Decisão: {'Aprovado' if decisao == 1 else 'Reprovado'}")
```

??? tip "Relembrando: O que o `np.dot` faz?"
    O `np.dot` calcula o que chamamos de **Produto Escalar**. Ele pega o primeiro item do cliente e multiplica pelo primeiro peso, logo após pega o segundo item e multiplica pelo segundo peso, e assim por diante. No final, soma tudo.
    
    Em vez de você ter que digitar manualmente todas as contas:
    `soma = (7.0 * 0.3) + (8.0 * 0.8) + (4.0 * 0.1) + (6.0 * 0.5)`
    
    O comando `np.dot` resolve e soma todos esses valores para você de uma só vez em uma curta linha!

---

## O Poder do Lote (Batch Processing)

E se o terminal do Banco precisar avaliar o limite de **3 clientes simultâneos** de uma vez só?
Isso é fácil: nós agrupamos os perfis deles em **linhas de uma Tabela (Matriz)**. O genial de usar o NumPy é que ele consegue rodar o exato mesmo código para avaliar inúmeros clientes num tempo mínimo.

```python
# Tabela de Clientes agrupada - Cada linha é um cliente diferente
# Ordem das colunas: Renda, Histórico, Idade, Garantia
clientes_lote = np.array([
    [7.0, 8.0, 4.0, 6.0],  # Cliente A (Bom perfil geral)
    [3.0, 2.0, 5.0, 0.0],  # Cliente B (Risco alto, sem garantia de bens)
    [5.0, 5.0, 5.0, 10.0]  # Cliente C (Renda média, mas com ótima garantia)
])

# O NumPy calcula TODOS os clientes de uma vez, sem precisar de repetições e loops (ex: for)
Z_lote = np.dot(clientes_lote, pesos) + bias

# Testagem e Condensação
decisoes_lote = (Z_lote >= 0).astype(int)

# Saída Visual
for i, decisao in enumerate(decisoes_lote):
    status = "APROVADO" if decisao == 1 else "REPROVADO"
    print(f"Cliente {i+1} -> Z={Z_lote[i]:.2f} | Veredito: {status}")
```

Em vez de fazer um laço de repetição (`for`) lento no qual preveria um cliente por vez, o NumPy processa a matriz inteira de forma simultânea. Ele aplica a mesma lógica para as múltiplas linhas usando uma única operação, e então devolve todas as decisões consolidadas, demonstrando de fato como IAs conseguem ser computacionalmente velozes ao lidar com grandes lotes (batches).

## Empacotando o Perceptron em Lote (POO)

Assim como fizemos na aula passada sem bibliotecas, na vida real as empresas não deixam suas variáveis de NumPy soltas pelo código procedural. Elas sempre empacotam o neurônio numa **Classe** muito bem dividida.

Lá embaixo no seu arquivo de notebook, instancie uma Classe para representar nosso neurônio vetorizado. É essa estrutura isolada que as empresas usam em Produção.

```python
class PerceptronNumPy:
    def __init__(self, pesos, bias):
        # A classe guarda nossa "memória" de aprendizado vetorial
        self.weights = np.array(pesos)
        self.bias = bias
        
    def predict(self, matriz_clientes):
        # Processa todos os clientes graças ao np.dot
        z = np.dot(matriz_clientes, self.weights) + self.bias
        
        # 1. A condicional (z >= 0) testa os clientes e retorna booleanos (Ex: [True, False, True])
        # 2. O .astype(int) "As Type Integer" força a conversão para binários (Ex: [1, 0, 1])
        return (z >= 0).astype(int)
```

??? tip "O poder enxuto do `.astype(int)` na Função Degrau"
    Em vez de escrevermos um grande laço contendo `if / else` para avaliar se cada pessoa no dataframe passou, a simples avaliação `(z >= 0)` do NumPy cruza **todos** os clientes instantaneamente. O resultado, porém, é retornado inicialmente como respostas lógicas (`True` ou `False`). O método encadeado no final da linha, `.astype(int)`, age mapeando forçadamente os resultados booleanos para nosso tão esperado número real binário! Todo cliente `True` é convertido em `1` (Aprovado), e o `False` em `0` (Reprovado).

A grande vantagem disso é que agora testar dezenas de clientes em lote vira um processo imediato, com um código muito limpo! Na célula final, acione sua Classe para observar a avaliação:

```python
# 1. Instanciando nosso cérebro artificial vazio e carregando os conhecimentos
nosso_modelo = PerceptronNumPy(pesos=[0.3, 0.8, 0.1, 0.5], bias=-9.0)

# 2. Chamando a testagem e reaproveitando "clientes_lote" já criados antes
resultados = nosso_modelo.predict(clientes_lote)

print("Status Completo da Tabela Lote:", resultados)  
# Se a máquina operou perfeitamente, o print exibirá -> [1, 0, 1] 
# (Ou seja, de forma super rápida: Aprovado, Reprovado, Aprovado na ordem das cadeiras)
```

---

## De/Para: O Banco vs A Escala de Lote na API

Essa mesma lógica super flexível do Lote é exatamente a que usamos no código de Backend final em Python do nosso sistema FATEC para classificar e recomendar múltiplas músicas!

| Arquitetura em NumPy | Escopo do Banco | Projeto Base |
| :--- | :--- | :--- |
| **Ponto Clássico Base (Pesos)** | Atributo `self.weights = np.array([w1, w2...])` | Vetor `self.weights = np.array([0.8, 0.2])` |
| **A Múltipla Composição Completa (Batch)** | Matriz massiva `clientes_lote` cruzada inteira | Matriz `features_matrix` iterada de centenas de `request.tracks` unidos |
| **O Motor Cego do Coração Vetorial** | `Z = np.dot(clientes_lote, self.weights) + self.bias` | `Z = np.dot(X, self.weights) + self.bias` |
| **O Corte da Decisão Coletiva** | Veredito isolado `(Z >= 0).astype(int)` | Limiar de filtragem final `(Z >= 0.5).astype(int)` |


---

## Desafio Prático: Engenharia Reversa

Até agora só testamos clientes dentro do esperado. Mas a fundação de Aprendizado de Máquina não é feita apenas de acertos matemáticos da máquina, serve também para os devs entenderem os "pontos cegos" de seus próprios Pesos. 

No seu Jupyter, após o bloco do código do Lote (`clientes_lote`), adicione uma **nova célula exclusiva para esse teste de mesa**.

**Sua Missão como Analista de Fraudes:**

Crie um **Cliente D** em um pequeno lote e cruze-o com nossos pesos originais. O seu perfil será restritamente um "Perfil de Risco Crítico". 

As regras inquebráveis exigidas na construção dele são que você utilize:

- Histórico de pagador **zerado** (`0.0`), significando calotes contínuos.
- Sem nenhum bem de garantia (`0.0`).
- A "Idade Score" travada na média padronizada (`5.0`).

Sua pergunta como auditor: *É possível que a nossa Inteligência tão restritiva APROVE inocentemente esse estelionatário gerando um falso positivo no status?* 

**O seu desafio prático e avaliativo em sala hoje é manipular livremente a única variável que restou solta (a "Renda") dentro do cliente D!**
Tente ir alterando e rodando os testes, tentando "forçar" matematicamente para que o cálculo interno vetorizado cego no terminal ultrapasse a barreira dura que criamos no Bias de `-9.0` gerando um "Veredito: Aprovado"!

??? example "Gabarito: Por qual brecha o Cliente seria aprovado?"
    Se você iterou valores de Renda na tentativa até quebrar as travas e passar, percebeu que precisou jogar a nota de Renda dele lá nas alturas (algo como nota financeira irreal de `29.0` ou mais, fora da realidade de uma nota usual 0 a 10).
    
    **Qual principal lição de arquitetos percebida?**
    Como zeramos o Histórico de Pagamentos e as Garantias, o Perceptron perdeu boa parte de suas somatórias brutas. Porém, a equação linear pura (Produto Escalar) é, antes de tudo, uma máquina aritmética cega. Se você superestima desproporcionalmente uma variável (Renda vezes seu peso fraco de `0.3`), essa alta astronômica única compensará artificialmente os zeros de Histórico e o Bias impiedoso, forçando o limiar estourar em `Z >= 0`!
    
    A partir de agora, aprendemos um ensinamento que vai refletir nas próximas semanas: Nunca jogue métricas cruas, e sem limites de barreiras de formato ou normalização, diretamente no Modelo, caso contrário trapaceiros manipularão a Rede para obter avaliações favoráveis extremas!

---

## Exercícios de Fixação

> Ajuste todas as aulas e valide seu discernimento nestas perguntas cegas de NumPy e ML Vetorial.

<quiz>
Qual a grande justificativa em termos práticos de usarmos o `np.dot` no código base do neurônio em vez de multiplicar cada variável manualmente?

* [ ] O `np.dot` funciona nivelando as notas flutuantes (floats) para garantir que apenas números inteiros entrem na rede neural, prevenindo fraudes.
* [ ] Ele atua como a "Função de Ativação", convertendo os valores numéricos em status binários (`IF/ELSE`) operados pelo Scikit-Learn.
* [x] O comando `np.dot` é o coração da IA Vetorial. Ele cruza simultaneamente as características do cliente com os Pesos, multiplicando e somando tudo em uma única operação automática, dispensando cálculos longos e repetitivos manuais no código.
</quiz>

<quiz>
As Inteligências modernas jamais analisam um cliente por vez se puderem processar mil simultaneamente. O que o cálculo em Lote (Batch) permite na prática?

* [ ] Ele requer que a IA realize vários loops de repetição normais (ex: laços `for`), lendo os clientes um a um na memória, mas escondendo isso do programador.
* [x] Ele unifica os cálculos idênticos. O modelo empilha centenas de clientes em uma Tabela de Dados (Matriz Matemática) e dispara a avaliação contra os Pesos em uma única tacada vetorial e instantânea!
* [ ] O Machine Learning recorta apenas os números primários de cada cliente, avaliando metade do Lote isoladamente para não pesar o servidor e devolvendo erros parciais.
</quiz>

<quiz>
Montando arrays com NumPy: se a sua planilha fonte coloca a "Renda" na primeira coluna e a "Idade" na terceira, o que isso exige do nosso vetor de Pesos?

* [x] Exige lealdade posicional irrestrita. O vetor de "Pesos" (Weights) deve ter exatamente a mesma ordem das colunas para que a biblioteca cruze as linhas sem misturar: a Renda bate no Peso 1, a Idade bate no Peso 3.
* [ ] A ordem é puramente visual. Os algoritmos do NumPy conseguem ler as strings do DataFrame do Pandas, embaralhando internamente as posições via Nuvem para alinhar sem falhas no final.
* [ ] A ordem não importa, pois o modelo de Perceptron anula as Idades aleatoriamente, cruzando tudo pelo valor nativo de Bias durante o arrasto matricial no NumPy.
</quiz>

<quiz>
Por que Python processa matrizes via NumPy de forma muito mais imediata perante aos laços normais (For-Loops clássicos)? 

* [x] O NumPy é escrito na linguagem de baixo nível "C", além de usar matrizes que organizam a memória de forma contínua no computador. Isso gera a Vetorização: cálculos paralelos brutais inatingíveis rodando Python nativo puro.
* [ ] O NumPy, por padrão, roda apenas em Supercomputadores do Google Cloud, eliminando os fatores e entregando a precisão pela velocidade nativa exclusiva da internet local do usuário.
* [ ] Ao contrário de um código puro, laços limitados tradicionais no NumPy bloqueiam matematicamente clientes com notas negativas e ganham velocidade ao desprezá-los no vetor final escalonado em bloco.
</quiz>

<quiz>
Ao aplicarmos o comando limite `(Z_lote >= 0).astype(int)` em cima do saldo da rede neural em lote, o que estamos efetivamente concluindo no código base estrutural da resposta?

* [ ] Tem o mero desígnio funcional inútil visando cortar limpezas de casas decimais (arredondar) para a API exibir `flutuantes` perfeitos para o painel.
* [ ] Trabalha convertendo todos os numéricos abertos espalhados na matriz em `strings` brutas, as repassando para formatação textual final no Front-end Web.
* [x] Converte uma barreira condicional em números definitivos! Aplica uma restrição para testar as dezenas de saldos (`Z >= 0`), transformando imediatamente quem passou no limiar em número real estrito 1 (True/Aprovado) e quem falhou em estrito 0 (False/Reprovado), finalizando numa lista limpa como `[1, 0, 1]`.
</quiz>

<!-- mkdocs-quiz results -->
