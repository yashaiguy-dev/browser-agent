# Facebook Ads Spy — Claude Code Skill

Scrape any advertiser's Facebook ads from the Meta Ad Library. Downloads all images, videos, extracts audio, transcribes with Deepgram, and saves everything as Obsidian-ready Markdown.

## What It Does

- Searches Meta Ad Library for any advertiser by name
- Extracts ad copy, landing URLs, CTAs, start dates, platforms, and media
- Downloads all images and videos locally
- Converts video audio to MP3 and transcribes using Deepgram
- Generates a clean Obsidian Markdown file with everything organized
- Uses Patchright (anti-detection) to bypass Facebook's bot protection

## Requirements

- Python 3.8+
- macOS, Linux, or Windows
- ffmpeg (for video audio extraction) — optional but recommended
- Deepgram API key (for transcription) — optional, free tier available at [deepgram.com](https://deepgram.com)

## Installation

### 1. Copy the tool

```bash
mkdir -p ~/.claude/skills/ads-spy
cp fb_ads_spy.py ~/.claude/skills/ads-spy/fb_ads_spy.py
```

### 2. Install dependencies

```bash
pip3 install requests patchright
patchright install chromium
```

### 3. Install ffmpeg (optional — for video transcription)

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (via chocolatey)
choco install ffmpeg
```

### 4. Set up Deepgram (optional — for video transcription)

Get a free API key at [deepgram.com](https://deepgram.com), then:

```bash
export DEEPGRAM_API_KEY="your-key-here"
```

Add to your `~/.zshrc` or `~/.bashrc` to persist across sessions.

Without this key, everything works — you just won't get video transcripts.

### 5. Add the skill to Claude Code

```bash
cp ads-spy.md ~/.claude/commands/ads-spy.md
```

### 6. Done

Open Claude Code and type `/ads-spy` or just ask "spy on Nike's Facebook ads" — it will handle the rest.

## Standalone Usage (without Claude Code)

Works as a regular CLI tool too:

```bash
# Basic usage
python3 fb_ads_spy.py "Nike"

# Limit to 50 ads
python3 fb_ads_spy.py "Nike" --max-ads 50

# Custom output directory
python3 fb_ads_spy.py "Nike" --output-dir ~/my-ads
```

## Output Structure

```
~/obsidian-vault/facebook-ads/
└── nike/
    ├── nike.md           ← Main Markdown file with all ads
    ├── images/           ← Downloaded ad images
    │   ├── ad-1-1.jpg
    │   └── ad-2-1.jpg
    ├── videos/           ← Downloaded ad videos
    │   └── ad-3-1.mp4
    └── audio/            ← Extracted audio from videos
        └── ad-3-1.mp3
```

Open `~/obsidian-vault/facebook-ads/` as an Obsidian vault to browse everything with embedded images and videos.

## How It Works

1. Opens a real Chromium browser (with anti-detection via Patchright)
2. Navigates to Meta Ad Library and searches for the advertiser
3. Selects the advertiser from the autocomplete dropdown
4. Scrolls to load all ads (up to your specified max)
5. Extracts structured data from each ad card via JavaScript
6. Enriches ads missing landing URLs by visiting their detail pages
7. Downloads all media, converts video audio, transcribes
8. Generates a single Obsidian Markdown file

## Tips

- **First run may take longer** as Patchright downloads Chromium
- **Facebook may rate-limit** if you scrape too aggressively — the tool has built-in random delays
- **Videos have expiring CDN links** — some may fail to download if Facebook rotates them quickly
- **The browser window is visible** so you can watch it work (and manually solve CAPTCHAs if needed)
