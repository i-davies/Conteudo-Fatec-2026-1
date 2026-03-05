# Seed de Dados, Swagger e Rotas da API

**Objetivo:**Popular o banco com dados iniciais (seed), documentar a API com Swagger UI e criar as rotas HTTP do servidor Ktor.

**Pré-requisitos:**
- Projeto da Semana 02 funcionando (`lddm-merge-skills`)
- Docker Desktop rodando com o banco PostgreSQL ativo (`docker compose up -d`)
- Variáveis de ambiente configuradas no IntelliJ

---

## Conceitos-Chave

| Conceito | O que é | Por que importa |
|---|---|---|
| **Seed**| Dados iniciais inseridos no banco | Sistema já nasce com conteúdo para testes |
| **Swagger UI**| Interface web para testar a API | Documenta e testa rotas sem precisar de Postman |
| **Rotas (Routes)**| Endpoints HTTP que a API expõe | É a "porta de entrada" para o App acessar dados |
| **Extension Function**| Função "adicionada" a uma classe existente | Permite organizar rotas em arquivos separados |

---

## Parte 1: Seed de Dados e Swagger UI

### Adicionando Dependências do Swagger

Precisamos de duas novas bibliotecas: Swagger UI (documentação) e Status Pages (tratamento de erros).

**Passo 1: Version Catalog (`gradle/libs.versions.toml`)**

Na seção `[libraries]`, adicione:
```toml
# Semana 03: Swagger UI
ktor-server-swagger = { module = "io.ktor:ktor-server-swagger-jvm", version.ref = "ktor" }
ktor-server-status-pages = { module = "io.ktor:ktor-server-status-pages-jvm", version.ref = "ktor" }
```

**Passo 2: Server Build (`server/build.gradle.kts`)**

Na seção `dependencies`, adicione:
```kotlin
// Semana 03: Swagger UI
implementation(libs.ktor.server.swagger)
implementation(libs.ktor.server.status.pages)
```

**Passo 3:** Sincronize o Gradle (`Ctrl+Shift+O`)

### Criando a Documentação OpenAPI

O Swagger UI lê um arquivo YAML que descreve todas as rotas da API.

**Criar: `server/src/main/resources/openapi/documentation.yaml`**

```yaml
openapi: 3.0.3
info:
  title: API LDDM - MergeSkills
  description: API do Sistema de Gestão de Aprendizagem
  version: 1.0.0
servers:
  - url: http://localhost:8080
    description: Servidor de Desenvolvimento Local

tags:
  - name: Cursos
    description: Gerenciamento de cursos
  - name: Conteúdo
    description: Lições e questões
  - name: Progresso
    description: Acompanhamento do estudante

paths:
  /courses:
    get:
      tags: [Cursos]
      summary: Listar todos os cursos
      responses:
        '200':
          description: Lista de cursos
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Course'

  /courses/{id}/lessons:
    get:
      tags: [Conteúdo]
      summary: Listar lições de um curso
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Lista de lições
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Lesson'

  /lessons/{id}/questions:
    get:
      tags: [Conteúdo]
      summary: Listar questões de uma lição
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Lista de questões
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Question'

  /questions/{id}:
    get:
      tags: [Conteúdo]
      summary: Obter detalhes de uma questão
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Questão encontrada
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Question'
        '404':
          description: Questão não encontrada

  /progress/submit:
    post:
      tags: [Progresso]
      summary: Enviar resposta
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SubmitAnswerRequest'
      responses:
        '200':
          description: Resposta verificada
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SubmitAnswerResponse'

  /progress/reset:
    post:
      tags: [Progresso]
      summary: Reiniciar progresso
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ResetProgressRequest'
      responses:
        '200':
          description: Progresso reiniciado

  /progress/history/{userId}:
    get:
      tags: [Progresso]
      summary: Histórico do usuário
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Histórico retornado

components:
  schemas:
    Course:
      type: object
      properties:
        id: { type: integer }
        title: { type: string }
        description: { type: string }
        icon: { type: string }
        color: { type: string }
        total_lessons: { type: integer }

    Lesson:
      type: object
      properties:
        id: { type: integer }
        course_id: { type: integer }
        title: { type: string }
        description: { type: string }
        order: { type: integer }

    Question:
      type: object
      properties:
        id: { type: integer }
        lesson_id: { type: integer }
        question: { type: string }
        code: { type: string }
        options:
          type: array
          items: { type: string }
        correct_answer: { type: integer }
        order: { type: integer }

    SubmitAnswerRequest:
      type: object
      properties:
        userId: { type: integer }
        questionId: { type: integer }
        selectedOption: { type: integer }

    SubmitAnswerResponse:
      type: object
      properties:
        isCorrect: { type: boolean }
        correctAnswer: { type: integer }
        message: { type: string }

    ResetProgressRequest:
      type: object
      properties:
        userId: { type: integer }
        lessonId: { type: integer }
```

