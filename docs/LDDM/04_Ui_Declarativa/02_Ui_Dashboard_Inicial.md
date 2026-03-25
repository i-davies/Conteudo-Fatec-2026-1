# Dashboard Administrativo com Jetpack Compose

> Projeto utilizado: <a href="https://github.com/i-davies/lddm-merge-skills-aula" target="_blank">lddm-merge-skills</a>.

---

!!! info "Objetivo"
    Construir o Dashboard Administrativo do aplicativo Android com contadores de recursos (cursos, lições e questões) consumidos diretamente da API Ktor, utilizando Jetpack Compose de forma incremental.

!!! abstract "Pré-requisitos"
    - Backend Ktor funcionando com as rotas `/courses`, `/courses/{id}/lessons` e `/lessons/{id}/questions`.
    - `ApiClient.kt` configurado com Ktor Client e ContentNegotiation.
    - Emulador Android ou celular físico configurado.

---

## O que é Compose Multiplatform?

Nós vamos usar **Compose Multiplatform (CMP)**, que é desenvolvido pela JetBrains. Ele utiliza a exata mesma engine e API do **Jetpack Compose** (do Google), mas com capacidade de rodar não apenas no Android, mas também em iOS e Desktop. No nosso projeto atual, estamos focando no Android, mas a fundação multiplataforma já está pronta.

Diferente do jeito antigo (XML), onde você tinha `activity_main.xml` para a UI e o código Kotlin separado, com Compose **a tela é definida diretamente via código Kotlin**.

---

## Primeira Tela: do Zero

Abra o arquivo `composeApp/src/androidMain/kotlin/.../App.kt`. **Apague absolutamente tudo que estiver dentro da classe / arquivo** (mas mantenha a declaração do `package` na primeira linha).

Nós vamos começar digitando o "Hello World" mais simples possível para entender como o framework monta a tela. Digite (não copie e cole!):

```kotlin
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier

@Composable
fun App() {
    MaterialTheme {
        Text("Olá, Mundo do Compose!")
    }
}
```

??? tip "O que cada parte faz?"
    - `@Composable`: Diz ao compilador que esta função desenha algo na tela. Elementos de UI em Compose são sempre funções.
    - `MaterialTheme`: Aplica o estilo de design do Google (cores base, fontes).
    - `Text()`: O componente primitivo para exibir texto na tela.

Ao rodar, o texto aparece espremido no canto superior esquerdo — isso é esperado por enquanto.

---

## Adicionando Layout: Modifiers e Containers

Em Compose, ajustamos espaçamentos, tamanhos e cores através de `Modifier`. Digite e modifique o seu código para utilizar uma `Column` (que empilha elementos verticalmente) e uma `Surface` (que dá um "fundo" branco para a tela).

```kotlin
// ... imports ...
import androidx.compose.ui.Alignment
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun App() {
    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize(), color = Color.White) {
            
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .statusBarsPadding()    // Não deixa a UI ficar embaixo do relógio/wifi do Android
                    .padding(16.dp),        // Margem de 16 espaços (density pixels) em todos os lados
                verticalArrangement = Arrangement.Center, // Centraliza as coisas na vertical
                horizontalAlignment = Alignment.CenterHorizontally // Centraliza na horizontal
            ) {
                Text("Dashboard Administrativo", fontSize = 24.sp) // sp = scale-independent pixels
                Spacer(modifier = Modifier.height(8.dp)) // Espaçamento vazio
                Text("Bem-vindo ao LDDM Merge Skills")
            }

        }
    }
}
```

Ao rodar, o texto estará centralizado e com fundo branco constante.

---

## Consumindo a API na Tela

A tela estática não ajuda muito. Precisamos buscar dinamicamente quantos cursos existem na API.

### Preparando o Cliente HTTP

Nós já instalamos a biblioteca base do **Ktor Client** no Gradle. Agora vamos criar um objeto que sabe conversar com o nosso servidor.

**Crie um novo arquivo:** `composeApp/src/androidMain/kotlin/.../network/ApiClient.kt` e digite:

