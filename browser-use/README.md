# Browser Use — Claude Code Skill

Give Claude Code full browser control. Navigate pages, click buttons, fill forms, take screenshots, and read page content — all through a real Chromium browser.

## What It Does

- Launches a real Chromium browser controlled via Chrome DevTools Protocol (CDP)
- Claude can navigate, click, type, screenshot, and read any web page
- Persistent login profile — log in once, stay logged in across sessions
- Optional anti-detection mode (Patchright) for sites with bot protection
- Accessibility tree snapshots for token-efficient page understanding

## Requirements

- Python 3.8+
- macOS, Linux, or Windows

## Installation

### 1. Copy the tool

```bash
mkdir -p ~/.browser-tool
cp browser_tool.py ~/.browser-tool/browser_tool.py
```

### 2. Install dependencies

```bash
python3 ~/.browser-tool/browser_tool.py install
```

This installs Playwright and downloads Chromium automatically.

**Optional — anti-detection mode** (for Cloudflare/DataDome protected sites):

```bash
python3 ~/.browser-tool/browser_tool.py install --with-patchright
```

### 3. Add the skill to Claude Code

Copy the skill file to your Claude Code commands directory:

```bash
mkdir -p ~/.claude/commands
cp browser.md ~/.claude/commands/browser.md
```

### 4. Done

Open Claude Code and type `/browser` to activate browser control. Or just ask Claude to "open a browser and go to example.com" — it will know what to do.

## How It Works

```
You (Claude Code) ──> browser_tool.py ──> CDP ──> Chromium
                                                    ↑
                                          Stays open as a
                                          detached process
```

1. `launch` starts Chromium with `--remote-debugging-port=9222` as a detached process
2. Every other command (navigate, click, screenshot...) connects via CDP, does its work, disconnects
3. The browser stays open independently — no process blocking
4. Login sessions persist in `~/.browser-tool/profile/`

## Quick Reference

| Command | What it does |
|---------|-------------|
| `launch` | Start Chromium (or `--patchright` for anti-detection) |
| `navigate <url>` | Go to a URL |
| `click <selector>` | Click an element |
| `type <selector> <text>` | Type into a field (`--clear` to replace) |
| `snapshot` | Get accessibility tree (best for AI reasoning) |
| `screenshot` | Save viewport screenshot |
| `html` | Get page HTML |
| `evaluate <js>` | Run JavaScript |
| `wait --selector <sel>` | Wait for element to appear |
| `pages` | List open tabs |
| `status` | Check if browser is running |
| `close` | Kill the browser |

## Tips

- **Use `snapshot` over `screenshot`** when Claude needs to understand page structure — it's faster and more token-efficient
- **Use `--patchright`** when a site has Cloudflare, DataDome, or similar bot detection
- **Logins persist** — once you log into a site, you stay logged in across Claude Code sessions
- **Screenshots** are saved to `/tmp/browser_screenshots/` and auto-opened in Preview (macOS)
