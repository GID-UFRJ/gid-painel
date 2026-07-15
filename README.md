# GID Painel - Dockerized Django + PostgreSQL + Caddy + Redis

O Escritório de Gestão de Indicadores da UFRJ ([GID](https://pr2.ufrj.br/gid)) desenvolveu este painel com o intuito de promover acesso perene às mais diversas métricas e dados institucionais. Sendo um órgão vinculado à Pró-Reitoria de Pesquisa e Pós-Graduação ([PR-2](https://pr2.ufrj.br/)), a ferramenta é especialmente focada em dados associados à produção científica e atuação dos PPGs (Programas de Pós-Graduação).

A aplicação, desenvolvida primariamente em Django, é dividida em vários subpainéis, que detalham vários aspectos da pesquisa e pós-graduação da UFRJ. Esperamos que estes proverão informações valiosas tanto para uso institucional interno (em auditoria e gerenciamento, por exemplo) quanto para o consumo pelo público geral.

O deploy da aplicação utiliza **Docker Compose** com serviços para o backend (Django + Gunicorn), banco de dados (PostgreSQL), cache (Redis), servidor web (Caddy) e um sistema de atualização automática (Watchtower).

---

## 🔧 Requisitos

- Docker
- Docker Compose

---

## 🚀 Subindo a Aplicação

1. Copie o `.env.example` para `.env` e configure as variáveis de ambiente:

bash
cp .env.example .env


2. Construa e inicie os serviços:

bash
docker compose up -d


*Nota: As migrações do banco de dados, coleta de estáticos e outras inicializações são tratadas internamente pelo contêiner `gid-painel`.*

---

## 📊 Importação e Atualização de Dados

Todo o processo de importação e atualização do banco de dados é realizado de forma gráfica e integrada **através do Painel de Controle da aplicação**. Após subir os contêineres e acessar o sistema com o seu superusuário, basta navegar até a área administrativa para baixar o dump mais recente e atualizar o banco de dados.

---

## 🛠 Serviços

### `gid-painel`

- Serviço principal Django (usando Gunicorn).
- Lê as configurações do arquivo `.env`.
- Expõe a aplicação internamente para o Caddy.
- Serve arquivos estáticos no volume `static_volume`.
- Monitorado pelo Watchtower para atualizações automáticas via label.

### `postgres`

- Banco de dados PostgreSQL (versão 17.5).
- Inicializado com as credenciais definidas no `.env`.
- Utiliza volume persistente `postgres_data`.

### `redis`

- Servidor Redis (7-alpine) usado para cache e outras funcionalidades.
- Configuração padrão com limite de memória de 64MB e política `allkeys-lru`.

### `caddy`

- Servidor HTTP/HTTPS reverso para servir o Django com TLS automático via Let's Encrypt.
- Usa as variáveis `CADDY_DOMAIN` e `CADDY_EMAIL` para configuração de domínio e certificado.
- Serve os arquivos estáticos a partir do volume compartilhado `static_volume`.
- Expõe as portas 80 (HTTP) e 443 (HTTPS/QUIC) mapeadas para 8000 e 8443 no host.

### `watchtower` e `dockerproxy`

- **Watchtower:** Verifica automaticamente por novas versões da imagem `gidpr2/gid-painel` e atualiza o contêiner sem intervenção manual.
- **Docker Socket Proxy:** Aumenta a segurança limitando o acesso do Watchtower apenas às APIs estritamente necessárias do Docker, bloqueando comandos perigosos.

---

## 📁 Estrutura de Volumes

- `static_volume`: arquivos estáticos coletados pelo Django e compartilhados com o Caddy.
- `postgres_data`: dados persistentes do banco de dados PostgreSQL.
- `caddy_data`: certificados SSL e configurações persistentes do Caddy.

---

## 📄 Variáveis de Ambiente (.env)

Exemplo de configuração básica:

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

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=1

# Credenciais Superusuário Django (Opcional para primeiro setup)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=senha_segura

# Caddy
CADDY_DOMAIN=localhost
CADDY_EMAIL=dev@example.com

# Dump Database URL (Para atualizações)
DUMP_URL=https://doi.org/10.5281/zenodo.20563334
```


> **Nota:** Para gerar uma chave segura do Django, use:
> ``bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

## 🌐 Acesso à Aplicação

Após subir os serviços, a aplicação estará disponível na porta 8000 (HTTP) ou 8443 (HTTPS):

- Acesse via navegador: [http://localhost:8000](http://localhost:8000)
- Em produção, substitua `localhost` pelo domínio configurado em `CADDY_DOMAIN`.

---

## 🗑️ Parar e Limpar

Parar todos os serviços:

bash
docker compose down


Parar e remover volumes persistentes (Isso apagará o banco de dados):

bash
docker compose down -v


---

## 📝 Licença

Este projeto é mantido pelo Escritório de Gestão de Indicadores Institucionais da UFRJ ([GID](https://pr2.ufrj.br/gid)). Licenciamento e termos de uso podem ser definidos conforme sua organização.