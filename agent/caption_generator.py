import os
import anthropic


class CaptionGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def generate(self, dish: dict, platform: str = "instagram") -> str:
        platform_guidance = {
            "instagram": "engaging, emoji-rich, with 10-15 relevant hashtags at the end",
            "youtube": "descriptive title and first 2 sentences optimized for search, no hashtags",
        }.get(platform, "engaging with relevant hashtags")

        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Write a {platform} caption for a food video of '{dish['name']}' "
                        f"({dish['cuisine']} cuisine). Make it {platform_guidance}. "
                        f"Tags to include: {', '.join(dish.get('tags', []))}. "
                        "Return only the caption text."
                    ),
                }
            ],
        )
        return message.content[0].text.strip()

    def generate_youtube_title(self, dish: dict) -> str:
        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=128,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Write a compelling YouTube Shorts title (max 60 chars) for a food video "
                        f"of '{dish['name']}' ({dish['cuisine']} cuisine). "
                        "Return only the title text, no quotes."
                    ),
                }
            ],
        )
        return message.content[0].text.strip()
