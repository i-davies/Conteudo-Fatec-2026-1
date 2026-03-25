# UI Declarativa com Jetpack Compose

> Projeto utilizado: <a href="https://github.com/i-davies/lddm-merge-skills-aula" target="_blank">lddm-merge-skills</a>.

---

!!! info "Objetivo"
    Construir a primeira tela inicial do aplicativo Android que se conecta à API Ktor e exibe dados vindos do banco de dados, utilizando Jetpack Compose de forma incremental.

!!! abstract "Pré-requisitos"
    - Backend Ktor funcionando com as rotas `/courses` (GET e POST).
    - IntelliJ IDEA com plugin Compose instalado.
    - Celular físico configurado.

---

## O que é Jetpack Compose?

Jetpack Compose é o toolkit **moderno** do Android para construir interfaces. Em vez de usar arquivos XML (o método antigo), nós **descrevemos** a tela diretamente em código Kotlin usando funções anotadas com `@Composable`.

**Vantagens:**
- Menos código (sem XML, sem Adapters, sem ViewHolders)
- Visualização em tempo real no IntelliJ IDEA (Preview)
- Estado reativo: a tela se atualiza sozinha quando os dados mudam

---

## Atualizando o App durante o Desenvolvimento

Existem duas formas de ver mudanças durante o desenvolvimento:

**Compose Live Edit (Preview e Emulador):**

O IntelliJ IDEA possui o **Compose Live Edit**, que atualiza a Preview e o emulador em tempo real conforme você edita funções `@Composable`.

1. `File → Settings → Editor → Compose Live Edit`
2. Marque a opção para habilitar
3. Funciona automaticamente com **Preview** (`@Preview`) e **emulador**

!!! warning "Limitação no celular físico"
    O Compose Live Edit **não envia mudanças automaticamente para celular físico**. Nesse caso, use o Run (`Shift+F10`) para recompilar e reinstalar o app.

**Para o celular físico:**

1. Faça suas alterações no código
2. Pressione **Run** (ou `Shift+F10`) para reinstalar no celular
3. O IntelliJ recompila e instala rapidamente (build incremental)

!!! tip "Servidor Ktor em modo contínuo"
    Use `./gradlew -t :server:run` para o backend. A flag `-t` ativa o *continuous build*: a cada mudança no código do servidor, ele recompila e reinicia automaticamente.

---

## Configuração de Permissões de Internet

Para que o aplicativo Android consiga acessar a API Ktor, ele precisa de **permissão explícita** — o Android bloqueia acesso à rede por padrão.

Abra o arquivo `composeApp/src/androidMain/AndroidManifest.xml` e verifique se ele contém as permissões e configurações corretas:

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Permissão para acessar a internet (obrigatória!) -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
            android:allowBackup="true"
            android:icon="@mipmap/ic_launcher"
            android:label="@string/app_name"
            android:roundIcon="@mipmap/ic_launcher_round"
            android:supportsRtl="true"
            android:theme="@android:style/Theme.Material.Light.NoActionBar"
            android:usesCleartextTraffic="true"
            android:networkSecurityConfig="@xml/network_security_config">
        <!-- ... activity ... -->
    </application>
</manifest>
```

!!! note "Por que `usesCleartextTraffic="true"`?"
    O Android 9+ bloqueia conexões HTTP (sem HTTPS). Como o servidor local não possui certificado SSL, é necessário permitir "tráfego em texto claro" para os IPs da rede local.

---

## Configuração de Segurança de Rede

Crie o arquivo `composeApp/src/androidMain/res/xml/network_security_config.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<!--
  Permite conexões HTTP (sem HTTPS) durante o desenvolvimento.
  Necessário porque o servidor Ktor local não usa certificado SSL.
-->
<network-security-config>
    <!-- Permite HTTP para QUALQUER domínio/IP (modo desenvolvimento) -->
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>

```

---

## Configurando o IP do Servidor

Abra `shared/src/commonMain/kotlin/.../Constants.kt` e verifique as constantes de conexão:

```kotlin
package com.fatec.lddm_merge_skills

const val SERVER_PORT = 8080

const val SERVER_HOST = "10.0.2.2"  // TROCAR ao usar celular físico!

