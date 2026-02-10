# Configuração do Ambiente

> Material didático para a aula de AM usando a stack de ferramentas apresentada.
> Projeto utilizado: [am-primeiro-projeto](https://github.com/i-davies/AM-primeiro-projeto).

---

## Slides

<div style="position: relative; width: 100%; height: 0; padding-top: 56.2500%;
 padding-bottom: 0; box-shadow: 0 2px 8px 0 rgba(63,69,81,0.16); margin-top: 1.6em; margin-bottom: 0.9em; overflow: hidden;
 border-radius: 8px; will-change: transform;">
  <iframe loading="lazy" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0; border: none; padding: 0;margin: 0;"
    src="https://www.canva.com/design/DAHA8bgu0iU/eSjZy3v3eBRgHEn5YBJj3A/view?embed" allowfullscreen="allowfullscreen" allow="fullscreen">
  </iframe>
</div>
<a href="https:&#x2F;&#x2F;www.canva.com&#x2F;design&#x2F;DAHA8bgu0iU&#x2F;eSjZy3v3eBRgHEn5YBJj3A&#x2F;view?utm_content=DAHA8bgu0iU&amp;utm_campaign=designshare&amp;utm_medium=embeds&amp;utm_source=link" target="_blank" rel="noopener">02</a> de Icaro Davies

---

## Python e UV

!!! info "Objetivos"
- Entender a importância do Python no ecossistema de IA.
- Utilizar o UV para unificar a gestão de pacotes e versões com alta performance.

!!! abstract "Conceitos-chave"
- **Python**: Ferramenta que permite construir ecossistemas inteiros com produtividade e código limpo.
- **UV**: Gerenciador All-in-One feito em Rust, sendo até 100x mais rápido que o pip.
- **Performance**: Gestão de projetos com cache e zero atrito no ambiente de desenvolvimento.

> **Exemplo de inicialização (UV)**

```bash
# Cria o projeto e adiciona as dependências base
uv init
uv add scikit-learn pandas numpy matplotlib

```

---

## Back-end API (FastAPI)

!!! info "Objetivos"
- Expor modelos de Machine Learning através de APIs modernas.
- Utilizar documentação automática para transparência no contrato da API.

!!! abstract "Diferenciais"
- **Async Nativo**: Alta performance com suporte a operações assíncronas.
- **Swagger**: Interface interativa para testes e documentação viva (OpenAPI 3).
- **Tipagem**: Uso de Type Hints do Python para garantir robustez.

---

## Processamento e Modelagem

!!! info "Objetivos"
- Manipular e limpar grandes volumes de dados antes do treinamento.
- Aplicar algoritmos de aprendizado clássico e deep learning.

!!! abstract "Bibliotecas Core"
- **Pandas**: Manipulação de DataFrames, limpeza e análise exploratória.
- **NumPy**: Fundação matemática para álgebra linear e operações em matrizes com velocidade de C.
- **Scikit-Learn**: Ferramentas para classificação, previsão e inteligência preditiva clássica.
- **TensorFlow**: Infraestrutura para redes neurais complexas e produção em larga escala.

---

## Visualização e Experimentação

!!! info "Objetivos"
- Transformar números em gráficos claros para diagnóstico do modelo.
- Criar documentos interativos que unem código e narrativa.

!!! abstract "Ferramentas"
- **Matplotlib**: A "voz visual" dos dados, permitindo customização de gráficos e heatmaps.
- **Jupyter Notebook**: Laboratório para prototipagem rápida e visualização instantânea.
- **Kaggle**: Comunidade para acesso a datasets gigantes, competições e uso gratuito de GPU/TPU.

---

## Exercícios de fixação

> Responda às questões abaixo para consolidar os conceitos aprendidos sobre a nossa stack de ferramentas.

<quiz>
Qual é o diferencial de performance do gerenciador UV em relação ao pip tradicional?

* [ ] É escrito em Python e 2x mais lento.
* [x] É feito em Rust e pode ser até 100x mais rápido.
* [ ] Ele apenas gerencia versões do Python, não pacotes.
</quiz>

<quiz>
Qual biblioteca é considerada a "fundação matemática" para operações em matrizes e álgebra linear?

* [ ] Matplotlib
* [ ] Pandas
* [x] NumPy
</quiz>

<quiz>
No contexto de APIs, o que o Swagger (OpenAPI) fornece para o desenvolvedor?

* [ ] Treinamento automático de modelos de IA.
* [x] Uma interface interativa e documentação viva do contrato da API.
* [ ] Limpeza automática de tabelas do banco de dados.
</quiz>

<quiz>
Qual ferramenta é ideal para manipulação de tabelas (DataFrames) e análise exploratória de dados?

* [ ] TensorFlow
* [x] Pandas
* [ ] VS Code
</quiz>

<quiz>
Para treinar e implantar Redes Neurais complexas em larga escala industrial, qual biblioteca é indicada?

* [x] TensorFlow
* [ ] Scikit-Learn
* [ ] NumPy
</quiz>

<quiz>
Onde podemos encontrar datasets gratuitos e utilizar GPU/TPU sem custo para praticar IA?

* [ ] Apenas localmente no VS Code.
* [ ] No repositório do Git Nativo.
* [x] No Kaggle.
</quiz>

<quiz> Qual classe do Scikit-Learn é utilizada para encontrar a relação linear entre duas variáveis?

* [ ] fastapi.FastAPI()
* [x] sklearn.linear_model.LinearRegression()
* [ ] pandas.DataFrame()
</quiz>

<!-- mkdocs-quiz results -->

## Prática

Crie um projeto simples utilizando UV e FastAPI que retorne, por meio de uma API, um exemplo de Regressão Linear implementado com scikit-learn.