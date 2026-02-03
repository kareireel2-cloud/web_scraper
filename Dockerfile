FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml ./
COPY uv.lock ./

RUN uv sync

COPY . .

EXPOSE 8000

CMD ["uv", "run", "main.py"]
