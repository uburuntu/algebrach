# 🤖 Algebrach Bot, Remastered

Open in Telegram: https://t.me/algebrach_bot

## Commands

- `/kek` 😎
- `/kek_add` to suggest a reply to be a kek
- `/kek_info` to get stats
- Inline mode: type `@algebrach_bot` in any chat for random or text search

## Previous implementation

- Legendary https://github.com/arvego/mm-randbot by Artemy G

## Used technologies

- [aiogram 3](https://github.com/aiogram/aiogram) — a modern asynchronous framework for Telegram Bot API
  - Docs: https://docs.aiogram.dev/en/v3.29.0/
  - Guide (rus): https://mastergroosha.github.io/aiogram-3-guide/
- [Airtable](https://airtable.com/invite/r/20o5538r/) — a cloud platform to store and process spreadsheet data
  - Docs: https://airtable.com/developers/web
  - Library: https://github.com/gtalarico/pyairtable
    - Not async, so used with a Thread Executor to not block the event loop
  - Why: to have a visualised editable view of keks with different content types
  - Self-hosted alternatives:
    - NocoDB: https://nocodb.com/, https://github.com/nocodb/nocodb
    - Baserow: https://baserow.io/, https://github.com/bram2w/baserow

## Local development

### Install Python 3.14

https://www.python.org/downloads/

### Install dependencies

Using [`uv`](https://docs.astral.sh/uv/getting-started/installation/):

```bash
uv sync
```

### Start the bot

From the `algebrach/app/` folder:

```bash
# Set up tokens: copy .env.example to .env and edit it
cp .env.example .env
nano .env
```

To run:

```bash
uv run python -u __main__.py
```

### Used dev tools

[Pre Commit](https://pre-commit.com/) hooks from [.pre-commit-config.yaml](.pre-commit-config.yaml) file:

```bash
# To init (required only once)
uv run pre-commit install --install-hooks

# To check hooks before commit
uv run pre-commit run --all-files
```

[Ruff](https://github.com/astral-sh/ruff/) for linting and formatting, with settings from [pyproject.toml](pyproject.toml) file:

```bash
# To format project files
uv run ruff format .

# To detect linter issues and auto fix them where applicable
uv run ruff check --fix .

# To run ruff in a watcher mode to check any file edit
uv run ruff check --fix . --watch
```

Run the automated tests and dependency audit from the repository root:

```bash
uv run pytest
uv run pip-audit
```

## Deploy on a server

Update to the latest revision:

```bash
git pull
```

Build and start Docker container:

```bash
cp app/.env.example app/.env.prod
# Set ENVIRONMENT=prod and replace the example tokens in app/.env.prod
docker compose up --build -d --force-recreate
```

See [Next-stage architecture](docs/next-stage-architecture.md) for the prioritized
structural improvements that are intentionally outside routine maintenance.