const val BASE_URL = "http://$SERVER_HOST:$SERVER_PORT"
```

!!! tip "Entendendo o IP `10.0.2.2`"
    Quando o app roda no **emulador**, o emulador vive em uma rede virtual isolada. O IP `10.0.2.2` é um alias especial que o emulador traduz para `localhost` da máquina host. Ao testar no **celular físico**, o celular está na rede WiFi real e precisa do IP real da máquina (ex: `192.168.1.100`).

---

## Dependências no Gradle

Precisamos adicionar o **Ktor Client** ao módulo `composeApp`. Ele é a contraparte do Ktor Server: enquanto o servidor recebe requisições, o client as envia.

No arquivo `gradle/libs.versions.toml`, na seção `[libraries]`, verifique as dependências abaixo:

```toml
ktor-client-core = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }
ktor-client-okhttp = { module = "io.ktor:ktor-client-okhttp", version.ref = "ktor" }
ktor-client-content-negotiation = { module = "io.ktor:ktor-client-content-negotiation", version.ref = "ktor" }
```

No arquivo `composeApp/build.gradle.kts`, verifique o plugin de serialização e as dependências:

```kotlin
plugins {
    // ... plugins existentes ...
    alias(libs.plugins.kotlinSerialization) // Para deserializar JSON
}

kotlin {
    sourceSets {
        androidMain.dependencies {
            implementation(libs.compose.uiToolingPreview)
            implementation(libs.androidx.activity.compose)
            implementation(libs.ktor.client.okhttp)           // Engine HTTP nativo Android
        }
        commonMain.dependencies {
            // ... dependências existentes ...
            implementation(libs.ktor.client.core)                  // Ktor Client base
            implementation(libs.ktor.client.content.negotiation)   // Conversão JSON automática
            implementation(libs.ktor.serialization.kotlinx.json)   // Serialization plugin
            implementation(libs.kotlinx.serialization.json)        // kotlinx.serialization
        }
    }
}
```

!!! warning "Sincronize o Gradle"
    Após modificar o Gradle, clique no ícone de elefante (Sync Now) que aparece no IntelliJ IDEA, ou vá em `File → Sync Project with Gradle Files`.

---

## Criando o ApiClient

Crie o arquivo `composeApp/src/androidMain/kotlin/com/fatec/lddm_merge_skills/network/ApiClient.kt`:

```kotlin
package com.fatec.lddm_merge_skills.network

import com.fatec.lddm_merge_skills.BASE_URL
import com.fatec.lddm_merge_skills.model.Course
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.okhttp.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.json.Json

object ApiClient {

    private val httpClient = HttpClient(OkHttp) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
                prettyPrint = false
            })
        }
    }

    /** GET /courses → Lista todos os cursos */
    suspend fun getCourses(): List<Course> {
        return httpClient.get("$BASE_URL/courses").body()
    }

    /** POST /courses → Cria um novo curso */
    suspend fun createCourse(title: String, description: String?): Course {
        return httpClient.post("$BASE_URL/courses") {
            contentType(ContentType.Application.Json)
            setBody(Course(title = title, description = description))
        }.body()
    }
}
```

**Conceitos importantes:**

| Conceito | Explicação |
|----------|-----------|
| `object` | Singleton — só existe uma instância no app inteiro |
| `HttpClient(OkHttp)` | Cria um cliente HTTP com o engine OkHttp |
| `ContentNegotiation` | Plugin que converte JSON ↔ Kotlin automaticamente |
| `suspend fun` | Função assíncrona (não trava a tela enquanto espera) |
| `.body()` | Converte a resposta HTTP para o tipo Kotlin desejado |
| `contentType(...)` | Define o header `Content-Type: application/json` |
| `setBody(...)` | Serializa o objeto Kotlin como JSON no corpo da requisição |

---

## Construindo a UI por Etapas

A proposta é construir de forma incremental. Cada etapa adiciona algo novo. Rode o app após cada etapa para ver o resultado.

### Tela mínima

Comece com o mais simples possível, apenas para garantir que tudo compila e executa.

Edite `composeApp/src/androidMain/kotlin/.../App.kt`:

```kotlin
package com.fatec.lddm_merge_skills

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
@Preview
fun App() {
    MaterialTheme {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Text("Hello Compose!", fontSize = 24.sp)
        }
    }
}
```

Ao rodar, o texto deve aparecer centralizado na tela.

!!! tip "Testando o Live Edit"
    Com o app rodando, mude o texto e veja a tela atualizar em tempo real (se o Live Edit estiver habilitado). Atalho manual: `Ctrl+F10`.

---

### Buscando dados da API

Adicione os estados reativos e o `LaunchedEffect` para buscar os cursos:

```kotlin
package com.fatec.lddm_merge_skills

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.fatec.lddm_merge_skills.model.Course
import com.fatec.lddm_merge_skills.network.ApiClient

