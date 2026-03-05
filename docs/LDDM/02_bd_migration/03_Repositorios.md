# Repositórios e Conexão com o Banco

**Objetivo:**Criar as interfaces de repositório, implementá-las com Exposed ORM e conectar as rotas da API ao banco de dados PostgreSQL real.

**Pré-requisitos:**
- Primeira parte completa (rotas e seed criados)
- Docker com banco PostgreSQL ativo

---

## Conceitos-Chave

| Conceito | O que é | Por que importa |
|---|---|---|
| **Repository Pattern**| Interface que define operações de dados | Desacopla "o quê" do "como" |
| **Exposed DSL**| Linguagem Kotlin para consultas SQL | Escrevemos SQL em Kotlin, com tipagem |
| **newSuspendedTransaction**| Transaction assíncrona do Exposed | Não bloqueia a thread do servidor |
| **ResultRow → Model**| Conversão de linha do banco para data class | Transforma dados brutos em objetos Kotlin |

---

## Parte 3: Criando os Repositórios

### Interfaces no Shared

Antes de implementar, definimos os "contratos". As interfaces ficam no `shared` porque o Android também pode usá-las.

!!! important
    Já temos o `CourseRepository` da Semana 02. Agora criamos os repositórios para Lições e Questões.

**Criar: `shared/.../repository/LessonRepository.kt`**

```kotlin
package com.fatec.lddm_merge_skills.repository

import com.fatec.lddm_merge_skills.model.Lesson

interface LessonRepository {
    suspend fun getByCourseId(courseId: Int): List<Lesson>
    suspend fun getById(id: Int): Lesson?
}
```

**Criar: `shared/.../repository/QuestionRepository.kt`**

```kotlin
package com.fatec.lddm_merge_skills.repository

import com.fatec.lddm_merge_skills.model.Question

interface QuestionRepository {
    suspend fun getByLessonId(lessonId: Int): List<Question>
    suspend fun getById(id: Int): Question?
}
```

!!! tip
    **Padrão:**Cada interface de repositório define as operações de leitura que a API precisa. Nesta etapa, só precisamos de `get` por enquanto.

### Implementação do CourseRepository

**Criar: `server/.../db/ExposedCourseRepository.kt`**

```kotlin
package com.fatec.lddm_merge_skills.db

import com.fatec.lddm_merge_skills.model.Course
import com.fatec.lddm_merge_skills.repository.CourseRepository
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.SqlExpressionBuilder.eq
import org.jetbrains.exposed.sql.transactions.experimental.newSuspendedTransaction

class ExposedCourseRepository : CourseRepository {

    // Converte uma linha do banco para o model Course
    private fun ResultRow.toCourse() = Course(
        id = this[Courses.id].value,
        title = this[Courses.title],
        description = this[Courses.description],
        icon = this[Courses.icon],
        color = this[Courses.color],
        totalLessons = this[Courses.totalLessons]
    )

    override suspend fun getAll(): List<Course> = newSuspendedTransaction {
        Courses.selectAll().map { it.toCourse() }
    }

    override suspend fun getById(id: Int): Course? = newSuspendedTransaction {
        Courses.selectAll()
            .where { Courses.id eq id }
            .map { it.toCourse() }
            .singleOrNull()
    }

    override suspend fun create(course: Course): Course = newSuspendedTransaction {
        val insertStatement = Courses.insert {
            it[title] = course.title
            it[description] = course.description
            it[icon] = course.icon
            it[color] = course.color
            it[totalLessons] = course.totalLessons
        }
        insertStatement.resultedValues!!.first().toCourse()
    }

    override suspend fun update(id: Int, course: Course): Course = newSuspendedTransaction {
        Courses.update({ Courses.id eq id }) {
            it[title] = course.title
            it[description] = course.description
            it[icon] = course.icon
            it[color] = course.color
            it[totalLessons] = course.totalLessons
        }
        Courses.selectAll()
            .where { Courses.id eq id }
            .map { it.toCourse() }
            .single()
    }

    override suspend fun delete(id: Int): Unit = newSuspendedTransaction {
        Courses.deleteWhere { Courses.id eq id }
    }
}
```