```kotlin
package com.fatec.lddm_merge_skills.network

import com.fatec.lddm_merge_skills.BASE_URL
import com.fatec.lddm_merge_skills.model.Course
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.okhttp.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.json.Json

object ApiClient {
    // 1: Configuramos o 'motor' (OkHttp) que fará a requisição real de forma nativa no Android
    private val httpClient = HttpClient(OkHttp) {
        // 2: ContentNegotiation: Um plugin que vai ler strings JSON que chegarem 
        // pela rede e convertê-las organicamente em "Data Classes" do Kotlin
        install(ContentNegotiation) {
            json(Json { ignoreUnknownKeys = true })
        }
    }

    // 3: Nossa primeira função de busca. 
    // "suspend" significa que não vai travar a tela enquanto espera a internet.
    suspend fun getCourses(): List<Course> {
        return httpClient.get("$BASE_URL/courses").body()
    }
}
```

!!! warning "Atenção ao BASE_URL"
    Em `shared/src/commonMain/kotlin/Constants.kt`, o `BASE_URL` deve apontar para `http://10.0.2.2:8080` no emulador, ou para o IP da máquina na rede Wi-Fi ao usar celular físico (ex: `http://192.168.1.10:8080`).

### Reatividade de UI — o conceito de Estado

Quando você chama uma API, o resultado não chega no mesmo milissegundo. Enquanto isso, a UI precisa mostrar "Carregando...". Quando o array de cursos chega, a UI precisa "perceber" e se redesenhar com os cursos. No Compose chamamos isso de **State** (Estado). Se o State mudar, a UI redesenha.

Modifique o seu `App.kt` introduzindo o gerenciamento de Estado:

```kotlin
// ... imports ...
import com.fatec.lddm_merge_skills.network.ApiClient
import com.fatec.lddm_merge_skills.model.Course

@Composable
fun App() {
    MaterialTheme {
        // 1. Criamos os "Estados Reactivos" que a tela vai observar:
        var coursesCount by remember { mutableStateOf(0) }
        var loading by remember { mutableStateOf(true) }

        // 2. LaunchedEffect = "Efeito colateral ao Iniciar a tela"
        // O código aqui dentro roda UMA VEZ assim que o App() é montado
        LaunchedEffect(Unit) {
            loading = true
            try {
                // Requisição na API!
                val courses = ApiClient.getCourses()
                coursesCount = courses.size // Pegamos apenas a quantidade para o Dashboard
            } catch (e: Exception) {
                println("Erro ao buscar cursos: ${e.message}")
            }
            loading = false // Terminamos de carregar
        }

        Surface(modifier = Modifier.fillMaxSize(), color = Color.White) {
            Column(
                modifier = Modifier.fillMaxSize().statusBarsPadding().padding(16.dp),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // 3. E na parte gráfica, checamos o "State" para decidir como desenhar a tela:
                if (loading) {
                    CircularProgressIndicator() // A "bolinha" girando do Material UI
                    Text("Buscando dados na API...")
                } else {
                    Text("Dados Carregados!", fontSize = 24.sp)
                    Spacer(Modifier.height(16.dp))
                    Text("Total de Cursos: $coursesCount", fontSize = 18.sp)
                }
            }
        }
    }
}
```

Com o servidor rodando (`./gradlew :server:run`), o `CircularProgressIndicator` aparece por um instante e em seguida exibe "Total de Cursos: X".

---

## Layout Moderno de Dashboard

Com a API conectada, vamos buscar mais dados e exibir KPIs no estilo do framework frontend `shadcn/ui`.

### Buscando Lições e Questões

Abra o seu `ApiClient.kt` e adicione os métodos de buscas de Lições e Questões, logo abaixo de `getCourses()`:

```kotlin
    // ... codigo anterior 
    suspend fun getLessons(courseId: Int): List<Lesson> {
        return httpClient.get("$BASE_URL/courses/$courseId/lessons").body()
    }

    suspend fun getQuestions(lessonId: Int): List<Question> {
        return httpClient.get("$BASE_URL/lessons/$lessonId/questions").body()
    }
```

### O Componente Card

Podemos criar novos `@Composable` sempre que quisermos evitar código repetido. 
Crie a função `DashboardCard` no final do arquivo `App.kt` (fora da função `App()`):

