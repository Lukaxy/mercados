# Bentão Atacado — Backend + Painel Admin

Backend completo para gerenciar a landing page do **Bentão Atacado** (Sidrolândia - MS),
com painel administrativo profissional e banco de dados PostgreSQL. O projeto traz
dois caminhos de deploy prontos — escolha o que fizer mais sentido para você:

| | Recomendado para | SSL / domínio |
|---|---|---|
| 🚀 **[Deploy no Render](RENDER_DEPLOY.md)** (mais simples) | Quem quer colocar no ar rápido, sem administrar servidor | Automático, grátis, sem configuração |
| 🖥️ **[Deploy em VPS própria](#instalação-em-produção-vps-ubuntudebian)** | Quem já tem/quer uma VPS e mais controle sobre a infraestrutura | Via `acme.sh` (ZeroSSL/Let's Encrypt) ou autoassinado (IP) |

**Se você só quer subir o site o mais rápido possível, vá direto para o
[guia de deploy no Render](RENDER_DEPLOY.md)** — não precisa ler o resto deste
README para isso. As seções abaixo cobrem a stack, a estrutura do projeto e o
deploy manual em VPS (mais avançado).

## Stack utilizada

- **Flask 3** (app factory, blueprints) — backend e servidor da landing page
- **PostgreSQL** + **SQLAlchemy** + **Flask-Migrate (Alembic)** — banco de dados e migrações
- **Flask-Login** — autenticação do painel admin
- **Flask-WTF / WTForms** — formulários e proteção CSRF
- **Pillow** — otimização/redimensionamento de imagens enviadas
- **Gunicorn** — servidor WSGI de produção
- **HTMX** + **Alpine.js** + **Tailwind CSS** (via CDN) — frontend do painel admin, leve e reativo, sem build step
- **Nginx** — proxy reverso e terminação SSL (apenas no deploy em VPS própria)
- **acme.sh** — emissão e renovação automática de certificados SSL (ZeroSSL por padrão, ou Let's Encrypt — apenas no deploy em VPS própria; no Render o SSL é automático)

## O que o painel administra

Tudo o que aparece na landing page é editável pelo painel, sem precisar mexer em código:

- Barra superior (texto e selo de destaque)
- Seção principal (hero): textos, botões, estatísticas e slides do carrossel
- Galeria de fotos da loja
- Departamentos / abas ("Nossos Departamentos")
- Ofertas / encarte da semana (produtos com preço, preço antigo, categoria, destaque)
- Localização, horário de funcionamento e mapa incorporado
- Número e mensagens padrão do WhatsApp
- Identidade (nome do site, logotipo, favicon, descrição para SEO)
- Usuários administradores (criar, desativar, remover outros admins — apenas para administradores "master")

## Estrutura do projeto

```
bentao-backend/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Configurações (dev/produção)
│   ├── extensions.py        # db, migrate, login_manager, csrf
│   ├── models.py            # Modelos (AdminUser, SiteSettings, HeroSlide, GalleryItem, Department, Offer)
│   ├── cli.py                # Comandos: flask create-admin / flask seed-db
│   ├── public/routes.py      # Rota pública que renderiza a landing page
│   ├── admin/routes.py       # Rotas do painel administrativo
│   ├── admin/forms.py        # Formulários (WTForms)
│   ├── utils/uploads.py      # Upload e otimização de imagens
│   ├── templates/public/     # Template da landing page (Tailwind)
│   └── templates/admin/      # Templates do painel (Tailwind + HTMX + Alpine)
├── migrations/                # Migrações Alembic (Flask-Migrate)
├── seed_data.py                # Popula o banco com o conteúdo original do site
├── wsgi.py                     # Ponto de entrada para Gunicorn
├── requirements.txt
├── .env.example
├── render.yaml                 # Blueprint de deploy no Render (1 clique)
├── render-build.sh             # Build usado pelo Render (instala deps + roda migrações)
├── RENDER_DEPLOY.md             # Guia passo a passo do deploy no Render
└── deploy/
    ├── install.sh               # Instalador completo (VPS nova)
    ├── update.sh                 # Rotina de atualização segura
    ├── nginx/site.conf.template
    └── systemd/bentao-backend.service.template
```

## Deploy rápido no Render (recomendado para a maioria dos casos)

Não exige VPS, Nginx ou configuração de SSL — o Render cuida de tudo, inclusive
domínio próprio com certificado grátis. Resumo dos passos (guia completo em
**[RENDER_DEPLOY.md](RENDER_DEPLOY.md)**):

1. Suba este projeto para um repositório no GitHub.
2. No painel do Render, crie um **Blueprint** apontando para o repositório — ele lê
   o `render.yaml` e cria sozinho o Web Service, o banco PostgreSQL e o disco
   persistente para as imagens enviadas pelo painel.
3. Depois do primeiro deploy, abra a aba **Shell** do serviço no Render e rode
   `flask create-admin` para criar seu usuário administrador.
4. Pronto — acesse `https://SEU-SERVICO.onrender.com/admin/login`.

Atualizações depois disso são só `git push`: o Render refaz o build e reinicia
sozinho (instalando dependências e aplicando migrações via `render-build.sh`).

## Instalação em produção (VPS Ubuntu/Debian)

> Esta seção é para quem prefere administrar a própria VPS em vez de usar o
> Render. Se você só quer o caminho mais simples, use o
> [deploy no Render](RENDER_DEPLOY.md) acima e pule esta seção.

1. Envie esta pasta para o seu servidor (ex: via `scp` ou `rsync`) e extraia o `.zip`.
2. Entre na pasta do projeto e rode o instalador como root:

   ```bash
   cd bentao-backend
   sudo bash deploy/install.sh
   ```

3. O instalador vai perguntar, interativamente:
   - Diretório de instalação (padrão `/opt/bentao-backend`)
   - Se você tem um **domínio** apontado para o servidor, ou se quer usar **apenas o IP**
   - Se usar domínio: qual CA usar (**ZeroSSL** ou **Let's Encrypt**) e um e-mail de contato
   - Nome/usuário/senha do banco PostgreSQL (senha pode ser gerada automaticamente)
   - Se deseja popular o site com o conteúdo inicial de exemplo (recomendado na 1ª instalação)
   - **Usuário, e-mail e senha do administrador do painel** (criado na hora, com senha oculta)

4. Ao final, o instalador exibe a URL do site, a URL do painel (`/admin/login`) e as credenciais do banco.

### O que o instalador configura automaticamente

- Pacotes do sistema (Python, PostgreSQL, Nginx, acme.sh)
- Usuário de sistema dedicado rodando o serviço (sem privilégios de root)
- Ambiente virtual Python isolado e dependências
- Banco de dados e usuário PostgreSQL
- Arquivo `.env` com `SECRET_KEY` aleatória e credenciais do banco
- Migrações do banco de dados (`flask db upgrade`)
- Serviço `systemd` (`bentao-backend`) rodando Gunicorn, com reinício automático em caso de falha
- Nginx como proxy reverso, com redirecionamento HTTP → HTTPS
- **Certificado SSL**:
  - Com domínio: emitido via `acme.sh` (ZeroSSL ou Let's Encrypt), com **renovação automática** (o próprio `acme.sh` instala uma tarefa agendada)
  - Sem domínio (apenas IP): certificado autoassinado (o navegador mostrará um aviso de segurança até que um domínio seja configurado — isso é uma limitação das autoridades certificadoras públicas, que não emitem certificados válidos para IPs)
- Firewall (`ufw`) liberando apenas SSH, HTTP e HTTPS

## Atualizações (rotina simples e segura)

Sempre que houver uma nova versão do backend:

```bash
sudo bash deploy/update.sh /caminho/para/nova-versao-extraida
```

O script:

1. Faz backup do banco de dados (`pg_dump`) e do `.env` antes de qualquer alteração
2. Sincroniza o novo código, preservando `.env`, uploads de imagens e o ambiente virtual
3. Atualiza as dependências Python
4. Aplica novas migrações do banco de dados
5. Reinicia o serviço e valida se a aplicação voltou a responder
6. **Se algo falhar, restaura automaticamente o backup do banco** e mostra os logs do erro

## Uso local para desenvolvimento

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edite .env e configure DATABASE_URL para seu Postgres local
# (ou aponte para um SQLite local: DATABASE_URL=sqlite:///dev.db)

export FLASK_APP=wsgi.py
export FLASK_ENV=development

flask db upgrade
flask seed-db            # opcional: conteúdo inicial de exemplo
flask create-admin       # cria seu usuário administrador

flask run
```

Acesse `http://localhost:5000/` para o site e `http://localhost:5000/admin/login` para o painel.

## Comandos úteis (CLI Flask)

```bash
flask create-admin     # cria ou atualiza um administrador (interativo)
flask seed-db           # popula o banco com o conteúdo inicial de exemplo
flask db upgrade        # aplica migrações pendentes
flask db migrate -m ""  # gera uma nova migração após alterar app/models.py
```

## Segurança

- Senhas de administrador são armazenadas com hash (`werkzeug.security`), nunca em texto puro.
- Todos os formulários do painel são protegidos por CSRF (Flask-WTF), inclusive as
  requisições feitas via HTMX (o token é injetado automaticamente no header `X-CSRFToken`).
- O `.env` tem permissões restritas (`600`) e nunca deve ser versionado em Git.
- O serviço systemd roda com um usuário sem privilégios, `NoNewPrivileges` e acesso de
  escrita restrito apenas ao diretório da aplicação.
- Recomenda-se trocar a senha do banco de dados e revisar os usuários administradores
  periodicamente pelo próprio painel (`/admin/users`).

## Observações sobre o certificado sem domínio

Nenhuma autoridade certificadora pública (ZeroSSL, Let's Encrypt, etc.) emite certificados
válidos para um endereço IP puro — isso é uma regra do ecossistema de certificados, não uma
limitação deste sistema. Ao optar por "apenas IP" na instalação, o instalador gera um
certificado autoassinado, que criptografa a conexão normalmente, mas exibirá um aviso de
segurança no navegador até que os visitantes aceitem a exceção manualmente. Assim que você
tiver um domínio, basta reexecutar `sudo bash deploy/install.sh` (ou rodar novamente apenas
a etapa de SSL) para obter um certificado confiável automaticamente.
