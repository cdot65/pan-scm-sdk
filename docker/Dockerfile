FROM python:3.12-alpine

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev make curl git

# Install Poetry as root, copy binary to /usr/bin, and set permissions
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cp /root/.local/bin/poetry /usr/bin/poetry && \
    chmod a+x /usr/bin/poetry

# Set working directory
WORKDIR /app

# Copy Poetry files first for dependency caching
COPY pyproject.toml poetry.lock* ./

# Disable Poetry virtualenvs (install into system site-packages)
ENV POETRY_VIRTUALENVS_CREATE=false

# Install dependencies (including dev for linting/formatting)
RUN /usr/bin/poetry install --with dev --no-root

# Copy the rest of the source code (optional for IDE, but good for completion)
COPY . .

# Set the locale to avoid issues with emoji rendering
ENV LANG=C.UTF-8

## Create a non-root user
#RUN adduser -D panadmin
#USER panadmin
#
# Default command (PyCharm will override)
CMD ["sleep", "infinity"]
