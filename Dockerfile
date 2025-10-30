# Initial temporary stage to build dependecies only
FROM python:3.11-buster as builder

#
## Expected folder view at the end:
##
## /
## └── usr
##     ├── .venv
##     │   └── bin/
##     └── app
##         ├── __main__.py
##         └── entrypoint.sh
#

# Environment variables to build a virtual environment
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_HOME=/opt/poetry \
    POETRY_CACHE_DIR=/tmp/poetry/cache

RUN curl -sSL --retry 3 --max-time 10 https://raw.githubusercontent.com/python-poetry/install.python-poetry.org/main/install-poetry.py | python3 - --version 1.5.0

# Set up a working directory
WORKDIR /usr

# Include Poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN $POETRY_HOME/bin/poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# Final stage to run an app
FROM python:3.11-slim as runtime

# Environment variables to build and run a final stage
ENV VENV_PATH=/usr/.venv \
    PATH=/usr/.venv/bin:$PATH

# Set up a working directory
WORKDIR /usr/app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create a user without root permissions
RUN addgroup --system app && adduser --system --group app

# Remove root permissions by using a restricted user
USER app

# Expose health check port (optional, used if ENABLE_HEALTH_CHECK=true)
EXPOSE 8080

# Healthcheck: try HTTP endpoint first, fall back to process check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/health 2>/dev/null || pgrep -f "python" >/dev/null

# Include prepared dependencies from the previous stage
COPY --from=builder ${VENV_PATH} ${VENV_PATH}

# Include app's code
COPY app .

# App's main entrypoint
ENTRYPOINT ["bash", "entrypoint.sh"]
