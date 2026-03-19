# atl-context-scout

A small CLI tool that pulls current Atlanta news, weather, and events via [Brave Search](https://brave.com/search/api/) and generates a personalized markdown context report.

## Features

- Searches Brave for current Atlanta news headlines
- Pulls today's weather forecast
- Finds upcoming local events and things to do
- Fetches personalization data from a private Notion vault page
- Outputs a clean markdown report to stdout or a file

## Setup

```bash
# Clone the repo
git clone https://github.com/Joconnell04/atl-context-scout.git
cd atl-context-scout

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and fill in your BRAVE_API_KEY and NOTION_TOKEN
```

## Usage

```bash
# Basic run (uses DEFAULT_LOCATION from .env)
python main.py

# Specify a location
python main.py --location "Midtown Atlanta"

# Skip Notion vault lookup
python main.py --no-personalize

# Write report to a file
python main.py --output report.md
```

## Environment Variables

| Variable | Description |
|---|---|
| `BRAVE_API_KEY` | Brave Search API subscription token |
| `NOTION_TOKEN` | Notion integration secret |
| `NOTION_VAULT_PAGE_ID` | Page ID of your Notion vault page |
| `DEFAULT_LOCATION` | Default city/area for the report |

## Project Structure

```
atl-context-scout/
├── main.py                 # CLI entrypoint
├── requirements.txt
├── .env.example
└── src/
    ├── config.py           # Env/config loader
    ├── brave_client.py     # Brave Search API wrapper
    ├── notion_vault.py     # Notion vault reader
    └── report.py           # Markdown report formatter
```
