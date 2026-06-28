# Mini Food Videos

Automated pipeline for generating and publishing short-form food videos to Instagram Reels and YouTube Shorts using Claude AI, Runway ML, and Notion.

## Architecture

```
pipeline.py          # Generate dishes → prompts → videos → Notion entries
uploader.py          # Upload generated videos to Instagram & YouTube
agent/
  dish_selector.py   # Claude selects trending dishes
  prompt_generator.py  # Claude writes video generation prompts
  caption_generator.py # Claude writes platform-specific captions
  video_generator.py   # Runway ML Gen-3 video generation
  instagram_uploader.py # Upload Reels via instagrapi
  youtube_uploader.py   # Upload Shorts via YouTube Data API v3
  notion_tracker.py    # Track status in Notion database
```

## Setup

### 1. Clone & install dependencies

```bash
git clone https://github.com/ankita-m-44/mini-food-videos.git
cd mini-food-videos
pip install -r requirements.txt
```

### 2. Environment variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude |
| `RUNWAY_API_KEY` | Runway ML API key for video generation |
| `NOTION_API_KEY` | Notion integration token |
| `NOTION_DATABASE_ID` | ID of the Notion tracking database |
| `INSTAGRAM_USERNAME` | Instagram account username |
| `INSTAGRAM_PASSWORD` | Instagram account password |
| `YOUTUBE_CREDENTIALS_JSON` | OAuth2 credentials JSON for YouTube Data API |

### 3. Notion database schema

Create a Notion database with these properties:

| Property | Type |
|---|---|
| Name | Title |
| Cuisine | Rich Text |
| Status | Select (Pending, Generating, Generated, Uploading, Uploaded, Failed) |
| Created | Date |
| Tags | Multi-select |
| Instagram URL | URL |
| YouTube URL | URL |

## Usage

### Generate videos locally

```bash
python pipeline.py --count 3 --output-dir output
```

### Upload videos locally

```bash
python uploader.py --output-dir output --platforms instagram youtube
```

## GitHub Actions

### `generate_videos.yml`
Runs daily at 8 AM UTC (or manually). Generates videos and stores them as workflow artifacts.

**Required secrets:** `ANTHROPIC_API_KEY`, `RUNWAY_API_KEY`, `NOTION_API_KEY`, `NOTION_DATABASE_ID`

### `upload_videos.yml`
Triggered manually. Downloads artifacts from a generate run and uploads to social platforms.

**Required secrets:** `NOTION_API_KEY`, `NOTION_DATABASE_ID`, `INSTAGRAM_USERNAME`, `INSTAGRAM_PASSWORD`, `YOUTUBE_CREDENTIALS_JSON`

## YouTube OAuth2 setup

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable YouTube Data API v3
3. Create OAuth 2.0 credentials (Desktop app)
4. Run the OAuth flow once locally to get a refresh token
5. Store the full credentials JSON as the `YOUTUBE_CREDENTIALS_JSON` secret
