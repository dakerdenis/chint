# CHINT Caucasus — Corporate Platform

![CI](https://github.com/dakerdenis/chint/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)
![Ruff](https://img.shields.io/badge/linting-ruff-261230?logo=ruff&logoColor=white)

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
| Quality | Ruff (linting), GitHub Actions (CI) |

## Architecture Highlights

- **Custom database router** (`config/db_router.py`) — routes catalog models to a dedicated database, keeping product data isolated from site content
- **Management commands** — `sync_chint`, `catalog_import`, and maintenance commands automate catalog synchronization and cleanup
- **Service layer** — catalog import, category tree building, and breadcrumb generation separated into dedicated service modules
- **Modular apps** — `catalog`, `web`, and `api` separated by responsibility
- **Health-check endpoint** — `/health/` for container orchestration and uptime monitoring

## Code Quality & CI

Every push runs an automated pipeline via GitHub