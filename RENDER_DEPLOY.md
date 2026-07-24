# Deploy no Render (modo simples)

Esta é a forma mais simples de colocar o backend no ar: sem VPS, sem Nginx, sem
configurar SSL manualmente. O [Render](https://render.com) cuida de tudo isso
automaticamente — inclusive domínio próprio com certificado SSL grátis.

## TL;DR

1. `git push` deste projeto para um repositório no GitHub.
2. No Render: **New +** → **Blueprint** → selecione o repositório → **Apply**.
3. Espere o primeiro deploy terminar → aba **Shell** do serviço → `flask create-admin`.
4. Acesse `https://SEU-SERVICO.onrender.com/admin/login`.

O restante deste guia detalha cada etapa e cobre domínio próprio, atualizações
e solução de problemas comuns.

## Passo a passo

### 1. Suba o projeto para o GitHub

O Render faz deploy a partir de um repositório Git. Se você ainda não tem um:

```bash
cd bentao-backend
git init
git add .
git commit -m "Deploy inicial - Bentão Atacado"
```

Crie um repositório vazio no GitHub (ou GitLab) e depois:

```bash
git remote add origin https://github.com/SEU-USUARIO/bentao-backend.git
git branch -M main
git push -u origin main
```

### 2. Crie o Blueprint no Render

1. Acesse [dashboard.render.com](https://dashboard.render.com) e faça login (ou crie uma conta grátis).
2. Clique em **New +** → **Blueprint**.
3. Selecione o repositório que você acabou de criar.
4. O Render vai detectar o arquivo `render.yaml` deste projeto e mostrar o que será criado:
   - Um **Web Service** (o backend Flask, rodando com Gunicorn)
   - Um **banco PostgreSQL** gerenciado (plano gratuito)
   - Um **disco persistente** de 1GB para guardar as imagens enviadas pelo painel
5. Clique em **Apply** / **Create**. O Render vai instalar as dependências e aplicar
   as migrações do banco automaticamente (isso está definido em `render-build.sh`).
6. Em alguns minutos, o serviço estará no ar em uma URL como:
   `https://bentao-backend.onrender.com` — já com HTTPS ativo por padrão.

### 3. Crie o usuário administrador

O Render não permite instalação interativa durante o build, então o admin é
criado depois do primeiro deploy, usando o terminal do próprio painel do Render:

1. No painel do serviço `bentao-backend`, clique na aba **Shell**.
2. Rode:

   ```bash
   flask create-admin
   ```

3. Responda usuário, e-mail e senha quando solicitado. Pronto — acesse
   `https://SEU-SERVICO.onrender.com/admin/login` para entrar no painel.

Opcionalmente, você também pode popular o site com o conteúdo inicial de exemplo
(caso ainda não tenha cadastrado nada):

```bash
flask seed-db
```

### 4. Usando seu próprio domínio (opcional)

Por padrão você já recebe um subdomínio gratuito `*.onrender.com` com SSL. Se
quiser usar um domínio próprio (ex: `www.bentaoatacado.com.br`):

1. No painel do serviço, vá em **Settings** → **Custom Domains** → **Add Custom Domain**.
2. Informe o domínio e siga as instruções para criar o registro DNS (`CNAME` ou `A`)
   indicado pelo Render junto ao seu provedor de domínio.
3. O Render emite e renova o certificado SSL automaticamente para o domínio — não
   é preciso rodar nada manualmente (o acme.sh usado no instalador de VPS não é
   necessário aqui, o Render já cuida disso internamente).

## Atualizações

Diferente do instalador de VPS (`deploy/install.sh` + `deploy/update.sh`), no Render
a atualização é automática: basta dar `git push` para o branch conectado
(`main`, por padrão) que o Render refaz o build (instala dependências e roda as
migrações via `render-build.sh`) e reinicia o serviço sozinho. Não é necessário
rodar `update.sh` nem fazer backup manual do banco — o Render mantém backups
automáticos do PostgreSQL gerenciado (a política de retenção depende do plano).

## Diferenças em relação ao deploy em VPS própria

| | VPS (`deploy/install.sh`) | Render (`render.yaml`) |
|---|---|---|
| SSL | ZeroSSL/Let's Encrypt via `acme.sh`, ou autoassinado (IP) | Automático e gratuito, inclusive para domínio próprio |
| Servidor web | Nginx + Gunicorn + systemd, configurados manualmente | Gerenciado inteiramente pelo Render |
| Banco de dados | PostgreSQL instalado e administrado por você | PostgreSQL gerenciado pelo Render |
| Atualizações | `sudo bash deploy/update.sh <nova-versão>` | `git push` |
| Controle/custos | Total controle, custo de VPS | Zero manutenção de infraestrutura, plano gratuito disponível (com limitações de uso) |

Use o Render se você quer a forma mais simples possível de colocar o site e o
painel no ar sem administrar servidor. Use o instalador de VPS (`deploy/install.sh`)
se precisar de mais controle, desempenho constante ou não quiser depender de um
provedor de PaaS.

## Limitações do plano gratuito do Render (importante saber)

- O Web Service gratuito "dorme" após um período de inatividade e demora alguns
  segundos para acordar na próxima visita.
- O banco PostgreSQL gratuito tem um tempo de expiração e limite de armazenamento
  (verifique as condições atuais na página de preços do Render antes de decidir).
- Para uso comercial contínuo (uma loja real recebendo clientes o tempo todo),
  o recomendado é migrar para um plano pago do Render (`starter` em diante), que
  remove o "sleep" e aumenta os limites do banco.

## Variáveis de ambiente (o que o `render.yaml` já configura)

Você não precisa preencher nada manualmente — o Blueprint já define tudo isso.
Esta tabela é só para referência, caso precise ajustar algo depois pelo painel
(**Environment** do serviço):

| Variável | Origem | Para que serve |
|---|---|---|
| `DATABASE_URL` | Preenchida automaticamente a partir do banco `bentao-db` | Conexão do backend com o PostgreSQL |
| `SECRET_KEY` | Gerada automaticamente pelo Render (`generateValue: true`) | Assinatura de sessão/cookies do Flask |
| `FLASK_ENV` | `production` (fixo no `render.yaml`) | Ativa configurações de produção |
| `SESSION_COOKIE_SECURE` / `PREFERRED_URL_SCHEME` | `true` / `https` (fixo) | Cookies seguros, já que o Render serve tudo em HTTPS |
| `PYTHON_VERSION` | `3.11.9` (fixo) | Garante a versão do Python usada no build |

## Solução de problemas comuns

**O build falhou com erro de dependência ou de banco.**
Abra a aba **Logs** do serviço no Render durante o deploy. Se o erro for de
`flask db upgrade` no `render-build.sh`, confirme que o banco `bentao-db`
apareceu como "Available" no painel antes do deploy do Web Service terminar
(na primeira vez, o Render pode levar um minuto a mais para provisionar o
banco antes do build conseguir se conectar — se falhar, clique em **Manual
Deploy** → **Deploy latest commit** para tentar de novo).

**O site abre, mas o login do admin dá "usuário ou senha inválidos".**
Confirme que você realmente rodou `flask create-admin` na aba Shell (ele não
roda sozinho — é intencional, para você escolher sua própria senha). Rode de
novo se não tiver certeza; o comando também pode ser usado para redefinir a
senha de um usuário existente.

**As imagens enviadas pelo painel somem depois de um novo deploy.**
Isso só deve acontecer se o disco persistente (`bentao-uploads`, definido no
`render.yaml`) não tiver sido criado — confira em **Disks**, na página do
serviço, se ele aparece montado em `app/static/uploads`. Sem esse disco, o
Render trata o filesystem como temporário e apaga uploads a cada deploy.

**Erro de `SSLError`/conexão recusada com o banco.**
Geralmente é o banco gratuito que "dormiu" por inatividade (assim como o Web
Service). Acesse o painel do `bentao-db` para reativá-lo, ou aguarde alguns
segundos e recarregue a página.

**Quero rodar comandos manuais (seed, criar outro admin, ver dados).**
Use sempre a aba **Shell** do serviço no painel do Render — ela já abre com o
ambiente virtual e as variáveis de ambiente corretas carregadas, então basta
rodar `flask <comando>` diretamente.
