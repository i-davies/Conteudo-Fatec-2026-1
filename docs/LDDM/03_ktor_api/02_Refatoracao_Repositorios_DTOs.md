# Refatoração de Repositórios e DTOs

> Projeto utilizado: <a href="https://github.com/i-davies/lddm-merge-skills-aula" target="_blank">lddm-merge-skills</a>.

---

!!! info "Objetivo"
    Nesta aula, consolidaremos todas as correções e melhorias estruturais necessárias para o CRUD funcionar corretamente, tanto no banco local (**Exposed**) quanto na nuvem (**Supabase**), utilizando DTOs para eliminar duplicação de código.

!!! abstract "Pré-requisitos"
    - Modelos de dados (Course, Lesson, Question) criados.
    - Interfaces de repositório definidas.
    - Tabelas do Exposed e Supabase configuradas.
    - Entendimento sobre padrão DTO e extension functions.

---

## Conceitos-Chave

| Conceito | O que é | Por que importa |
|---|---|---|
| **DTO (Data Transfer Object)** | Classe especializada apenas para envio/recebimento de dados | Evita expor a estrutura interna do Model e centraliza conversões |
| **applyTo()** | Método que aplica valores de um DTO a um builder do Exposed | Simplifica a lógica de INSERT/UPDATE no banco local |
| **Extension Function** | Função "adicionada" a uma classe existente | Permite conversões limpas como `course.toInsertDTO()` |
| **Serialização JSON** | Conversão de objetos para JSON e vice-versa | Necessária para comunicação HTTP e persistência em banco |
| **Exposed vs Supabase** | Dois backends: local e cloud | Ambos usam os mesmos Models, mas conversões diferentes |

---

## Visão Geral dos Problemas

Sem uma estratégia padronizada de conversão entre Models e banco de dados, o código sofre de:

- **Duplicação:** O mesmo mapeamento (`campo = valor`) é escrito em cada repositório.
- **Inconsistência:** Alterações em um lugar não se refletem em outro.
- **Fragilidade:** Qualquer mudança no schema quebra múltiplos lugares.

A solução é centralizar toda lógica de conversão no `Dtos.kt`.

---

## Parte 1: Ajustar os Models (ID com Valor Padrão)

Para que possamos criar objetos sem precisar passar um ID (já que o banco gera automaticamente), definimos um valor padrão de `0` para o campo `id` em todos os models.

### Atualizar Course.kt

**Arquivo:** `shared/src/commonMain/kotlin/.../model/Course.kt`

```kotlin
@Serializable
data class Course(
    val id: Int = 0,
    val title: String,
    val description: String? = null,
    val icon: String? = null,
    val color: String? = null,
    @SerialName("total_lessons") val totalLessons: Int? = null
)
```

### Atualizar Lesson.kt

**Arquivo:** `shared/src/commonMain/kotlin/.../model/Lesson.kt`

```kotlin
@Serializable
data class Lesson(
    val id: Int = 0,
    @SerialName("course_id") val courseId: Int,
    val title: String,
    val description: String? = null,
    val order: Int? = null
)
```

### Atualizar Question.kt

**Arquivo:** `shared/src/commonMain/kotlin/.../model/Question.kt`

```kotlin
@Serializable
data class Question(
    val id: Int = 0,
    @SerialName("lesson_id") val lessonId: Int,
    val question: String,
    val code: String? = null,
    val options: List<String> = emptyList(),
    @SerialName("correct_answer") val correctAnswer: Int? = null,
    val order: Int? = null
)
```

---

## Parte 2: Criar o Arquivo Dtos.kt

Este arquivo é o "coração" da refatoração. Ele centraliza as regras de como converter dados entre o Banco e o Model, evitando repetição nos repositórios.

### Criar Dtos.kt

**Arquivo:** `server/src/main/kotlin/.../db/dto/Dtos.kt`

