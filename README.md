# trends_library

## Overview

Automated Trend Library is a Python-based platform that collects trending topics from Google Trends for over 100 countries, generates long-form articles and high-resolution images using AI models (GPT‑4o, DALL·E 3), and publishes the content to a web portal.

## Features

- **Data collection** – Periodically crawls Google Trends via PyTrends and RSS feeds. Supports 18 Google categories with a configurable polling interval (default 10 minutes) and a nightly full refresh.
- **Content generation** – Uses OpenAI GPT‑4o to author multi‑section articles (introduction, history, current situation, impact, FAQ) in the native language of each country. Generates a 1024×1024 8K quality cover image with an alt‑text for accessibility.
- **Publishing** – Sends the generated articles to a Strapi CMS via a REST endpoint (`/articles`) with idempotent versioning. The resulting URL template is `/country/category/slug`.
- **Web portal** – A Next.js single‑page application displays a library of trends. The `/latest` page lists recent posts with real‑time updates, pagination, and sorting.
- **Infrastructure** – Built with FastAPI, Celery, PostgreSQL, S3, Redis/RabbitMQ, GitHub Actions, Helm/Kubernetes and optional deployment on Hugging Face Spaces. Monitoring via Prometheus/Grafana and Sentry.

## Repository structure

- `trends_crawler/` – collects trending searches.
- `article_generator/` – wraps OpenAI chat completions to produce articles.
- `image_creator/` – wraps OpenAI image generation.
- `publisher/` – REST client for the CMS.
- `server/` – FastAPI app providing internal API endpoints.
- `celery_app.py` – Celery configuration and tasks.
- `docs/` – Documentation (OpenAPI JSON, architecture diagrams).
- `.github/workflows/` – CI/CD pipelines.
- `requirements.txt` – Python dependencies.

## Getting started

1. Ensure Python 3.12 is installed.
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set environment variables for your OpenAI API key (`OPENAI_API_KEY`), CMS base URL (`CMS_BASE_URL`) and authentication token (`CMS_TOKEN`).
5. Start the Celery worker and beat scheduler:
   ```bash
   celery -A celery_app.celery_app worker -B --loglevel=info
   ```
6. Run the FastAPI server:
   ```bash
   uvicorn server.main:app --host 0.0.0.0 --port 8000
   ```

## CI/CD

The repository includes GitHub Actions workflows for linting, testing, building Docker images and deploying with Helm. These workflows run automatically on pull requests and pushes to the `dev` and `main` branches.

## Documentation

OpenAPI schema and architecture diagrams will be placed under the `/docs` folder.
