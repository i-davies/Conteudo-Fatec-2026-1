# Configuração de Variáveis de Ambiente com Dotenv

> Projeto utilizado: <a href="https://github.com/i-davies/lddm-merge-skills-aula" target="_blank">lddm-merge-skills</a>.


---

!!! info "Objetivo"
    Nesta aula, configuraremos o projeto para ler variáveis de ambiente de forma dinâmica. Isso garantirá que o sistema funcione corretamente tanto no ambiente de desenvolvimento local quanto em contêineres Docker, sem expor informações sensíveis no código-fonte.

!!! abstract "Pré-requisitos"
    - Projeto `lddm-merge-skills` configurado.
    - IntelliJ IDEA instalado.
    - Entendimento básico de variáveis de ambiente.

---

## Por que usar o Dotenv-Kotlin?

Originalmente, o projeto lia variáveis apenas via `System.getenv()`. Isso funciona perfeitamente dentro de contêineres Docker, pois o Docker injeta as variáveis no sistema. No entanto, ao rodar o projeto diretamente pela IDE (IntelliJ) ou Gradle, as variáveis do arquivo `.env` são ignoradas pelo sistema operacional por padrão.

A biblioteca `dotenv-kotlin` preenche essa lacuna, permitindo que o código carregue o arquivo `.env` manualmente sem a necessidade de configurações complexas na IDE.

!!! note "Vantagem Didática"
    Utilizar o Dotenv facilita o compartilhamento de configurações entre membros da equipe e garante que o comportamento do sistema seja previsível em diferentes máquinas.

---

## Configuração de Dependências

As dependências foram centralizadas no **Version Catalog** do projeto para manter o padrão de gestão de bibliotecas.

### Version Catalog (`gradle/libs.versions.toml`)

Adicionamos a versão e a definição da biblioteca na seção correspondente:

```toml
[versions]
dotenv = "6.4.1"

[libraries]
dotenv = { module = "io.github.cdimascio:dotenv-kotlin", version.ref = "dotenv" }
```

### Configuração do Módulo Server (`server/build.gradle.kts`)

Incluímos a biblioteca no módulo do servidor para que o backend possa realizar a leitura das variáveis:

```kotlin
dependencies {
    implementation(libs.dotenv)
}
```

---

## Implementação no Código

Para garantir que o projeto funcione de forma padronizada, utilizamos a biblioteca para carregar as configurações diretamente do arquivo em pontos estratégicos de inicialização.

### Utilização no `Application.kt`

No ponto de entrada do servidor, instanciamos o `dotenv` para consumo imediato:

```kotlin
import io.github.cdimascio.dotenv.dotenv

val dotenv = dotenv() // Carrega o arquivo .env obrigatoriamente

// Exemplo de leitura direta
val useSupabase = dotenv["USE_SUPABASE"]?.toBoolean() ?: false

...

if (!useSupabase) {
    DatabaseFactory.init() // Engine Local
}
```

### Configuração no `SupabaseFactory.kt`

Para a integração com o Supabase, as chaves de acesso são recuperadas do ambiente local:

```kotlin
object SupabaseFactory {
    val client: SupabaseClient by lazy {
        val dotenv = dotenv()
        createSupabaseClient(
            supabaseUrl = dotenv["SUPABASE_URL"] ?: "",
            supabaseKey = dotenv["SUPABASE_KEY"] ?: ""
        ) {
            install(Postgrest)
        }
    }
}
```

### Configuração no `DatabaseFactory.kt`

A conexão com o banco de dados (Exposed e Flyway) também segue este padrão:

```kotlin
object DatabaseFactory {
    fun init() {
        val dotenv = dotenv()

        val dbUrl = dotenv["DB_URL"] ?: "jdbc:postgresql://localhost:5432/mergeskills"
        val dbUser = dotenv["DB_USER"] ?: "devuser"
        val dbPassword = dotenv["DB_PASSWORD"] ?: "devpassword"
        
        // ... lógica de conexão e migração
    }
}
```

---

## Como Gerenciar o Arquivo .env

Para que o sistema reconheça as variáveis localmente, siga estes passos:

1. Certifique-se de que o arquivo `.env` existe na raiz da pasta `server` do projeto.
2. Adicione suas configurações seguindo o modelo de chave=valor:
   ```properties
   DB_URL=jdbc:postgresql://localhost:5432/mergeskills
   DB_USER=devuser
   DB_PASSWORD=devpassword

   SUPABASE_URL=https://<SUPABASE_URL>.supabase.co
   SUPABASE_KEY=<SUPABASE_KEY>
   USE_SUPABASE=true
   ```
3. Execute o projeto normalmente. 

!!! warning "Atenção com a Segurança"
    Se o arquivo `.env` estiver faltando e for obrigatório, a biblioteca lançará um erro. Isso é uma medida de segurança para evitar que o sistema rode sem as configurações necessárias.

---

## Prática e Boas Práticas

- **Segurança:** O arquivo `.env` **nunca** deve ser enviado para o repositório Git. 
- **Verificação:** Certifique-se de que o arquivo `.env` está devidamente listado no seu `.gitignore`.
- **Exemplos:** É uma boa prática manter um arquivo `.env.example` com chaves vazias para que outros alunos saibam quais variáveis precisam configurar.

---

## Troubleshooting

<details>
<summary>Erro "DotenvException: Could not find .env file"</summary>
Verifique se o arquivo `.env` está realmente dentro da pasta `server/` e não na raiz principal do projeto, pois o contexto de execução do backend geralmente se inicia dentro do módulo.
</details>

<details>
<summary>As variáveis não são carregadas no Docker</summary>
Dentro do Docker, as variáveis devem ser passadas via `docker-compose.yml` ou arquivo de ambiente do contêiner. O `dotenv-kotlin` é uma ferramenta focada principalmente no **desenvolvimento local**.
</details>