!!! tip
    O arquivo YAML descreve a API no padrão OpenAPI 3.0. O Swagger UI lê esse arquivo e gera a interface de teste automaticamente!

### Criando o Seed de Dados

Vamos popular o banco com dados iniciais usando uma migração Flyway. Assim o seed roda **apenas uma vez**e na ordem correta.

!!! important
    **Por que usar Flyway para o seed?** Se colocássemos os dados no `Application.kt`, eles seriam inseridos toda vez que o servidor inicia, duplicando dados. Com o Flyway, o seed é uma migração (V3) e roda apenas uma vez.

Criar: `server/src/main/kotlin/com/fatec/lddm_merge_skills/db/migration/V3__Seed_Data.kt`

```kotlin
package com.fatec.lddm_merge_skills.db.migration

import com.fatec.lddm_merge_skills.db.Courses
import com.fatec.lddm_merge_skills.db.Lessons
import com.fatec.lddm_merge_skills.db.Questions
import org.flywaydb.core.api.migration.BaseJavaMigration
import org.flywaydb.core.api.migration.Context
import org.jetbrains.exposed.sql.Database
import org.jetbrains.exposed.sql.insert
import org.jetbrains.exposed.sql.transactions.transaction

class V3__Seed_Data : BaseJavaMigration() {

    override fun migrate(context: Context) {
        val safeConnection = FlywayConnection(context.connection)
        val database = Database.connect({ safeConnection })

        transaction(database) {
            seedCourses()
            seedLessons()
            seedQuestions()
        }
    }

    private fun seedCourses() {
        data class CourseData(
            val title: String, val description: String,
            val icon: String, val color: String, val totalLessons: Int
        )
        val courses = listOf(
            CourseData("Java Icaro", "Aprenda os fundamentos de Java", "code", "#E76F00", 4),
            CourseData("Kotlin", "Domine Kotlin desde o início", "code", "#7F52FF", 4),
            CourseData("Python", "Explore fundamentos de Python", "code", "#3776AB", 4),
            CourseData("TypeScript", "Tipagem segura com TypeScript", "code", "#3178C6", 4)
        )
        courses.forEach { c ->
            Courses.insert {
                it[title] = c.title
                it[description] = c.description
                it[icon] = c.icon
                it[color] = c.color
                it[totalLessons] = c.totalLessons
            }
        }
    }

    private fun seedLessons() {
        // Cada curso tem 4 lições: Variáveis, Laços, Funções, Classes
        data class LessonData(
            val courseId: Int, val title: String,
            val description: String, val order: Int
        )
        val lessons = listOf(
            // Java (course 1)
            LessonData(1, "Variáveis", "Tipos de dados e declarações em Java", 1),
            LessonData(1, "Laços de Repetição", "for, while e do-while", 2),
            LessonData(1, "Funções", "Métodos, parâmetros e retorno", 3),
            LessonData(1, "Classes", "POO com classes Java", 4),
            // Kotlin (course 2)
            LessonData(2, "Variáveis", "val, var e inferência de tipo", 1),
            LessonData(2, "Laços de Repetição", "for, while e ranges", 2),
            LessonData(2, "Funções", "Funções, lambdas e extensões", 3),
            LessonData(2, "Classes", "Data classes e herança", 4),
            // Python (course 3)
            LessonData(3, "Variáveis", "Tipagem dinâmica e tipos", 1),
            LessonData(3, "Laços de Repetição", "for-in e comprehensions", 2),
            LessonData(3, "Funções", "def, *args e **kwargs", 3),
            LessonData(3, "Classes", "POO em Python, __init__", 4),
            // TypeScript (course 4)
            LessonData(4, "Variáveis", "let, const e anotações de tipo", 1),
            LessonData(4, "Laços de Repetição", "for-of e métodos de array", 2),
            LessonData(4, "Funções", "Arrow functions e generics", 3),
            LessonData(4, "Classes", "Classes e interfaces", 4)
        )
        lessons.forEach { l ->
            Lessons.insert {
                it[courseId] = l.courseId
                it[title] = l.title
                it[description] = l.description
                it[order] = l.order
            }
        }
    }

    private fun seedQuestions() {
        // 5 questões por lição (total: 80 questões)
        // Exemplo: Lição 1 (Java - Variáveis)
        data class QuestionData(
            val lessonId: Int, val question: String, val code: String?,
            val options: String, val correctAnswer: Int, val order: Int
        )
        val questions = listOf(
            // Java — Variáveis (lição 1)
            QuestionData(1, "Qual tipo armazena inteiros em Java?", null,
                """["float","int","String","boolean"]""", 1, 1),
            QuestionData(1, "Qual palavra declara uma constante?", null,
                """["const","static","final","let"]""", 2, 2),
            // ... (demais questões seguem o mesmo padrão)
            // O arquivo completo já está no projeto!
        )
        questions.forEach { q ->
            Questions.insert {
                it[lessonId] = q.lessonId
                it[question] = q.question
                it[code] = q.code
                it[options] = q.options
                it[correctAnswer] = q.correctAnswer
                it[order] = q.order
            }
        }
    }
}
```

