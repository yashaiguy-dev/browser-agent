#!/bin/bash
# Browser Use — One-command installer
# Supports: Claude Code, Qwen Code, standalone
# Usage: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Installing Browser Use ==="
echo ""

# Step 1: Copy tool to shared location
echo "[1/3] Copying tool to ~/.browser-tool/"
mkdir -p ~/.browser-tool
cp "$SCRIPT_DIR/browser_tool.py" ~/.browser-tool/browser_tool.py
echo "  Done ✓"

# Step 2: Install dependencies
echo ""
echo "[2/3] Installing Python dependencies + Chromium..."
python3 ~/.browser-tool/browser_tool.py install
echo "  Done ✓"

# Step 3: Detect and install for available AI CLIs
echo ""
echo "[3/3] Installing skill files..."

INSTALLED=""

# Claude Code
if [ -d "$HOME/.claude" ] || command -v claude &>/dev/null; then
    mkdir -p ~/.claude/commands
    cp "$SCRIPT_DIR/browser.md" ~/.claude/commands/browser.md
    echo "  Claude Code ✓  (command installed)"
    INSTALLED="$INSTALLED claude"
fi

# Qwen Code
if [ -d "$HOME/.qwen" ] || command -v qwen &>/dev/null; then
    mkdir -p ~/.qwen/skills/browser
    cp "$SCRIPT_DIR/browser_tool.py" ~/.qwen/skills/browser/browser_tool.py
    cp "$SCRIPT_DIR/SKILL.md" ~/.qwen/skills/browser/SKILL.md
    mkdir -p ~/.qwen/commands
    cp "$SCRIPT_DIR/browser.md" ~/.qwen/commands/browser.md
    echo "  Qwen Code ✓  (skill + command installed)"
    INSTALLED="$INSTALLED qwen"
fi

# Fallback: install for both if neither detected
if [ -z "$INSTALLED" ]; then
    echo "  No AI CLI detected. Installing for both Claude Code and Qwen Code..."
    mkdir -p ~/.claude/commands
    cp "$SCRIPT_DIR/browser.md" ~/.claude/commands/browser.md
    mkdir -p ~/.qwen/skills/browser ~/.qwen/commands
    cp "$SCRIPT_DIR/browser_tool.py" ~/.qwen/skills/browser/browser_tool.py
    cp "$SCRIPT_DIR/SKILL.md" ~/.qwen/skills/browser/SKILL.md
    cp "$SCRIPT_DIR/browser.md" ~/.qwen/commands/browser.md
    echo "  Claude Code ✓"
    echo "  Qwen Code ✓"
fi

echo ""
echo "=== Installation complete! ==="
echo ""
echo "Usage:"
echo "  • Claude Code:  type /browser or ask 'open a browser and go to google.com'"
echo "  • Qwen Code:    type /browser or ask 'open a browser and go to google.com'"
echo "  • Standalone:   python3 ~/.browser-tool/browser_tool.py launch"
echo ""
echo "Optional — anti-detection mode (for Cloudflare/DataDome sites):"
echo "  python3 ~/.browser-tool/browser_tool.py install --with-patchright"