```kotlin
package com.fatec.lddm_merge_skills.db.dto

import com.fatec.lddm_merge_skills.db.*
import com.fatec.lddm_merge_skills.model.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.SerialName
import kotlinx.serialization.json.Json
import kotlinx.serialization.encodeToString
import org.jetbrains.exposed.sql.ResultRow
import org.jetbrains.exposed.sql.statements.UpdateBuilder

// DTO: Course
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

fun ResultRow.toCourse() = Course(
    id = this[Courses.id].value,
    title = this[Courses.title],
    description = this[Courses.description],
    icon = this[Courses.icon],
    color = this[Courses.color],
    totalLessons = this[Courses.totalLessons]
)

// DTO: Lesson
@Serializable
data class LessonInsertDTO(
    @SerialName("course_id") val courseId: Int,
    val title: String,
    val description: String?,
    val order: Int?
) {
    fun applyTo(builder: UpdateBuilder<*>) {
        builder[Lessons.courseId] = courseId
        builder[Lessons.title] = title
        builder[Lessons.description] = description
        builder[Lessons.order] = order
    }
}

fun Lesson.toInsertDTO() = LessonInsertDTO(courseId, title, description, order)

fun ResultRow.toLesson() = Lesson(
    id = this[Lessons.id].value,
    courseId = this[Lessons.courseId].value,
    title = this[Lessons.title],
    description = this[Lessons.description],
    order = this[Lessons.order]
)

// DTO: Question
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

fun ResultRow.toQuestion(): Question {
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
```

---

## Parte 3: Sincronizar Interfaces (Shared)

As interfaces definem o contrato que os dois bancos devem seguir. Com isso, tanto Exposed quanto Supabase implementam exatamente os mesmos métodos.

### Atualizar CourseRepository.kt

**Arquivo:** `shared/src/commonMain/kotlin/.../repository/CourseRepository.kt`

```kotlin
interface CourseRepository {
    suspend fun getAll(): List<Course>
    suspend fun getById(id: Int): Course?
    suspend fun create(course: Course): Course
    suspend fun update(id: Int, course: Course): Course
    suspend fun delete(id: Int)
}
```

### Atualizar LessonRepository.kt

**Arquivo:** `shared/src/commonMain/kotlin/.../repository/LessonRepository.kt`

```kotlin
interface LessonRepository {
    suspend fun getByCourseId(courseId: Int): List<Lesson>
    suspend fun getById(id: Int): Lesson?
    suspend fun create(lesson: Lesson): Lesson
    suspend fun update(id: Int, lesson: Lesson): Lesson
    suspend fun delete(id: Int)
}
```

### Atualizar QuestionRepository.kt

**Arquivo:** `shared/src/commonMain/kotlin/.../repository/QuestionRepository.kt`

```kotlin
interface QuestionRepository {
    suspend fun getByLessonId(lessonId: Int): List<Question>
    suspend fun getById(id: Int): Question?
    suspend fun create(question: Question): Question
    suspend fun update(id: Int, question: Question): Question
    suspend fun delete(id: Int)
}
```

---

## Parte 4: Implementar Repositórios Exposed (Local)

No Exposed, usamos as extensões do `Dtos.kt` para leitura (`toModel`) e escrita (`toInsertDTO().applyTo(it)`).

Nas funções de `delete`, use corpo com `{ }` para deixar explícito o retorno `Unit` do contrato da interface.

### Atualizar ExposedCourseRepository.kt

**Arquivo:** `server/src/main/kotlin/.../db/ExposedCourseRepository.kt`

```kotlin
package com.fatec.lddm_merge_skills.db

import com.fatec.lddm_merge_skills.db.dto.*
import com.fatec.lddm_merge_skills.model.Course
import com.fatec.lddm_merge_skills.repository.CourseRepository
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.SqlExpressionBuilder.eq
import org.jetbrains.exposed.sql.transactions.experimental.newSuspendedTransaction

class ExposedCourseRepository : CourseRepository {
    override suspend fun getAll(): List<Course> = newSuspendedTransaction {
        Courses.selectAll().map { it.toCourse() }
    }
    override suspend fun getById(id: Int): Course? = newSuspendedTransaction {
        Courses.selectAll().where { Courses.id eq id }.map { it.toCourse() }.singleOrNull()
    }
    override suspend fun create(course: Course): Course = newSuspendedTransaction {
        val insertStatement = Courses.insert { course.toInsertDTO().applyTo(it) }
        insertStatement.resultedValues!!.first().toCourse()
    }
    override suspend fun update(id: Int, course: Course): Course = newSuspendedTransaction {
        Courses.update({ Courses.id eq id }) { course.toInsertDTO().applyTo(it) }
        getById(id) ?: course
    }
    override suspend fun delete(id: Int) {
        newSuspendedTransaction {
            Courses.deleteWhere { Courses.id eq id }
        }
    }
}
```

