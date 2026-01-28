from datetime import datetime, timezone
from typing import Union

from engine.discovery.youtube_fetcher import YouTubeVideo
from engine.discovery.twitch_fetcher import TwitchVOD


def _hours_since(dt_str: str) -> float:
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return max((datetime.now(timezone.utc) - dt).total_seconds() / 3600, 1)


def score_youtube(v: YouTubeVideo) -> float:
    h = _hours_since(v.published_at)
    view_velocity = v.views / h
    like_velocity = v.likes / h
    comment_velocity = v.comments / h

    return (
        view_velocity * 0.6 +
        like_velocity * 0.2 +
        comment_velocity * 0.2
    )


def score_twitch(v: TwitchVOD) -> float:
    h = _hours_since(v.created_at)
    view_velocity = v.view_count / h

    # Twitch has less metadata, so scale views higher
    return view_velocity * 0.9
