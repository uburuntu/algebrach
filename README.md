# 🤖 Algebrach Bot, Remastered

Open in Telegram: https://t.me/algebrach_bot

## Commands

- `/kek` 😎


- `/kek_add` to suggest a reply to be a kek
- `/kek_info` to get stats

## Previous implementation

- Legendary https://github.com/arvego/mm-randbot by Artemy G

## Used technologies

- [aiogram 3](https://github.com/aiogram/aiogram) — a modern asynchronous framework for Telegram Bot API
  - Docs: https://docs.aiogram.dev/en/dev-3.x/
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

Using [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (recommended):

```bash
uv sync
```

Or by using `pip` in a virtual environment (acceptable):

```bash
python3.14 -m venv ./venv
source ./venv/bin/activate
pip install -e .
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
pre-commit install --install-hooks

# To check hooks before commit
pre-commit run
```

[Ruff](https://github.com/astral-sh/ruff/) for linting and formatting, with settings from [pyproject.toml](pyproject.toml) file:

```bash
# To format project files
ruff format .

# To detect linter issues and auto fix them where applicable
ruff check --fix .

# To run ruff in a watcher mode to check any file edit
ruff check --fix . --watch
```

## Deploy on a server

Update to the latest revision:

```bash
git pull
```

Build and start Docker container:

```bash
docker-compose up --build -d --force-recreate
```
