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

# Create a user without root permissions
RUN addgroup --system app && adduser --system --group app

# Remove root permissions by using a restricted user
USER app

# Healthcheck to check the process is running
HEALTHCHECK CMD pgrep -f "python" >/dev/null

# Include prepared dependencies from the previous stage
COPY --from=builder ${VENV_PATH} ${VENV_PATH}

# Include app's code
COPY app .

# App's main entrypoint
ENTRYPOINT ["bash", "entrypoint.sh"]