```kotlin
// ... no FINAL do arquivo App.kt

// Cores Constantes (design estilo shadcn/ui)
private val Border = Color(0xFFE5E7EB)
private val Muted = Color(0xFF6B7280)

@Composable
fun DashboardCard(title: String, value: String, modifier: Modifier = Modifier) {
    OutlinedCard(
        modifier = modifier,  // Permite passar coisas como peso "weight(1f)"
        shape = RoundedCornerShape(8.dp),  // Cantos suavemente curvados
        border = BorderStroke(1.dp, Border), // Borda fina acinzentada
        colors = CardDefaults.outlinedCardColors(containerColor = Color.White)
    ) {
        Column(Modifier.padding(16.dp)) { // Padding INTERNO do card
            Text(title, fontSize = 13.sp, color = Muted, fontWeight = FontWeight.Medium)
            Spacer(Modifier.height(4.dp))
            Text(value, fontSize = 28.sp, fontWeight = FontWeight.Bold) // O número bem grande!
        }
    }
}
```

### Consolidando o App

Substitua agora totalmente o `App()` principal com a versão visual robusta completa:

```kotlin
@Composable
fun App() {
    MaterialTheme {
        var coursesCount by remember { mutableStateOf(0) }
        var lessonsCount by remember { mutableStateOf(0) }
        var questionsCount by remember { mutableStateOf(0) }
        var loading by remember { mutableStateOf(true) }

        LaunchedEffect(Unit) {
            try {
                // Passo 1: Busca todos os cursos
                val courses = ApiClient.getCourses()
                coursesCount = courses.size

                var totalLessons = 0
                var totalQuestions = 0

                // Passo 2: Itera os cursos e busca as Lessons e Questions relacionadas 
                // para conseguir as contagens totais (para demonstração no Dashboard)
                for (course in courses) {
                    val lessons = ApiClient.getLessons(course.id)
                    totalLessons += lessons.size
                    for (lesson in lessons) {
                        val questions = ApiClient.getQuestions(lesson.id)
                        totalQuestions += questions.size
                    }
                }
                lessonsCount = totalLessons
                questionsCount = totalQuestions

            } catch (e: Exception) {
                e.printStackTrace()
            }
            loading = false
        }

        Surface(modifier = Modifier.fillMaxSize(), color = Color.White) {
            // Em vez de centralizado como antes, 
            // este layout joga pra "Cima" e alinha ao começo da margem
            Column(
                modifier = Modifier.fillMaxSize().statusBarsPadding().padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp) 
            ) {
                // Cabeçalho da página
                Column {
                    Text("Dashboard", fontSize = 24.sp, fontWeight = FontWeight.Bold)
                    Text("System Overview", fontSize = 14.sp, color = Muted)
                }

                HorizontalDivider(color = Border) // A linha divisória reta

                if (loading) {
                    Box(Modifier.fillMaxWidth().height(200.dp), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator(color = Muted)
                    }
                } else {
                    // Distribui os nossos 3 cards usando peso (weight) 
                    // para dividirem o espaço igualmente lado a lado
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        DashboardCard("Courses", coursesCount.toString(), Modifier.weight(1f))
                        DashboardCard("Lessons", lessonsCount.toString(), Modifier.weight(1f))
                        DashboardCard("Questions", questionsCount.toString(), Modifier.weight(1f))
                    }
                }
            }
        }
    }
}
```

Ao rodar, o loading aparece por um instante e em seguida três cards surgem lado a lado com os totais de cada recurso.

---

## Formulários e Requisições POST

Com os contadores funcionando, a próxima etapa é permitir criar recursos diretamente pelo app.

### Navegação por Estado

Podemos declarar um controle simples no começo do arquivo `App.kt` e fazer com que a UI inteira seja governada por ele. 
**No começo do seu arquivo, fora de funções:**

```kotlin
// As 3 telas do nosso escopo:
enum class Screen { DASHBOARD, COURSES, ADD_COURSE }
```

### Formulário com campos de entrada

Para criar um recurso, nós enviamos um JSON (um Body) para a API via método POST (e não GET). Para montar esse corpo, o usuário digita nos TextFields de celular.

Na sua `ApiClient.kt`, cadastre nosso POST que envia as strings de forma estruturada baseada no modelo `Course`:

