# Do Neurônio Biológico ao Perceptron Artificial

> Material didático para a Semana 02 de AM, explorando a transição da biologia para a engenharia de software.
> 
> 
> Projeto utilizado: [Visualização da Fronteira de Decisão (Google Colab)](https://colab.research.google.com/drive/1Mj4tYfBgvWIvk2PSUZCuEQvhoZeZ4e9c).

---

## Slides

<div style="position: relative; width: 100%; height: 0; padding-top: 56.2500%;
 padding-bottom: 0; box-shadow: 0 2px 8px 0 rgba(63,69,81,0.16); margin-top: 1.6em; margin-bottom: 0.9em; overflow: hidden;
 border-radius: 8px; will-change: transform;">
  <iframe loading="lazy" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0; border: none; padding: 0;margin: 0;"
    src="https://www.canva.com/design/DAHBWd6bfvg/tc8toHsJ568jsRRxVNvbuQ/view?embed" allowfullscreen="allowfullscreen" allow="fullscreen">
  </iframe>
</div>
<a href="https:&#x2F;&#x2F;www.canva.com&#x2F;design&#x2F;DAHBWd6bfvg&#x2F;tc8toHsJ568jsRRxVNvbuQ&#x2F;view?utm_content=DAHBWd6bfvg&amp;utm_campaign=designshare&amp;utm_medium=embeds&amp;utm_source=link" target="_blank" rel="noopener">03</a> de Icaro Davies

## Do estímulo à decisão

!!! info "Objetivos"
    * Entender o funcionamento básico do cérebro humano como inspiração para a IA.
    * Compreender os conceitos de estímulo, soma e limiar de disparo.

O cérebro possui cerca de **86 bilhões de neurônios**. Eles funcionam como acumuladores de sinais: não disparam por qualquer motivo.

* 
**Entrada**: Recebe estímulos externos como visão, som ou cheiro.


* 
**Soma (Corpo Celular)**: O neurônio acumula a intensidade desses sinais elétricos.


* 
**Disparo**: Se a soma ultrapassar um **limiar (threshold)**, o sinal é transmitido ao próximo neurônio.



---

## 1958: O primeiro neurônio artificial

!!! abstract "O Nascimento do Perceptron"
Em 1958, Frank Rosenblatt propôs transformar esse comportamento biológico em um modelo matemático. A revolução foi parar de programar regras fixas e permitir que o sistema aprendesse ajustando **parâmetros**.

Embora existam outras linhagens de IA (como sistemas especialistas ou algoritmos genéticos), quase toda a **IA Generativa** atual (Claude, GPT, Gemini) descende diretamente do Perceptron.

---

## A Anatomia do Neurônio Artificial

!!! info "Objetivos"
    * Identificar os componentes matemáticos de um Perceptron.
    * Aplicar a fórmula da combinação linear para tomada de decisão.

### A Equação da Decisão

Dentro de cada neurônio artificial, ocorre uma soma ponderada dos estímulos de entrada:

$$
z = \sum_{i=1}^{n} (w_i \cdot x_i) + b
$$

ou de forma mais simples:

$$
z = (x_1 \cdot w_1) + (x_2 \cdot w_2) + \dots + b
$$



Onde:

* 
**Entradas ($x$):** Os estímulos ou dados brutos.


* 
**Pesos ($w$):** O ajuste de importância de cada entrada.


* 
**Bias ($b$):** O limiar de ativação ou "preço" para o neurônio dizer "sim".



### Função de ativação(Função Degrau)

A decisão final ($y$) é binária (0 ou 1) baseada no valor de ($z$):

* Se $z \geq 0 \rightarrow y = 1$   (**Ativado**).


* Se $z < 0 \rightarrow y = 0$   (**Desativado**).



---

## Exemplo Prático: O Dilema da Festa

Imagine que você avalia dois estímulos para decidir se sai de casa:

1. **Amigos ($x_1$):** Eles vão? (1 para sim, 0 para não).
2. **Chuva ($x_2$):** Está chovendo? (1 para sim, 0 para não).

**Sua Personalidade (Parâmetros):**

* **Peso dos Amigos ($w_1$):** Muito importante.
* **Peso da Chuva ($w_2$):** Te desanima, mas não anula os amigos.
* **Preguiça (Bias $b$):** Sua resistência natural para sair do sofá.

> **Cenário:** Seus amigos vão ($x_1 = 1$) e está chovendo ($x_2 = 1$).
> 
> $(1 \cdot 10) + (1 \cdot -5) - 2 = 3$
> 
> Como $3 \geq 0$, a decisão é **Vou à festa!** Mesmo com chuva, o desejo de ver os amigos superou o desânimo e a preguiça.

---

## A Geometria da Decisão: "A Dança da Reta"

O Perceptron atua como um separador de classes (ex: Cães vs. Gatos) em um gráfico.

* 
**Pesos ($w$):** Controlam a **inclinação** da reta (girando a régua).


* 
**Bias ($b$):** Controla a **posição** da reta (empurrando-a para frente ou para trás).



Tens toda a razão! Faltaram as variáveis matemáticas na frase e o conceito de "ajuste automático", que é o que realmente diferencia o aprendizado da programação tradicional.

Aqui está uma versão corrigida e mais técnica para o teu material:

---

### O que significa "Aprender"?

!!! abstract "A Essência do Aprendizado"


**Aprender em Aprendizado de Máquina** é o processo de ajustar automaticamente os **Pesos** ($w$) e o **Bias** ($b$) para encontrar a **fronteira de decisão** (reta) que melhor separa os dados com o menor erro possível.

Em vez de um humano escrever uma regra estrita , o algoritmo utiliza a **Experiência (E)** para "calibrar" esses parâmetros matemáticos até que o **Modelo** consiga tomar decisões precisas sozinho.


---

## Exercícios de Fixação

> Responda às questões abaixo para consolidar a lógica do neurônio artificial.

<quiz>
Se o Bias ($b$) de um neurônio for um valor positivo muito alto (ex: +100), como ele se comportará?

* [ ] Será um neurônio "exigente", que raramente dispara.
* [x] Será um neurônio "empolgado", que dirá SIM para quase qualquer entrada.
* [ ] Ele não terá impacto na decisão final.
</quiz>

<quiz>
No "Dilema da Festa", se mudarmos o peso da chuva ($w_2$) de -5 para -15, o que acontece?

* [ ] Você passa a gostar mais de chuva.
* [x] Você fica mais desanimado com a chuva, tornando mais difícil sair de casa.
* [ ] A chuva deixa de ter importância no cálculo.
</quiz>

<quiz>
Qual é a função dos Pesos ($w$) na geometria do Perceptron?

* [ ] Mover a reta para frente ou para trás sem mudar o ângulo.
* [x] Controlar a inclinação da fronteira de decisão (reta).
* [ ] Definir o valor das entradas brutas.
</quiz>

## Prática

Acesse o **Google Colab** para visualizar como a alteração manual de pesos e bias move a fronteira de decisão em tempo real:

[Visualização da Fronteira de Decisão - Colab](https://colab.research.google.com/drive/1Mj4tYfBgvWIvk2PSUZCuEQvhoZeZ4e9c)

??? example "Código Fonte (Python Local)"
    ```python
    import matplotlib.pyplot as plt
    import numpy as np

    # 1. Configurações (Ajuste para testar)
    w_amigos = 10
    w_chuva = -5
    bias = -2

    # 2. Cenários (x1=Amigos, x2=Chuva)
    cenarios = [[0,0], [0,1], [1,0], [1,1]]

    pontos_x, pontos_y, cores = [], [], []

    print("--- VALIDAÇÃO DA LÓGICA ---")
    for x in cenarios:
        z = (x[0] * w_amigos) + (x[1] * w_chuva) + bias
        decisao = 1 if z >= 0 else 0

        status = "VOU! (1)" if decisao == 1 else "FICO (0)"
        print(f"Amigos: {x[0]} | Chuva: {x[1]} -> z: {z:3} | Resultado: {status}")

        pontos_x.append(x[0])
        pontos_y.append(x[1])
        cores.append('green' if decisao == 1 else 'red')

    plt.figure(figsize=(8, 6))

    # Reta de Decisão (z = 0)
    # Equação da reta: w1*x1 + w2*x2 + b = 0  =>  x2 = (-w1*x1 - b) / w2
    x_linha = np.linspace(-0.5, 1.5, 100)
    if w_chuva != 0:
        y_linha = (-w_amigos * x_linha - bias) / w_chuva
        plt.plot(x_linha, y_linha, color='blue', linestyle='--', label='Fronteira de Decisão')
        
        # Colorir regiões
        plt.fill_between(x_linha, y_linha, 2, color='red', alpha=0.1, label='Zona FICO (0)')
        plt.fill_between(x_linha, y_linha, -1, color='green', alpha=0.1, label='Zona VOU (1)')
    else:
        plt.axvline(x=-bias/w_amigos, color='blue', linestyle='--', label='Fronteira de Decisão')

    plt.scatter(pontos_x, pontos_y, c=cores, s=200, edgecolors='black', zorder=5)

    plt.title("O Perceptron Decidindo: 1=Vou, 0=Fico")
    plt.xlabel("Amigos (0 ou 1)")
    plt.ylabel("Chuva (0 ou 1)")
    plt.xlim(-0.2, 1.2)
    plt.ylim(-0.2, 1.2)
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.show()
    ```
