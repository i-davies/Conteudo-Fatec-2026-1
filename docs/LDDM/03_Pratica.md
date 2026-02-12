# Exemplo: KMP + Ktor + Compose

> Material didático para a aula prática de LDDM.
> Projeto utilizado: [lddm-primeiro-projeto](https://github.com/i-davies/lddm-primeiro-projeto).

---


!!! info "Objetivos"
- Criar um exemplo mínimo com Shared Logic, Server Ktor e UI Compose.

## 1. Shared: Lógica Compartilhada

Vamos começar criando as classes e funções que serão usadas tanto pelo Android/Desktop quanto pelo Servidor (Backend).

Crie/Edite o arquivo: `shared/src/commonMain/kotlin/com/example/kmp_intro/SimpleExamples.kt`

```kotlin
val courseName = "LDDM"

fun sum(a: Int, b: Int): Int = a + b

class Aluno(val nome: String, val idade: Int) {
    fun resumo(): String = "$nome ($idade)"
}
```

---

## 2. Shared: Configuração de Host (Platform-Specific)

Como o emulador Android usa um IP diferente (`10.0.2.2`) para acessar o localhost do computador, precisamos de uma lógica específica por plataforma.

**Common (Interface)**
`shared/src/commonMain/kotlin/com/example/kmp_intro/Platform.kt` (adicione no final)
```kotlin
expect fun serverHost(): String
```

**Android (Implementação)**
`shared/src/androidMain/kotlin/com/example/kmp_intro/Platform.android.kt`
```kotlin
actual fun serverHost(): String = "10.0.2.2"
```

**JVM/Desktop (Implementação)**
`shared/src/jvmMain/kotlin/com/example/kmp_intro/Platform.jvm.kt`
```kotlin
actual fun serverHost(): String = "localhost"
```

---

## 3. Shared: Cliente HTTP (Ktor)

Vamos configurar o Ktor Client para fazer requisições HTTP.

**Common (Lógica do Cliente)**
`shared/src/commonMain/kotlin/com/example/kmp_intro/ApiClient.kt`

```kotlin
import io.ktor.client.HttpClient
import io.ktor.client.request.get
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.client.statement.bodyAsText

expect fun createHttpClient(): HttpClient

class ApiClient {
    private val client = createHttpClient()
    private val baseUrl = "http://${serverHost()}:$SERVER_PORT" // Verifique a porta do seu server

    suspend fun hello(): String = client.get("$baseUrl/hello").bodyAsText()

    suspend fun echo(text: String): String = client.post("$baseUrl/echo") {
        setBody(text)
    }.bodyAsText()
}
```

**Android (Engine OkHttp)**
`shared/src/androidMain/kotlin/com/example/kmp_intro/HttpClient.android.kt`

```kotlin
import io.ktor.client.HttpClient
import io.ktor.client.engine.okhttp.OkHttp

actual fun createHttpClient(): HttpClient = HttpClient(OkHttp)
```

**JVM (Engine CIO)**
`shared/src/jvmMain/kotlin/com/example/kmp_intro/HttpClient.jvm.kt`

```kotlin
import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO

actual fun createHttpClient(): HttpClient = HttpClient(CIO)
```

---

## 4. Dependências (Gradle)

Verifique se as bibliotecas do Ktor estão declaradas.

`gradle/libs.versions.toml`

Adicione as bibliotecas:

```toml
ktor-clientCore = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }
ktor-clientOkHttp = { module = "io.ktor:ktor-client-okhttp", version.ref = "ktor" }
ktor-clientCio = { module = "io.ktor:ktor-client-cio", version.ref = "ktor" }
kotlinx-coroutinesCore = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "kotlinx-coroutines" }
```

No arquivo `shared/build.gradle.kts`:

```kotlin
// commonMain
implementation(libs.ktor.clientCore)
implementation(libs.kotlinx.coroutinesCore)

// androidMain
implementation(libs.ktor.clientOkHttp)

// jvmMain
implementation(libs.ktor.clientCio)
```

---

## 5. Server Ktor: Rotas

No módulo do servidor, vamos criar rotas simples para serem consumidas.

Edite: `server/src/main/kotlin/com/example/kmp_intro/Application.kt`

```kotlin
routing {
    get("/hello") { 
        call.respondText("Olá! ${Greeting().greet()}") 
    }
    
    post("/echo") { 
        call.respondText(call.receiveText()) 
    }
}
```

---

## 6. Compose UI (Common)

Agora vamos criar a interface que será compartilhada (Android e Desktop) e que consumirá nossa API e lógica compartilhada.

Edite: `composeApp/src/commonMain/kotlin/com/example/kmp_intro/App.kt`

```kotlin
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.safeContentPadding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import kotlinx.coroutines.launch

@Composable
@Preview
fun App() {
    MaterialTheme {
        // remember guarda o valor entre as recomposicoes (quando o Compose redesenha a UI).
        // mutableStateOf cria um estado observavel; quando muda, a UI e redesenhada.
        var apiText by remember { mutableStateOf("-") }
        var isLoading by remember { mutableStateOf(false) }
        val scope = rememberCoroutineScope()
        // Estas classes/funcoes estao no modulo shared e no mesmo package
        // (com.example.kmp_intro), por isso o Kotlin encontra sem import explicito.
        val api = remember { ApiClient() }
        val aluno = remember { Aluno("Ana", 20) }
        Column(
            modifier = Modifier
                .safeContentPadding()
                .fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            val greeting = remember { Greeting().greet() }
            Text("Compose: $greeting")
            Text("Variavel: $courseName")
            Text("Funcao: 2 + 3 = ${sum(2, 3)}")
            Text("Classe: ${aluno.resumo()}")
            Button(
                onClick = {
                    isLoading = true
                    scope.launch {
                        apiText = api.hello()
                        isLoading = false
                    }
                }
            ) {
                Text("GET /hello")
            }
            Button(
                onClick = {
                    isLoading = true
                    scope.launch {
                        apiText = api.echo("Oi do Compose")
                        isLoading = false
                    }
                }
            ) {
                Text("POST /echo")
            }
            Text("API: ${if (isLoading) "carregando..." else apiText}")
        }
    }
}
```

---

## 7. Executando o Projeto

1.  **Inicie o Servidor**:
    Execute o comando ou a configuração de Run do módulo `:server`.
    ```bash
    ./gradlew :server:run
    ```

2.  **Rode o App Android e Desktop**:
    Selecione e execute as configurações `composeApp` (Android) e `composeApp[desktop]`.

3.  **Teste**:
    Clique nos botões e veja a mágica acontecer! O app fará requisições para o seu servidor local, compartilhando a lógica de negócios e a UI.
