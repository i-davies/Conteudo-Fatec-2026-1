# Refatoração com DTOs e Correções Finais

> Projeto utilizado: <a href="https://github.com/i-davies/lddm-merge-skills-aula" target="_blank">lddm-merge-skills</a>.


---

!!! info "Objetivo"
    Nesta aula, refatoraremos os repositórios para eliminar a repetição de código nas operações de criação e atualização, utilizando DTOs (Data Transfer Objects). Também faremos ajustes finos nos Models e corrigiremos as rotas para suportar requisições JSON.

!!! abstract "Pré-requisitos"
    - Integração básica com Supabase concluída.
    - Repositórios locais e remotos implementados.
    - Entendimento sobre o padrão DTO.

---

## Ajuste nos Models (ID como Default)

Quando criamos um objeto em memória para enviar ao banco de dados, o ID ainda não existe. No Kotlin, se o campo `id` não for opcional, somos obrigados a inicializá-lo com algum valor (por exemplo, `0`). Para evitar a repetição dessa atribuição, vamos definir `id = 0` como valor padrão em todos os models de dados do módulo `shared`.

### Atualização no `Course.kt`, `Lesson.kt` e `Question.kt`

Substitua a declaração da classe adicionando `= 0` ao parâmetro `id`:

```kotlin
// Em Course.kt
data class Course(val id: Int = 0, ...)

// Em Lesson.kt
data class Lesson(val id: Int = 0, ...)

// Em Question.kt
data class Question(val id: Int = 0, ...)
```

---

## Criação dos DTOs Compartilhados

O DTO (Data Transfer Object) é um padrão que nos ajuda a transitar apenas os dados necessários em uma operação. Neste caso, criaremos um arquivo contendo os dados de inserção/atualização (reaproveitáveis e sem envolver o campo de ID) e funções de extensão para transformar o Model no respectivo DTO e aplicar essas configurações no Exposed.

Crie o arquivo `server/src/main/kotlin/com/fatec/lddm_merge_skills/db/dto/Dtos.kt`:

```kotlin
package com.fatec.lddm_merge_skills.db.dto

import com.fatec.lddm_merge_skills.db.*
import com.fatec.lddm_merge_skills.model.*
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.jetbrains.exposed.sql.statements.UpdateBuilder

@Serializable
data class CourseInsertDTO(
    val title: String,
    val description: String?,
    val icon: String?,
    val color: String?,
    @SerialName("total_lessons") val totalLessons: Int?
) {
    fun applyTo(builder: UpdateBuilder<*>) {
        builder[Courses.title] = title
        builder[Courses.description] = description
        builder[Courses.icon] = icon
        builder[Courses.color] = color
        builder[Courses.totalLessons] = totalLessons
    }
}

fun Course.toInsertDTO() = CourseInsertDTO(title, description, icon, color, totalLessons)

@Serializable
data class LessonInsertDTO(
    @SerialName("course_id") val courseId: Int,
    val title: String,
    val description: String?,
    val order: Int?,
    @SerialName("difficulty_level") val difficultyLevel: String?
) {
    fun applyTo(builder: UpdateBuilder<*>) {
        builder[Lessons.courseId] = courseId
        builder[Lessons.title] = title
        builder[Lessons.description] = description
        builder[Lessons.order] = order
        builder[Lessons.difficultyLevel] = difficultyLevel
    }
}

fun Lesson.toInsertDTO() = LessonInsertDTO(courseId, title, description, order, difficultyLevel)

@Serializable
data class QuestionInsertDTO(
    @SerialName("lesson_id") val lessonId: Int,
    val question: String,
    val code: String?,
    val options: List<String>,
    @SerialName("correct_answer") val correctAnswer: Int?,
    val order: Int?
) {
    fun applyTo(builder: UpdateBuilder<*>) {
        builder[Questions.lessonId] = lessonId
        builder[Questions.question] = question
        builder[Questions.code] = code
        builder[Questions.options] = Json.encodeToString(options)
        builder[Questions.correctAnswer] = correctAnswer
        builder[Questions.order] = order
    }
}

fun Question.toInsertDTO() = QuestionInsertDTO(lessonId, question, code, options, correctAnswer, order)
```

!!! note "Vantagem"
    A utilização de DTOs melhora a manutenibilidade do código. Em vez de reescrevermos os mapeamentos campo a campo em cada operação e em cada banco diferente de dados, centralizamos a conversão em uma única rotina padronizada e segura.

---

## Refatoração dos Repositórios Exposed

No padrão Exposed, substituímos a repetição de `it[coluna] = campo` em métodos de criação e atualização pelas chamadas simplificadas a `applyTo`.

Exemplo para `ExposedCourseRepository.kt`:

```kotlin
import com.fatec.lddm_merge_skills.db.dto.toInsertDTO

// No create:
val insertStatement = Courses.insert {
    course.toInsertDTO().applyTo(it)
}

// No update:
Courses.update({ Courses.id eq id }) {
    course.toInsertDTO().applyTo(it)
}
```

!!! tip "Dica de Implementação"
    Repita o mesmo padrão lógico de refatoração para os arquivos `ExposedLessonRepository` e `ExposedQuestionRepository`.

---

## Refatoração dos Repositórios Supabase

Nas operações via Supabase, a mudança é simples: enviamos o DTO diretamente para o banco nas operações de inserção ou atualização. O pacote de serialização usará nativamente as anotações `@SerialName`.

Exemplo para `SupabaseCourseRepository.kt`:

```kotlin
// No create:
return@withContext table.insert(course.toInsertDTO()) { select() }.decodeSingle<Course>()

// No update:
return@withContext table.update(course.toInsertDTO()) {
    filter { eq("id", id) }
    select()
}.decodeSingle<Course>()
```

---

## Correções nas Rotas da API

Para o servidor Ktor conseguir processar informações recebidas em JSON em chamadas POST e PUT, alguns detalhes precisam ser observados:

- **Import Obrigatório:** Assegure-se de que os arquivos de rota tenham a instrução `import io.ktor.server.request.*`. Sem ela, a função `call.receive<T>()` não compilará ou apresentará erros em tempo de execução.
- **Tratamento de Exceções:** Ao esperar a entrada de parâmetros obrigatórios e um payload em JSON, utilize blocos `try/catch` envolvendo `call.receive<T>()`. Assim, ao invés da aplicação parar, você devolverá o código `400 Bad Request` com uma mensagem amigável ao cliente da API caso ocorram falhas de formatação.

Exemplo no `CourseRoutes.kt`:

```kotlin
post("/courses") {
    try {
        val courseRequest = call.receive<Course>()
        val created = courseRepository.create(courseRequest)
        call.respond(HttpStatusCode.Created, created)
    } catch (e: Exception) {
        call.respond(HttpStatusCode.BadRequest, mapOf("error" to (e.message ?: "Erro na formatação ou dados do JSON")))
    }
}
```

---