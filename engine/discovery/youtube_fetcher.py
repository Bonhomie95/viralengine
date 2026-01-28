from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
import requests


YOUTUBE_API = "https://www.googleapis.com/youtube/v3"


@dataclass
class YouTubeVideo:
    platform: str
    creator_id: str
    creator_label: str
    video_id: str
    title: str
    published_at: str
    channel_id: str
    channel_title: str
    url: str
    views: int
    likes: int
    comments: int


def _utc_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class YouTubeFetcher:
    def __init__(self, api_key: str, user_agent: str = "viral-engine/1.0") -> None:
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def fetch_recent_videos(
        self,
        creator_id: str,
        creator_label: str,
        channel_id: str,
        days_lookback: int = 14,
        max_results: int = 25,
    ) -> List[YouTubeVideo]:
        after = datetime.now(timezone.utc) - timedelta(days=days_lookback)

        # 1) search for recent videos on channel
        search_params = {
            "part": "snippet",
            "channelId": channel_id,
            "maxResults": min(max_results, 50),
            "order": "date",
            "type": "video",
            "publishedAfter": _utc_iso(after),
            "key": self.api_key,
        }

        r = self.session.get(f"{YOUTUBE_API}/search", params=search_params, timeout=30)
        r.raise_for_status()
        items = r.json().get("items", [])

        video_ids: List[str] = []
        snippets: Dict[str, Dict[str, Any]] = {}

        for it in items:
            vid = (it.get("id") or {}).get("videoId")
            snip = it.get("snippet") or {}
            if not vid:
                continue
            video_ids.append(vid)
            snippets[vid] = snip

        if not video_ids:
            return []

        # 2) fetch stats for those videos
        stats_params = {
            "part": "snippet,statistics",
            "id": ",".join(video_ids),
            "maxResults": 50,
            "key": self.api_key,
        }

        r2 = self.session.get(f"{YOUTUBE_API}/videos", params=stats_params, timeout=30)
        r2.raise_for_status()
        vitems = r2.json().get("items", [])

        out: List[YouTubeVideo] = []
        for v in vitems:
            vid = v.get("id", "")
            snip = v.get("snippet") or snippets.get(vid) or {}
            stats = v.get("statistics") or {}

            out.append(
                YouTubeVideo(
                    platform="youtube",
                    creator_id=creator_id,
                    creator_label=creator_label,
                    video_id=vid,
                    title=snip.get("title", ""),
                    published_at=snip.get("publishedAt", ""),
                    channel_id=snip.get("channelId", channel_id),
                    channel_title=snip.get("channelTitle", ""),
                    url=f"https://www.youtube.com/watch?v={vid}",
                    views=int(stats.get("viewCount", 0) or 0),
                    likes=int(stats.get("likeCount", 0) or 0),
                    comments=int(stats.get("commentCount", 0) or 0),
                )
            )

        # Ensure newest first
        out.sort(key=lambda x: x.published_at, reverse=True)
        return out