!!! important
    **`newSuspendedTransaction`**é a versão assíncrona do `transaction`. Ela permite que o Ktor continue processando outras requisições enquanto espera a consulta no banco terminar.

### Implementação dos demais Repositórios

**Criar: `server/.../db/ExposedLessonRepository.kt`**

```kotlin
package com.fatec.lddm_merge_skills.db

import com.fatec.lddm_merge_skills.model.Lesson
import com.fatec.lddm_merge_skills.repository.LessonRepository
import org.jetbrains.exposed.sql.ResultRow
import org.jetbrains.exposed.sql.selectAll
import org.jetbrains.exposed.sql.transactions.experimental.newSuspendedTransaction

class ExposedLessonRepository : LessonRepository {

    private fun ResultRow.toLesson() = Lesson(
        id = this[Lessons.id].value,
        courseId = this[Lessons.courseId].value,
        title = this[Lessons.title],
        description = this[Lessons.description],
        order = this[Lessons.order],
        difficultyLevel = this[Lessons.difficultyLevel]
    )

    override suspend fun getByCourseId(courseId: Int): List<Lesson> = newSuspendedTransaction {
        Lessons.selectAll()
            .where { Lessons.courseId eq courseId }
            .orderBy(Lessons.order)
            .map { it.toLesson() }
    }

    override suspend fun getById(id: Int): Lesson? = newSuspendedTransaction {
        Lessons.selectAll()
            .where { Lessons.id eq id }
            .map { it.toLesson() }
            .singleOrNull()
    }
}
```

**Criar: `server/.../db/ExposedQuestionRepository.kt`**

```kotlin
package com.fatec.lddm_merge_skills.db

import com.fatec.lddm_merge_skills.model.Question
import com.fatec.lddm_merge_skills.repository.QuestionRepository
import kotlinx.serialization.json.Json
import org.jetbrains.exposed.sql.ResultRow
import org.jetbrains.exposed.sql.selectAll
import org.jetbrains.exposed.sql.transactions.experimental.newSuspendedTransaction

class ExposedQuestionRepository : QuestionRepository {

    // Converte ResultRow para Question
    // ATENÇÃO: o campo options precisa de conversão JSON → List<String>
    private fun ResultRow.toQuestion(): Question {
        val optionsJson = this[Questions.options]
        val optionsList: List<String> = try {
            Json.decodeFromString(optionsJson)
        } catch (e: Exception) {
            emptyList()
        }

        return Question(
            id = this[Questions.id].value,
            lessonId = this[Questions.lessonId].value,
            question = this[Questions.question],
            code = this[Questions.code],
            options = optionsList,
            correctAnswer = this[Questions.correctAnswer],
            order = this[Questions.order]
        )
    }

    override suspend fun getByLessonId(lessonId: Int): List<Question> = newSuspendedTransaction {
        Questions.selectAll()
            .where { Questions.lessonId eq lessonId }
            .orderBy(Questions.order)
            .map { it.toQuestion() }
    }

    override suspend fun getById(id: Int): Question? = newSuspendedTransaction {
        Questions.selectAll()
            .where { Questions.id eq id }
            .map { it.toQuestion() }
            .singleOrNull()
    }
}
```

!!! note
    **Conversão de `options`:**No banco, as opções são armazenadas como texto JSON (`["opção A", "opção B"]`). No model Kotlin, é `List<String>`. Usamos `Json.decodeFromString()` para converter.

---

## Parte 4: Integrando Tudo e Testando

### Conectando Repositórios no Application.kt

**Editar `Application.kt`**— criar os repositórios e passá-los para as rotas:

```kotlin
fun Application.module() {
    install(ContentNegotiation) { json() }
    install(StatusPages) {
        exception<Throwable> { call, cause ->
            call.respond(HttpStatusCode.InternalServerError,
                mapOf("error" to (cause.message ?: "Erro interno")))
        }
    }

    DatabaseFactory.init()

    //  Instanciando os repositórios (Exposed = banco real)
    val courseRepository = ExposedCourseRepository()
    val lessonRepository = ExposedLessonRepository()
    val questionRepository = ExposedQuestionRepository()

    routing {
        get("/") { call.respondText("Ktor: ${Greeting().greet()}") }
        get("/health") { call.respondText("OK") }

        swaggerUI(path = "swagger", swaggerFile = "openapi/documentation.yaml")

        // Passando os repositórios para as rotas
        courseRoutes(courseRepository, lessonRepository)
        lessonRoutes(questionRepository)
        questionRoutes(questionRepository)
        progressRoutes(questionRepository)
    }
}
```

