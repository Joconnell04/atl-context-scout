"""Configuration loader for atl-context-scout.

Loads environment variables from .env file (if present) and exposes
a typed Config dataclass consumed by the rest of the application.
"""

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass


@dataclass(frozen=True)
class Config:
    brave_api_key: str
    notion_token: str
    notion_vault_page_id: str
    default_location: str


def load_config() -> Config:
    """Read configuration from environment and return a Config instance."""
    brave_api_key = os.environ.get("BRAVE_API_KEY", "")
    notion_token = os.environ.get("NOTION_TOKEN", "")
    vault_page_id = os.environ.get(
        "NOTION_VAULT_PAGE_ID", "32829338df998115b710fe39ba94569d"
    )
    default_location = os.environ.get("DEFAULT_LOCATION", "Atlanta, GA")

    if not brave_api_key:
        raise EnvironmentError(
            "BRAVE_API_KEY is not set. Copy .env.example to .env and fill in your key."
        )
    if not notion_token:
        raise EnvironmentError(
            "NOTION_TOKEN is not set. Copy .env.example to .env and fill in your token."
        )

    return Config(
        brave_api_key=brave_api_key,
        notion_token=notion_token,
        notion_vault_page_id=vault_page_id,
        default_location=default_location,
    )