### Atualizar ExposedLessonRepository.kt

**Arquivo:** `server/src/main/kotlin/.../db/ExposedLessonRepository.kt`

```kotlin
package com.fatec.lddm_merge_skills.db

import com.fatec.lddm_merge_skills.db.dto.*
import com.fatec.lddm_merge_skills.model.Lesson
import com.fatec.lddm_merge_skills.repository.LessonRepository
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.SqlExpressionBuilder.eq
import org.jetbrains.exposed.sql.transactions.experimental.newSuspendedTransaction

class ExposedLessonRepository : LessonRepository {
    override suspend fun getByCourseId(courseId: Int): List<Lesson> = newSuspendedTransaction {
        Lessons.selectAll().where { Lessons.courseId eq courseId }.orderBy(Lessons.order).map { it.toLesson() }
    }
    override suspend fun getById(id: Int): Lesson? = newSuspendedTransaction {
        Lessons.selectAll().where { Lessons.id eq id }.map { it.toLesson() }.singleOrNull()
    }
    override suspend fun create(lesson: Lesson): Lesson = newSuspendedTransaction {
        val insertStatement = Lessons.insert { lesson.toInsertDTO().applyTo(it) }
        insertStatement.resultedValues!!.first().toLesson()
    }
    override suspend fun update(id: Int, lesson: Lesson): Lesson = newSuspendedTransaction {
        Lessons.update({ Lessons.id eq id }) { lesson.toInsertDTO().applyTo(it) }
        getById(id) ?: lesson
    }
    override suspend fun delete(id: Int) {
        newSuspendedTransaction {
            Lessons.deleteWhere { Lessons.id eq id }
        }
    }
}
```

### Atualizar ExposedQuestionRepository.kt

**Arquivo:** `server/src/main/kotlin/.../db/ExposedQuestionRepository.kt`

```kotlin
package com.fatec.lddm_merge_skills.db

import com.fatec.lddm_merge_skills.db.dto.*
import com.fatec.lddm_merge_skills.model.Question
import com.fatec.lddm_merge_skills.repository.QuestionRepository
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.SqlExpressionBuilder.eq
import org.jetbrains.exposed.sql.transactions.experimental.newSuspendedTransaction

class ExposedQuestionRepository : QuestionRepository {
    override suspend fun getByLessonId(lessonId: Int): List<Question> = newSuspendedTransaction {
        Questions.selectAll().where { Questions.lessonId eq lessonId }.orderBy(Questions.order).map { it.toQuestion() }
    }
    override suspend fun getById(id: Int): Question? = newSuspendedTransaction {
        Questions.selectAll().where { Questions.id eq id }.map { it.toQuestion() }.singleOrNull()
    }
    override suspend fun create(question: Question): Question = newSuspendedTransaction {
        val insertStatement = Questions.insert { question.toInsertDTO().applyTo(it) }
        insertStatement.resultedValues!!.first().toQuestion()
    }
    override suspend fun update(id: Int, question: Question): Question = newSuspendedTransaction {
        Questions.update({ Questions.id eq id }) { question.toInsertDTO().applyTo(it) }
        getById(id) ?: question
    }
    override suspend fun delete(id: Int) {
        newSuspendedTransaction {
            Questions.deleteWhere { Questions.id eq id }
        }
    }
}
```

---

## Parte 5: Implementar Repositórios Supabase (Nuvem)

Agora aplicamos o mesmo contrato das interfaces no Supabase, reutilizando `toInsertDTO()` para simplificar `create` e `update`.

Importante: no `delete`, não use `=` antes de `withContext`; isso força inferência de retorno do `PostgrestResult` e conflita com o retorno `Unit` da interface.

### Atualizar SupabaseCourseRepository.kt

**Arquivo:** `server/src/main/kotlin/.../db/SupabaseCourseRepository.kt`

