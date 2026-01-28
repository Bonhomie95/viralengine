from __future__ import annotations

from pathlib import Path
from typing import Optional, cast

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.credentials import Credentials
from google.oauth2.credentials import Credentials as OAuthCreds
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _get_creds() -> Credentials:
    token_path = Path("secrets/token.json")
    client_secret = Path("secrets/client_secret.json")

    token_path.parent.mkdir(parents=True, exist_ok=True)

    creds: Optional[Credentials] = None

    if token_path.exists():
        creds = cast(
            Credentials,
            OAuthCreds.from_authorized_user_file(str(token_path), SCOPES),
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), SCOPES)
            creds = cast(Credentials, flow.run_local_server(port=0))

        # Save only if OAuth credentials
        if isinstance(creds, OAuthCreds):
            token_path.write_text(creds.to_json())

    return creds


def upload_short(
    video_path: Path,
    title: str,
    description: str,
    privacy: str = "public",
) -> str:
    creds = _get_creds()
    youtube = build("youtube", "v3", credentials=creds)

    if "#shorts" not in description.lower():
        description = description.strip() + "\n\n#Shorts #shorts"

    body = {
        "snippet": {
            "title": title[:95],
            "description": description,
            "categoryId": "24",
            "tags": ["shorts", "Shorts"],
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    print("🚀 Uploading to YouTube...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"📤 Upload progress: {int(status.progress() * 100)}%")

    print(f"✅ Uploaded: {response['id']}")
    return response["id"]