```kotlin
    import io.ktor.client.request.post
    import io.ktor.client.request.setBody
    import io.ktor.http.ContentType
    import io.ktor.http.contentType

    // ...
    suspend fun createCourse(title: String, description: String?): Course {
        return httpClient.post("$BASE_URL/courses") {
            contentType(ContentType.Application.Json) // Header essencial pro backend aceitar o JSON!
            setBody(Course(title = title, description = description)) // A magia converte Auto para JSON
        }.body()
    }
```

### Tela de criação de curso

Crie um novo arquivo `composeApp/src/androidMain/kotlin/.../AddCourseScreen.kt`, usando uma abordagem visual simples:

```kotlin
package com.fatec.lddm_merge_skills

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.fatec.lddm_merge_skills.network.ApiClient
import kotlinx.coroutines.launch

@Composable
fun AddCourseScreen(
    onBack: () -> Unit,
    onCourseCreated: () -> Unit // Passamos essa função de callback ("o que fazer ao terminar")
) {
    // 1. Estado para os campos de digitação (Value Holders)
    var title by remember { mutableStateOf("") }
    var description by remember { mutableStateOf("") }
    val scope = rememberCoroutineScope() // Necessário para lançar 'suspend API calls' direto num clique de botão

    Column(modifier = Modifier.fillMaxSize().statusBarsPadding().padding(16.dp)) {
        OutlinedTextField(
            value = title,
            onValueChange = { title = it }, // Cada vez q a pessoa bate o dedo na tecla, o 'estado' renova o componente todo
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Title *") },
            singleLine = true
        )

        Spacer(Modifier.height(16.dp))

        OutlinedTextField(
            value = description,
            onValueChange = { description = it },
            modifier = Modifier.fillMaxWidth().height(120.dp),
            label = { Text("Description") }
        )

        Spacer(Modifier.height(24.dp))

        // 2. Botão de enviar com Click Action
        Button(
            onClick = {
                if (title.isBlank()) return@Button // Previne crash por title vazio

                scope.launch {
                    try {
                        ApiClient.createCourse(title.trim(), description.trim().ifBlank { null })
                        onCourseCreated() // Volta para a tela principal (sucesso!)
                    } catch (e: Exception) {
                        println("Erro de Salvamento! ${e.message}")
                    }
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Save Course")
        }
        
        Spacer(Modifier.height(8.dp))
        
        TextButton(onClick = onBack, modifier = Modifier.fillMaxWidth()) {
            Text("Cancel / Voltar")
        }
    }
}
```

### Integrando as telas no App principal

Agora só precisamos que nosso App principal possibilite a troca entre aquele enorme "Dashboard" para esse novo "AddCourseScreen". Volte no arquivo `App.kt`:

1. Renomeie a sua função completa `@Composable fun App()` para `@Composable fun DashboardScreen(onNavigate: () -> Unit)`.
2. Em seguida, na DashboardScreen, lá debaixo dos seus três Cards, adicione um botão de navegação:

```kotlin
                // ... Fica Embaixo da linha do Row de DashboardCards
                Spacer(Modifier.height(16.dp))
                
                Button(
                    onClick = onNavigate, // Chame o evento de callback injetado!
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Adicionar Curso Manualmente")
                }
```
3. Finalmente, crie uma **nova** função mestre `App()` que comanda tudo via Enum (o State Controller Principal da aplicação). 

```kotlin
@Composable
fun App() {
    MaterialTheme {
        // Estado root da árvore: Define onde nosso app inteiro foca globalmente.
        var currentScreen by remember { mutableStateOf(Screen.DASHBOARD) }

        // Switch case nativo Kotlin direcionado pelo estado acima
        when (currentScreen) {
            Screen.DASHBOARD -> DashboardScreen(
                onNavigate = { currentScreen = Screen.ADD_COURSE } // Direciona pra segunda pag
            )
            // Nossa segunda pag. Quando terminar (ou cancelar), currentScreen volta a DASHBOARD.
            Screen.ADD_COURSE -> AddCourseScreen(
                onBack = { currentScreen = Screen.DASHBOARD }, 
                onCourseCreated = { currentScreen = Screen.DASHBOARD }
            )
            Screen.COURSES -> {} // Em branco por enquanto pro futuro da semana 7
        }
    }
}
```

Com isso, o app possui um Dashboard funcional com contadores reais e uma tela de criação de cursos integrada ao banco de dados.
