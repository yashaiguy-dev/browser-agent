#!/bin/bash
# Browser Use — One-command installer
# Usage: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Installing Browser Use ==="
echo ""

# Step 1: Copy tool
echo "[1/3] Copying tool to ~/.browser-tool/"
mkdir -p ~/.browser-tool
cp "$SCRIPT_DIR/browser_tool.py" ~/.browser-tool/browser_tool.py
echo "  Done ✓"

# Step 2: Install dependencies
echo ""
echo "[2/3] Installing Python dependencies + Chromium..."
python3 ~/.browser-tool/browser_tool.py install
echo "  Done ✓"

# Step 3: Install skill file
echo ""
echo "[3/3] Adding skill to Claude Code..."
mkdir -p ~/.claude/commands
cp "$SCRIPT_DIR/browser.md" ~/.claude/commands/browser.md
echo "  Done ✓"

echo ""
echo "=== Installation complete! ==="
echo ""
echo "Usage:"
echo "  • In Claude Code: type /browser or ask 'open a browser and go to google.com'"
echo ""
echo "Optional — anti-detection mode (for Cloudflare/DataDome sites):"
echo "  python3 ~/.browser-tool/browser_tool.py install --with-patchright"
