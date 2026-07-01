"""HTTP client for email analysis through a local Ollama instance."""

from typing import Any

import requests

from app.config import OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS, OLLAMA_URL
from app.prompts import build_email_analysis_prompt
from app.utils import JsonExtractionError, extract_json_from_text


class OllamaError(RuntimeError):
    """Base error for failures while communicating with Ollama."""


class OllamaUnavailableError(OllamaError):
    """Raised when the local Ollama service cannot be reached."""


class OllamaTimeoutError(OllamaError):
    """Raised when Ollama does not respond before the timeout."""


class OllamaModelNotFoundError(OllamaError):
    """Raised when the configured model is unavailable in Ollama."""


class OllamaInvalidResponseError(OllamaError):
    """Raised when Ollama returns an unexpected or invalid response."""


def _ollama_error_message(response: requests.Response) -> str:
    try:
        payload = response.json()
    except requests.JSONDecodeError:
        return response.text.strip() or f"HTTP {response.status_code}"

    if isinstance(payload, dict):
        return str(payload.get("error") or payload)
    return str(payload)


def analyze_email_with_ollama(subject: str, body: str) -> dict[str, Any]:
    """Send an email to Ollama and return its structured analysis."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": build_email_analysis_prompt(subject, body),
        "stream": False,
        "format": "json",
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
    except requests.Timeout as exc:
        raise OllamaTimeoutError(
            f"Ollama did not respond within {OLLAMA_TIMEOUT_SECONDS} seconds."
        ) from exc
    except requests.ConnectionError as exc:
        raise OllamaUnavailableError(
            "Ollama is unavailable. Make sure it is installed and running locally."
        ) from exc
    except requests.RequestException as exc:
        raise OllamaUnavailableError(f"Failed to connect to Ollama: {exc}") from exc

    if response.status_code == 404:
        details = _ollama_error_message(response)
        raise OllamaModelNotFoundError(
            f"Ollama model '{OLLAMA_MODEL}' was not found. Details: {details}"
        )

    if not response.ok:
        details = _ollama_error_message(response)
        if "model" in details.lower() and "not found" in details.lower():
            raise OllamaModelNotFoundError(
                f"Ollama model '{OLLAMA_MODEL}' was not found. Details: {details}"
            )
        raise OllamaError(
            f"Ollama returned HTTP {response.status_code}: {details}"
        )

    try:
        response_payload = response.json()
    except requests.JSONDecodeError as exc:
        raise OllamaInvalidResponseError(
            "Ollama returned a response that is not valid JSON."
        ) from exc

    model_text = response_payload.get("response") if isinstance(response_payload, dict) else None
    if not isinstance(model_text, str):
        raise OllamaInvalidResponseError(
            "Ollama response does not contain the required 'response' field."
        )

    try:
        return extract_json_from_text(model_text)
    except JsonExtractionError as exc:
        raise OllamaInvalidResponseError(
            f"The model returned invalid analysis JSON: {exc}"
        ) from exc

