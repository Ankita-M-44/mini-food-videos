import os
import anthropic


class PromptGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def generate(self, dish: dict) -> str:
        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Create a detailed video generation prompt for a mouth-watering "
                        f"short-form food video of '{dish['name']}' ({dish['cuisine']} cuisine). "
                        f"Description: {dish['description']}\n\n"
                        "The prompt should describe: camera angles, lighting, motion, plating, "
                        "colors, textures, and atmosphere. Keep it under 200 words and make it "
                        "suitable for an AI video generation model. Return only the prompt text."
                    ),
                }
            ],
        )
        return message.content[0].text.strip()
