# Zircon FRT

**OSINT Web Portal for Automated Data Collection, Storage, Search & Monitoring**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org)

---

## About

Zircon FRT is a web portal for automated collection, storage, search, and monitoring of data for OSINT activities. It provides a unified workspace for:

- **Uploading & indexing** local files (TXT, CSV, JSON, SQL, PDF, DOCX, XLSX)
- **Full-text search** with AND/OR/NOT operators across all indexed content
- **Automated monitoring** via scheduled background tasks
- **OSINT integrations** with external services (Shodan, VirusTotal, Censys, etc.)
- **Brand protection** monitoring and alerting

**Target audience:** Cybersecurity specialists, OSINT analysts, brand protection and anti-fraud teams.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Nginx (Port 80)                       │
│              Reverse proxy + static file serving             │
└─────────┬───────────────────────────────────┬───────────────┘
          │ /api/*                            │ /*
          ▼                                   ▼
┌─────────────────┐                 ┌──────────────────┐
│  FastAPI Backend │                 │  React Frontend  │
│  Python 3.12    │                 │  Vite + Tailwind │
│  Port 8000      │                 │  i18n (EN/RU/UK) │
└────────┬────────┘                 └──────────────────┘
         │
    ┌────┴──────────────────────────────────┐
    │                                       │
    ▼                                       ▼
┌──────────┐  ┌──────────┐  ┌────────────┐  ┌────────┐
│PostgreSQL│  │  Redis   │  │Elasticsearch│  │ClamAV │
│   16     │  │    7     │  │     8      │  │ Daemon │
└──────────┘  └──────────┘  └────────────┘  └────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌───────────────┐  ┌─────────────────┐
│ Celery Worker │  │  Celery Beat    │
│ (file tasks)  │  │  (scheduler)    │
└───────────────┘  └─────────────────┘
```

---

## Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| API Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Task Queue | Celery + Redis |
| Full-text Search | Elasticsearch 8 |
| File Parsing | PyMuPDF, python-docx, pandas/openpyxl |
| Antivirus | ClamAV (pyclamd) |
| Encryption | AES-256-GCM (cryptography) |
| HTTP Client | httpx |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 18 + TypeScript |
| Build | Vite |
| Styling | Tailwind CSS (dark cybersecurity theme) |
| State | Zustand |
| i18n | i18next (EN, RU, UK) |
| HTTP | Axios |
| Routing | react-router-dom v6 |

### Infrastructure
| Component | Technology |
|-----------|-----------|
| Containers | Docker + docker-compose |
| Reverse Proxy | Nginx |
| Database | PostgreSQL 16 |
| Cache/Broker | Redis 7 |
| Search Engine | Elasticsearch 8 |
| AV Scanning | ClamAV |

---

## Quick Start

### Prerequisites
- Docker 24+
- docker-compose 2+

### 1. Clone and configure

```bash
git clone https://github.com/oss0018/zircon.git
cd zircon
cp .env.example .env
# Edit .env and set strong values for SECRET_KEY and ENCRYPTION_KEY
```

### 2. Generate a secure encryption key

```bash
python3 -c "import base64,os; print(base64.b64encode(os.urandom(32)).decode())"
```

Set the output as `ENCRYPTION_KEY` in `.env`.

### 3. Start all services

```bash
docker-compose up --build
```

The portal will be available at **http://localhost**.

### 4. Run database migrations

```bash
docker-compose exec backend alembic upgrade head
```

---

## Project Structure

```
zircon/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/v1/             # REST endpoints (auth, files, search, ...)
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic (auth, search, indexer, ...)
│   │   ├── tasks/              # Celery tasks
│   │   └── integrations/       # OSINT integration base class
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Pytest tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # React SPA
│   ├── src/
│   │   ├── pages/              # Login, Dashboard, Files, Search, ...
│   │   ├── components/         # Reusable UI components
│   │   ├── store/              # Zustand state (auth, search)
│   │   ├── api/                # Axios client
│   │   └── i18n/               # Translations (EN, RU, UK)
│   └── Dockerfile
├── nginx/
│   └── nginx.conf              # Reverse proxy configuration
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## API Documentation

Once running, API docs are available at:

- **Swagger UI:** http://localhost/api/docs
- **ReDoc:** http://localhost/api/redoc
- **Health check:** http://localhost/api/health

### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login, get JWT |
| GET | `/api/v1/auth/me` | Get current user |
| POST | `/api/v1/files/upload` | Upload file |
| GET | `/api/v1/files/list` | List files |
| DELETE | `/api/v1/files/{id}` | Delete file |
| GET | `/api/v1/files/{id}/download` | Download file |
| POST | `/api/v1/search` | Full-text search |
| GET | `/api/v1/integrations` | List OSINT integrations |
| POST | `/api/v1/integrations` | Add integration |
| GET | `/api/v1/monitoring` | List monitoring tasks |
| POST | `/api/v1/monitoring` | Create monitoring task |
| GET | `/api/v1/brand/status` | Brand protection status |
| POST | `/api/v1/brand/scan` | Trigger brand scan |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | — | JWT signing secret (required) |
| `ENCRYPTION_KEY` | — | AES-256 key for API keys (base64, 32 bytes) |
| `POSTGRES_USER` | `zircon` | PostgreSQL username |
| `POSTGRES_PASSWORD` | — | PostgreSQL password |
| `POSTGRES_DB` | `zircon` | PostgreSQL database name |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URL |
| `ELASTICSEARCH_URL` | `http://elasticsearch:9200` | Elasticsearch URL |
| `CLAMAV_HOST` | `clamav` | ClamAV daemon host |
| `CLAMAV_PORT` | `3310` | ClamAV daemon port |
| `UPLOAD_DIR` | `./uploads` | File upload directory |
| `MAX_FILE_SIZE` | `104857600` | Max file size in bytes (100 MB) |
| `DEBUG` | `false` | Enable debug mode |
| `NGINX_HTTP_PORT` | `80` | Nginx HTTP port |

---

## Search Syntax

Zircon FRT uses Elasticsearch's `query_string` syntax:

```
password AND leaked
"exact phrase"
error OR warning
NOT test
filename:report AND 2024
```

Filters available: file type, date range, project ID.

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

---

## License

[MIT](LICENSE) © 2024 Zircon FRT