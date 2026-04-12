# Revisão: Escalando com Vetores e NumPy

> A segunda parte do guia de revisão. Aqui, saímos das variáveis soltas e usamos o NumPy para avaliar múltiplos clientes de uma só vez, adicionando complexidade ao modelo que construímos previamente.

---

## O Novo Cenário do Banco

No primeiro notebook, nosso código funcionou super bem para **um único** cliente, usando só **duas** informações (Renda e Histórico). 
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

---

## De/Para: O Banco vs A Escala de Lote na API

Essa mesma lógica flexível do Lote é a que usamos no código de Backend em Python do nosso sistema para classificar e recomendar múltiplas músicas!

| Arquitetura em NumPy | Escopo do Banco  | Projeto Base (`03_Vetores_Matrizes_NumPy.md`) |
| :--- | :--- | :--- |
| **Ponto Base (Pesos)** | Vetor `pesos = np.array([w1, w2, w3, w4])` | Vetor `self.weights = np.array([0.8, 0.2])` |
| **Entrada Limitada (Isolada)** | Matriz em array: `np.array([7, 8, 4, 6])` | Acomodação em vetor: `X = np.array([energy, loudness_norm])` |
| **Composição Completa (Batch)** | Matriz `clientes_lote` (matriz de perfis independentes) | Matriz `features_matrix` gerado de todos `request.tracks` (canções simultâneas em array bidimensional) |
| **Engrenagem Matemática** | `Z = np.dot(clientes_lote, pesos) + bias` | `Z = np.dot(X, self.weights) + self.bias` |
| **Eixo Condicional/Decisão** | Regra condensada `(Z >= 0).astype(int)` | Limiar de API `(Z >= 0.5).astype(int)` |

---

## Exercícios de Fixação

> Ajuste as células acima e avalie para solidificar a matéria vetorial.

<quiz>
Por que abandonamos os blocos convencionais do Python (`for` ou `while()`) em favor do interposto `np.dot` visando escalar um Perceptron?

* [ ] Porque listas normais do Python não interagem com matrizes grandes.
* [x] Porque o NumPy roda o código pesado da física/matemática dos dados usando o processamento super otimizado na linguagem C nos bastidores. Ele encurta dramaticamente o tempo de processamento nas empresas atuais.
* [ ] Devido às exigências de que não podemos somar valores com pontos.
</quiz>



<quiz>
Na Matriz de teste que usamos em nosso Lote (Batch), a segunda linha é dedicada ao "Cliente B". Na hora que o `np.dot` vai fazer o cálculo do Produto Escalar da Idade deste cliente, que ação exata ocorre nos bastidores?

* [x] Ele pega o número que está na 3ª coluna de dados do cliente B (Idade = 5.0) e multiplica pelo exato número que está também na 3ª posição lá no vetor de Pesos (Peso da Idade = 0.1).
* [ ] Ele bagunça a idade e multiplica ela aleatoriamente pelos quatro pesos.
* [ ] Ele anula a divisão.
</quiz>



<quiz>
Avaliando a performance real, se a agência do banco escalar e pedir para nossa matriz "pular" de 3 clientes para incríveis **100.000 clientes simultâneos**, o que acontecerá com o nosso script do NumPy?

* [ ] O código Python vai parar, pois o `np.dot` foi feito no máximo para 100 alunos.
* [x] O NumPy vai injetar tudo numa enorme matriz e multiplicar os dados na mesma batida, devolvendo a lista unificada com os 100.000 vereditos de aprovação ser sofrer grande impacto de velocidade.
* [ ] O NumPy terá que virar um loop `for` temporário para processar cada pessoa individualmente.
</quiz>

<!-- mkdocs-quiz results -->
