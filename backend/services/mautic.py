"""Helper utilities for interacting with the Mautic REST API."""

from __future__ import annotations
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

from ..utils.config import settings

logger = logging.getLogger(__name__)


@dataclass
class MauticConfig:
    """Configuration required to communicate with Mautic."""

    base_url: str
    username: str
    password: str

    @property
    def api_root(self) -> str:
        return self.base_url.rstrip("/") + "/api"


class MauticClient:
    """Thin async wrapper around the Mautic REST API using basic auth."""

    def __init__(self, config: MauticConfig) -> None:
        self._config = config
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "MauticClient":
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._config.api_root,
                auth=(self._config.username, self._config.password),
                timeout=httpx.Timeout(15.0, connect=5.0),
            )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    @staticmethod
    def from_settings() -> Optional["MauticConfig"]:
        """Construct configuration from environment settings."""
        if not settings.MAUTIC_BASE_URL or not settings.MAUTIC_API_USERNAME or not settings.MAUTIC_API_PASSWORD:
            return None
        return MauticConfig(
            base_url=settings.MAUTIC_BASE_URL,
            username=settings.MAUTIC_API_USERNAME,
            password=settings.MAUTIC_API_PASSWORD,
        )

    async def find_contact_id(self, email: str) -> Optional[int]:
        """Return an existing Mautic contact id for the email, if present."""
        assert self._client is not None, "Client not initialised"
        try:
            response = await self._client.get("/contacts", params={"search": f"email:{email}"})
            response.raise_for_status()
        except httpx.HTTPError as exc:  # pragma: no cover - network dependent
            logger.warning("Mautic contact lookup failed: %s", exc)
            return None

        data = response.json()
        contacts = data.get("contacts") or {}
        if not contacts:
            return None

        first_key = next(iter(contacts.keys()), None)
        if first_key is None:
            return None
        try:
            return int(first_key)
        except (TypeError, ValueError):
            return None

    async def create_contact(self, email: str, fields: Dict[str, Any]) -> Optional[int]:
        """Create a new contact and return its id."""
        assert self._client is not None, "Client not initialised"
        payload = {"email": email, **{k: v for k, v in fields.items() if v is not None}}
        try:
            response = await self._client.post("/contacts/new", data=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:  # pragma: no cover - network dependent
            logger.error("Failed to create Mautic contact: %s", exc)
            return None

        contact = response.json().get("contact") or {}
        contact_id = contact.get("id")
        try:
            return int(contact_id)
        except (TypeError, ValueError):
            return None

    async def update_contact(self, contact_id: int, fields: Dict[str, Any]) -> bool:
        """Update an existing contact with new field values."""
        assert self._client is not None, "Client not initialised"
        payload = {k: v for k, v in fields.items() if v is not None}
        if not payload:
            return True
        try:
            response = await self._client.put(f"/contacts/{contact_id}/edit", data=payload)
            response.raise_for_status()
            return True
        except httpx.HTTPError as exc:  # pragma: no cover - network dependent
            logger.error("Failed to update Mautic contact %s: %s", contact_id, exc)
            return False

    async def add_note(self, contact_id: int, title: str, content: str) -> bool:
        """Attach a note to the specified contact for auditing."""
        assert self._client is not None, "Client not initialised"
        note_payload = {
            "text": content,
            "title": title,
            "type": "general",
        }
        try:
            response = await self._client.post(f"/contacts/{contact_id}/notes/new", data=note_payload)
            response.raise_for_status()
            return True
        except httpx.HTTPError as exc:  # pragma: no cover - network dependent
            logger.error("Failed to add note to contact %s: %s", contact_id, exc)
            return False


def _extract_first(values: Optional[Any]) -> Optional[str]:
    if values is None:
        return None
    if isinstance(values, list):
        return str(values[0]) if values else None
    return str(values)


def _lookup(payload: Dict[str, Any], *keys: str) -> Optional[str]:
    for key in keys:
        if key in payload and payload[key] not in (None, ""):
            return _extract_first(payload[key])
    return None


def _truncate(text: str, limit: int = 1200) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


async def sync_thrivecart_event(payload: Dict[str, Any]) -> None:
    """Best-effort Mautic synchronisation for a ThriveCart webhook event."""
    config = MauticClient.from_settings()
    if not config:
        logger.debug("Skipping Mautic sync; configuration incomplete")
        return

    email = _lookup(
        payload,
        "customer[email]",
        "customer.email",
        "email",
        "customer[customer_email]",
    )
    if not email:
        logger.info("ThriveCart payload missing email; skipping Mautic sync")
        return

    first_name = _lookup(payload, "customer[first_name]", "customer.firstname", "first_name", "firstname")
    last_name = _lookup(payload, "customer[last_name]", "customer.lastname", "last_name", "lastname")
    company = _lookup(payload, "customer[company]", "company")
    phone = _lookup(payload, "customer[phone]", "phone")
    event_type = _lookup(payload, "event", "type") or "unknown"

    note_title = f"ThriveCart event: {event_type}"
    note_content = _truncate(json.dumps(payload, indent=2, default=str))

    async with MauticClient(config) as client:
        contact_id = await client.find_contact_id(email)
        contact_fields = {
            "firstname": first_name,
            "lastname": last_name,
            "company": company,
            "phone": phone,
        }

        if contact_id is None:
            contact_id = await client.create_contact(email, contact_fields)
            if contact_id:
                logger.info("Created Mautic contact %s for %s", contact_id, email)
        else:
            updated = await client.update_contact(contact_id, contact_fields)
            if updated:
                logger.debug("Updated Mautic contact %s", contact_id)

        if not contact_id:
            logger.warning("Unable to persist contact for ThriveCart event; skipping note")
            return

        note_ok = await client.add_note(contact_id, note_title, note_content)
        if note_ok:
            logger.debug("Attached ThriveCart note to Mautic contact %s", contact_id)

*** End of File
