from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Sequence, Union

from .youtube_fetcher import YouTubeFetcher, YouTubeVideo
from .twitch_fetcher import TwitchFetcher, TwitchVOD


Creator = Dict[str, Any]
DiscoveryItem = Union[YouTubeVideo, TwitchVOD]


def load_creators(path: str = "config/creators.json") -> Sequence[Creator]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Missing creators file: {path}")
    return json.loads(p.read_text(encoding="utf-8"))


class DiscoveryService:
    def __init__(
        self,
        yt: YouTubeFetcher,
        tw: TwitchFetcher,
        days_lookback: int = 14,
        max_results_per_creator: int = 25,
    ) -> None:
        self.yt = yt
        self.tw = tw
        self.days_lookback = days_lookback
        self.max_results_per_creator = max_results_per_creator

    def fetch_for_creator(self, c: Creator) -> Sequence[DiscoveryItem]:
        platform = str(c.get("platform") or "")
        cid = str(c.get("id") or "")
        label = str(c.get("label") or cid)

        if not cid:
            raise ValueError("Creator missing 'id'")
        if not label:
            raise ValueError("Creator missing 'label'")

        if platform == "youtube":
            return self.yt.fetch_recent_videos(
                creator_id=cid,
                creator_label=label,
                channel_id=str(c["channel_id"]),
                days_lookback=self.days_lookback,
                max_results=self.max_results_per_creator,
            )

        if platform == "twitch":
            return self.tw.fetch_recent_vods(
                creator_id=cid,
                creator_label=label,
                twitch_login=str(c["twitch_login"]),
                days_lookback=self.days_lookback,
                max_results=self.max_results_per_creator,
            )

        raise ValueError(f"Unknown platform: {platform}")

    def fetch_all(
        self, creators: Sequence[Creator]
    ) -> Dict[str, Sequence[DiscoveryItem]]:
        out: Dict[str, Sequence[DiscoveryItem]] = {}
        for c in creators:
            cid = str(c.get("id") or "")
            if not cid:
                continue
            out[cid] = self.fetch_for_creator(c)
        return out