@Composable
@Preview
fun App() {
    MaterialTheme {
        // Estados reativos
        var courses by remember { mutableStateOf<List<Course>>(emptyList()) }
        var loading by remember { mutableStateOf(true) }
        var error by remember { mutableStateOf<String?>(null) }

        // Busca os cursos UMA vez ao montar a tela
        LaunchedEffect(Unit) {
            try {
                courses = ApiClient.getCourses()
            } catch (e: Exception) {
                error = e.message
            }
            loading = false
        }

        // Renderiza baseado no estado
        when {
            loading -> {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            }
            error != null -> {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text("Erro: $error", fontSize = 16.sp)
                }
            }
            else -> {
                LazyColumn(
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(courses) { course ->
                        Text("• ${course.title}", fontSize = 16.sp)
                    }
                }
            }
        }
    }
}
```

**Conceitos-chave do Compose:**

| Conceito | O que faz |
|----------|----------|
| `@Composable` | Marca uma função como "componente de UI" |
| `remember { }` | Preserva o valor entre redesenhos |
| `mutableStateOf` | Cria um valor "observável" — Compose redesenha quando muda |
| `LaunchedEffect` | Executa código assíncrono dentro de um Composable |
| `when` | Switch/case que decide o que renderizar |

Certifique-se de que o servidor está rodando (`./gradlew :server:run`). Você verá os nomes dos cursos listados na tela.

---

### Estilização da lista e refresh

Substitua o conteúdo de `App.kt` pela versão estilizada com cards, header e botão de refresh:

```kotlin
package com.fatec.lddm_merge_skills

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.fatec.lddm_merge_skills.model.Course
import com.fatec.lddm_merge_skills.network.ApiClient
import kotlinx.coroutines.launch

// ─── Cores shadcn/ui (tema claro) ───
private val Border = Color(0xFFE5E7EB)
private val Muted = Color(0xFF6B7280)

