# 🤖 Algebrach Bot, Remastered

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

https://t.me/algebrach_bot

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

### Install Python 3.11

https://www.python.org/downloads/

### Install dependencies

Using [`poetry`](https://python-poetry.org/docs/#installing-with-the-official-installer) (recommended):

```bash
poetry install --no-root
```

Or by using `pip` in a virtual environment (acceptable):

```bash
python3.11 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

Or by using `pip` directly (not recommended):

```bash
pip3.11 install -r requirements.txt
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
# Replace `python` with `python3.11` if you didn't create virtual environment
python -u __main__.py
```

### Used dev tools

[Pre Commit](https://pre-commit.com/) hooks from [.pre-commit-config.yaml](.pre-commit-config.yaml) file:

```bash
# To init (required only once)
pre-commit install --install-hooks

# To check hooks before commit
pre-commit run
```

[Black Formatter](https://github.com/psf/black/) with settings from [pyproject.toml](pyproject.toml) file:

```bash
# To format project files
black .
```

[Ruff Linter](https://github.com/astral-sh/ruff/) with settings from [pyproject.toml](pyproject.toml) file:

```bash
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
