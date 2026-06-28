import os
import time
import base64
import requests


class VideoGenerator:
    """Generates videos via Google Veo 2 (Gemini API, free tier)."""

    API_BASE = "https://generativelanguage.googleapis.com/v1beta"
    MODEL = "veo-2.0-generate-001"

    def __init__(self):
        self.api_key = os.environ["GEMINI_API_KEY"]

    def generate(self, prompt: str, output_path: str, duration: int = 8) -> str:
        operation_name = self._start_generation(prompt, duration)
        video_data = self._poll(operation_name)
        return self._save(video_data, output_path)

    def _start_generation(self, prompt: str, duration: int) -> str:
        url = f"{self.API_BASE}/models/{self.MODEL}:predictLongRunning"
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "aspectRatio": "9:16",
                "durationSeconds": duration,
            },
        }
        resp = requests.post(
            url,
            json=payload,
            params={"key": self.api_key},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["name"]

    def _poll(self, operation_name: str, max_wait: int = 600) -> bytes:
        url = f"{self.API_BASE}/{operation_name}"
        deadline = time.time() + max_wait
        while time.time() < deadline:
            resp = requests.get(url, params={"key": self.api_key}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if data.get("done"):
                if "error" in data:
                    raise RuntimeError(f"Veo 2 generation failed: {data['error']}")
                prediction = data["response"]["predictions"][0]
                if "bytesBase64Encoded" in prediction:
                    return base64.b64decode(prediction["bytesBase64Encoded"])
                if "video" in prediction and "uri" in prediction["video"]:
                    return self._fetch_uri(prediction["video"]["uri"])
                raise RuntimeError(f"Unexpected response shape: {prediction.keys()}")
            time.sleep(15)
        raise TimeoutError(f"Veo 2 generation timed out after {max_wait}s")

    def _fetch_uri(self, uri: str) -> bytes:
        resp = requests.get(uri, params={"key": self.api_key}, timeout=120)
        resp.raise_for_status()
        return resp.content

    def _save(self, video_bytes: bytes, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(video_bytes)
        return output_path
