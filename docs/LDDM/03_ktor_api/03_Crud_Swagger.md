# Implementação de Endpoints CRUD e Testes no Swagger

> Projeto utilizado: <a href="https://github.com/i-davies/lddm-merge-skills-aula" target="_blank">lddm-merge-skills</a>.

---

!!! info "Objetivo"
    Nesta aula, vamos concluir a camada de rede do backend Ktor com rotas completas de CRUD para as entidades **Course**, **Lesson** e **Question**, validando todo o fluxo ponta a ponta com o Swagger.

!!! abstract "Pré-requisitos"
    - Configuração do banco local com Exposed finalizada.
    - Integração com Supabase funcionando.
    - Repositórios de Course, Lesson e Question já implementados.
    - Rotas básicas de consulta (`GET`) criadas.

---

## Visão Geral dos Endpoints

Endpoints são as portas de entrada da API. Cada rota recebe uma requisição HTTP, aciona o repositório responsável e retorna uma resposta ao cliente.

- `GET`: consulta dados
- `POST`: cria registros
- `PUT`: atualiza registros
- `DELETE`: remove registros

!!! tip "Boas práticas"
    Mantenha sempre um padrão de resposta para erro, usando `try/catch` e códigos HTTP coerentes (`400`, `404`, `500`). Isso facilita a integração com frontend e testes automatizados.

---

## Rotas de Course

No arquivo `server/src/main/kotlin/com/fatec/lddm_merge_skills/routes/CourseRoutes.kt`, implemente por etapas.

### Etapa A: criar o POST

Primeiro, adicione apenas a rota de criacao:

```kotlin
post("/courses") {
    try {
        val courseRequest = call.receive<com.fatec.lddm_merge_skills.model.Course>()
        val createdCourse = courseRepository.create(courseRequest)
        call.respond(HttpStatusCode.Created, createdCourse)
    } catch (e: Exception) {
        call.respond(HttpStatusCode.BadRequest, mapOf("error" to "Formato de curso invalido"))
    }
}
```

### Etapa B: adicionar o PUT

Com o POST validado no Swagger, acrescente a atualizacao:

```kotlin
put("/courses/{id}") {
    val id = call.parameters["id"]?.toIntOrNull()
        ?: return@put call.respond(HttpStatusCode.BadRequest, "ID ausente")

    val courseRequest = call.receive<com.fatec.lddm_merge_skills.model.Course>()

    try {
        val updatedCourse = courseRepository.update(id, courseRequest)
        call.respond(HttpStatusCode.OK, updatedCourse)
    } catch (e: Exception) {
        call.respond(HttpStatusCode.NotFound, mapOf("error" to "Curso nao encontrado"))
    }
}
```

### Etapa C: finalizar com o DELETE

Por ultimo, implemente a remocao:

```kotlin
delete("/courses/{id}") {
    val id = call.parameters["id"]?.toIntOrNull()
        ?: return@delete call.respond(HttpStatusCode.BadRequest, "ID ausente ou invalido")

    try {
        courseRepository.delete(id)
        call.respond(HttpStatusCode.NoContent)
    } catch (e: Exception) {
        call.respond(HttpStatusCode.NotFound, mapOf("error" to "Curso nao encontrado"))
    }
}
```

---

## Rotas de Lesson

No arquivo `LessonRoutes.kt`, repita a mesma estrategia incremental.

### Etapa A: criar o POST

```kotlin
post("/lessons") {
    try {
        val lessonRequest = call.receive<com.fatec.lddm_merge_skills.model.Lesson>()
        val createdLesson = lessonRepository.create(lessonRequest)
        call.respond(HttpStatusCode.Created, createdLesson)
    } catch (e: Exception) {
        call.respond(HttpStatusCode.BadRequest, mapOf("error" to "Formato de licao invalido: verifique course_id"))
    }
}
```

### Etapa B: adicionar o PUT

```kotlin
put("/lessons/{id}") {
    val id = call.parameters["id"]?.toIntOrNull()
        ?: return@put call.respond(HttpStatusCode.BadRequest, "ID invalido")

    val lessonRequest = call.receive<com.fatec.lddm_merge_skills.model.Lesson>()

    try {
        val updatedLesson = lessonRepository.update(id, lessonRequest)
        call.respond(HttpStatusCode.OK, updatedLesson)
    } catch (e: Exception) {
        call.respond(HttpStatusCode.NotFound, mapOf("error" to "Licao nao encontrada"))
    }
}
```

### Etapa C: finalizar com o DELETE

```kotlin
delete("/lessons/{id}") {
    val id = call.parameters["id"]?.toIntOrNull()
        ?: return@delete call.respond(HttpStatusCode.BadRequest, "ID invalido")

    try {
        lessonRepository.delete(id)
        call.respond(HttpStatusCode.NoContent)
    } catch (e: Exception) {
        call.respond(HttpStatusCode.NotFound, mapOf("error" to "Licao nao encontrada"))
    }
}
```

!!! note "Relacionamento e cascade"
    Se a chave estrangeira estiver configurada com `ON DELETE CASCADE`, ao remover um curso com `DELETE /courses/{id}`, as licoes vinculadas a ele tambem serao removidas automaticamente.

---

## Rotas de Question

No arquivo `QuestionRoutes.kt`, aplique o mesmo fluxo por etapas.

### Etapa A: criar o POST

```kotlin
post("/questions") {
    try {
        val questionRequest = call.receive<com.fatec.lddm_merge_skills.model.Question>()
        val createdQuestion = questionRepository.create(questionRequest)
        call.respond(HttpStatusCode.Created, createdQuestion)
    } catch (e: Exception) {
        call.respond(HttpStatusCode.BadRequest, mapOf("error" to "Formato de questao invalido"))
    }
}
```

### Etapa B: adicionar o PUT

```kotlin
put("/questions/{id}") {
    val id = call.parameters["id"]?.toIntOrNull()
        ?: return@put call.respond(HttpStatusCode.BadRequest, "ID invalido")

    val questionRequest = call.receive<com.fatec.lddm_merge_skills.model.Question>()

    try {
        val updatedQuestion = questionRepository.update(id, questionRequest)
        call.respond(HttpStatusCode.OK, updatedQuestion)
    } catch (e: Exception) {
        call.respond(HttpStatusCode.NotFound, mapOf("error" to "Questao nao encontrada"))
    }
}
```

### Etapa C: finalizar com o DELETE

```kotlin
delete("/questions/{id}") {
    val id = call.parameters["id"]?.toIntOrNull()
        ?: return@delete call.respond(HttpStatusCode.BadRequest, "ID invalido")

    try {
        questionRepository.delete(id)
        call.respond(HttpStatusCode.NoContent)
    } catch (e: Exception) {
        call.respond(HttpStatusCode.NotFound, mapOf("error" to "Questao nao encontrada"))
    }
}
```

!!! info "Observacao importante"
    A entidade `Question` possui o campo `options` como lista de strings. Se a Data Class estiver corretamente tipada, o Ktor realiza a conversao JSON automaticamente.

---
