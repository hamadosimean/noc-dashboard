# 🖥️ NOC ANPTIC Dashboard

> **Tableau de bord du Centre des Opérations Réseau (NOC) de l'ANPTIC**  
> Network Operations Center dashboard for centralized KPI monitoring, availability tracking, and real-time incident management.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Design System & Theming](#design-system--theming)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Configure Environment Variables](#2-configure-environment-variables)
  - [3. Run with Docker (Recommended)](#3-run-with-docker-recommended)
  - [4. Run Locally (Development)](#4-run-locally-development)
- [Services & Ports](#services--ports)
- [Supervision Map](#supervision-map)
- [Authentication](#authentication)
- [Branding: Logo & Favicon](#branding-logo--favicon)
- [Integrations](#integrations)
- [API Documentation](#api-documentation)
- [Demo Data & Simulator](#demo-data--simulator)
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
                        │   :80 → 301 redirect     :443 TLS (self-      │
                        │                          signed cert)         │
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

                        ┌─────────────────────────────────────────────┐
                        │  ETL simulator — posts a synthetic incident  │
                        │  to /api/incidents/ingest every 20-60s        │
                        └─────────────────────────────────────────────┘
```

| Layer | Technology | Role |
|---|---|---|
| **Frontend** | React 19 + Vite | Interactive real-time dashboard UI |
| **Backend** | FastAPI (Python 3.12) | REST API, KPI computation, webhooks, JWT auth |
| **Database** | PostgreSQL 15 | Persistent storage (dimensions, incidents, users) |
| **Cache** | Redis 7 | KPI caching, performance optimization |
| **Proxy** | NGINX | TLS termination, HTTP→HTTPS redirect, reverse proxy |
| **ETL** | Python | Simulates supervision-tool webhooks so the demo feels live |

---

## Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** `0.103.1` — Modern async Python web framework
- **[SQLAlchemy](https://www.sqlalchemy.org/)** `2.0.36` — Python ORM
- **[Uvicorn](https://www.uvicorn.org/)** `0.23.2` — ASGI server
- **[Psycopg2](https://www.psycopg.org/)** `2.9.10` — PostgreSQL adapter
- **[Redis-py](https://redis-py.readthedocs.io/)** `5.0.0` — Redis client
- **[fpdf2](https://pypi.org/project/fpdf2/)** `2.7.9` — Monthly report PDF export
- **[Python-dotenv](https://pypi.org/project/python-dotenv/)** `1.0.0` — Environment variable management

### Frontend
- **[React](https://react.dev/)** `19` — UI library
- **[Vite](https://vite.dev/)** `8` — Build tool & dev server
- **[TailwindCSS](https://tailwindcss.com/)** `4` — Utility-first CSS framework
- **[TanStack Query](https://tanstack.com/query)** `5` — Server state management & caching
- **[Axios](https://axios-http.com/)** — HTTP client
- **[Chart.js](https://www.chartjs.org/) + react-chartjs-2** — Data visualization & charting
- **[Leaflet](https://leafletjs.com/) + react-leaflet** — Supervision map (OpenStreetMap tiles)
- **[Zustand](https://zustand-demo.pmnd.rs/)** `5` — Global state management
- **[React Router DOM](https://reactrouter.com/)** `7` — Client-side routing
- **[Lucide React](https://lucide.dev/)** — Icon library
- **[date-fns](https://date-fns.org/)** — Date utility library

---

## Design System & Theming

The dashboard is **dark-first**: a NOC command-center aesthetic, with a fully supported light mode reached via the sun/moon toggle in the header (state persisted in `localStorage`, see `frontend/src/store/theme.js`). Tailwind v4's class-based dark variant is enabled in `frontend/src/index.css`:

```css
@custom-variant dark (&:where(.dark, .dark *));
```

All surface/text/accent colors are CSS custom properties (`--color-page`, `--color-surface`, `--color-accent`, …) defined once for each theme in `index.css`, so components read `var(--color-*)` rather than hardcoding Tailwind gray/blue shades — flipping the `.dark` class on `<html>` re-themes the whole app instantly, charts included.

Chart/map colors can't use CSS variables (Chart.js and Leaflet's canvas/SVG rendering don't see them), so the same palette is mirrored as plain JS constants in `frontend/src/theme/colors.js`:

- **Categorical** (chart series) and **status** (severity/availability) colors were run through the [dataviz skill](https://github.com/anthropics/claude-code)'s six-check validator — lightness band, chroma floor, CVD (colorblind) separation, and contrast — against both the light (`#fcfcfb`) and dark (`#0b1220`) surfaces actually used here.
- `useChartTheme()` (`frontend/src/hooks/useChartTheme.js`) exposes the active theme's chrome (grid/axis/ink) and categorical ramp to every Chart.js component.
- Status colors (`good`/`warning`/`serious`/`critical`) are fixed and reused everywhere severity or availability is encoded (badges, map markers, SLA trackers) — never repurposed as a chart series color.

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
│
├── database/
│   ├── 01_schema.sql             # DB schema (tables, indexes, materialized view, dim_user)
│   ├── 02_seed.sql               # Generated demo dataset (see below) — auto-run after the schema
│   └── generate_seed.py          # Regenerates 02_seed.sql (regions/localities/nodes/incidents/demo users)
│
├── nginx/
│   ├── Dockerfile
│   ├── nginx.conf                # HTTP->HTTPS redirect + TLS termination + reverse proxy
│   ├── generate_cert.sh          # Regenerates the self-signed cert in certs/
│   └── certs/                    # Self-signed TLS cert/key (gitignored — never commit)
│
├── backend/                      # FastAPI application (Python 3.12)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py               # FastAPI entry point, CORS + router wiring
│       ├── core/                 # Config/constants, security (JWT + webhook API key)
│       ├── db/                   # SQLAlchemy session & Redis client
│       ├── models/               # SQLAlchemy ORM models (dimensions, fact_incident, dim_user)
│       ├── schemas/               # Pydantic request/response schemas
│       ├── routes/               # REST endpoint routers (/api/kpi, /api/sla, /api/alerts, /api/incidents, /api/auth, /api/report)
│       └── services/             # Business logic (KPI queries, incident lifecycle, cache, auth, iTop stub, PDF report)
│
├── frontend/                     # React application (Vite)
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js            # Includes a dev-server proxy: /api -> localhost:8000
│   ├── tailwind.config.js
│   ├── index.html                # Favicon links + <title>
│   ├── generate_icons.py         # Regenerates favicons/logo variants from the master logo (see Branding)
│   ├── public/                   # favicon.ico, favicon-*.png, apple-touch-icon.png, icon-*.png
│   └── src/
│       ├── App.jsx               # Root component + route protection (redirects to /login)
│       ├── main.jsx              # React entry point (wraps app in QueryClientProvider)
│       ├── index.css             # Design tokens (CSS vars per theme) + Leaflet theming
│       ├── theme/colors.js       # Chart/map color constants (validated palette, mirrors index.css)
│       ├── assets/images/        # Brand assets (master logo + generated sizes)
│       ├── api/                  # Axios HTTP clients (kpi, sla, alerts, auth) + auth interceptor
│       ├── components/           # Reusable UI components
│       │   ├── charts/           # Chart.js-based chart components (theme-aware)
│       │   ├── map/              # BurkinaFasoMap (Leaflet/OSM) + LocalityBulletList
│       │   └── layout/           # Header, TabNav
│       ├── hooks/                # useKPI, useRealtime, useChartTheme, useClock
│       ├── pages/                # Login + dashboard views (Global, Localities, SLA, Interop, Data Model)
│       └── store/                # Zustand stores: period, theme, auth (persisted)
│
└── etl/                          # Simulated collector service (see "Demo Data & Simulator" below)
    ├── app.py                    # Entry point: waits for the API, then runs the collector loop
    ├── extract/                  # Per-tool event simulators (Zabbix/Nagios/NetXMS/Centreon)
    ├── transform/                # Normalizes simulator events into the ingest payload shape
    └── load/                     # Posts normalized incidents to /api/incidents/ingest
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

# ── Webhook auth ─────────────────────────────────────────
# Static bearer key supervision tools (Centreon/Zabbix) must send when
# calling POST /api/incidents/ingest — Authorization: Bearer $NOC_API_KEY
NOC_API_KEY=your_webhook_api_key

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
| **Application (via NGINX, HTTPS)** | https://localhost:8443 | Main entry point — self-signed cert, browser will warn |
| **Application (via NGINX, HTTP)** | http://localhost:8888 | Redirects (301) to the HTTPS URL above |
| **Frontend** | http://localhost:3000 | React dashboard UI, direct (no TLS) |
| **Backend API** | http://localhost:8000 | FastAPI REST API, direct (no TLS) |
| **API Docs (Swagger)** | http://localhost:8000/docs | Interactive API documentation |
| **API Docs (ReDoc)** | http://localhost:8000/redoc | Alternative API documentation |

> **Note:** The frontend (`:3000`) and backend (`:8000`) ports are exposed directly for debugging and bypass TLS entirely. Only the NGINX gateway enforces HTTPS.

### HTTPS / TLS

The NGINX gateway terminates TLS with a **self-signed certificate** (cahier des charges §10.1: "HTTPS obligatoire"), generated by `nginx/generate_cert.sh` into `nginx/certs/` (gitignored — never commit private keys). Because it's self-signed, browsers and `curl` will flag it as untrusted:

```bash
# Browser: click through the "not secure" warning (expected for self-signed certs)
curl -k https://localhost:8443/api/kpi/summary?month=7&year=2026   # -k skips cert verification
```

To regenerate the certificate (e.g. after its ~825-day validity expires, or to add another SAN entry):

```bash
./nginx/generate_cert.sh
docker compose restart nginx
```

For a real deployment, replace `nginx/certs/*` with a certificate from Let's Encrypt or ANPTIC's internal CA — the generated cert's CN/SAN already match the production domains referenced elsewhere in this README (`noc.anptic.bf`, `noc-api.anptic.bf`).

---

## Supervision Map

The "Vue Globale" and "Vue par Localité" tabs render a real **Leaflet + OpenStreetMap** map of Burkina Faso (`frontend/src/components/map/BurkinaFasoMap.jsx`), fed by `GET /api/kpi/localities/map` (every locality with coordinates, incident count, and availability for the selected month — unlike `/api/kpi/localities`, this one includes localities with zero incidents so the map never has "missing" nodes).

- **Markers**: colored by availability (green ≥97%, amber 90–97%, red <90%), sized by incident volume (`sqrt` scale), with a pulsing ring on critical ones. Hover for a tooltip, click to select.
- **Dark mode**: OSM only publishes one (light) cartography, so dark mode applies a CSS filter (`invert + hue-rotate + contrast`) scoped to just the tile pane in `index.css` (`.leaflet-dark-map .leaflet-tile-pane`) — markers/popups are on a separate pane and stay unaffected.
- **Scroll-zoom gating**: the map requires one click before the scroll wheel zooms it (with a fading hint chip), so scrolling the dashboard page over the map doesn't get hijacked into zooming it — a standard embedded-map pattern.
- **Bounded**: `maxBounds`/`minZoom`/`maxZoom` keep panning/zooming scoped to Burkina Faso.
- **`LocalityBulletList`** (the panel next to the map) is the same data as a plain clickable list — a table-view/keyboard-accessible companion to the map, not just decoration.
- **Cross-page navigation**: clicking a marker or bullet in "Vue Globale" calls `navigate('/locality', { state: { localityId } })`; `LocalityView` reads that state to preselect the clicked locality (falling back to the busiest one if navigated to directly via the tab).

---

## Authentication

The dashboard is gated behind a login screen (`/login`) with two methods, both
issuing the same JWT (`dim_user` table, `backend/app/services/auth_service.py`):

- **Username + password** — bcrypt-hashed.
- **PIN quick login** — a 4-digit code, SHA-256 hashed for fast direct lookup
  (a short PIN doesn't warrant adaptive hashing, and needs to support lookup
  by hash rather than iterating every user).

Demo accounts (seeded by `database/generate_seed.py`):

| Username | Password | PIN | Role |
|---|---|---|---|
| `admin` | `admin123` | `1234` | admin |
| `analyst` | `analyst123` | `2222` | analyst |
| `noc_agent` | `noc123` | `3333` | noc_agent |

The frontend stores the JWT in `localStorage` (zustand `persist`, see
`frontend/src/store/auth.js`) and attaches it to every API call via an axios
request interceptor; a 401 response anywhere logs the session out. Only the
incident-action endpoints (`acknowledge`/`resolve`) require the JWT server-side
today — read endpoints stay open, matching the demo's read-heavy dashboard use.

---

## Branding: Logo & Favicon

The app logo (`frontend/src/assets/images/noc-logo.png`) is the brand master asset: a navy-and-signal-blue mark (location pin + radio/signal waves) matching the dashboard's dark-first palette. It's used directly in the `Header` and `Login` page, and derived into the full browser favicon set.

The source PNG shipped with a plain white canvas around a rounded-square mark (no alpha channel) — unusable as-is on a dark header, since the white corners would show as a halo. `frontend/generate_icons.py` (Pillow) fixes this and produces every size the app needs:

- Masks the 4 corners transparent using a **geometric rounded-rect mask**, not color-keying — the mark itself has white accents (the signal-gap bar) that color-keying on "near white" would incorrectly erase.
- Writes back the cleaned master (`noc-logo.png`, transparent corners) plus a light `noc-logo-256.png` actually imported by the UI (the raw master is 1254px/1.2MB — far more than a ~56px header icon needs; 256px covers retina displays at that size for ~70KB).
- Flattens onto the brand navy (`#0b1220`) for the favicon set, since transparency reads worse than a solid tab-color background at 16–32px: `favicon.ico` (multi-size), `favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png` (180px), `icon-192.png`, `icon-512.png` — all in `frontend/public/`, linked from `frontend/index.html`.

Re-run after swapping in a new logo:

```bash
python3 frontend/generate_icons.py
```

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

Key endpoints (all read endpoints take `month`/`year` query params):

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/kpi/summary` | Monthly KPI summary + delta vs. previous month |
| GET | `/api/kpi/localities` | Top localities by incident count |
| GET | `/api/kpi/nodes` | Top nodes (optionally filtered by `locality_id`) |
| GET | `/api/kpi/recurrent` | Nodes with ≥ `min_count` incidents |
| GET | `/api/kpi/trend` | Last N months of incidents/availability |
| GET | `/api/kpi/hour-distribution` | Incidents per hour of day (H24) |
| GET | `/api/kpi/causes` | Incident breakdown by cause category |
| GET | `/api/sla` | SLA indicators vs. targets |
| GET | `/api/alerts/open` | Open/acknowledged alerts, oldest first |
| GET | `/api/locality/{id}/nodes` | Node detail for one locality |
| GET | `/api/kpi/localities/map` | Every locality with coordinates + KPIs, for the map |
| POST | `/api/incidents/ingest` | Webhook ingestion (requires `Authorization: Bearer $NOC_API_KEY`) |
| PATCH | `/api/incidents/{id}/acknowledge` | Mark an incident acknowledged (requires login) |
| PATCH | `/api/incidents/{id}/resolve` | Resolve an incident (requires login) |
| GET | `/api/report/monthly` | Monthly report, `format=json` or `format=pdf` |
| POST | `/api/auth/login` | Username/password login → JWT |
| POST | `/api/auth/pin-login` | 4-digit PIN quick login → JWT |
| GET | `/api/auth/me` | Current user (session restore) |

---

## Demo Data & Simulator

The database ships with a generated demo dataset so the dashboard is fully interactive out of the box — no real Zabbix/Nagios/Centreon/iTop instance required:

- **13 regions**, **14 localities**, **~157 nodes** across Burkina Faso, **6 months of incidents**, and the 3 demo user accounts (see [Authentication](#authentication)) — all in `database/02_seed.sql`, produced by `database/generate_seed.py`.
- On a **fresh** Postgres volume, `01_schema.sql` then `02_seed.sql` run automatically via `docker-entrypoint-initdb.d`. To regenerate the dataset or force a reseed:
  ```bash
  python3 database/generate_seed.py   # rewrites database/02_seed.sql
  docker compose down
  docker volume rm noc_pgdata         # drops the existing DB so init scripts re-run
  docker compose up -d
  ```
- The **`etl` service** keeps the dashboard feeling live: it simulates a supervision-tool alert on a random active node every 20–60s and posts it to `/api/incidents/ingest`, approximating the always-on Zabbix/Nagios/Centreon → webhook flow from the cahier des charges (§2.2, §7.1). Its collectors (`etl/extract/simulators.py`) are stand-ins — swap them for real HTTP calls once real supervision tools are reachable.
- iTop ticket creation is similarly stubbed (`backend/app/services/itop_service.py`): it mints a `TKT-<year>-<id>` reference in the same shape the real iTop REST webservice would return.

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
