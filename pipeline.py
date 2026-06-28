#!/usr/bin/env python3
"""
Mini food video generation pipeline.
Selects dishes, generates video prompts, creates videos, and tracks in Notion.
"""
import os
import sys
import argparse
import json
from pathlib import Path

from agent.dish_selector import DishSelector
from agent.prompt_generator import PromptGenerator
from agent.caption_generator import CaptionGenerator
from agent.notion_tracker import NotionTracker
from agent.video_generator import VideoGenerator


def run(count: int = 1, output_dir: str = "output") -> list[dict]:
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    dish_selector = DishSelector()
    prompt_gen = PromptGenerator()
    caption_gen = CaptionGenerator()
    notion = NotionTracker()
    video_gen = VideoGenerator()

    results = []
    dishes = dish_selector.select(count)

    for dish in dishes:
        print(f"Processing: {dish['name']}")

        video_prompt = prompt_gen.generate(dish)
        ig_caption = caption_gen.generate(dish, platform="instagram")
        yt_caption = caption_gen.generate(dish, platform="youtube")
        yt_title = caption_gen.generate_youtube_title(dish)

        page_id = notion.create_entry(dish, video_prompt)
        notion.update_status(page_id, "Generating")

        safe_name = dish["name"].lower().replace(" ", "_").replace("/", "-")
        video_path = os.path.join(output_dir, f"{safe_name}.mp4")

        try:
            video_gen.generate(video_prompt, video_path)
            notion.update_status(page_id, "Generated")
        except Exception as exc:
            print(f"  Video generation failed: {exc}", file=sys.stderr)
            notion.update_status(page_id, "Failed")
            continue

        result = {
            "dish": dish,
            "page_id": page_id,
            "video_path": video_path,
            "ig_caption": ig_caption,
            "yt_title": yt_title,
            "yt_caption": yt_caption,
        }
        results.append(result)

        manifest_path = video_path.replace(".mp4", "_meta.json")
        with open(manifest_path, "w") as f:
            json.dump(result, f, indent=2)

        print(f"  Done: {video_path}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate mini food videos")
    parser.add_argument("--count", type=int, default=1, help="Number of dishes to generate")
    parser.add_argument("--output-dir", default="output", help="Output directory for videos")
    args = parser.parse_args()
    run(count=args.count, output_dir=args.output_dir)
