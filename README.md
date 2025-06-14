# GID Painel - Dockerized Django + PostgreSQL + Caddy

O Escritório de Gestão de Indicadores da UFRJ ([GID](https://pr2.ufrj.br/gid)) desenvolveu este painel com o intuito de promover acesso perene às mais diversas métricas e dados institucionais. Sendo um órgão vinculado à Pró-Reitoria de Pesquisa e Pós-Graduação ([PR-2](https://pr2.ufrj.br/)), a ferramenta é especialmente focada em dados associados à produção científica e atuação dos PPGs (Programas de Pós-Graduação).

A aplicação, desenvolvida primariamente em Django, é dividida em vários subpainéis, que detalham vários aspectos da pesquisa e pós-graduação da UFRJ. Esperamos que estes proverão informações valiosas tanto para uso institucional interno (em auditoria e gerenciamento, por exemplo) quanto para o consumo pelo público geral.

O deploy da aplicação utiliza **Docker Compose** com serviços para o backend (Django + Gunicorn), banco de dados (PostgreSQL), servidor web (Caddy) e um serviço auxiliar para **inicialização da base de dados**.


---

## 🔧 Requisitos

- Docker
- Docker Compose

---

## 🚀 Subindo a Aplicação

1. Copie o `.env.example` para `.env` e configure as variáveis de ambiente:

```bash
cp .env.example .env
```

2. Construa e inicie os serviços principais:

```bash
docker compose up -d
```

3. Execute o script de inicialização da base de dados (migrações, coleta de estáticos e importação inicial):

```bash
docker compose run --rm init-db
```
**Nota:** A importação inicial depende de arquivos csvs previamente adicionados à pasta `importar`, que deve estar na raiz do projeto.

---

## 🛠 Serviços

### `gid-painel`

- Serviço principal Django (usando Gunicorn).
- Lê as configurações do arquivo `.env`.
- Expõe a aplicação internamente na porta definida por `DJANGO_PORT`.
- Serve arquivos estáticos no volume `static_volume`.

### `postgres`

- Banco de dados PostgreSQL.
- Inicializado com as credenciais definidas no `.env`.
- Utiliza volume persistente `postgres_data`.

### `init-db`

- Serviço opcional para **migração e importação inicial**.
- Executa os seguintes comandos:
  - `python manage.py migrate`
  - `python manage.py collectstatic`
  - `python manage.py importar_programas`
  - `python manage.py importar_rankings`
- Deve ser executado manualmente com `--rm` para auto remoção.

### `caddy`

- Servidor HTTP/HTTPS reverso para servir o Django com TLS automático via Let's Encrypt.
- Usa as variáveis `CADDY_DOMAIN` e `CADDY_EMAIL` para configuração de domínio e certificado.
- Serve os arquivos estáticos a partir do volume compartilhado `static_volume`.
- Único serviço que mapeará portas do sistema operacional hospedeiro, definindo a porta em que a aplicação será disponibilizada.
- Pode ser usado com outro proxy reverso externo.
- Para HTTPS (terminação SSL/TLS) diretamente no Caddy, a linha referente à configuração tls deve ser descomentada em `caddy/Caddyfile`.

---

## 📁 Estrutura de Volumes

- `static_volume`: arquivos estáticos coletados pelo Django.
- `postgres_data`: dados persistentes do banco de dados PostgreSQL.
- `caddy_data`: certificados SSL e cache usados pelo Caddy.

---

## 📄 Variáveis de Ambiente (.env)

```env
# Django
DJANGO_SECRET_KEY=sua_chave_secreta_aqui
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_PORT=8000
GUNICORN_WORKERS=1
DJANGO_STATIC_ROOT=/app/staticfiles

# Banco de Dados PostgreSQL
POSTGRES_USER=gid
POSTGRES_DB=gid_db
POSTGRES_PASSWORD=gid_dashboard
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Caddy
CADDY_DOMAIN=localhost
CADDY_EMAIL=dev@example.com
```

> **Nota:** Para gerar uma chave segura do Django, use:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

## 🌐 Acesso à Aplicação

Após subir os serviços:

- Acesse via navegador: [http://localhost:8000](http://localhost:8000)
- Em produção, substitua `localhost` por seu domínio real.

---

## 🗑️ Parar e Limpar

Parar todos os serviços:

```bash
docker compose down
```

Parar e remover volumes persistentes:

```bash
docker compose down -v
```

---

## 📝 Licença

Este projeto é mantido pelo Escritório de Gestão de Indicadores Institucionais da UFRJ ([GID](https://pr2.ufrj.br/gid)). Licenciamento e termos de uso podem ser definidos conforme sua organização.
