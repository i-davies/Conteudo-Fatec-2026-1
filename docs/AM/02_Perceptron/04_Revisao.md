# Revisão: O Perceptron

> Um roteiro isolado do projeto principal, focado puramente em fixar a matemática e a lógica do neurônio artificial utilizando Jupyter Notebook.

---

## Preparando o Ambiente

Para o conceito ficar bem claro, vamos deixar a nossa API de lado por um momento. Vamos construir um Perceptron simples e do zero, usando apenas Python básico no **Jupyter Notebook**.

Crie uma nova pasta no seu sistema chamada `revisao_perceptron` e abra-a no seu editor de código (como o VS Code).

Agora precisamos inicializar o motor de dependências. Acesse o **Terminal Integrado** e rode estes comandos:

```bash
uv init

uv add ipykernel notebook
```

Tudo pronto! Crie um novo arquivo chamado `revisao_perceptron.ipynb` dentro dessa pasta e escolha o ambiente `.venv` recém gerado como o Kernel (motor de execução).

---

## O Problema: Aprovação de Crédito

Imagine que precisamos criar um neurônio para um banco decidir se vai **Aprovar (1)** ou **Reprovar (0)** o limite de crédito de um cliente.

Ele vai analisar somente duas informações do cliente:

1. **Renda Mensal** (valores de 0 a 10, representando faixas salariais).
2. **Histórico de Pagamento** (nota de 0 a 10, onde 10 é um excelente pagador).

---

### Definindo as Entradas no Notebook

No seu notebook recém-criado, digite o código abaixo na primeira célula e execute para definir o nosso cliente de teste:

```python
# Entradas (Features) do cliente que estamos avaliando
renda_mensal = 6.0
historico_pagador = 5.0

print(f"Analisando Cliente -> Renda: {renda_mensal} | Histórico: {historico_pagador}")
```

---

### A Política do Banco (Pesos e Bias)

Agora precisamos parametrizar a "exigência" do banco. Para a instituição, o histórico de bom pagador importa muito mais do que a renda mensal em si.

Crie uma nova célula abaixo da anterior e digite:

```python
# Pesos (Weights)
peso_renda = 0.3      # Importante, mas não decisivo isoladamente
peso_historico = 0.8  # Peso massivo no histórico financeiro

# Bias (A resistência natural em emprestar dinheiro)
# Um valor negativo que funciona como um "obstáculo", dificultando a aprovação caso o cliente tenha notas muito baixas.
bias = -7.0
```

??? tip "A Função do Bias"
    O bias negativo (`-7.0`) atua como uma barreira que o cliente deve obrigatoriamente superar pelo somatório das suas notas. Se o bias fosse zero, qualquer pessoa com renda e histórico mínimos passaria, o que causaria um risco enorme de prejuízo ao banco.

---

### A Combinação Linear

Agora o neurônio vai juntar essas informações. Ele pega as notas, multiplica pelos pesos e soma tudo para gerar um valor final.

```python
# Cálculo Z (Equação da Decisão)
z = (renda_mensal * peso_renda) + (historico_pagador * peso_historico) + bias

print(f"O valor interno gerado pelo Perceptron (Z) foi: {z:.2f}")
```

Se você executar, a conta será: `(6.0 * 0.3) + (5.0 * 0.8) - 7.0 = 1.8 + 4.0 - 7.0 = -1.2`.
O resultado deu negativo. Ou seja, até agora a tendência é o crédito ser negado.

---

### A Decisão Final (Degrau)

O Perceptron precisa tomar uma decisão final fixa: **sim (1)** ou **não (0)**. Não existe "meio aprovado". Para isso ele usa uma regra simples (chamada de Função de Ativação Degrau): se o valor Z for maior ou igual a zero, a resposta é 1. Se não, é 0.

Crie a quarta célula:

```python
# Função de Ativação (Degrau / Step)
if z >= 0:
    decisao = 1
    motivo = "Aprovado! O perfil atendeu às exigências do banco."
else:
    decisao = 0
    motivo = "Reprovado. Risco de crédito muito alto."

print(f"Decisão Final: {decisao}")
print(f"Veredito: {motivo}")
```

Execute a célula. Como esperado, o retorno será **Reprovado**.

---

## Modificando Cenários em Tempo Real

A grande vantagem de entender o Perceptron no Jupyter Notebook é a capacidade de alterar o ambiente e reenviar os dados com agilidade.

Volte na **Primeira Célula** (que define as entradas), altere os dados do cliente e rode **todas as células novamente** (você pode utilizar o atalho da sua plataforma para executar tudo de uma vez).

Analise o comportamento do Perceptron para os seguintes perfis:

1. **O Cliente que ganha muito, mas não paga ninguém:**
   * Renda Mensal: `10.0`
   * Histórico Pagador: `2.0`
   * *Resultado esperado: Qual vai ser o veredito?*

2. **O Cliente que ganha o mínimo, mas é rigoroso com as dívidas:**
   * Renda Mensal: `2.0`
   * Histórico Pagador: `10.0`
   * *Resultado esperado: Qual vai ser o veredito?*

??? tip "Como as máquinas aprendem?"
    Neste exemplo de revisão, **nós** atuamos como o banco e escolhemos manualmente os melhores números para os Pesos e Bias. Quando começarmos a estudar modelos de regressão, você perceberá que o verdadeiro "Aprendizado de Máquina" ocorre quando fornecemos mil casos de clientes passados para o computador e pedimos para que o próprio algoritmo faça tentativas cegas até "descobrir" sozinho que o peso ideal do histórico é `0.8` e o Bias ideal é `-7.0`.

---

## Empacotando em uma Classe (Orientação a Objetos)

Até o momento, nossas variáveis de pesos e rendas continuam soltas ao longo das células. Para que no mundo real uma aplicação "importe" o nosso modelo, a melhor prática é guardá-lo numa **Classe** bem organizada!

Lá embaixo no seu arquivo de notebook, instancie uma Classe para representar nosso neurônio. É essa estrutura isolada que as empresas usam em Produção.

```python
class PerceptronSimples:
    def __init__(self, peso_renda=0.3, peso_historico=0.8, bias=-7.0):
        # O neurônio já nasce com suas regras e limites padrão gravados na memória
        self.peso_renda = peso_renda
        self.peso_historico = peso_historico
        self.bias = bias
        
    def prever(self, renda, historico):
        # A famosa Combinação Linear (Z) atuando nos bastidores
        z = (renda * self.peso_renda) + (historico * self.peso_historico) + self.bias
        
        # A Função Degrau decide com base puramente na meta do Z>=0
        if z >= 0:
            return "Aprovado"
        else:
            return "Reprovado"
```

A grande vantagem disso é que agora testar clientes vira um processo imediato, com um código muito limpo! Na célula final, acione sua Classe para observar a avaliação:

```python
# Colocando o "Cérebro" para funcionar
analista_automatico = PerceptronSimples()

# O código ficou fácil de usar para testes rápidos!
resultado_ana = analista_automatico.prever(renda=7.0, historico=8.0)
print(f"Cliente Ana: {resultado_ana}")  # Deve aprovar

resultado_pedro = analista_automatico.prever(renda=2.0, historico=3.0)
print(f"Cliente Pedro: {resultado_pedro}")  # Risco de crédito

resultado_lucas = analista_automatico.prever(renda=8.0, historico=5.0)
print(f"Cliente Lucas: {resultado_lucas}")  # Reprova (A renda não compensou o histórico na matemática do banco)
```

---

## De/Para: O Banco vs A API de Músicas

Para consolidar o conhecimento, veja como essa exata matemática do notebook de revisão se traduziu na prática para o nosso projeto principal de recomendação do Spotify:

