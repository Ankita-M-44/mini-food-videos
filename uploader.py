#!/usr/bin/env python3
"""
Upload generated food videos to Instagram and YouTube.
Reads metadata JSON files produced by pipeline.py and uploads each video.
"""
import os
import sys
import glob
import json
import argparse

from agent.notion_tracker import NotionTracker
from agent.instagram_uploader import InstagramUploader
from agent.youtube_uploader import YouTubeUploader


def run(output_dir: str = "output", platforms: list[str] | None = None) -> None:
    if platforms is None:
        platforms = ["instagram", "youtube"]

    notion = NotionTracker()
    ig = InstagramUploader() if "instagram" in platforms else None
    yt = YouTubeUploader() if "youtube" in platforms else None

    meta_files = glob.glob(os.path.join(output_dir, "*_meta.json"))
    if not meta_files:
        print("No metadata files found in output directory.", file=sys.stderr)
        sys.exit(1)

    for meta_file in meta_files:
        with open(meta_file) as f:
            meta = json.load(f)

        video_path = meta["video_path"]
        page_id = meta["page_id"]

        if not os.path.exists(video_path):
            print(f"  Skipping {video_path}: file not found", file=sys.stderr)
            continue

        dish_name = meta["dish"]["name"]
        print(f"Uploading: {dish_name}")

        ig_url = ""
        yt_url = ""

        if ig:
            try:
                ig_url = ig.upload_reel(video_path, meta["ig_caption"])
                print(f"  Instagram: {ig_url}")
            except Exception as exc:
                print(f"  Instagram upload failed: {exc}", file=sys.stderr)

        if yt:
            try:
                yt_url = yt.upload_short(video_path, meta["yt_title"], meta["yt_caption"])
                print(f"  YouTube: {yt_url}")
            except Exception as exc:
                print(f"  YouTube upload failed: {exc}", file=sys.stderr)

        notion.mark_uploaded(page_id, instagram_url=ig_url, youtube_url=yt_url)

    if ig:
        ig.logout()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload generated food videos")
    parser.add_argument("--output-dir", default="output", help="Directory containing generated videos")
    parser.add_argument(
        "--platforms",
        nargs="+",
        choices=["instagram", "youtube"],
        default=["instagram", "youtube"],
        help="Platforms to upload to",
    )
    args = parser.parse_args()
    run(output_dir=args.output_dir, platforms=args.platforms)
