from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "").strip()
    twitch_client_id: str = os.getenv("TWITCH_CLIENT_ID", "").strip()
    twitch_client_secret: str = os.getenv("TWITCH_CLIENT_SECRET", "").strip()

    days_lookback: int = int(os.getenv("DAYS_LOOKBACK", "14"))
    max_results_per_creator: int = int(os.getenv("MAX_RESULTS_PER_CREATOR", "25"))
    user_agent: str = os.getenv("USER_AGENT", "viral-engine/1.0")


def get_settings() -> Settings:
    s = Settings()
    # Hard fail early so you don't waste time debugging later.
    if not s.youtube_api_key:
        raise RuntimeError("Missing YOUTUBE_API_KEY in .env")
    if not s.twitch_client_id or not s.twitch_client_secret:
        raise RuntimeError("Missing TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET in .env")
    return s
