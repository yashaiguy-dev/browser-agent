
# Browser Control Tool

You have a browser control tool at `~/.browser-tool/browser_tool.py` that controls a real visible Chromium browser via CDP (Chrome DevTools Protocol).

## How to use

Run commands via shell. Always launch the browser first.

```bash
BT="python3 ~/.browser-tool/browser_tool.py"

# Launch browser (runs as detached process, returns immediately)
$BT launch

# Navigate
$BT navigate "https://example.com"

# Get page structure (use this to understand what's on the page)
$BT snapshot

# Take screenshot
$BT screenshot

# Interact
$BT click "button.submit"
$BT type "input[name=email]" "user@example.com"
$BT type "input[name=email]" "new@example.com" --clear

# Get HTML
$BT html
$BT html --selector "div.main"

# Run JavaScript
$BT evaluate "document.title"

# Wait for elements
$BT wait --selector "div.loaded" --timeout 15

# Management
$BT pages       # list tabs
$BT status      # check if running
$BT close       # kill browser
```

## Key rules
- Always run `launch` before any other command
- Use `snapshot` to understand page structure — it returns an accessibility tree that's fast and accurate
- Use `screenshot` when the user wants to see what's on screen
- Browser stays open between commands — no need to relaunch
- Profile persists at `~/.browser-tool/profile/` — logins survive across sessions
