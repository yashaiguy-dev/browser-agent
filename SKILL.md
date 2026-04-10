---
name: browser
description: Control a real Chromium browser — navigate pages, click buttons, fill forms, take screenshots, read page content via accessibility tree. Use when the user asks to open a browser, visit a website, interact with a web page, or scrape visible content.
---

# Browser Control Skill

You have a browser control tool at `~/.qwen/skills/browser/browser_tool.py` that controls a real visible Chromium browser via CDP.

## First-Time Setup

If the tool isn't installed yet, run:
```bash
python3 ~/.qwen/skills/browser/browser_tool.py install
```

## Architecture
- `launch` starts Chromium as a **detached process** with `--remote-debugging-port=9222`
- All other commands **connect via CDP**, do their work, disconnect
- Browser stays open independently — no blocking needed
- Persistent profile at `~/.browser-tool/profile/` — logins survive across sessions

## Commands

```bash
BT="python3 ~/.qwen/skills/browser/browser_tool.py"

# Launch (NOT background — it detaches automatically)
$BT launch                      # Playwright
$BT launch --patchright          # Anti-detection mode
$BT launch --connect 9222       # Attach to existing Chrome

# Navigation & interaction
$BT navigate "https://example.com"
$BT click "button.submit"
$BT type "input[name=email]" "user@example.com"
$BT type "input[name=email]" "new@example.com" --clear

# Observation
$BT snapshot                     # accessibility tree — structured text, token-efficient
$BT snapshot --selector "main"   # scoped to a section
$BT screenshot                   # saves /tmp/browser_screenshots/latest.png
$BT screenshot --name "step1"    # saves /tmp/browser_screenshots/step1.png
$BT screenshot --full            # full page
$BT html                         # get full page HTML
$BT html --selector "div.main"   # get element HTML
$BT evaluate "document.title"    # run JS

# Waiting
$BT wait --selector "div.loaded" --timeout 15

# Management
$BT pages                        # list tabs
$BT status                       # check if running
$BT close                        # kill browser
```

## Rules

1. **Launch first** — always run `launch` before any other command
2. **Use snapshot for AI reasoning** — when you need to understand page structure, use `snapshot` first — it's faster and more accurate than screenshots
3. **Use Patchright** for sites with Cloudflare, DataDome, or other bot detection
4. **Profile persists** — user logs in once, stays logged in next time
5. **launch is NOT blocking** — it detaches the browser process and returns immediately