!!! tip
    **Inversão de Dependência:**As rotas recebem o repositório como parâmetro. Se quiser trocar para mock (testes), basta mudar aqui sem alterar nenhuma rota!

### Testando a API Completa

**Checklist antes de testar:**

- [ ] Docker Desktop rodando (ícone verde 🟢)
- [ ] Banco ativo: `docker compose up -d`
- [ ] Variáveis de ambiente configuradas no IntelliJ
- [ ] Gradle sincronizado

**Suba o servidor** (▶️ no IntelliJ ou `.\gradlew.bat :server:run`)

**O que esperar nos logs:**
```
 Conectando ao banco: jdbc:postgresql://localhost:5432/mergeskills
 Flyway: 1 migração(ões) executada(s)    ← V3 (seed)!
 Exposed conectado ao banco de dados
```

**Testes no navegador ou Swagger UI:**

| Teste | URL | Esperado |
|---|---|---|
| Swagger UI | http://localhost:8080/swagger | Interface de documentação |
| Listar cursos | http://localhost:8080/courses | 4 cursos em JSON |
| Lições do curso 1 | http://localhost:8080/courses/1/lessons | 4 lições de Java |
| Questões da lição 1 | http://localhost:8080/lessons/1/questions | 5 questões de Variáveis |
| Detalhe questão 1 | http://localhost:8080/questions/1 | Questão sobre tipos em Java |
| ID inválido | http://localhost:8080/courses/abc/lessons | `{"error":"ID inválido"}` |
| Questão inexistente | http://localhost:8080/questions/999 | 404 |

### Testando via Swagger UI

1. Acesse http://localhost:8080/swagger
2. Expanda `GET /courses` → clique **Try it out**→ **Execute**
3. Veja os 4 cursos retornados!
4. Teste `POST /progress/submit` com o corpo:
```json
{
  "userId": 1,
  "questionId": 1,
  "selectedOption": 1
}
```
5. Resultado esperado: `"isCorrect": true, "message": "Resposta correta! "`

---

## Resumo de Conceitos

| Conceito | Explicação |
|---|---|
| **Repository Pattern**| Interface define O QUE, implementação define COMO |
| **Exposed DSL**| ORM que permite escrever SQL em Kotlin |
| **`newSuspendedTransaction`**| Transaction assíncrona (não bloqueia) |
| **`ResultRow.toModel()`**| Padrão para converter linhas do banco em objetos |
| **Extension Function**| Permite organizar rotas em arquivos separados |
| **`call.receive<T>()`**| Converte JSON do body para objeto Kotlin |
| **`call.parameters["id"]`**| Extrai parâmetros da URL |

---

## 🔧 Troubleshooting

<details>
<summary> Swagger UI mostra página em branco</summary>

- Verifique se o arquivo `documentation.yaml` está em `server/src/main/resources/openapi/`
- Faça rebuild: `.\gradlew.bat :server:build`
</details>

<details>
<summary> Seed não inseriu dados (tabelas vazias)</summary>

- Se o banco já existia, o Flyway pode não re-executar V3
- Solução: `docker compose down -v` e `docker compose up -d` (apaga e recria)
- Rode o servidor novamente — Flyway executará V1, V2 e V3
</details>

<details>
<summary> "options" retorna string ao invés de array</summary>

- Verifique que `ExposedQuestionRepository` usa `Json.decodeFromString()` para converter
- O import correto é: `import kotlinx.serialization.json.Json`
</details>

<details>
<summary> "Unresolved reference: eq" no repositório</summary>

- Adicione o import: `import org.jetbrains.exposed.sql.SqlExpressionBuilder.eq`
- Ou use wildcard: `import org.jetbrains.exposed.sql.*`
</details>

---
