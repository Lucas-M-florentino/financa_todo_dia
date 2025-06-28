FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy the project into the image
COPY requirements.txt /app/

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app
RUN pip install -r requirements.txt

# Copiar o resto do código
COPY /app ./


CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001", "--reload"]