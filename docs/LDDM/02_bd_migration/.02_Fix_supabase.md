# Supabase CLI com Exposed DSL

> Documentação alternativa para resolução de problemas de rede com o Supabase.

---

!!! info "Objetivo"
    Integrar o Supabase CLI ao projeto para permitir o desenvolvimento backend com Exposed e Flyway em ambientes com restrições de rede (como proxies ou bloqueios de portas da Fatec).

---

## Preparando o Supabase CLI

Para utilizar as ferramentas do Supabase localmente e contornar bloqueios de portas de banco de dados, é necessário configurar o Supabase CLI no projeto.

**Passo 1: Verificação do Ambiente (Node.js)**

O Supabase CLI requer o Node.js para ser executado via `npx`. Verifique se a versão instalada é compatível (nos laboratórios da Fatec, utiliza-se a versão `24.12.0`):

```bash
node -v
# Esperado: v24.12.0
```

**Passo 2: Inicialização e Login**

No terminal da raiz do projeto, inicialize a estrutura da CLI e faça a autenticação:

```bash
# Inicializa o Supabase no diretório do projeto (cria a pasta supabase/)
npx supabase init

# Realiza o login na conta do Supabase (Abre o navegador para gerar o token)
npx supabase login

# Vincula o projeto local ao seu projeto remoto na nuvem (opcional para deploy)
npx supabase link --project-ref seu-project-id
```

!!! tip
    O `project-id` pode ser encontrado na URL do painel do seu projeto no Supabase. O login criará um token de acesso na sua máquina, permitindo que a CLI se comunique de forma segura com seu projeto na nuvem sem precisar de senhas a cada execução.

---

## docker-compose up vs supabase start: Qual usar?

| Característica | `docker-compose up` (Padrão) | `supabase start` (Alternativa) |
|---|---|---|
| O que ele sobe? | **Apenas** o PostgreSQL e recursos super básicos configurados no YAML. | O pacote **completo** do Supabase local (PostgreSQL, GoTrue/Auth, Storage, Studio, PostgREST). |
| Peso na máquina | Leve. | Mais pesado (sobe ~10 contêineres Docker). |
| Funcionalidades Extras | Nenhuma. | Painel local (Studio) no navegador (porta 54323) e ferramentas avançadas do CLI. |

!!! important
    Para o dia a dia e aprendizado focado no Ktor/Exposed, o **`docker-compose` é muito mais fácil**, direto e exige menos da máquina do aluno. E a boa notícia é que **podemos usar o Supabase CLI junto com o `docker-compose`**, sem a necessidade de rodar `supabase start`.

---

## Gerando SQL via Exposed DSL com o Supabase CLI usando apenas o Docker Compose

**SIM!** Essa é a principal vantagem de usar a CLI, e nem precisamos do `supabase start` para isso. Se você criou uma nova tabela no Kotlin (com Exposed) e não quer escrever o SQL de migração `.sql` manualmente, o Supabase CLI pode fazer isso por você examinando o banco do seu Docker Compose.

**Passo a passo para gerar o Diff:**

1. Certifique-se de estar rodando seu banco localmente via `docker-compose up -d`. *(Isso disponibiliza um banco para o Ktor na porta configurada, geralmente `5432`)*.
2. Atualize o seu código do Exposed (ex: `Tables.kt`) com um novo campo ou tabela.
3. Rode o seu servidor Ktor apontando para o seu banco local. Atualize as variáveis de ambiente, caso necessário:
   - `DB_URL=jdbc:postgresql://localhost:5432/mergeskills`
   - `DB_USER=devuser`
   - `DB_PASSWORD=devpassword`
4. Quando a aplicação Ktor rodar, o Exposed vai atualizar o schema criando ou alterando as tabelas dentro do banco do seu Docker.
5. Em seguida, com o código do servidor parado, execute o seguinte comando da CLI, passando a URL do banco do seu Docker:

   ```bash
   npx supabase db diff -f nome_da_sua_migracao --db-url "postgresql://devuser:devpassword@localhost:5432/mergeskills"
   ```

