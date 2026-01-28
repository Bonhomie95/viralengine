from typing import List, Tuple, Union

from engine.discovery.youtube_fetcher import YouTubeVideo
from engine.discovery.twitch_fetcher import TwitchVOD
from .virality_score import score_youtube, score_twitch


Candidate = Union[YouTubeVideo, TwitchVOD]


def rank_candidates(all_items: List[Candidate]) -> List[Tuple[float, Candidate]]:
    scored: List[Tuple[float, Candidate]] = []

    for item in all_items:
        if isinstance(item, YouTubeVideo):
            score = score_youtube(item)
        elif isinstance(item, TwitchVOD):
            score = score_twitch(item)
        else:
            continue  # safety

        scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored
