#!/bin/bash
# Browser Agent — One-command installer
# Gives any AI CLI (Claude Code, Gemini, Qwen, OpenCode, Aider) browser control
#
# Install:
#   curl -fsSL https://raw.githubusercontent.com/yashaiguy-dev/browser-agent/main/install.sh | bash
#
# With anti-detection (bypasses Cloudflare/DataDome):
#   curl -fsSL https://raw.githubusercontent.com/yashaiguy-dev/browser-agent/main/install.sh | bash -s -- --with-patchright

set -e

TOOL_DIR="$HOME/.browser-tool"
REPO_RAW="https://raw.githubusercontent.com/yashaiguy-dev/browser-agent/main"
WITH_PATCHRIGHT=false

for arg in "$@"; do
    case $arg in
        --with-patchright) WITH_PATCHRIGHT=true ;;
    esac
done

echo ""
echo "  =========================================="
echo "    Browser Agent Installer"
echo "  =========================================="
echo ""

# Step 1: Check Python 3
echo "[1/4] Checking Python 3..."
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version 2>&1)
    echo "  $PY_VERSION"
else
    echo ""
    echo "  Python 3 is required but not found."
    echo ""
    echo "  Install it:"
    echo "    macOS:   brew install python3"
    echo "    Ubuntu:  sudo apt install python3 python3-pip"
    echo "    Windows: https://python.org/downloads"
    echo ""
    exit 1
fi

# Step 2: Download browser_tool.py
echo ""
echo "[2/4] Downloading browser_tool.py..."
mkdir -p "$TOOL_DIR"
if curl -fsSL "$REPO_RAW/browser_tool.py" -o "$TOOL_DIR/browser_tool.py"; then
    chmod +x "$TOOL_DIR/browser_tool.py"
    echo "  Saved to $TOOL_DIR/browser_tool.py"
else
    echo "  Failed to download. Check your internet connection."
    exit 1
fi

# Step 3: Install dependencies (Playwright + Chromium)
echo ""
echo "[3/4] Installing dependencies..."
if $WITH_PATCHRIGHT; then
    python3 "$TOOL_DIR/browser_tool.py" install --with-patchright
else
    python3 "$TOOL_DIR/browser_tool.py" install
fi

# Step 4: Install AI CLI skill files
echo ""
echo "[4/4] Setting up AI CLI integrations..."

# --- Claude Code ---
CLAUDE_CMD_DIR="$HOME/.claude/commands"
mkdir -p "$CLAUDE_CMD_DIR"
curl -fsSL "$REPO_RAW/skills/claude-code.md" -o "$CLAUDE_CMD_DIR/browser.md" 2>/dev/null
if [ -f "$CLAUDE_CMD_DIR/browser.md" ]; then
    echo "  Claude Code: $CLAUDE_CMD_DIR/browser.md"
fi

# --- Gemini CLI ---
GEMINI_FILE="$HOME/.gemini/GEMINI.md"
if [ -d "$HOME/.gemini" ] || command -v gemini &>/dev/null; then
    if [ -f "$GEMINI_FILE" ]; then
        if ! grep -q "browser-tool" "$GEMINI_FILE" 2>/dev/null; then
            echo "" >> "$GEMINI_FILE"
            curl -fsSL "$REPO_RAW/skills/gemini.md" >> "$GEMINI_FILE" 2>/dev/null
            echo "  Gemini CLI: appended to $GEMINI_FILE"
        else
            echo "  Gemini CLI: already configured"
        fi
    else
        mkdir -p "$HOME/.gemini"
        curl -fsSL "$REPO_RAW/skills/gemini.md" -o "$GEMINI_FILE" 2>/dev/null
        echo "  Gemini CLI: $GEMINI_FILE"
    fi
fi

echo ""
echo "  =========================================="
echo "    Installation Complete!"
echo "  =========================================="
echo ""
echo "  Quick start:"
echo "    python3 ~/.browser-tool/browser_tool.py launch"
echo "    python3 ~/.browser-tool/browser_tool.py navigate \"https://example.com\""
echo "    python3 ~/.browser-tool/browser_tool.py snapshot"
echo "    python3 ~/.browser-tool/browser_tool.py screenshot"
echo ""
echo "  In Claude Code, just say: /browser"
echo "  In Gemini CLI, just ask it to browse a website"
echo ""
