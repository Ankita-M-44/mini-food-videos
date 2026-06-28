import os
import time
import requests


class InstagramUploader:
    """Upload Reels via the official Instagram Graph API."""

    GRAPH_BASE = "https://graph.facebook.com/v22.0"

    def __init__(self):
        self.access_token = os.environ["INSTAGRAM_ACCESS_TOKEN"]
        self.account_id = os.environ["INSTAGRAM_ACCOUNT_ID"]

    def upload_reel(self, video_url: str, caption: str) -> str:
        container_id = self._create_container(video_url, caption)
        self._wait_for_container(container_id)
        media_id = self._publish(container_id)
        return f"https://www.instagram.com/reel/{media_id}/"

    def _create_container(self, video_url: str, caption: str) -> str:
        resp = requests.post(
            f"{self.GRAPH_BASE}/{self.account_id}/media",
            data={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "access_token": self.access_token,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["id"]

    def _wait_for_container(self, container_id: str, max_wait: int = 300) -> None:
        deadline = time.time() + max_wait
        while time.time() < deadline:
            resp = requests.get(
                f"{self.GRAPH_BASE}/{container_id}",
                params={
                    "fields": "status_code,status",
                    "access_token": self.access_token,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            status_code = data.get("status_code")
            if status_code == "FINISHED":
                return
            if status_code == "ERROR":
                raise RuntimeError(f"Instagram container processing failed: {data.get('status')}")
            time.sleep(10)
        raise TimeoutError(f"Instagram container processing timed out after {max_wait}s")

    def _publish(self, container_id: str) -> str:
        resp = requests.post(
            f"{self.GRAPH_BASE}/{self.account_id}/media_publish",
            data={
                "creation_id": container_id,
                "access_token": self.access_token,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["id"]
