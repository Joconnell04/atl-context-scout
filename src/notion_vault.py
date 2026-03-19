"""Notion Secure Vault reader for atl-context-scout.

Fetches the user's personal context (phone number, location, name)
from a private Notion page using the Notion REST API.
The vault page is expected to contain a table with 'Item Name' and
'Value' columns — same structure as the Engineering Hub Secure Vault.
"""

from __future__ import annotations

import re
import requests
from typing import Any

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _get_page_blocks(token: str, page_id: str) -> list[dict[str, Any]]:
    """Retrieve all blocks from a Notion page."""
    clean_id = re.sub(r"[^a-f0-9]", "", page_id.lower())
    formatted = f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:]}"
    url = f"{NOTION_API_BASE}/blocks/{formatted}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    results = []
    cursor = None
    while True:
        params: dict[str, Any] = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return results


def _extract_plain_text(rich_text: list[dict[str, Any]]) -> str:
    """Collapse a Notion rich_text array to a plain string."""
    return "".join(chunk.get("plain_text", "") for chunk in rich_text)


def _parse_table_block(block: dict[str, Any], token: str) -> list[list[str]]:
    """Return a 2-D list of cell strings from a Notion table block."""
    block_id = block["id"]
    url = f"{NOTION_API_BASE}/blocks/{block_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    rows = []
    for row_block in resp.json().get("results", []):
        if row_block.get("type") != "table_row":
            continue
        cells = row_block["table_row"]["cells"]
        rows.append([_extract_plain_text(cell) for cell in cells])
    return rows


def read_vault(token: str, vault_page_id: str) -> dict[str, str]:
    """Read the Secure Vault page and return a {item_name: value} dict."""
    blocks = _get_page_blocks(token, vault_page_id)
    vault: dict[str, str] = {}
    for block in blocks:
        if block.get("type") != "table":
            continue
        rows = _parse_table_block(block, token)
        # First row is the header; skip it
        for row in rows[1:]:
            if len(row) >= 2 and row[0] and row[1]:
                vault[row[0].strip()] = row[1].strip()
    return vault


def get_phone_number(token: str, vault_page_id: str) -> str:
    """Convenience wrapper — returns the Contact Phone from the vault."""
    vault = read_vault(token, vault_page_id)
    return vault.get("Contact Phone", "")
