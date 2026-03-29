# Browser Agent

Give any AI coding CLI (Claude Code, Gemini CLI, Qwen, OpenCode, Aider) the ability to control a real browser — navigate, click, type, take screenshots, and read page structure.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/yashaiguy-dev/browser-agent/main/install.sh | bash
```

With anti-detection (bypasses Cloudflare, DataDome, bot protection):
```bash
curl -fsSL https://raw.githubusercontent.com/yashaiguy-dev/browser-agent/main/install.sh | bash -s -- --with-patchright
```

### What it installs
- `~/.browser-tool/browser_tool.py` — the browser control tool
- `~/.claude/commands/browser.md` — Claude Code skill (auto-detected)
- `~/.gemini/GEMINI.md` — Gemini CLI instructions (auto-detected)
- Playwright + Chromium browser

### Requirements
- Python 3.8+
- macOS, Linux, or Windows

## Usage

```bash
BT="python3 ~/.browser-tool/browser_tool.py"

# Launch browser (opens visible Chromium window)
$BT launch

# Navigate to a page
$BT navigate "https://example.com"

# Get page structure (AI-friendly accessibility tree)
$BT snapshot

# Take screenshot
$BT screenshot

# Click, type, interact
$BT click "button.submit"
$BT type "input[name=email]" "hello@example.com"
$BT type "input[name=email]" "new@example.com" --clear

# Get HTML
$BT html
$BT html --selector "div.main"

# Run JavaScript
$BT evaluate "document.title"

# Wait for elements
$BT wait --selector "div.loaded" --timeout 15

# Manage
$BT pages       # list open tabs
$BT status      # check if browser is running
$BT close       # close browser
```

## How It Works

```
AI CLI (Claude/Gemini/Qwen)
  → runs shell command
    → browser_tool.py connects via CDP (port 9222)
      → controls real Chromium browser
        → returns results to AI
```

- **Visible browser** — you can watch what the AI is doing
- **Persistent profile** — log in once, stays logged in across sessions
- **Snapshot** — returns accessibility tree (structured text) instead of screenshots, so the AI understands the page with fewer tokens
- **Anti-detection** — optional Patchright mode bypasses Cloudflare, DataDome, and other bot protection

## Commands

| Command | Description |
|---|---|
| `install` | Install all dependencies (Playwright + Chromium) |
| `install --with-patchright` | Also install anti-detection engine |
| `launch` | Launch Chromium with CDP |
| `launch --patchright` | Launch with anti-detection |
| `launch --connect 9222` | Attach to existing Chrome |
| `navigate <url>` | Navigate to URL |
| `click <selector>` | Click an element |
| `type <selector> <text>` | Type into an element |
| `type <selector> <text> --clear` | Clear field, then type |
| `screenshot` | Take screenshot |
| `screenshot --full` | Full page screenshot |
| `screenshot --name <name>` | Named screenshot |
| `snapshot` | Get accessibility tree |
| `snapshot --selector <sel>` | Scoped accessibility tree |
| `html` | Get page HTML |
| `html --selector <sel>` | Get element HTML |
| `evaluate <js>` | Run JavaScript |
| `wait --selector <sel>` | Wait for element |
| `pages` | List open tabs |
| `status` | Check browser status |
| `close` | Close browser |

## AI CLI Integration

### Claude Code
After install, the `/browser` skill is available automatically. Just tell Claude to browse a website.

### Gemini CLI
After install, instructions are added to `~/.gemini/GEMINI.md`. Just ask Gemini to browse a website.

### Other CLIs (Qwen, OpenCode, Aider)
Copy the contents of `skills/gemini.md` into your CLI's system prompt or instructions file.

## Snapshot vs Screenshot

| | Screenshot | Snapshot |
|---|---|---|
| Output | PNG image | Structured text |
| Token cost | ~1000+ tokens | ~100-300 tokens |
| AI accuracy | Guesses from pixels | Exact element names/roles |
| Hidden elements | Can't see | Sees everything |
| Best for | Human viewing | AI reasoning |

Use `snapshot` when the AI needs to understand the page. Use `screenshot` when you want to see it yourself.

## License

MIT
