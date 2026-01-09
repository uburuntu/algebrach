# Build stage for installing dependencies
FROM python:3.14-slim AS builder

#
## Expected folder view at the end:
##
## /
## └── usr
##     └── app
##         ├── .venv/
##         ├── __main__.py
##         └── entrypoint.sh
#

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set up a working directory
WORKDIR /usr/app

# Environment variables for uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install dependencies (cached layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy application code
COPY app .
COPY pyproject.toml uv.lock README.md ./

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Final stage to run the app
FROM python:3.14-slim AS runtime

# Environment variables for runtime
ENV PATH=/usr/app/.venv/bin:$PATH

# Set up a working directory
WORKDIR /usr/app

# Create a user without root permissions
RUN addgroup --system app && adduser --system --group app

# Include prepared venv and app from the builder stage
COPY --from=builder --chown=app:app /usr/app /usr/app

# Remove root permissions by using a restricted user
USER app

# Healthcheck to check the process is running
HEALTHCHECK CMD pgrep -f "python" >/dev/null

# App's main entrypoint
ENTRYPOINT ["bash", "entrypoint.sh"]
