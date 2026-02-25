# Persistência Code-First com KMP, Docker e Supabase

> Material didático para a aula de banco de dados e migrações.
> Projeto utilizado: lddm-merge-skills.

---

!!! info "Objetivo"
    Ao final desta aula, o pipeline de banco de dados estará configurado de forma profissional, garantindo que o código Kotlin seja a autoridade máxima sobre o schema, executando de forma consistente tanto no ambiente local (Docker) quanto na nuvem (Supabase).

!!! abstract "Pré-requisitos"
    - IntelliJ IDEA (ou Android Studio) instalado.
    - Docker Desktop instalado ([download](https://docker.com/products/docker-desktop)).
    - Conta no Supabase ([supabase.com](https://supabase.com)).

---

## Criando o Projeto Base

Inicie o desenvolvimento criando o projeto a partir do zero utilizando o assistente do Kotlin Multiplatform.

1. No IntelliJ IDEA, crie um **New Project** selecionando **Kotlin Multiplatform**.
2. Defina o nome do projeto como `lddm-merge-skills`.
3. Defina o **Group ID** (pacote base) como `com.fatec`.
4. Na seleção de plataformas (**Target platforms**), selecione **apenas** `Android` e `Server`.

Aguarde a sincronização inicial do Gradle (o download das dependências) terminar antes de prosseguir.

---

## Parte 1: O Contrato de Domínio

### Entendendo a Arquitetura do Projeto

O projeto KMP (Kotlin Multiplatform) é estruturado em 3 módulos principais:

```text
lddm-merge-skills/
├── shared/          ← Modelos e contratos (Android + Backend)
│   └── src/commonMain/kotlin/com/fatec/lddm_merge_skills/
│       ├── model/          ← data classes (Course, Lesson, Question)
│       └── repository/     ← interfaces de repositório
├── server/          ← Backend Ktor (API REST)
│   └── src/main/kotlin/com/fatec/lddm_merge_skills/
│       ├── Application.kt  ← Ponto de entrada do servidor
│       └── db/              ← Tabelas e migrações
│           ├── Tables.kt
│           ├── DatabaseFactory.kt
│           └── migration/
│               ├── FlywayConnection.kt
│               ├── V1__Initial_Schema.kt
│               └── V2__Add_Difficulty_To_Lessons.kt
└── composeApp/      ← App Android (Jetpack Compose)
```

!!! important
    **Single Source of Truth:** Os modelos são mantidos no módulo `shared` para estarem disponíveis tanto para o aplicativo Android quanto para o Backend. Ao alterar o modelo de dados, ambos os lados são atualizados.

### Adicionando o Plugin de Serialização

Antes de implementar os modelos, é necessário adicionar o plugin `kotlinx.serialization`, responsável por converter os objetos do Kotlin para o formato JSON.

!!! note
    **Por que JSON?** O JSON funciona como uma ponte de comunicação entre o aplicativo e o servidor. A serialização garante que os dados armazenados possam ser trafegados e exibidos na interface de forma legível.

**Passo 1: Adicionar o plugin no version catalog (`gradle/libs.versions.toml`)**

Na seção `[versions]`, adicione:
```toml
kotlinx-serialization = "1.8.1"
```

Na seção `[libraries]`, adicione:
```toml
kotlinx-serialization-json = { module = "org.jetbrains.kotlinx:kotlinx-serialization-json", version.ref = "kotlinx-serialization" }
```

Na seção `[plugins]`, adicione:
```toml
kotlinSerialization = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
```

!!! tip
    **Gestão de Dependências:**
    1. No `gradle/libs.versions.toml` (Version Catalog), as dependências são **catalogadas** (versões e aliases são definidos de forma centralizada).
    2. No `build.gradle.kts` de cada módulo, o plugin ou biblioteca é **ativado** conforme a necessidade.

**Passo 2: Aplicar o plugin no `shared/build.gradle.kts`**

```kotlin
plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidLibrary)
    alias(libs.plugins.kotlinSerialization) // Adicionar o plugin
}

// Na seção sourceSets → commonMain.dependencies:
commonMain.dependencies {
    implementation(libs.kotlinx.serialization.json) // Adicionar a biblioteca
}
```

**Passo 3: Sincronizar o Gradle**
- Execute a sincronização do projeto (atalho como `Ctrl + Shift + O` ou botão superior).

### Criando os Modelos

Para representar as informações do sistema, utiliza-se a estrutura de `data class` em Kotlin. Essas classes são otimizadas para armazenamento e transporte de dados, incluindo funcionalidades essenciais como comparação e cópia de instâncias.

As classes devem ser organizadas na pasta `model/` para definir o **Domínio** — o conjunto de regras e estruturas fundamentais do sistema, visíveis para todos os módulos.

!!! tip
    **Classe ou Arquivo?** 
    No IntelliJ, ao criar um novo elemento, selecione a opção **Kotlin Class/Interface**.
    - Selecione **Class** quando o arquivo se dedicará a uma única classe (que é o padrão usado aqui).
    - Selecione **File** para agrupar múltiplas funções ou estruturas soltas.

**Criar: `shared/src/commonMain/kotlin/com/fatec/lddm_merge_skills/model/Course.kt`**

```kotlin
package com.fatec.lddm_merge_skills.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// @Serializable: habilita a conversão da classe para/de JSON
@Serializable
data class Course(
    val id: Int,
    val title: String,
    val description: String? = null,    // Null Safety: permite valores nulos
    val icon: String? = null,
    val color: String? = null,
    @SerialName("total_lessons")        // Mapeamento automático camelCase → snake_case
    val totalLessons: Int? = null
)
```

**Criar: `shared/.../model/Lesson.kt`**

```kotlin
package com.fatec.lddm_merge_skills.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Lesson(
    val id: Int,
    @SerialName("course_id")
    val courseId: Int,           // Chave Estrangeira
    val title: String,
    val description: String? = null,
    val order: Int? = null,
    val questions: List<Question>? = null
)
```

**Criar: `shared/.../model/Question.kt`**

```kotlin
package com.fatec.lddm_merge_skills.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Question(
    val id: Int,
    @SerialName("lesson_id")
    val lessonId: Int,                       // Chave Estrangeira
    val question: String,
    val code: String? = null,
    val options: List<String> = emptyList(),
    @SerialName("correct_answer")
    val correctAnswer: Int? = null,
    val order: Int? = null
)
```

### Criando a Interface do Repositório

Antes de configurar diretamente o banco de dados, é boa prática definir o contrato de persistência. Este passo introduz o **Repository Pattern**.

**Criar: `shared/src/commonMain/kotlin/com/fatec/lddm_merge_skills/repository/CourseRepository.kt`**

```kotlin
package com.fatec.lddm_merge_skills.repository

import com.fatec.lddm_merge_skills.model.Course

// Interface atua como um contrato funcional
interface CourseRepository {
    // suspect evita o bloqueio da lógica principal
    suspend fun getAll(): List<Course>
    suspend fun getById(id: Int): Course?
    suspend fun create(course: Course): Course
    suspend fun update(id: Int, course: Course): Course
    suspend fun delete(id: Int)
}
```

---

## Parte 2: Infraestrutura Local com Docker

### Preparando o Ambiente Docker

A infraestrutura de desenvolvimento requer a execução do banco de dados na máquina local simulando a nuvem.

!!! note
    Verifique a instalação do Docker com os comandos abaixo no terminal:

```bash
docker --version
# Esperado: Docker version 24.x ou superior

docker compose version
# Esperado: Docker Compose version v2.x
```

### Criando o Docker Compose

Crie o arquivo que define e provisiona a infraestrutura do projeto de forma automatizada.

**Na raiz do projeto (`lddm-merge-skills/`), crie `docker-compose.yml`:**

```yaml
services:
  db:
    image: postgres:15-alpine    # Versão otimizada que reflete o ambiente do Supabase
    container_name: mergeskills-db
    restart: unless-stopped
    ports:
      - "5432:5432"              # Mapeia Porta PC:Porta Container
    environment:
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: mergeskills
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

!!! important
    **Compatibilidade de Versões:** Manter a configuração em `postgres:15-alpine` reflete a arquitetura usada no servidor em nuvem, prevenindo surpresas na hora do deploy.

### Subindo o Banco Local

Utilize o terminal para gerenciar o contêiner do ambiente.

```bash
# Inicia de forma desanexada
docker compose up -d

# Validar processamento ativo
docker compose ps
```

!!! tip
    **Comandos de rotina úteis do Docker:**
    - `docker compose down`: Encerra o container de forma limpa.
    - `docker compose down -v`: Encerra e **elimina volumes salvos**, restaurando do zero.
    - `docker compose logs db`: Exibe as saídas e erros da base.

### Adicionando Dependências ao Projeto

A aplicação precisa agora das bibliotecas voltadas para persistência de dados e controle de migrações.

**Passo 1: Version Catalog (`gradle/libs.versions.toml`)**

Na seção `[versions]`, adicione:
```toml
exposed = "0.60.0"
flyway = "11.5.0"
postgresql = "42.7.5"
```

Na seção `[libraries]`, adicione:
```toml
ktor-server-content-negotiation = { module = "io.ktor:ktor-server-content-negotiation-jvm", version.ref = "ktor" }
ktor-serialization-kotlinx-json = { module = "io.ktor:ktor-serialization-kotlinx-json", version.ref = "ktor" }

# Pacotes para banco de dados e migrações
exposed-core = { module = "org.jetbrains.exposed:exposed-core", version.ref = "exposed" }
exposed-dao = { module = "org.jetbrains.exposed:exposed-dao", version.ref = "exposed" }
exposed-jdbc = { module = "org.jetbrains.exposed:exposed-jdbc", version.ref = "exposed" }
exposed-json = { module = "org.jetbrains.exposed:exposed-json", version.ref = "exposed" }
flyway-core = { module = "org.flywaydb:flyway-core", version.ref = "flyway" }
flyway-database-postgresql = { module = "org.flywaydb:flyway-database-postgresql", version.ref = "flyway" }
postgresql = { module = "org.postgresql:postgresql", version.ref = "postgresql" }
```

**Passo 2: Configuração do Módulo Server (`server/build.gradle.kts`)**

Ative a serialização nos plugins:
```kotlin
plugins {
    alias(libs.plugins.kotlinJvm)
    alias(libs.plugins.ktor)
    alias(libs.plugins.kotlinSerialization)
    application
}
```

Atualize as dependências do server:
```kotlin
// Serialização JSON para respostas da API
implementation(libs.ktor.server.content.negotiation)
implementation(libs.ktor.serialization.kotlinx.json)

// ORM Jetbrains Exposed
implementation(libs.exposed.core)
implementation(libs.exposed.dao)
implementation(libs.exposed.jdbc)
implementation(libs.exposed.json)

// Controle de esquemas - Flyway
implementation(libs.flyway.core)
implementation(libs.flyway.database.postgresql)

// Interação oficial JDBC
implementation(libs.postgresql)
```

**Passo 3: Sincronize o Gradle**.

---

## Parte 3: Mapeamento e Migrações

### Criando as Tabelas com Exposed DSL

O código atuará como um mapeador, convertendo a sintaxe simplificada de modelo para estruturas robustas SQL.

**Criar: `server/src/main/kotlin/com/fatec/lddm_merge_skills/db/Tables.kt`**

```kotlin
package com.fatec.lddm_merge_skills.db

import org.jetbrains.exposed.dao.id.IntIdTable
import org.jetbrains.exposed.sql.ReferenceOption

object Courses : IntIdTable("courses") {
    val title = text("title")
    val description = text("description").nullable()
    val icon = text("icon").nullable()
    val color = text("color").nullable()
    val totalLessons = integer("total_lessons").nullable().default(0)
}

object Lessons : IntIdTable("lessons") {
    val courseId = reference("course_id", Courses, onDelete = ReferenceOption.CASCADE)
    val title = text("title")
    val description = text("description").nullable()
    val order = integer("order").nullable()
}

object Questions : IntIdTable("questions") {
    val lessonId = reference("lesson_id", Lessons, onDelete = ReferenceOption.CASCADE)
    val question = text("question")
    val code = text("code").nullable()
    val options = text("options").default("[]")
    val correctAnswer = integer("correct_answer").nullable()
    val order = integer("order").nullable()
}
```

!!! tip
    **Explicação dos mapeadores:**
    A classe `IntIdTable` automaticamente lida com a chave primária incremental (`id`). Opções como `CASCADE` controlam o ciclo de vida referenciado (filhos sendo eliminados juntos com objetos pais). O uso estruturado de `reference` indica nativamente ao PostgreSQL a implantação de uma Chave Estrangeira.

### Configurando o Serviço de Banco de Dados

Criação da fábrica e provedor central do banco.

**Criar: `server/.../db/DatabaseFactory.kt`**

```kotlin
package com.fatec.lddm_merge_skills.db

import org.flywaydb.core.Flyway
import org.jetbrains.exposed.sql.Database

object DatabaseFactory {
    fun init() {
        val dbUrl = System.getenv("DB_URL") ?: System.getProperty("DB_URL") ?: "jdbc:postgresql://localhost:5432/mergeskills"
        val dbUser = System.getenv("DB_USER") ?: System.getProperty("DB_USER") ?: "devuser"
        val dbPassword = System.getenv("DB_PASSWORD") ?: System.getProperty("DB_PASSWORD") ?: "devpassword"

        println("Conectando ao banco: $dbUrl")

        // Início da etapa de verificação de esquema
        val flyway = Flyway.configure()
            .dataSource(dbUrl, dbUser, dbPassword)
            .locations("classpath:com/fatec/lddm_merge_skills/db/migration")
            .baselineOnMigrate(true)
            .load()
            
        val result = flyway.migrate()
        println("Flyway executou: ${result.migrationsExecuted} relatórios")

        // Ligar o Exposed ao contexto migrado
        Database.connect(
            url = dbUrl,
            driver = "org.postgresql.Driver",
            user = dbUser,
            password = dbPassword
        )
    }
}
```

### Intervenção de Conexão no Flyway

Para manter estabilidade paralela, implementa-se um conector modificado.

**Criar: `server/.../db/migration/FlywayConnection.kt`**

```kotlin
package com.fatec.lddm_merge_skills.db.migration

import java.sql.Connection

/**
 * Wrapper de conexão técnica (impede travamentos entre Flyway e Exposed)
 */
class FlywayConnection(private val delegate: Connection) : Connection by delegate {
    override fun close() {}
    override fun setTransactionIsolation(level: Int) {}
    override fun setAutoCommit(autoCommit: Boolean) {}
    override fun setReadOnly(readOnly: Boolean) {}
}
```

### Criando a Migração V1

Instrua de forma explícita a base sobre onde o script deve iniciar.

!!! warning
    O arquivo de migração obedece estritamente a convenção de nome: `V{número}__{descrição}.kt` com *dois underlines* obrigatoriamente separando o V da descrição.

**Criar: `server/.../db/migration/V1__Initial_Schema.kt`**

```kotlin
package com.fatec.lddm_merge_skills.db.migration

import com.fatec.lddm_merge_skills.db.Courses
import com.fatec.lddm_merge_skills.db.Lessons
import com.fatec.lddm_merge_skills.db.Questions
import org.flywaydb.core.api.migration.BaseJavaMigration
import org.flywaydb.core.api.migration.Context
import org.jetbrains.exposed.sql.Database
import org.jetbrains.exposed.sql.SchemaUtils
import org.jetbrains.exposed.sql.transactions.transaction

class V1__Initial_Schema : BaseJavaMigration() {
    override fun migrate(context: Context) {
        val safeConnection = FlywayConnection(context.connection)
        val database = Database.connect({ safeConnection })

        transaction(database) {
            // A prioridade e precedência ditam o uso das Chaves Estrangeiras
            SchemaUtils.create(Courses, Lessons, Questions)
        }
    }
}
```

### Integrando a Lógica ao Inicializador

**Editar `server/.../Application.kt`:**

```kotlin
import com.fatec.lddm_merge_skills.db.DatabaseFactory

fun Application.module() {
    install(ContentNegotiation) {
        json()
    }

    DatabaseFactory.init() // Delegação do banco inserida na inicialização do Ktor

    routing {
        get("/") { call.respondText("Serviço Ktor ativo.") }
        get("/health") { call.respondText("OK") }
    }
}
```

---

## Parte 4: Variáveis de Ambiente e Homologação

### Configurando Variáveis de Ambiente

Manter credenciais expostas no código contraria os princípios de segurança. Crie meios seguros para injetar dependências externas.

**Passo 1: Criar configuração protótipo `.env.example`**
```env
DB_URL=jdbc:postgresql://localhost:5432/mergeskills
DB_USER=devuser
DB_PASSWORD=devpassword
```

**Passo 2: Adicionar exclusão no `.gitignore`:**
```text
.env
```

**Passo 3: Mapeamento pela IDE (Run Configuration no IntelliJ)**
Edite as configurações do servidor backend, repassando essas variáveis dentro do parâmetro `Environment variables`.

### Testando Localmente com Docker

Execute o servidor verificando a saída que relata as migrações automáticas:
```text
Conectando ao banco: jdbc:postgresql://localhost:5432/mergeskills (user: devuser)
Flyway: 2 migração(ões) executada(s)
```

### Transição para o Supabase

Um ambiente Code-First facilita a transição transparente para um SGBD gerido em Nuvem (BaaS).

**Passo 1:** No painel Supabase em **Settings → Database**, as informações de Host, User e senha da sessão de rede podem ser coletadas.

**Passo 2:** Altere as variáveis locais injetando as dependências de Nuvem:
`DB_URL=jdbc:postgresql://db.XXXXXX.supabase.co:5432/postgres`

Quando executado novamente, o Flyway refletirá instantaneamente todas as lógicas projetadas no painel do banco em produção.

---

## Exercício de Fixação: Evolução do Schema

A capacidade da migração se prova lidando com campos imprevistos em iterações de software.

**Tarefa Estrutural:** A tabela `Lessons` precisa suportar informações de dificuldade (`difficulty_level`).

1. Adicionar o valor serializado `difficultyLevel` na respectiva `data class` em Kotlin (`shared/`).
2. Implementar a tipagem do texto (`difficulty_level`) usando a função textual `.nullable()` em `server/.../db/Tables.kt`.
3. Assinar uma nova migração como `V2__Add_Difficulty_To_Lessons.kt` contendo `SchemaUtils.createMissingTablesAndColumns(Lessons)`.
4. Processar o backend e validar a inclusão exata via logs do terminal.

---

## Resumo de Conceitos

| Conceito | Explicação |
|---|---|
| **JDBC** | Protocolo estrutural de ponta-a-ponta usado pelo Java. |
| **Exposed** | ORM/DSL em Kotlin focado na definição direta do banco. |
| **Flyway** | Mantenedor do versionamento dinâmico baseado no Code-First. |

---

## Troubleshooting

<details>
<summary>"Connection refused" ao rodar o servidor</summary>

Verifique se a sessão com o Docker Desktop e o contêiner `mergeskills-db` responde localmente ou se a porta de ambiente encontra-se conflituosa (`5432`).
</details>

<details>
<summary>"No migrations found" (Flyway)</summary>

Revise se o pacote e a extensão refletem sem pontuações ou traços indesejados e se foram separados corretamente por *dois underlines*.
</details>

<details>
<summary>"Connection is closed" ao usar Flyway</summary>

Assegure a aplicação explícita classificada como `FlywayConnection` no contorno do migrador, garantindo não interferência nas chamas de metadados do Exposed.
</details>

<details>
<summary>Erros associados ao Gradle Sync</summary>

Certifique a exata tipografia nos blocos `.toml` e force invalidação e limpeza de cachê `File → Invalidate Caches → Restart` do IntelliJ.
</details>
