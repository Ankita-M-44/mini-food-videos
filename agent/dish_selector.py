import os
import json
import anthropic


class DishSelector:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def select(self, count: int = 1) -> list[dict]:
        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You are a food content creator. Select {count} unique, visually "
                        "appealing mini food dish(es) that would make great short-form videos. "
                        "For each dish return a JSON array with objects containing: "
                        "'name' (dish name), 'cuisine' (cuisine type), 'description' "
                        "(1-2 sentence visual description), 'tags' (list of relevant hashtag "
                        "strings without #). Return only valid JSON, no markdown."
                    ),
                }
            ],
        )
        text = message.content[0].text.strip()
        dishes = json.loads(text)
        if isinstance(dishes, dict):
            dishes = [dishes]
        return dishes
