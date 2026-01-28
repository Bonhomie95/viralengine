from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import requests


TWITCH_OAUTH = "https://id.twitch.tv/oauth2/token"
TWITCH_HELIX = "https://api.twitch.tv/helix"


@dataclass
class TwitchVOD:
    platform: str
    creator_id: str
    creator_label: str
    vod_id: str
    title: str
    created_at: str
    duration: str
    url: str
    view_count: int
    user_id: str
    user_login: str


def _parse_utc(dt_str: str) -> datetime:
    # Example: "2026-01-25T08:12:34Z"
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).astimezone(
        timezone.utc
    )


class TwitchFetcher:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str = "viral-engine/1.0",
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self._token: Optional[str] = None

    def _get_token(self) -> str:
        if self._token is not None:
            return self._token

        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        r = self.session.post(TWITCH_OAUTH, params=params, timeout=30)
        r.raise_for_status()

        data = r.json()
        token = data.get("access_token")

        if not token:
            raise RuntimeError("Failed to obtain Twitch OAuth token")

        self._token = str(token)
        return self._token

    def _helix_get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        token = self._get_token()
        headers = {
            "Client-Id": self.client_id,
            "Authorization": f"Bearer {token}",
        }
        r = self.session.get(
            f"{TWITCH_HELIX}{path}", params=params, headers=headers, timeout=30
        )
        r.raise_for_status()
        return r.json()

    def resolve_user_id(self, login: str) -> Optional[Dict[str, str]]:
        data = self._helix_get("/users", {"login": login}).get("data", [])
        if not data:
            return None
        u = data[0]
        return {"id": u["id"], "login": u.get("login", login)}

    def fetch_recent_vods(
        self,
        creator_id: str,
        creator_label: str,
        twitch_login: str,
        days_lookback: int = 14,
        max_results: int = 25,
    ) -> List[TwitchVOD]:
        resolved = self.resolve_user_id(twitch_login)
        if not resolved:
            return []

        user_id = resolved["id"]
        after = datetime.now(timezone.utc) - timedelta(days=days_lookback)

        # Pull recent videos (archives/highlights/uploads)
        # We'll keep it broad; scoring can prefer type later.
        payload = self._helix_get(
            "/videos",
            {"user_id": user_id, "first": min(max_results, 100), "sort": "time"},
        )
        items = payload.get("data", [])

        out: List[TwitchVOD] = []
        for it in items:
            created_at = it.get("created_at", "")
            if not created_at:
                continue

            if _parse_utc(created_at) < after:
                continue

            out.append(
                TwitchVOD(
                    platform="twitch",
                    creator_id=creator_id,
                    creator_label=creator_label,
                    vod_id=it.get("id", ""),
                    title=it.get("title", ""),
                    created_at=created_at,
                    duration=it.get("duration", ""),
                    url=it.get("url", ""),
                    view_count=int(it.get("view_count", 0) or 0),
                    user_id=user_id,
                    user_login=twitch_login,
                )
            )

        out.sort(key=lambda x: x.created_at, reverse=True)
        return out
