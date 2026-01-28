from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path
import time
import os

from engine.utils.registry import (
    get_last_cycle_at,
    set_last_cycle_at,
    mark_uploaded,
    upsert_processed,
    is_video_used,
    is_clip_used,
    set_clip_key,
)
from engine.youtube.uploader import upload_short

from engine.video.downloader import download_video
from engine.video.moment_detector import find_best_moment
from engine.video.clipper import extract_clip
from engine.editing.renderer import render_shorts

from engine.discovery.discovery import DiscoveryService, load_creators
from engine.discovery.youtube_fetcher import YouTubeVideo
from engine.scoring.ranker import rank_candidates


def format_remaining(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}h {m:02d}m {s:02d}s"


def seconds_until_next_run(interval_hours: int) -> int:
    last = get_last_cycle_at()
    if not last:
        return 0

    last_dt = _parse_iso(last)
    next_dt = last_dt + timedelta(hours=interval_hours)
    remaining = (next_dt - datetime.now(timezone.utc)).total_seconds()
    return max(0, int(remaining))


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def should_run(interval_hours: int) -> bool:
    last = get_last_cycle_at()
    if not last:
        return True
    last_dt = _parse_iso(last)
    return datetime.now(timezone.utc) - last_dt >= timedelta(hours=interval_hours)


def run_once(
    discovery: DiscoveryService, creators_path: str, privacy: str = "public"
) -> None:
    creators = load_creators(creators_path)
    results = discovery.fetch_all(creators)

    all_items = []
    for items in results.values():
        all_items.extend(items)

    if not all_items:
        print("No candidates discovered.")
        return

    ranked = rank_candidates(all_items)

    # Pick first unused source video (never repeat)
    selected = None
    for score, item in ranked:
        video_id = item.video_id if isinstance(item, YouTubeVideo) else item.vod_id
        if not is_video_used(video_id):
            selected = (item, video_id)
            break

    if not selected:
        print("No new viral videos available.")
        return

    top_item, video_id = selected
    print(f"\n🎯 Selected: {top_item.title}")

    # Download
    video_path = download_video(top_item.url, video_id)

    # Moment detect
    start, end = find_best_moment(video_path)

    # Clip identity (no file hashing)
    if is_clip_used(video_id, start, end):
        print("Clip identity already used, skipping.")
        return
    set_clip_key(video_id, start, end)

    # Extract clip
    clip_path = extract_clip(video_path, start, end, video_id)

    # Render shorts (your renderer cleans up intermediates)
    final_path = render_shorts(clip_path)

    # Save metadata to registry BEFORE deleting source
    # (description can be improved later, keep it simple now)
    title = f"{top_item.title} #shorts"
    description = (
        f"{top_item.title}\n\nSource: {top_item.url}\nCreator: {top_item.creator_label}"
    )
    upsert_processed(
        video_id=video_id,
        creator=top_item.creator_label,
        title=title,
        description=description,
        clip_start=start,
        clip_end=end,
        final_path=str(final_path),
    )

    # Optional: delete downloaded source to save space
    print("🗑 Removing source video...")
    try:
        if Path(video_path).exists():
            Path(video_path).unlink()
    except Exception as e:
        print("⚠️ Could not delete source video:", e)

    # Upload
    yt_id = upload_short(
        video_path=Path(final_path),
        title=title,
        description=description,
        privacy=privacy,
    )

    # Mark uploaded only AFTER success
    mark_uploaded(video_id, yt_id)

    # Optional: delete final after upload (if you ever want this)
    if os.getenv("DELETE_FINAL_AFTER_UPLOAD", "0") == "1":
        try:
            Path(final_path).unlink()
            print("🧹 Deleted final after upload.")
        except Exception as e:
            print("⚠️ Could not delete final:", e)


def run_forever(discovery: DiscoveryService, creators_path: str) -> None:
    interval_hours = int(os.getenv("UPLOAD_INTERVAL_HOURS", "8"))
    privacy = os.getenv("YOUTUBE_PRIVACY", "public")

    print(f"⏱ Scheduler started. Interval: {interval_hours}h | Privacy: {privacy}")

    while True:
        if should_run(interval_hours):
            print("\n🚀 Time to run a new upload cycle!")
            set_last_cycle_at()
            try:
                run_once(discovery, creators_path, privacy=privacy)
            except Exception as e:
                print("❌ Cycle failed:", e)
        else:
            remaining = seconds_until_next_run(interval_hours)
            print(
                f"\r⏳ Next upload in: {format_remaining(remaining)}",
                end="",
                flush=True,
            )

        time.sleep(5)  # update countdown every 5 seconds
