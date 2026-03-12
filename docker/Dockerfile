FROM python:3.12-alpine

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev make curl git

# Install Poetry via pip so it's available system-wide
ENV POETRY_VERSION=1.8.2
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Set working directory
WORKDIR /app

# Copy Poetry files first for dependency caching
COPY pyproject.toml poetry.lock* ./

# Disable Poetry virtualenvs (install into system site-packages)
ENV POETRY_VIRTUALENVS_CREATE=false

# Install dependencies (including dev for linting/formatting)
RUN poetry install --with dev --no-root

# Copy the rest of the source code (optional for IDE, but good for completion)
COPY . .

# Set the locale to avoid issues with emoji rendering
ENV LANG=C.UTF-8

# NOTE: Non-root user is not enabled because docker-compose.yml mounts
# the host directory as a volume (-v .:/app), which bypasses COPY/chown.
# A non-root user would need a separate production Dockerfile.

# Default command (PyCharm will override)
CMD ["sleep", "infinity"]
