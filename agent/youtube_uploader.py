import os
import json
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeUploader:
    def __init__(self):
        creds_json = os.environ["YOUTUBE_CREDENTIALS_JSON"]
        creds_data = json.loads(creds_json)
        self.credentials = Credentials.from_authorized_user_info(creds_data, SCOPES)
        if self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(google.auth.transport.requests.Request())
        self.youtube = build("youtube", "v3", credentials=self.credentials)

    def upload_short(self, video_path: str, title: str, description: str) -> str:
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["food", "shorts", "foodie", "recipe", "cooking"],
                "categoryId": "26",
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }
        media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )
        response = None
        while response is None:
            _, response = request.next_chunk()
        video_id = response["id"]
        return f"https://www.youtube.com/shorts/{video_id}"
