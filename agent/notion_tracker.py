import os
from datetime import datetime, timezone
from notion_client import Client


class NotionTracker:
    def __init__(self):
        self.client = Client(auth=os.environ["NOTION_API_KEY"])
        self.database_id = os.environ["NOTION_DATABASE_ID"]

    def create_entry(self, dish: dict, video_prompt: str) -> str:
        response = self.client.pages.create(
            parent={"database_id": self.database_id},
            properties={
                "Name": {"title": [{"text": {"content": dish["name"]}}]},
                "Cuisine": {"rich_text": [{"text": {"content": dish.get("cuisine", "")}}]},
                "Status": {"select": {"name": "Pending"}},
                "Created": {"date": {"start": datetime.now(timezone.utc).isoformat()}},
                "Tags": {
                    "multi_select": [
                        {"name": tag} for tag in dish.get("tags", [])[:5]
                    ]
                },
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": f"Prompt:\n{video_prompt}"}}]
                    },
                }
            ],
        )
        return response["id"]

    def update_status(self, page_id: str, status: str, extra: dict | None = None) -> None:
        properties: dict = {"Status": {"select": {"name": status}}}
        if extra:
            properties.update(extra)
        self.client.pages.update(page_id=page_id, properties=properties)

    def mark_uploaded(self, page_id: str, instagram_url: str = "", youtube_url: str = "") -> None:
        properties: dict = {"Status": {"select": {"name": "Uploaded"}}}
        if instagram_url:
            properties["Instagram URL"] = {
                "url": instagram_url
            }
        if youtube_url:
            properties["YouTube URL"] = {
                "url": youtube_url
            }
        self.client.pages.update(page_id=page_id, properties=properties)