!!! info "Como funciona o diff"
    O Supabase CLI vai comparar o schema atual da sua pasta `supabase/migrations` (que representa o estado anterior) com o estado do banco rodando no seu Docker (modificado pelo Exposed). Ele notará as diferenças, gerará o código puramente em SQL dessa alteração (ex: `ALTER TABLE ... ADD COLUMN ...`) e salvará automaticamente a instrução na pasta `supabase/migrations/xxxx_nome_da_sua_migracao.sql`.

---

## O Comando Push e os Bloqueios de Rede

Uma vez que as migrações SQL estão criadas (seja pelo Exposed gerando ou criadas manualmente), normalmente executaríamos `npx supabase db push` para mandar as mudanças para o banco na nuvem.

**O Push vai bloquear?**

**Possivelmente sim.** O comando `supabase db push` se conecta ao banco remoto principalmente usando a porta padrão do PostgreSQL (5432) ou do pooler (6543) em segundo plano. Se a rede da faculdade intercepta conexões não web e bloqueia o protocolo nativo de bancos de dados via JDBC ou psql, o comando não conseguirá estabelecer a conexão.

**Solução Web Integrada:**

Não conseguir conectar via terminal não significa que o banco de dados não poderá ser atualizado. A interface web do Supabase acessível via porta 443 (HTTPS) nunca será bloqueada na instituição de ensino. Sempre que a faculdade bloquear o comando, siga estes passos:

1. Gere o seu script `.sql` localmente usando o passo do `db diff` ensinado acima (ou fazendo manualmente usando um `.sql` do Flyway).
2. Abra o seu arquivo da migração local e **copie todo o corpo do texto (SQL)**.
3. Acesse seu projeto pelo site oficial do [Supabase](https://supabase.com).
4. No menu lateral, acesse **SQL Editor**.
5. Crie uma **New Query**, cole o seu script SQL ali e clique em **Run**.

E o banco de dados em produção foi atualizado sem precisar burlar o proxy restrito da organização.

---

## Resumo do Fluxo em Rede Restrita

1. **Em ambiente sem restrição (Em casa):** Programe e teste utilizando todas as portas abertas (push, CLI livre, etc).
2. **Em ambiente fechado (Na faculdade):** Suba os bancos de dados **apenas localmente** executando seu conhecido `docker-compose up -d`.
3. **Propagando para a Nuvem:** Após criar e testar seu domínio e schemas locais em Kotlin com Exposed, gere os diffs apontando para o seu banco do Docker executando:
   `npx supabase db diff --db-url "URL_DO_BANCO"`
4. Utilize o **SQL Editor** no navegador no Painel do Supabase colando as migrações geradas no passo 3.

---

## Exercício de Fixação

??? example "Gerando sua primeira migração através da CLI via Docker Compose"
    **Objetivo:** Adicionar uma coluna em `Courses` usando o diff automático e Docker sem acessar uma porta restrita.

    1. Certifique-se de estar com o terminal na pasta raiz da aplicação e faça o login via terminal: `npx supabase login`.
    2. Suba em background o seu banco de dados padrão com `docker compose up -d`.
    3. Edite o arquivo `/db/Tables.kt` e inclua na sua estrutura de objeto `Courses` uma coluna de texto simples nomeada como `testColumn` ou semelhante, permitindo `nullable()`.
    4. Atualize as variáveis de configuração ou de execução local (Run Configuration) do Ktor para refletir o seu banco local (`localhost:5432` com usuário `devuser`).
    5. Inicie sua aplicação Ktor para testar a conexão e garantir que o Exposed irá criar o novo campo. Pare o Ktor após o êxito de inicialização.
    6. Execute o comando para ler a diferença baseando-se no banco local:
       `npx supabase db diff -f add_test_column --db-url "postgresql://devuser:devpassword@localhost:5432/mergeskills"`
    7. Abra a sua nova pasta do diretório raiz em `supabase/migrations/` e valide a qualidade do script gerado confirmando os comandos contidos. Esses arquivos representam as intruções exatas a rodar no editor Web.
