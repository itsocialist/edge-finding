"""Push webset results to HubSpot as contacts or companies."""

from __future__ import annotations

import os
from typing import Union

from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate as ContactInput
from hubspot.crm.companies import SimplePublicObjectInputForCreate as CompanyInput

from schemas import Person, Company


def _get_client() -> HubSpot:
    api_key = os.environ.get("HUBSPOT_API_KEY")
    if not api_key:
        raise RuntimeError("HUBSPOT_API_KEY environment variable is not set")
    return HubSpot(access_token=api_key)


def push_persons(persons: list[Person]) -> dict:
    """Create or update HubSpot contacts from Person entities."""
    client = _get_client()
    created = 0
    errors = []

    for person in persons:
        properties = {
            "firstname": person.name.split()[0] if person.name else "",
            "lastname": " ".join(person.name.split()[1:]) if person.name and " " in person.name else "",
            "jobtitle": person.title or "",
            "company": person.company or "",
        }

        if person.linkedin_url:
            properties["hs_linkedin_url"] = person.linkedin_url

        # Add seniority and signals as notes
        if person.seniority:
            properties["hs_lead_status"] = person.seniority

        try:
            contact_input = ContactInput(properties=properties)
            client.crm.contacts.basic_api.create(simple_public_object_input_for_create=contact_input)
            created += 1
        except Exception as exc:
            errors.append({"person": person.name, "error": str(exc)})

    return {
        "total": len(persons),
        "created": created,
        "errors": errors,
    }


def push_companies(companies: list[Company]) -> dict:
    """Create or update HubSpot companies from Company entities."""
    client = _get_client()
    created = 0
    errors = []

    for company in companies:
        properties = {
            "name": company.name,
            "domain": company.domain or "",
            "description": company.description or "",
            "industry": company.industry or "",
        }

        if company.size_range:
            properties["numberofemployees"] = company.size_range

        try:
            company_input = CompanyInput(properties=properties)
            client.crm.companies.basic_api.create(simple_public_object_input_for_create=company_input)
            created += 1
        except Exception as exc:
            errors.append({"company": company.name, "error": str(exc)})

    return {
        "total": len(companies),
        "created": created,
        "errors": errors,
    }


def push_entities(entities: list[Union[Person, Company]]) -> dict:
    """Route entities to the correct HubSpot push function."""
    persons = [e for e in entities if isinstance(e, Person)]
    companies = [e for e in entities if isinstance(e, Company)]

    result = {}
    if persons:
        result["contacts"] = push_persons(persons)
    if companies:
        result["companies"] = push_companies(companies)
    return result