@Composable
@Preview
fun App() {
    MaterialTheme {
        var courses by remember { mutableStateOf<List<Course>>(emptyList()) }
        var loading by remember { mutableStateOf(true) }
        var error by remember { mutableStateOf<String?>(null) }
        val scope = rememberCoroutineScope()

        fun refresh() {
            scope.launch {
                loading = true
                error = null
                try {
                    courses = ApiClient.getCourses()
                } catch (e: Exception) {
                    error = e.message
                }
                loading = false
            }
        }

        LaunchedEffect(Unit) { refresh() }

        Surface(modifier = Modifier.fillMaxSize(), color = Color.White) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .statusBarsPadding()
                    .padding(horizontal = 16.dp, vertical = 20.dp)
            ) {
                // Header
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("Courses", fontSize = 22.sp, fontWeight = FontWeight.SemiBold)
                        Text("All available courses.", fontSize = 14.sp, color = Muted)
                    }
                    OutlinedButton(
                        onClick = { refresh() },
                        shape = RoundedCornerShape(6.dp),
                        border = BorderStroke(1.dp, Border)
                    ) { Text("Refresh", fontSize = 13.sp, color = Color.Black) }
                }

                HorizontalDivider(
                    modifier = Modifier.padding(vertical = 12.dp),
                    color = Border
                )

                // Conteúdo
                when {
                    loading -> {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(20.dp),
                                strokeWidth = 2.dp,
                                color = Muted
                            )
                        }
                    }
                    error != null -> {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text("Connection failed", fontWeight = FontWeight.Medium)
                                Spacer(Modifier.height(4.dp))
                                Text(error.orEmpty(), fontSize = 13.sp, color = Muted)
                                Spacer(Modifier.height(12.dp))
                                OutlinedButton(
                                    onClick = { refresh() },
                                    shape = RoundedCornerShape(6.dp),
                                    border = BorderStroke(1.dp, Border)
                                ) { Text("Try again", fontSize = 13.sp, color = Color.Black) }
                            }
                        }
                    }
                    else -> {
                        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            items(courses) { course ->
                                OutlinedCard(
                                    modifier = Modifier.fillMaxWidth(),
                                    shape = RoundedCornerShape(8.dp),
                                    border = BorderStroke(1.dp, Border),
                                    colors = CardDefaults.outlinedCardColors(containerColor = Color.White)
                                ) {
                                    Column(Modifier.padding(14.dp)) {
                                        Text(
                                            course.title,
                                            fontWeight = FontWeight.Medium,
                                            fontSize = 14.sp
                                        )
                                        val desc = course.description
                                        if (!desc.isNullOrBlank()) {
                                            Text(desc, fontSize = 13.sp, color = Muted)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
```

Agora temos um header limpo, cards com estilo shadcn/ui e um botão de refresh funcional.

---

### Navegação entre telas

Vamos adicionar a capacidade de criar cursos pelo app. O primeiro passo é um sistema de navegação simples com `enum`.

Atualize o `App.kt` para incluir a navegação e o botão "+ Add":

```kotlin
package com.fatec.lddm_merge_skills

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.fatec.lddm_merge_skills.model.Course
import com.fatec.lddm_merge_skills.network.ApiClient
import kotlinx.coroutines.launch

// ─── Navegação simples por estado ───
enum class Screen { LIST, ADD }

// ─── Cores shadcn/ui ───
private val Border = Color(0xFFE5E7EB)
private val Muted = Color(0xFF6B7280)

@Composable
@Preview
fun App() {
    MaterialTheme {
        // Estado de navegação
        var currentScreen by remember { mutableStateOf(Screen.LIST) }

        // Estados da lista
        var courses by remember { mutableStateOf<List<Course>>(emptyList()) }
        var loading by remember { mutableStateOf(true) }
        var error by remember { mutableStateOf<String?>(null) }
        val scope = rememberCoroutineScope()

        fun refresh() {
            scope.launch {
                loading = true; error = null
                try { courses = ApiClient.getCourses() }
                catch (e: Exception) { error = e.message }
                loading = false
            }
        }

        LaunchedEffect(Unit) { refresh() }

        // Navegação entre telas
        when (currentScreen) {
            Screen.LIST -> CourseListScreen(
                courses = courses,
                loading = loading,
                error = error,
                onRefresh = { refresh() },
                onAddCourse = { currentScreen = Screen.ADD }
            )
            Screen.ADD -> AddCourseScreen(
                onBack = { currentScreen = Screen.LIST },
                onCourseCreated = {
                    currentScreen = Screen.LIST
                    refresh()   // Recarrega a lista com o curso novo!
                }
            )
        }
    }
}
```

O `App()` agora é apenas um **controlador de navegação**. A UI da lista foi movida para `CourseListScreen()`. Adicione essa função no mesmo arquivo:

```kotlin
@Composable
fun CourseListScreen(
    courses: List<Course>,
    loading: Boolean,
    error: String?,
    onRefresh: () -> Unit,
    onAddCourse: () -> Unit
) {
    Surface(modifier = Modifier.fillMaxSize(), color = Color.White) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .statusBarsPadding()
                .padding(horizontal = 16.dp, vertical = 20.dp)
        ) {
            // Header — agora com botão "+ Add"
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("Courses", fontSize = 22.sp, fontWeight = FontWeight.SemiBold)
                    Text("All available courses.", fontSize = 14.sp, color = Muted)
                }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(
                        onClick = onRefresh,
                        shape = RoundedCornerShape(6.dp),
                        border = BorderStroke(1.dp, Border)
                    ) { Text("Refresh", fontSize = 13.sp, color = Color.Black) }
                    Button(
                        onClick = onAddCourse,
                        shape = RoundedCornerShape(6.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color.Black,
                            contentColor = Color.White
                        )
                    ) { Text("+ Add", fontSize = 13.sp) }
                }
            }

            HorizontalDivider(
                modifier = Modifier.padding(vertical = 12.dp),
                color = Border
            )

            // Conteúdo (mesma lógica da etapa de estilização)
            when {
                loading -> {
                    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp), strokeWidth = 2.dp, color = Muted
                        )
                    }
                }
                error != null -> {
                    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Connection failed", fontWeight = FontWeight.Medium)
                            Spacer(Modifier.height(4.dp))
                            Text(error.orEmpty(), fontSize = 13.sp, color = Muted)
                            Spacer(Modifier.height(12.dp))
                            OutlinedButton(
                                onClick = onRefresh,
                                shape = RoundedCornerShape(6.dp),
                                border = BorderStroke(1.dp, Border)
                            ) { Text("Try again", fontSize = 13.sp, color = Color.Black) }
                        }
                    }
                }
                else -> {
                    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(courses) { course ->
                            OutlinedCard(
                                modifier = Modifier.fillMaxWidth(),
                                shape = RoundedCornerShape(8.dp),
                                border = BorderStroke(1.dp, Border),
                                colors = CardDefaults.outlinedCardColors(containerColor = Color.White)
                            ) {
                                Column(Modifier.padding(14.dp)) {
                                    Text(course.title, fontWeight = FontWeight.Medium, fontSize = 14.sp)
                                    val desc = course.description
                                    if (!desc.isNullOrBlank()) {
                                        Text(desc, fontSize = 13.sp, color = Muted)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
```

Ao rodar, o botão "+ Add" estará visível no header. Ainda não faz nada porque o `AddCourseScreen` será criado na próxima etapa.

---

### Formulário de criação de curso

Crie o arquivo `composeApp/src/androidMain/kotlin/.../AddCourseScreen.kt`:

```kotlin
package com.fatec.lddm_merge_skills

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.fatec.lddm_merge_skills.network.ApiClient
import kotlinx.coroutines.launch

// Reutilizando as cores do tema
private val Border = Color(0xFFE5E7EB)
private val Muted = Color(0xFF6B7280)
private val SuccessGreen = Color(0xFF16A34A)

@Composable
fun AddCourseScreen(
    onBack: () -> Unit,
    onCourseCreated: () -> Unit
) {
    var title by remember { mutableStateOf("") }
    var description by remember { mutableStateOf("") }
    var saving by remember { mutableStateOf(false) }
    var message by remember { mutableStateOf<String?>(null) }
    var isError by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    Surface(modifier = Modifier.fillMaxSize(), color = Color.White) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .statusBarsPadding()
                .padding(horizontal = 16.dp, vertical = 20.dp)
        ) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("New Course", fontSize = 22.sp, fontWeight = FontWeight.SemiBold)
                    Text("Fill in the details below.", fontSize = 14.sp, color = Muted)
                }
                OutlinedButton(
                    onClick = onBack,
                    shape = RoundedCornerShape(6.dp),
                    border = BorderStroke(1.dp, Border)
                ) { Text("← Back", fontSize = 13.sp, color = Color.Black) }
            }

            HorizontalDivider(
                modifier = Modifier.padding(vertical = 12.dp),
                color = Border
            )

            // Campo: Título
            Text("Title *", fontSize = 13.sp, fontWeight = FontWeight.Medium)
            Spacer(Modifier.height(4.dp))
            OutlinedTextField(
                value = title,
                onValueChange = { title = it },
                modifier = Modifier.fillMaxWidth(),
                placeholder = { Text("Ex: Kotlin Basics", color = Muted) },
                shape = RoundedCornerShape(6.dp),
                singleLine = true,
                colors = OutlinedTextFieldDefaults.colors(
                    unfocusedBorderColor = Border,
                    focusedBorderColor = Color.Black
                )
            )

            Spacer(Modifier.height(16.dp))

            // Campo: Descrição
            Text("Description", fontSize = 13.sp, fontWeight = FontWeight.Medium)
            Spacer(Modifier.height(4.dp))
            OutlinedTextField(
                value = description,
                onValueChange = { description = it },
                modifier = Modifier.fillMaxWidth().height(120.dp),
                placeholder = { Text("Course description (optional)", color = Muted) },
                shape = RoundedCornerShape(6.dp),
                maxLines = 5,
                colors = OutlinedTextFieldDefaults.colors(
                    unfocusedBorderColor = Border,
                    focusedBorderColor = Color.Black
                )
            )

            Spacer(Modifier.height(24.dp))

            // Botão Salvar
            Button(
                onClick = {
                    if (title.isBlank()) {
                        message = "Title is required."
                        isError = true
                        return@Button
                    }
                    scope.launch {
                        saving = true; message = null
                        try {
                            ApiClient.createCourse(
                                title = title.trim(),
                                description = description.trim().ifBlank { null }
                            )
                            message = "Course created!"
                            isError = false
                            kotlinx.coroutines.delay(600)
                            onCourseCreated()  // Volta para a lista
                        } catch (e: Exception) {
                            message = "Error: ${e.message}"
                            isError = true
                        }
                        saving = false
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(6.dp),
                enabled = !saving,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color.Black,
                    contentColor = Color.White
                )
            ) {
                if (saving) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(16.dp),
                        strokeWidth = 2.dp,
                        color = Color.White
                    )
                    Spacer(Modifier.width(8.dp))
                }
                Text(if (saving) "Saving..." else "Save Course", fontSize = 14.sp)
            }

            // Feedback
            if (message != null) {
                Spacer(Modifier.height(12.dp))
                Text(
                    message!!,
                    fontSize = 13.sp,
                    color = if (isError) Color(0xFFDC2626) else SuccessGreen,
                    fontWeight = FontWeight.Medium
                )
            }
        }
    }
}
```

Com isso, o fluxo completo estará funcional:

1. Toque em **"+ Add"** → abre o formulário
2. Preencha o título e a descrição
3. Toque em **"Save Course"** → faz POST na API
4. Retorna automaticamente para a lista com o novo curso
