import os
import time
import requests


class VideoGenerator:
    """Generates videos via the Runway ML Gen-3 API."""

    API_BASE = "https://api.runwayml.com/v1"

    def __init__(self):
        self.api_key = os.environ["RUNWAY_API_KEY"]
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def generate(self, prompt: str, output_path: str, duration: int = 5) -> str:
        payload = {
            "prompt": prompt,
            "duration": duration,
            "ratio": "9:16",
            "resolution": "720p",
        }
        resp = requests.post(
            f"{self.API_BASE}/generate/video",
            json=payload,
            headers=self.headers,
            timeout=30,
        )
        resp.raise_for_status()
        task_id = resp.json()["id"]

        video_url = self._poll(task_id)
        return self._download(video_url, output_path)

    def _poll(self, task_id: str, max_wait: int = 300) -> str:
        deadline = time.time() + max_wait
        while time.time() < deadline:
            resp = requests.get(
                f"{self.API_BASE}/tasks/{task_id}",
                headers=self.headers,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status")
            if status == "SUCCEEDED":
                return data["output"][0]
            if status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Video generation {status}: {data.get('error')}")
            time.sleep(10)
        raise TimeoutError(f"Video generation timed out after {max_wait}s")

    def _download(self, url: str, output_path: str) -> str:
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
