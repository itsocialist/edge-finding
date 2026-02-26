"""Export webset results to Google Sheets."""

from __future__ import annotations

import json
import os
from typing import Union

from google.oauth2 import service_account
from googleapiclient.discovery import build

from schemas import Person, Company

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_sheets_service():
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not creds_json:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable is not set")

    creds_info = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return build("sheets", "v4", credentials=credentials)


def _person_headers() -> list[str]:
    return [
        "Name", "LinkedIn URL", "GitHub Username", "Title",
        "Company", "Seniority", "Signals", "Source URLs", "Date Captured",
    ]


def _person_row(p: Person) -> list[str]:
    return [
        p.name,
        p.linkedin_url or "",
        p.github_username or "",
        p.title or "",
        p.company or "",
        p.seniority or "",
        "; ".join(p.signals),
        "; ".join(p.source_urls),
        p.date_captured,
    ]


def _company_headers() -> list[str]:
    return [
        "Name", "Domain", "Description", "Industry",
        "Size Range", "Tech Signals", "Source URLs", "Date Captured",
    ]


def _company_row(c: Company) -> list[str]:
    return [
        c.name,
        c.domain or "",
        c.description or "",
        c.industry or "",
        c.size_range or "",
        "; ".join(c.tech_signals),
        "; ".join(c.source_urls),
        c.date_captured,
    ]


def export_to_sheets(
    entities: list[Union[Person, Company]],
    sheet_id: str,
    entity_type: str,
    sheet_name: str = "Sheet1",
) -> dict:
    """Write entity data to a Google Sheet. Clears existing data and writes fresh."""
    service = _get_sheets_service()

    if entity_type == "person":
        headers = _person_headers()
        rows = [_person_row(e) for e in entities if isinstance(e, Person)]
    else:
        headers = _company_headers()
        rows = [_company_row(e) for e in entities if isinstance(e, Company)]

    values = [headers] + rows
    range_spec = f"{sheet_name}!A1"

    # Clear existing data
    service.spreadsheets().values().clear(
        spreadsheetId=sheet_id,
        range=sheet_name,
        body={},
    ).execute()

    # Write new data
    result = service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_spec,
        valueInputOption="USER_ENTERED",
        body={"values": values},
    ).execute()

    return {
        "spreadsheet_id": sheet_id,
        "updated_range": result.get("updatedRange", ""),
        "updated_rows": result.get("updatedRows", 0),
        "updated_cells": result.get("updatedCells", 0),
    }
