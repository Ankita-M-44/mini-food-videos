import os
from instagrapi import Client


class InstagramUploader:
    def __init__(self):
        self.client = Client()
        self.client.login(
            username=os.environ["INSTAGRAM_USERNAME"],
            password=os.environ["INSTAGRAM_PASSWORD"],
        )

    def upload_reel(self, video_path: str, caption: str) -> str:
        media = self.client.clip_upload(
            path=video_path,
            caption=caption,
        )
        media_id = media.pk
        code = media.code
        return f"https://www.instagram.com/reel/{code}/"

    def logout(self) -> None:
        self.client.logout()
