# News Application

## Project Description

This project is a Django-based news application designed to manage news articles, subscriptions, newsletters, and role-based user access. It supports readers, journalists, and editors, with article approval workflows and a REST API layer for future integrations.

## Local Setup (Virtual Environment)

1. Open a terminal in the project root.
2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the virtual environment:

### Windows (PowerShell)
```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS/Linux
```bash
source .venv/bin/activate
```

4. Install project dependencies:

```bash
pip install -r requirements.txt
```

5. Create a local environment file for secrets and settings:

```bash
copy .env.example .env
```

If `.env.example` does not exist, create a `.env` file manually and define the required variables.

6. Apply migrations:

```bash
python manage.py migrate
```

7. Start the development server:

```bash
python manage.py runserver
```

The app should be available locally at:

```text
http://127.0.0.1:8000/
```

## Docker Setup

Build the Docker image from the project root:

```bash
docker build -t news-app .
```

Run the container:

```bash
docker run -d -p 8000:8000 --name news-app-container news-app
```

Open the app in a browser at:

```text
http://localhost:8000/
```

To stop the container:

```bash
docker stop news-app-container
```

To remove it:

```bash
docker rm news-app-container
```

## Environment Variables / Secrets

Never store real passwords, secret keys, API tokens, or other credentials in a public repository.

Use a local `.env` file for development and a secure secrets manager or platform environment configuration in production.

Example `.env` file:

```env
SECRET_KEY=your_secret_key_here
DEBUG=True
USE_MYSQL=False
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

### Recommended practices
- Keep `.env` local and add it to `.gitignore`.
- Use environment variables provided by your hosting platform or Docker runtime in deployment.
- Do not commit real credentials to Git or any public repository.
- Use `docker run --env-file .env ...` if you want to load environment variables into the container without embedding secrets in the Dockerfile.

Example:

```bash
docker run -d -p 8000:8000 --env-file .env --name news-app-container news-app
```

## Notes

- The project can run with SQLite or MySQL depending on the `USE_MYSQL` setting and the values in the environment file.
- For production, set `DEBUG=False`, define a secure `SECRET_KEY`, and configure allowed hosts correctly.