| Lógica Computacional | Esta Revisão (Aprovação de Crédito) | Projeto Principal (Recomendador Musical) |
| :--- | :--- | :--- |
| **Entradas (Features)** | `renda` (0 a 10) e `historico` (0 a 10) | `energy` (0.0 a 1.0) e `loudness_norm` (0.0 a 1.0) |
| **Pesos (Weights)** | Renda (`0.3`) e Histórico (`0.8`) | Energy (`0.8`) e Loudness (`0.2`) |
| **Bias** | Dificulta a aprovação financeira (`-7.0`) | Viés de cálculo inicial (`+0.1`) |
| **Z (Cálculo Numérico)** | Z = (Renda * 0.3) + (Histórico * 0.8) - 7.0 | Z = (Energy * 0.8) + (Loudness * 0.2) + 0.1 |
| **Função de Ativação** | Se **Z >= 0**, resulta em 1. Se não, 0 | Se **Z >= 0.5**, resulta em 1. Se não, 0 |
| **Decisão (Saída)** | **1** (Aprovado) ou **0** (Reprovado) | **1** (Música de Festa) ou **0** (Música Relax) |

Note que o código e a parte matemática formam um modelo **idêntico**! A única coisa que mudou foi o assunto dos dados (Banco vs Música) e os pesos de cada um.

---

## Exercícios de Fixação

> Valide o seu entendimento respondendo aos questionamentos abaixo:

<quiz>
Na aula em que nos inspiramos na biologia, vimos que o Perceptron é a fundação da IA moderna. Qual destas definições melhor o descreve de forma didática?

* [ ] Um algoritmo clássico profundo focado exclusivamente em agrupar lotes estatísticos e gerar imagens neurais.
* [x] É o modelo pioneiro e mais simples de um neurônio artificial. Ele foi projetado matematicamente para analisar entradas e devolver uma decisão estrita e binária (0 ou 1).
* [ ] Um banco de vetores utilizado apenas para armazenar e enfileirar pesos no cache do NumPy.
</quiz>

<quiz>
Qual a grande diferença de base de um projeto criado com um Perceptron comparado a um sistema bancário tradicional inteiro em Python?

* [x] Em sistemas clássicos, inserimos as regras (IF/ELSE) para que o computador devolva as respostas. No Machine Learning, inserimos dados passados para que o próprio computador descubra as regras.
* [ ] A programação clássica requer variáveis numéricas sólidas. O Machine Learning elimina o uso de Matemática, apostando em modelos biológicos puramente orgânicos via Nuvem.
* [ ] O Machine Learning não depende de fase de testes manuais, pois a linguagem gera automaticamente todos os dados simulados dentro do código.
</quiz>

<quiz>
Quando analisamos o banco (ex: *Renda* e *Histórico*) ou repassamos de fato uma nova música na API (ex: *Energia* e *Volume*), o que essas Entradas (Features) representam para o nosso modelo?

* [ ] Elas definem os limites de ativação (o valor mínimo que a resposta final tem que ultrapassar para aprovar).
* [ ] Consistem na resposta final ou gabarito do histórico retornado, ou seja, o status rotulado final se a pessoa foi ou não aprovada no sistema.
* [x] Elas consistem na raiz do nosso problema. São as variáveis puras coletadas diretamente do mundo real. É aquilo que inserimos diretamente para o neurônio começar sua etapa analítica diária.
</quiz>

<quiz>
Toda Entrada que chega ao neurônio passa por uma multiplicação imposta pelo seu "Peso" pareado. Qual é a razão prática desses Pesos existirem internamente no algoritmo?

