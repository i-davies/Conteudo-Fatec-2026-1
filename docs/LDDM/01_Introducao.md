# Introdução

> Material didático para a aula introdutória de Laboratório de Desenvolvimento Mobile (LDDM).
> 

---

## Slides

<div style="position: relative; width: 100%; height: 0; padding-top: 56.2500%;
 padding-bottom: 0; box-shadow: 0 2px 8px 0 rgba(63,69,81,0.16); margin-top: 1.6em; margin-bottom: 0.9em; overflow: hidden;
 border-radius: 8px; will-change: transform;">
  <iframe loading="lazy" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0; border: none; padding: 0;margin: 0;"
    src="https://www.canva.com/design/DAHBAzhu_tI/36BOlRDtq2KyCYkcQe8Z2A/view?embed" allowfullscreen="allowfullscreen" allow="fullscreen">
  </iframe>
</div>
<a href="https:&#x2F;&#x2F;www.canva.com&#x2F;design&#x2F;DAHBAzhu_tI&#x2F;36BOlRDtq2KyCYkcQe8Z2A&#x2F;view?utm_content=DAHBAzhu_tI&amp;utm_campaign=designshare&amp;utm_medium=embeds&amp;utm_source=link" target="_blank" rel="noopener">LDDM</a> de Icaro Davies

## Ferramentas e Tecnologias

!!! info "Objetivos"
    * Consolidar o uso da linguagem Kotlin no desenvolvimento multiplataforma.
    * Configurar o ambiente com IntelliJ IDEA e gerenciamento via Gradle (Kotlin DSL).

!!! abstract "Stack Tecnológica"
    * **Linguagem**: Kotlin.
    * **Gerenciador**: Gradle (Kotlin DSL).
    * **API/Server**: Ktor.
    * **Banco de Dados**: PostgreSQL / Supabase.
    * **Interface**: Jetpack Compose.

---

## Kotlin Multiplatform (KMP)

!!! info "Objetivos"
    * Entender a diferença entre compartilhar UI e compartilhar lógica de negócio.
    * Unificar modelos, validações e chamadas de API em um único lugar.

!!! abstract "Conceitos-chave"
    * **Shared Logic**: Compartilha o "cérebro" do app (lógica, banco de dados e APIs).
    * **Native UI**: O usuário mantém a performance e os componentes originais de cada sistema (Android, iOS, Web, etc.).
    * **Casos de Sucesso**: Utilizado por gigantes como McDonald's, Google Workspace e Duolingo.

---

## Ktor Framework

!!! info "Objetivos"
    * Construir servidores robustos e clientes de API leves.
    * Migrar backends legados (ex: Flask) para uma infraestrutura assíncrona.

!!! abstract "Diferenciais"
    * **Assíncrono**: Construído sobre Coroutines para ser não-bloqueante e leve.
    * **Multiplataforma**: Funciona perfeitamente dentro do ecossistema KMP.
    * **DSL Intuitiva**: Facilita a definição de rotas e configurações de forma segura.

---

## Supabase & PostgreSQL

!!! info "Objetivos"
    * Escalar o PostgreSQL com ferramentas de Backend as a Service (BaaS).
    * Implementar busca vetorial para funcionalidades de Inteligência Artificial.

!!! abstract "Recursos Integrados"
    * **Auth Integrado**: Gerenciamento de usuários pronto para uso.
    * **Realtime**: Sincronização de dados em tempo real.
    * **Vector Search**: Armazenamento e busca de embeddings para IA.

---

## O que vamos construir?

!!! info "Roteiro do Projeto: Merge Skills"
    1.  **Migração do Backend**: Evoluir a lógica de Flask para Ktor.
    2.  **Shared Module**: Unificar regras de negócio com KMP.
    3.  **Domínio do Supabase**: Implementar autenticação e busca vetorial.
    4.  **App Admin**: Criar interface nativa moderna com Jetpack Compose.

---

## Exercícios de fixação

> Responda às questões abaixo para consolidar os conceitos de desenvolvimento multiplataforma.

<quiz>
Qual é a principal filosofia do Kotlin Multiplatform (KMP)?

* [ ] Rodar a mesma interface de usuário (UI) em todos os lugares.
* [x] Compartilhar a lógica de negócio mantendo a liberdade da UI nativa.
* [ ] Substituir completamente o desenvolvimento nativo de Android e iOS.
</quiz>

<quiz>
Sobre o framework Ktor, qual característica o torna ideal para aplicações modernas?

* [ ] É um framework pesado baseado em Java antigo.
* [ ] Funciona apenas para criar servidores, não clientes.
* [x] É assíncrono, leve e construído especificamente para Kotlin.
</quiz>

<quiz>
Qual recurso do Supabase permite implementar funcionalidades de Inteligência Artificial (IA)?

* [ ] JSONB Support
* [x] Vector Search (Busca Vetorial)
* [ ] API Auto-gerada
</quiz>

<quiz>
Quais empresas são citadas como casos de sucesso no uso de KMP?

* [ ] Apenas startups pequenas.
* [x] McDonald's, Google e Duolingo.
* [ ] Nenhuma empresa grande utiliza ainda.
</quiz>

<!-- mkdocs-quiz results -->
