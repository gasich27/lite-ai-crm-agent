"""Utilities for handling LLM responses."""

import json
import re
from typing import Any


class JsonExtractionError(ValueError):
    """Raised when a valid JSON object cannot be extracted from text."""


def extract_json_from_text(text: str) -> dict[str, Any]:
    """Extract and parse the first JSON object from an LLM response."""
    if not isinstance(text, str) or not text.strip():
        raise JsonExtractionError("Model response is empty; JSON was not found.")

    fenced_blocks = re.findall(
        r"```(?:json)?\s*(.*?)\s*```", text, flags=re.IGNORECASE | re.DOTALL
    )
    candidates = fenced_blocks + [re.sub(r"```(?:json)?|```", "", text, flags=re.IGNORECASE)]
    decoder = json.JSONDecoder()
    last_error: json.JSONDecodeError | None = None
    found_opening_brace = False

    for candidate in candidates:
        for match in re.finditer(r"\{", candidate):
            found_opening_brace = True
            try:
                value, _ = decoder.raw_decode(candidate[match.start() :])
            except json.JSONDecodeError as exc:
                last_error = exc
                continue

            if isinstance(value, dict):
                return value

    if found_opening_brace and last_error is not None:
        raise JsonExtractionError(
            "A JSON-like object was found, but it is invalid: "
            f"{last_error.msg} (position {last_error.pos})."
        ) from last_error

    raise JsonExtractionError("JSON object was not found in the model response.")

