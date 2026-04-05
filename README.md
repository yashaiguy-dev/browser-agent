# Agent Tech Skills (Open)

A collection of open-source skills for Claude Code — giving your AI agent real-world superpowers.

Each folder is a self-contained skill with its own README, install instructions, and source files.

## Skills

| Skill | Description | Status |
|-------|-------------|--------|
| [browser-use](./browser-use/) | Full browser control — navigate, click, type, screenshot, read pages | Ready |

## What Are Claude Code Skills?

Skills are markdown files that teach Claude Code how to use specific tools. When you place a `.md` file in `~/.claude/commands/`, it becomes available as a slash command (e.g., `/browser`). The skill file tells Claude what the tool can do, how to call it, and what rules to follow.

## How to Install Any Skill

Each skill folder contains:
- **`README.md`** — Full install guide and usage docs
- **Skill file** (`.md`) — Goes into `~/.claude/commands/`
- **Tool files** (`.py`, `.sh`, etc.) — The actual tool Claude will call

General steps:
1. Copy the tool file(s) to the location specified in the skill's README
2. Install any dependencies (usually one command)
3. Copy the `.md` skill file to `~/.claude/commands/`
4. Use it in Claude Code

## Contributing

Want to add a skill? Create a folder with:
```
your-skill/
  README.md          # Install + usage guide
  your-skill.md      # The Claude Code skill file
  tool_files...      # Whatever the skill needs
```
