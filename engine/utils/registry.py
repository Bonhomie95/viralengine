import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional

REG_PATH = Path("data/processed_registry.json")
REG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default() -> Dict[str, Any]:
    return {
        "videos": {},  # keyed by source video_id/vod_id
        "last_cycle_at": None,  # scheduler heartbeat
        "upload_history": [],  # list of uploaded shorts (final outputs)
    }


def _load() -> Dict[str, Any]:
    if not REG_PATH.exists():
        REG_PATH.write_text(json.dumps(_default(), indent=2))
        return _default()

    try:
        return json.loads(REG_PATH.read_text())
    except json.JSONDecodeError:
        print("⚠️ Registry corrupted. Resetting file.")
        REG_PATH.write_text(json.dumps(_default(), indent=2))
        return _default()


def _save(data: Dict[str, Any]) -> None:
    REG_PATH.write_text(json.dumps(data, indent=2))


# ----------------------------
# SOURCE VIDEO TRACKING
# ----------------------------
def is_video_used(video_id: str) -> bool:
    return video_id in _load()["videos"]


def upsert_processed(
    video_id: str,
    creator: str,
    title: str,
    description: str,
    clip_start: float,
    clip_end: float,
    final_path: str,
) -> None:
    data = _load()
    v = data["videos"].setdefault(video_id, {})
    v.update(
        {
            "creator": creator,
            "title": title,
            "description": description,
            "processed_at": _now_iso(),
            "clip_start": clip_start,
            "clip_end": clip_end,
            "final_path": final_path,
            "uploaded": v.get("uploaded", False),
            "uploaded_at": v.get("uploaded_at"),
            "youtube_video_id": v.get("youtube_video_id"),
        }
    )
    _save(data)


def is_clip_used(video_id: str, start: float, end: float) -> bool:
    data = _load()
    v = data["videos"].get(video_id)
    if not v:
        return False
    # unique identity without file hashing
    key = f"{video_id}|{int(start)}|{int(end)}"
    return v.get("clip_key") == key


def set_clip_key(video_id: str, start: float, end: float) -> None:
    data = _load()
    v = data["videos"].setdefault(video_id, {})
    v["clip_key"] = f"{video_id}|{int(start)}|{int(end)}"
    _save(data)


# ----------------------------
# UPLOAD TRACKING
# ----------------------------
def mark_uploaded(video_id: str, youtube_video_id: str) -> None:
    data = _load()
    v = data["videos"].get(video_id)
    if not v:
        return
    v["uploaded"] = True
    v["uploaded_at"] = _now_iso()
    v["youtube_video_id"] = youtube_video_id

    data["upload_history"].append(
        {
            "source_video_id": video_id,
            "youtube_video_id": youtube_video_id,
            "uploaded_at": v["uploaded_at"],
            "final_path": v.get("final_path"),
            "title": v.get("title"),
        }
    )
    _save(data)


def get_last_cycle_at() -> Optional[str]:
    return _load().get("last_cycle_at")


def set_last_cycle_at() -> None:
    data = _load()
    data["last_cycle_at"] = _now_iso()
    _save(data)
