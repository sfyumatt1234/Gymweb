"""Small ExerciseDB client for server-side integrations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


class ExerciseDbError(Exception):
    """Raised when the remote API request or response is invalid."""


def _validate_header_value(name: str, value: str) -> str:
    """Return a stripped HTTP header value or raise a safe integration error."""
    cleaned = (value or "").strip()
    if not cleaned:
        raise ExerciseDbError(f"Missing ExerciseDB header value for {name}.")
    try:
        cleaned.encode("latin-1")
    except UnicodeEncodeError as exc:
        raise ExerciseDbError(
            f"Invalid ExerciseDB setting for {name}; use the real RapidAPI value, not placeholder text."
        ) from exc
    return cleaned


@dataclass(frozen=True)
class ExerciseDbClient:
    base_url: str
    api_host: str
    api_key: str
    timeout: int = 20

    @classmethod
    def from_settings(cls) -> "ExerciseDbClient":
        return cls(
            base_url=settings.EXERCISEDB_API_BASE_URL.rstrip("/"),
            api_host=settings.EXERCISEDB_API_HOST,
            api_key=settings.EXERCISEDB_API_KEY,
            timeout=getattr(settings, "EXERCISEDB_TIMEOUT_SECONDS", 20),
        )

    @property
    def enabled(self) -> bool:
        return bool(getattr(settings, "EXERCISEDB_ENABLED", False) and (self.api_key or "").strip())

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-RapidAPI-Key": _validate_header_value("X-RapidAPI-Key", self.api_key),
            "X-RapidAPI-Host": _validate_header_value("X-RapidAPI-Host", self.api_host),
        }

    def _get(self, path: str, **params: Any) -> dict[str, Any]:
        if not self.enabled:
            raise ExerciseDbError("ExerciseDB integration is disabled.")

        clean_params = {
            key: value
            for key, value in params.items()
            if value not in (None, "", [], ())
        }
        query = urlencode(clean_params, doseq=True)
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{query}"

        request = Request(url, headers=self.headers, method="GET")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ExerciseDbError(f"ExerciseDB HTTP {exc.code}: {detail}") from exc
        except (URLError, TimeoutError, UnicodeEncodeError, json.JSONDecodeError) as exc:
            raise ExerciseDbError(f"ExerciseDB request failed: {exc}") from exc

        if payload.get("success") is False:
            raise ExerciseDbError(payload.get("error") or "ExerciseDB returned success=false.")
        return payload

    def list_exercises(self, **filters: Any) -> dict[str, Any]:
        return self._get("/api/v1/exercises", **filters)

    def search_exercises(self, search: str) -> list[dict[str, Any]]:
        return self._get("/api/v1/exercises/search", search=search).get("data", [])

    def get_exercise(self, exercise_id: str) -> dict[str, Any]:
        return self._get(f"/api/v1/exercises/{exercise_id}").get("data", {})
