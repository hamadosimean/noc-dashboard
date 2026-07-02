# 🖥️ NOC ANPTIC Dashboard

> **Tableau de bord du Centre des Opérations Réseau (NOC) de l'ANPTIC**  
> Network Operations Center dashboard for centralized KPI monitoring, availability tracking, and real-time incident management.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Configure Environment Variables](#2-configure-environment-variables)
  - [3. Run with Docker (Recommended)](#3-run-with-docker-recommended)
  - [4. Run Locally (Development)](#4-run-locally-development)
- [Services & Ports](#services--ports)
- [Integrations](#integrations)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)

---

## Overview

The NOC ANPTIC Dashboard centralizes network availability KPIs and incident data in real time. It integrates with industry-standard monitoring tools:

- **[Zabbix](https://www.zabbix.com/)** — Infrastructure and network monitoring
- **[Nagios](https://www.nagios.org/)** — IT infrastructure monitoring
- **[Centreon](https://www.centreon.com/)** — IT monitoring and observability platform
- **[NetXMS](https://www.netxms.org/)** — Network and infrastructure monitoring
- **[iTop](https://www.combodo.com/itop)** — IT Service Management (ITSM) & CMDB

---

## Architecture

The application follows a **containerized 3-tier architecture** orchestrated via Docker Compose:

```
                        ┌─────────────────────────────────────────────┐
                        │                   NGINX                      │
                        │              Reverse Proxy (:80)             │
                        └──────────────────┬──────────────────────────┘
                                           │
                        ┌──────────────────┴──────────────────┐
                        │                                      │
              ┌─────────▼──────────┐              ┌───────────▼────────┐
              │     Frontend       │              │      Backend       │
              │  React + Vite      │              │  FastAPI (Python)  │
              │     (:3000)        │              │      (:8000)       │
              └────────────────────┘              └──────┬─────┬───────┘
                                                         │     │
                                              ┌──────────▼─┐ ┌▼──────────┐
                                              │ PostgreSQL  │ │   Redis   │
                                              │  Database  │ │   Cache   │
                                              │  (:5432)   │ │  (:6379)  │
                                              └────────────┘ └───────────┘
```

| Layer | Technology | Role |
|---|---|---|
| **Frontend** | React 19 + Vite | Interactive real-time dashboard UI |
| **Backend** | FastAPI (Python 3.12) | REST API, KPI computation, webhooks |
| **Database** | PostgreSQL 15 | Persistent storage (dimensions & incidents) |
| **Cache** | Redis 7 | KPI caching, performance optimization |
| **Proxy** | NGINX | Traffic routing and reverse proxy |

---

## Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** `0.103.1` — Modern async Python web framework
- **[SQLAlchemy](https://www.sqlalchemy.org/)** `2.0.20` — Python ORM
- **[Uvicorn](https://www.uvicorn.org/)** `0.23.2` — ASGI server
- **[Psycopg2](https://www.psycopg.org/)** `2.9.7` — PostgreSQL adapter
- **[Redis-py](https://redis-py.readthedocs.io/)** `5.0.0` — Redis client
- **[Python-dotenv](https://pypi.org/project/python-dotenv/)** `1.0.0` — Environment variable management

### Frontend
- **[React](https://react.dev/)** `19` — UI library
- **[Vite](https://vite.dev/)** `8` — Build tool & dev server
- **[TailwindCSS](https://tailwindcss.com/)** `4` — Utility-first CSS framework
- **[TanStack Query](https://tanstack.com/query)** `5` — Server state management & caching
- **[Axios](https://axios-http.com/)** — HTTP client
- **[Chart.js](https://www.chartjs.org/) + react-chartjs-2** — Data visualization & charting
- **[Zustand](https://zustand-demo.pmnd.rs/)** `5` — Global state management
- **[React Router DOM](https://reactrouter.com/)** `7` — Client-side routing
- **[Lucide React](https://lucide.dev/)** — Icon library
- **[date-fns](https://date-fns.org/)** — Date utility library

---

## Prerequisites

Ensure you have the following installed before running the project:

| Tool | Minimum Version | Install |
|---|---|---|
| **Docker** | 24+ | [docs.docker.com](https://docs.docker.com/get-docker/) |
| **Docker Compose** | 2.20+ | Included with Docker Desktop |
| **Git** | Any | [git-scm.com](https://git-scm.com/) |
| **Node.js** *(dev only)* | 20+ | [nodejs.org](https://nodejs.org/) |
| **Python** *(dev only)* | 3.12+ | [python.org](https://www.python.org/) |

---

## Project Structure

```
noc/
├── .env                          # Environment variables (⚠️ never commit secrets!)
├── .gitignore
├── docker-compose.yml            # Docker service definitions
├── DOCUMENTATION.md              # Technical architecture documentation (French)
│
├── database/
│   └── init.sql                  # DB schema initialization (auto-run on first start)
│
├── nginx/
│   └── nginx.conf                # Reverse proxy routing rules
│
├── backend/                      # FastAPI application (Python 3.12)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py               # FastAPI entry point
│       ├── api/                  # REST endpoint routers (/api/kpi, /api/alerts, etc.)
│       ├── core/                 # Config, security (JWT), constants
│       ├── db/                   # Database connection & session management
│       ├── models/               # SQLAlchemy ORM models
│       ├── schemas/              # Pydantic request/response schemas
│       ├── routes/               # Additional route definitions
│       └── services/             # Business logic (KPI calculation, integrations)
│
├── frontend/                     # React application (Vite)
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── App.jsx               # Root component
│       ├── main.jsx              # React entry point
│       ├── api/                  # Axios HTTP clients for backend
│       ├── components/           # Reusable UI components
│       │   ├── charts/           # Chart.js-based chart components
│       │   └── layout/           # Navigation & layout components
│       ├── hooks/                # Custom React hooks (useKPI, useRealtime, etc.)
│       ├── pages/                # Dashboard views (Global, Localities, SLA)
│       └── store/                # Zustand global state (filters, auth, etc.)
│
└── etl/                          # ETL pipelines (data ingestion scripts)
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd noc
```

### 2. Configure Environment Variables

A `.env` file is already included in the project root. Review and update the values to match your environment before running:

```bash
# Open and edit the .env file
nano .env
```

Key variables to configure:

```env
# ── Database ─────────────────────────────────────────────
POSTGRES_USER=noc_db_user
POSTGRES_PASSWORD=your_secure_password   # ⚠️ Change this in production!
POSTGRES_DB=noc_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# ── Redis Cache ──────────────────────────────────────────
REDIS_HOST=redis
REDIS_PORT=6379
CACHE_TTL=300                            # Cache duration in seconds

# ── Security ─────────────────────────────────────────────
SECRET_KEY=your_secret_key               # ⚠️ Change this in production!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ── Monitoring Tool Integrations ─────────────────────────
ZABBIX_API_URL=http://your-zabbix-host/api_jsonrpc.php
ZABBIX_USER=your_zabbix_user
ZABBIX_PASSWORD=your_zabbix_password

ITOP_URL=http://your-itop-host/webservices/rest.php
ITOP_USER=your_itop_user
ITOP_PASS=your_itop_password

CENTREON_API_URL=http://your-centreon-host/api
CENTREON_API_KEY=your_centreon_api_key

NAGIOS_API_URL=http://your-nagios-host/
NAGIOS_API_KEY=your_nagios_api_key
```

> **⚠️ Security Note:** The `.env` file is listed in `.gitignore`. Never commit real credentials to source control. For production, use a secrets manager.

---

### 3. Run with Docker (Recommended)

This is the **easiest and recommended** method. Docker Compose will build and start all services automatically.

#### Build and Start All Services

```bash
# From the project root directory
docker-compose up --build
```

To run in **detached (background) mode**:

```bash
docker-compose up --build -d
```

#### Check Service Status

```bash
docker-compose ps
```

#### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

#### Stop All Services

```bash
docker-compose down
```

To also **remove volumes** (⚠️ this deletes all database data):

```bash
docker-compose down -v
```

#### Rebuild a Single Service

```bash
docker-compose up --build backend
docker-compose up --build frontend
```

---

### 4. Run Locally (Development)

If you prefer to develop without Docker, you can run each component separately.

#### 4a. Start Required Infrastructure

You still need PostgreSQL and Redis running. The easiest way is to start only those services via Docker:

```bash
docker-compose up -d postgres redis
```

#### 4b. Backend (FastAPI)

```bash
cd backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Update .env to use localhost for local dev
# DB_HOST=localhost, REDIS_HOST=localhost

# Start the development server (with hot-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4c. Frontend (React + Vite)

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start the Vite development server (with HMR)
npm run dev
```

The dev server starts at `http://localhost:5173` by default.

#### 4d. Other Frontend Commands

```bash
# Lint the codebase
npm run lint

# Build for production
npm run build

# Preview the production build
npm run preview
```

---

## Services & Ports

After starting the project, the following services are available:

| Service | URL | Description |
|---|---|---|
| **Application (via NGINX)** | http://localhost | Main entry point (reverse proxy) |
| **Frontend** | http://localhost:3000 | React dashboard UI |
| **Backend API** | http://localhost:8000 | FastAPI REST API |
| **API Docs (Swagger)** | http://localhost:8000/docs | Interactive API documentation |
| **API Docs (ReDoc)** | http://localhost:8000/redoc | Alternative API documentation |

> **Note:** In Docker mode, NGINX routes all traffic through port `80`. The frontend (`:3000`) and backend (`:8000`) ports are also exposed directly for debugging.

---

## Integrations

The dashboard integrates with the following monitoring systems via API or webhook:

| System | Protocol | Purpose |
|---|---|---|
| **Zabbix** | REST API (JSON-RPC) | Network infrastructure metrics |
| **Centreon** | REST API | IT monitoring events & alerts |
| **Nagios** | REST API | Host/service availability data |
| **NetXMS** | — | Network performance monitoring |
| **iTop** | REST API | Incident management & ITSM (CMDB) |

Configure integration URLs and credentials in the `.env` file as described in the [Environment Variables](#2-configure-environment-variables) section.

---

## API Documentation

Once the backend is running, interactive API documentation is available at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

Key API endpoint groups:

| Prefix | Description |
|---|---|
| `/api/kpi` | KPI metrics and aggregations |
| `/api/alerts` | Real-time alerts and incidents |
| `/api/nodes` | Network node information |
| `/api/regions` | Regional data |

---

## Contributing

1. **Fork** the repository and create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and ensure code quality:
   ```bash
   # Frontend linting
   cd frontend && npm run lint

   # Backend: ensure no broken imports
   cd backend && python -m py_compile app/main.py
   ```

3. **Commit** with a clear message:
   ```bash
   git commit -m "feat: add your feature description"
   ```

4. **Push** and open a Pull Request.

---

<div align="center">
  <sub>Built for <strong>ANPTIC</strong> — Agence Nationale de Promotion des TIC</sub>
</div>
