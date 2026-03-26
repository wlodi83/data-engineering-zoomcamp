"""PII anonymization utilities for the extraction pipeline."""

import hashlib
import os


HASH_SALT = os.environ.get("PII_HASH_SALT", "default-salt-change-me")


def hash_id(value: str | int | None) -> str | None:
    """One-way hash an identifier to preserve cardinality without exposing PII."""
    if value is None:
        return None
    raw = f"{HASH_SALT}:{value}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# Columns to anonymize per table
ANONYMIZE_COLUMNS: dict[str, list[str]] = {
    "logs": ["user_id"],
}

# Columns to drop entirely (contain PII or secrets)
DROP_COLUMNS: dict[str, list[str]] = {
    "logs": ["user", "referrer"],
    "workflow": ["owners"],
    "report": ["owners"],
}