* [ ] Eles funcionam como o "limite teimoso" principal que a máquina usa visando frear sumariamente a aprovação de contas de clientes, o conhecido preconceito nato natural fixo e impiedoso (Geralmente restringe os testes travado negativamente nativamente isolado limitador e freia nativamente para -7.0 de Bias cravado na modelagem inteira original sem auxílio estático manual sem perdas de escala da base sem sentido algum dos blocos).
* [x] O Peso atua como o grau de "prioridade e importância". Ele calibra quanto determinada Entrada (como por exemplo o "Histórico") irá dominar matematicamente a avaliação final acima das outras (ex: a "Renda").
* [ ] É o filtro da saída matemática total do Jupyter que aglutina puramente o placar unificado "Y" num valor esparso "Sinal 1" para finalizar.
</quiz>

<quiz>
Passada a conta dos multiplicadores, nós notamos sempre no final a presença fixa do Bias (Como o `bias = -7.0` que criamos para o banco). Qual a tradução dele para a nossa IA?

* [ ] O Bias mapeia puramente qual foi a devida margem residual matemática de "Erro" solto que a validação clássico inicial de base original unificada alcançou sem ajuda nos treinos do Numpy originais sem erros.
* [x] Ele age fundamentalmente feito uma "Barreira Física", o verdadeiro grau de bloqueio rígido isolado do sistema base. Todos os outros pacotes que processaram em Z tem que trabalhar ativamente superando a oposição isolada dele.
* [ ] Ele se comporta ativamente igual uma Feature oculta vinda da extração sem dados passados do Numpy (como Renda fantasma), funcionando repetidas incontáveis da raiz nula pra multiplicar limites errados velhos puros de todo cruzando e retornando ao modelo base do Jupyter e as antigas clássicas primitivos curtas originais limitadas originais primitivas originais velhas.
</quiz>

<quiz>
Iniciada a jornada da avaliação, o neurônio realiza uma grande conta para gerar um veredito numérico temporário (a "nota Z"). Como atua essa Combinação Linear nos bastidores?

* [ ] O algoritmo eleva as Entradas ao quadrado e divide pelo Viés, equalizando clientes que possuem salários fora de escala no banco.
* [x] Ela multiplica cada Entrada pelo seu respectivo Peso, soma todos esses pedaços juntos e, por fim, adiciona o valor absoluto do Bias.
* [ ] O algoritmo corta o valor das Entradas pela metade caso elas ultrapassem a "nota Z", evitando que o modelo aprove fraudes.
</quiz>

<quiz>
No mundo laboratório das simulações, você testou um cliente e, cruzando as rendas e dívidas nos cálculos matemáticos, incrivelmente a "Nota final Z" zerou (Z = `0.0`). O que a Função de Ativação Degrau decidirá sobre ele na nossa lógica base?

* [x] O cliente será "Aprovado" (Sinal 1). A regra condicional básica da Função Degrau exige puramente que o Z seja MAIOR ou IGUAL a zero (`Z >= 0`) para disparar aprovação.
* [ ] O cliente será sumariamente "Reprovado" (Sinal 0). No Machine Learning, é exigido estritamente que a nota Z supere o zero, exigindo valores puramente positivos (`Z > 0`).
* [ ] Ocorrerá um empate numérico. O sistema retornará um valor vazio (`Null`) para a API, pedindo revisão manual.
</quiz>

<quiz>
**O Propósito da Função de Ativação**
(como a nossa Degrau/Step). Qual é a principal utilidade dela em sistemas estritos de classificação?

* [ ] Transformar os números do backend em formatos textuais de linguagem humana (strings JSON) para que a API consiga ler os dados na tela do celular.
* [ ] Agir como um balanceador contínuo de matrizes. Ela pega notas muito negativas e zera apenas para evitar que nossa base SQL sofra penalidades estatísticas.
* [x] Atuar como um "interruptor" decisório cego e sem meio-termos. Ela pega a pontuação matemática fragmentada e a converte forçadamente em uma categoria final exata: "Reprovado" (Sinal 0) ou "Aprovado" (Sinal 1).
</quiz>

<!-- mkdocs-quiz results -->
