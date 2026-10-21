# News Application (Django)

This repository contains a Django-based News Application built for the Level 2 Capstone Project. This `README` is targeted at code reviewers and contains quick setup, testing, and deployment notes.

**Project**: News Application

**Quick Summary**
- Django backend with a custom user model and REST endpoints via DRF.
- Default database: MySQL (configurable to SQLite via environment variable).
- JWT + session authentication supported.

**Features**
- Create/read/update/delete articles
- User registration and authentication
- Newsletter creation and listing
- REST API endpoints (see `news_app/api_views.py` and `news_app/serializers.py`)

**Prerequisites**
- Python 3.11+ (match `requirements.txt`)
- pip
- MySQL server (optional; SQLite available)

**Reviewer Quick-Start (local)**
1. Create and activate venv:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment file and set values:

```bash
# PowerShell
Copy-Item .env.example .env
```

Then edit `.env` to set `SECRET_KEY`, database credentials (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, etc.), and `USE_MYSQL` if you want SQLite.

4. Apply migrations and create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Run the development server:

```bash
python manage.py runserver
```

6. Run tests:

```bash
python manage.py test
```

**Environment variables**
- See `.env.example` for all variables. Key variables:
  - `SECRET_KEY`
  - `DEBUG`
  - `USE_MYSQL` (set `false` to use SQLite)
  - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

**Notes for reviewers**
- Settings load from `.env` in `news_project/settings.py`.
- By default `EMAIL_BACKEND` is console; change in production.
- When deploying: set `DEBUG=False`, set secure `SECRET_KEY`, and configure `ALLOWED_HOSTS`.
- Run `python manage.py collectstatic` when serving static files in production.

**Files of interest**
- `news_app/models.py`, `news_app/views.py`, `news_app/serializers.py`, `news_app/urls.py`
- `news_project/settings.py` (configuration)

**Contact**
For questions, leave a review comment or contact the author.
