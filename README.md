# CHINT Caucasus — Corporate Platform

Corporate website and product catalog platform for **CHINT Caucasus**, the regional representative of [CHINT Global](https://chintglobal.com) — a global leader in intelligent electrical and energy solutions operating in 140+ countries.

🔗 **Live:** [chintcaucasus.com](https://chintcaucasus.com)

Developed end-to-end (backend, architecture, infrastructure, deployment) at [DAKER Studio](https://daker.site).

---

## Overview

A multilingual corporate platform that presents CHINT's industrial and energy product range in the Caucasus market, with an automated product catalog synced from CHINT's partner system.

## Key Features

- **Multilingual** — English, Russian, Azerbaijani, and Georgian via Django i18n
- **Product catalog** — hierarchical categories, product properties, technical documents, and certificates
- **External API integration** — automated catalog synchronization with CHINT's partner platform
- **Multi-database architecture** — separate database routing for catalog data
- **Content management** — news, library documents, and homepage content managed via Django admin

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.13, Django 5.1 |
| Database | SQLite (multi-DB with custom router) |
| Frontend | Django Templates, vanilla JS, CSS |
| Integration | CHINT partner REST API (`requests`) |
| Deployment | Docker, Gunicorn, Nginx, VPS |

## Architecture Highlights

- **Custom database router** (`config/db_router.py`) — routes catalog models to a dedicated database, keeping product data isolated from site content
- **Management commands** — `sync_chint`, `catalog_import`, and maintenance commands automate catalog synchronization and cleanup
- **Service layer** — catalog import, category tree building, and breadcrumb generation separated into dedicated service modules
- **Modular apps** — `catalog`, `web`, and `api` separated by responsibility

## Running Locally

```bash
# Clone and enter
git clone https://github.com/dakerdenis/chint.git
cd chint

# Set up environment
cp .env.example .env        # then fill in your values

# With Docker
docker compose up --build

# Or manually
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Environment Variables

See `.env.example` for the full list. Required:

- `DJANGO_SECRET_KEY` — Django secret key
- `DJANGO_DEBUG` — `True` / `False`
- `DJANGO_ALLOWED_HOSTS` — comma-separated hosts
- `CHINT_API_KEY` — API key for catalog synchronization
- `CHINT_API_BASE_URL` — partner API base URL

---

## Result

A stable, scalable, and maintainable corporate platform representing a global brand in the Caucasus region — built from scratch with full infrastructure ownership handed over to the client.

<sub>Built by [Denis Akershteyn](https://www.linkedin.com/in/denis-akershteyn) · [DAKER Studio](https://daker.site)</sub>