!!! note
    O arquivo completo do seed (`V3__Seed_Data.kt`) já está pronto no projeto com todas as 80 questões. O trecho acima mostra a estrutura — abra o arquivo para ver os dados completos.

### Integrando Swagger no Application.kt

**Editar `server/.../Application.kt`** — adicionar os imports e plugins:

```kotlin
// Novos imports:
import io.ktor.server.plugins.statuspages.*
import io.ktor.server.plugins.swagger.*

fun Application.module() {
    install(ContentNegotiation) { json() }

    //  Tratamento centralizado de erros
    install(StatusPages) {
        exception<Throwable> { call, cause ->
            call.respond(
                HttpStatusCode.InternalServerError,
                mapOf("error" to (cause.message ?: "Erro interno"))
            )
        }
    }

    DatabaseFactory.init()

    routing {
        get("/") { call.respondText("Ktor: ${Greeting().greet()}") }
        get("/health") { call.respondText("OK") }

        //  Swagger UI acessível em /swagger
        swaggerUI(path = "swagger", swaggerFile = "openapi/documentation.yaml")
    }
}
```

**Teste:** Rode o servidor e acesse [http://localhost:8080/swagger](http://localhost:8080/swagger) no navegador!

---

## Parte 2: Criando as Rotas da API

### Entendendo Extension Functions para Rotas

No Ktor, organizamos rotas em arquivos separados usando **Extension Functions**(funções de extensão).

```
server/src/main/kotlin/com/fatec/lddm_merge_skills/
├── Application.kt         ← Registra as rotas
├── routes/                ←  Pasta de rotas
│   ├── CourseRoutes.kt    ← GET /courses, GET /courses/{id}/lessons
│   ├── LessonRoutes.kt   ← GET /lessons/{id}/questions
│   ├── QuestionRoutes.kt ← GET /questions/{id}
│   └── ProgressRoutes.kt ← POST /progress/submit, reset, history
└── db/                    ← Banco de dados (Semana 02)
```

!!! tip
    **Extension Function**é como "adicionar um método" a uma classe que já existe. No caso, estamos adicionando funções à classe `Route` do Ktor para organizar nossas rotas em arquivos diferentes.

### Rotas de Cursos

**Criar: `server/.../routes/CourseRoutes.kt`**

```kotlin
package com.fatec.lddm_merge_skills.routes

import com.fatec.lddm_merge_skills.repository.CourseRepository
import com.fatec.lddm_merge_skills.repository.LessonRepository
import io.ktor.http.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Route.courseRoutes(
    courseRepository: CourseRepository,
    lessonRepository: LessonRepository
) {
    // GET /courses → Lista todos os cursos
    get("/courses") {
        val courses = courseRepository.getAll()
        call.respond(courses)
    }

    // GET /courses/{id}/lessons → Lições de um curso
    get("/courses/{id}/lessons") {
        val id = call.parameters["id"]?.toIntOrNull()
        if (id == null) {
            call.respond(HttpStatusCode.BadRequest, mapOf("error" to "ID inválido"))
            return@get
        }
        val lessons = lessonRepository.getByCourseId(id)
        call.respond(lessons)
    }
}
```

!!! important
    **`call.parameters["id"]`**extrai o valor `{id}` da URL. Como ele vem como String, usamos **`toIntOrNull()`**para converter de forma segura. Se alguém enviar `/courses/abc`, retornamos erro 400.

### Rotas de Lições e Questões

**Criar: `server/.../routes/LessonRoutes.kt`**

```kotlin
package com.fatec.lddm_merge_skills.routes

import com.fatec.lddm_merge_skills.repository.QuestionRepository
import io.ktor.http.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Route.lessonRoutes(questionRepository: QuestionRepository) {
    get("/lessons/{id}/questions") {
        val id = call.parameters["id"]?.toIntOrNull()
        if (id == null) {
            call.respond(HttpStatusCode.BadRequest, mapOf("error" to "ID inválido"))
            return@get
        }
        val questions = questionRepository.getByLessonId(id)
        call.respond(questions)
    }
}
```

**Criar: `server/.../routes/QuestionRoutes.kt`**

```kotlin
package com.fatec.lddm_merge_skills.routes

import com.fatec.lddm_merge_skills.repository.QuestionRepository
import io.ktor.http.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Route.questionRoutes(questionRepository: QuestionRepository) {
    get("/questions/{id}") {
        val id = call.parameters["id"]?.toIntOrNull()
        if (id == null) {
            call.respond(HttpStatusCode.BadRequest, mapOf("error" to "ID inválido"))
            return@get
        }
        val question = questionRepository.getById(id)
        if (question == null) {
            call.respond(HttpStatusCode.NotFound, mapOf("error" to "Questão não encontrada"))
            return@get
        }
        call.respond(question)
    }
}
```

### Rotas de Progresso

**Criar: `server/.../routes/ProgressRoutes.kt`**

```kotlin
package com.fatec.lddm_merge_skills.routes

import com.fatec.lddm_merge_skills.repository.QuestionRepository
import io.ktor.http.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.serialization.Serializable

// DTOs (Data Transfer Objects) — objetos usados na API
@Serializable
data class SubmitAnswerRequest(val userId: Int, val questionId: Int, val selectedOption: Int)

@Serializable
data class SubmitAnswerResponse(val isCorrect: Boolean, val correctAnswer: Int, val message: String)

@Serializable
data class ResetProgressRequest(val userId: Int, val lessonId: Int)

fun Route.progressRoutes(questionRepository: QuestionRepository) {
    // POST /progress/submit → Verifica resposta
    post("/progress/submit") {
        val request = call.receive<SubmitAnswerRequest>()
        val question = questionRepository.getById(request.questionId)
        if (question == null) {
            call.respond(HttpStatusCode.NotFound, mapOf("error" to "Questão não encontrada"))
            return@post
        }
        val isCorrect = request.selectedOption == question.correctAnswer
        call.respond(SubmitAnswerResponse(
            isCorrect = isCorrect,
            correctAnswer = question.correctAnswer ?: 0,
            message = if (isCorrect) "Resposta correta! " else "Tente novamente!"
        ))
    }

    // POST /progress/reset → Reseta progresso
    post("/progress/reset") {
        val request = call.receive<ResetProgressRequest>()
        call.respond(mapOf("message" to "Progresso resetado para lição ${request.lessonId}"))
    }

    // GET /progress/history/{userId} → Histórico (mock)
    get("/progress/history/{userId}") {
        val userId = call.parameters["userId"]?.toIntOrNull()
        if (userId == null) {
            call.respond(HttpStatusCode.BadRequest, mapOf("error" to "ID inválido"))
            return@get
        }
        call.respond(mapOf("completedLessons" to emptyList<Int>()))
    }
}
```

!!! note
    **`call.receive<SubmitAnswerRequest>()`**faz a "mágica" de converter o JSON do corpo da requisição para o objeto Kotlin. Isso funciona graças ao ContentNegotiation que instalamos na Semana 02.

### Registrando as Rotas no Application.kt

**Editar `Application.kt`**— no bloco `routing`, adicione:

```kotlin
routing {
    get("/") { call.respondText("Ktor: ${Greeting().greet()}") }
    get("/health") { call.respondText("OK") }

    swaggerUI(path = "swagger", swaggerFile = "openapi/documentation.yaml")

    //  Semana 03: Rotas da API
    courseRoutes(courseRepository, lessonRepository)
    lessonRoutes(questionRepository)
    questionRoutes(questionRepository)
    progressRoutes(questionRepository)
}
```

!!! warning
    Neste momento, os repositórios ainda não existem! Na próxima aula vamos criar as implementações. Por enquanto, o arquivo `Application.kt` completo já está pronto no projeto.

---

## Resumo

| Arquivo | O que faz |
|---|---|
| `documentation.yaml` | Descreve a API no padrão OpenAPI |
| `V3__Seed_Data.kt` | Popula o banco com 4 cursos, 16 lições e 80 questões |
| `CourseRoutes.kt` | Rotas GET /courses e /courses/{id}/lessons |
| `LessonRoutes.kt` | Rota GET /lessons/{id}/questions |
| `QuestionRoutes.kt` | Rota GET /questions/{id} |
| `ProgressRoutes.kt` | Rotas POST submit/reset e GET history |

---

## Próximos Passos

Na próxima aula, criaremos as **interfaces de repositório**e as **implementações com Exposed ORM** para conectar as rotas ao banco de dados real.
