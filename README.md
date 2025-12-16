# Calculations App — README

This repository contains a FastAPI application for managing calculations and user accounts. Below are concise instructions to run the app, run tests, and push a Docker image to Docker Hub.

## Run the application (local, development)

1. Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate.bat # Windows (PowerShell/CMD)
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the FastAPI application using Uvicorn (app object is `app` in `app.main`):

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 in your browser (web UI routes are available under `/register`, `/login`, `/dashboard`, `/profile`).

## Run tests locally

- Run the full test suite with pytest:

```bash
pytest -q
```

- Run a single test file (example Playwright tests):

```bash
pytest -q tests/e2e/test_profile_playwright.py
```

- Playwright UI tests require Playwright and browsers to be installed once in your environment:

```bash
pip install playwright
playwright install
```

Notes:
- Tests use fixtures in `tests/conftest.py` to start a test server and initialize a temporary database. Ensure the environment can open a local browser when running Playwright tests.

## Docker / Docker Hub

- Build the Docker image locally:

```bash
docker build -t your-docker-username/is601-final:latest .
```

- Log in to Docker Hub and push the image:

```bash
docker login
docker push your-docker-username/is601-final:latest
```

- Replace `your-docker-username` with your Docker Hub username. Your Docker Hub repository URL will look like:

https://hub.docker.com/repository/docker/your-docker-username/is601-final

## Quick Commands

```bash
# run app
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# run tests
pytest -q

# install playwright (for UI tests)
pip install playwright && playwright install

# build and push docker image
docker build -t your-docker-username/is601-final:latest .
docker login
docker push your-docker-username/is601-final:latest
```

## Where to edit configuration

- Application settings live in `app/core/config.py`. Adjust environment variables or values there for production.

---

If you want, I can update this README with your actual Docker Hub repository URL or add a short section describing environment variables used by the app.