```kotlin
package com.fatec.lddm_merge_skills.db

import com.fatec.lddm_merge_skills.db.dto.toInsertDTO
import com.fatec.lddm_merge_skills.model.Course
import com.fatec.lddm_merge_skills.repository.CourseRepository
import io.github.jan.supabase.postgrest.postgrest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class SupabaseCourseRepository : CourseRepository {
    private val table = SupabaseFactory.client.postgrest["courses"]

    override suspend fun getAll(): List<Course> = withContext(Dispatchers.IO) {
        table.select().decodeList<Course>()
    }
    override suspend fun getById(id: Int): Course? = withContext(Dispatchers.IO) {
        table.select { filter { eq("id", id) } }.decodeSingleOrNull<Course>()
    }
    override suspend fun create(course: Course): Course = withContext(Dispatchers.IO) {
        table.insert(course.toInsertDTO()) { select() }.decodeSingle<Course>()
    }
    override suspend fun update(id: Int, course: Course): Course = withContext(Dispatchers.IO) {
        table.update(course.toInsertDTO()) { filter { eq("id", id) }; select() }.decodeSingle<Course>()
    }
    override suspend fun delete(id: Int) {
        withContext(Dispatchers.IO) {
            table.delete { filter { eq("id", id) } }
        }
    }
}
```

### Atualizar SupabaseLessonRepository.kt

**Arquivo:** `server/src/main/kotlin/.../db/SupabaseLessonRepository.kt`

```kotlin
package com.fatec.lddm_merge_skills.db

import com.fatec.lddm_merge_skills.db.dto.toInsertDTO
import com.fatec.lddm_merge_skills.model.Lesson
import com.fatec.lddm_merge_skills.repository.LessonRepository
import io.github.jan.supabase.postgrest.postgrest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class SupabaseLessonRepository : LessonRepository {
    private val table = SupabaseFactory.client.postgrest["lessons"]

    override suspend fun getByCourseId(courseId: Int): List<Lesson> = withContext(Dispatchers.IO) {
        table.select { filter { eq("course_id", courseId) }; order("order", io.github.jan.supabase.postgrest.query.Order.ASCENDING) }.decodeList<Lesson>()
    }
    override suspend fun getById(id: Int): Lesson? = withContext(Dispatchers.IO) {
        table.select { filter { eq("id", id) } }.decodeSingleOrNull<Lesson>()
    }
    override suspend fun create(lesson: Lesson): Lesson = withContext(Dispatchers.IO) {
        table.insert(lesson.toInsertDTO()) { select() }.decodeSingle<Lesson>()
    }
    override suspend fun update(id: Int, lesson: Lesson): Lesson = withContext(Dispatchers.IO) {
        table.update(lesson.toInsertDTO()) { filter { eq("id", id) }; select() }.decodeSingle<Lesson>()
    }
    override suspend fun delete(id: Int) {
        withContext(Dispatchers.IO) {
            table.delete { filter { eq("id", id) } }
        }
    }
}
```

### Atualizar SupabaseQuestionRepository.kt

**Arquivo:** `server/src/main/kotlin/.../db/SupabaseQuestionRepository.kt`

```kotlin
package com.fatec.lddm_merge_skills.db

import com.fatec.lddm_merge_skills.db.dto.toInsertDTO
import com.fatec.lddm_merge_skills.model.Question
import com.fatec.lddm_merge_skills.repository.QuestionRepository
import io.github.jan.supabase.postgrest.postgrest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class SupabaseQuestionRepository : QuestionRepository {
    private val table = SupabaseFactory.client.postgrest["questions"]

    override suspend fun getByLessonId(lessonId: Int): List<Question> = withContext(Dispatchers.IO) {
        table.select { filter { eq("lesson_id", lessonId) }; order("order", io.github.jan.supabase.postgrest.query.Order.ASCENDING) }.decodeList<Question>()
    }
    override suspend fun getById(id: Int): Question? = withContext(Dispatchers.IO) {
        table.select { filter { eq("id", id) } }.decodeSingleOrNull<Question>()
    }
    override suspend fun create(question: Question): Question = withContext(Dispatchers.IO) {
        table.insert(question.toInsertDTO()) { select() }.decodeSingle<Question>()
    }
    override suspend fun update(id: Int, question: Question): Question = withContext(Dispatchers.IO) {
        table.update(question.toInsertDTO()) { filter { eq("id", id) }; select() }.decodeSingle<Question>()
    }
    override suspend fun delete(id: Int) {
        withContext(Dispatchers.IO) {
            table.delete { filter { eq("id", id) } }
        }
    }
}
```

---
