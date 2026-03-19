# Correção do Erro com JSONB (Supabase)

> Projeto utilizado: <a href="https://github.com/i-davies/lddm-merge-skills-aula" target="_blank">lddm-merge-skills</a>.

---

!!! info "Objetivo"
    Corrigir o erro `JsonDecodingException` ao buscar questões, ajustando o armazenamento da coluna `options` de `TEXT` para `JSONB` e alinhando o backend Kotlin para leitura/escrita tipada de `List<String>`.

!!! abstract "Pré-requisitos"
    - Projeto `lddm-merge-skills` já rodando localmente.
    - Acesso ao painel do Supabase (SQL Editor).
    - Conhecimento básico de Exposed, DTOs e migrações Flyway.

---

## Sintoma do Problema

Ao consultar questões, o backend tenta desserializar `options` como lista (`List<String>`), mas no banco o valor está salvo como `TEXT` (string JSON). Isso gera erro de decodificação no Kotlin.

---

## Corrigir Coluna no Supabase (Nuvem)

Se o banco da nuvem já possui dados, execute um script de conversão segura no SQL Editor do Supabase.

```sql
-- 1) Remove o default antigo (texto)
ALTER TABLE public.questions ALTER COLUMN options DROP DEFAULT;

-- 2) Converte a coluna de TEXT para JSONB
ALTER TABLE public.questions
ALTER COLUMN options TYPE JSONB
USING options::jsonb;

-- 3) Define novo default como array JSON vazio
ALTER TABLE public.questions
ALTER COLUMN options SET DEFAULT '[]'::jsonb;
```

---

## Ajustar Tabela no Exposed

No arquivo `server/src/main/kotlin/com/fatec/lddm_merge_skills/db/Tables.kt`, altere a definição da coluna `options` no objeto `Questions`:

```kotlin
val options = jsonb<List<String>>("options", Json.Default).default(emptyList())
```

Com isso, o Exposed passa a persistir e ler a coluna já como JSON tipado.

---

## Simplificar DTOs

No arquivo `server/src/main/kotlin/com/fatec/lddm_merge_skills/db/dto/Dtos.kt`, remova serialização manual da coluna `options`.

### QuestionInsertDTO.applyTo

Antes havia `Json.encodeToString(options)`. Agora a atribuição é direta:

```kotlin
builder[Questions.options] = options
```

### ResultRow.toQuestion

Antes havia `Json.decodeFromString(...)`. Agora a leitura é direta:

```kotlin
options = this[Questions.options]
```

---

## Ajustar Seed de Dados

No arquivo `server/src/main/kotlin/com/fatec/lddm_merge_skills/db/migration/V3__Seed_Data.kt`:

1. Na `data class QuestionData` (dentro de `seedQuestions()`), altere `options` de `String` para `List<String>`.
2. Troque strings JSON por listas Kotlin.

Exemplo:

```kotlin
// antes
val options: String

// depois
val options: List<String>

// antes
"""["A", "B", "C"]"""

// depois
listOf("A", "B", "C")
```

---

## Resetar Ambiente Local

Para garantir alinhamento completo com as migrations:

```powershell
docker-compose down -v
docker-compose up -d
```

Depois, suba o servidor para o Flyway recriar estrutura e seed no novo formato.

---

## Validar Resultado

Teste a rota `GET http://localhost:8080/lessons/1/questions`.

A resposta deve trazer `options` como array JSON real:

```json
{
  "question": "Pergunta exemplo?",
  "options": ["Opção A", "Opção B", "Opção C"]
}
```