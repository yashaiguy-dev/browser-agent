# Browser Control Skill

You have a browser control tool at `~/.browser-tool/browser_tool.py` that controls a real visible Chromium browser via CDP.

## First-Time Setup

If the tool isn't installed yet, run:
```bash
# Download the tool
mkdir -p ~/.browser-tool
# (copy browser_tool.py to ~/.browser-tool/)

# Install all dependencies (Playwright + Chromium)
python3 ~/.browser-tool/browser_tool.py install

# Optional: add anti-detection support
python3 ~/.browser-tool/browser_tool.py install --with-patchright
```

## Architecture
- `launch` starts Chromium as a **detached process** with `--remote-debugging-port=9222`
- All other commands **connect via CDP**, do their work, disconnect
- Browser stays open independently — no blocking needed
- Persistent profile at `~/.browser-tool/profile/` — logins survive across sessions

## Commands

```bash
BT="python3 ~/.browser-tool/browser_tool.py"

# Install dependencies (first time only)
$BT install                      # Playwright + Chromium
$BT install --with-patchright    # + anti-detection engine

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

## Showing Screenshots

After any command that takes a screenshot, open it in Preview for the user:
```bash
open -a Preview /tmp/browser_screenshots/latest.png
```

## Rules

1. **Launch first** — always run `launch` before any other command
2. **Show screenshots** — after navigate/click/type, open `/tmp/browser_screenshots/latest.png` in Preview so the user can see it
3. **Use Patchright** for sites with Cloudflare, DataDome, or other bot detection
4. **Profile persists** — user logs in once, stays logged in next time
5. **launch is NOT blocking** — it detaches the browser process and returns immediately
6. **Use snapshot for AI reasoning** — when you need to understand page structure (find buttons, read content, decide what to click), use `snapshot` first — it's faster and more accurate than reading a screenshot
