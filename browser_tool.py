#!/usr/bin/env python3
"""
Browser Control Tool for Claude Code.
Architecture: Launch Chromium with --remote-debugging-port, then
all commands connect via CDP. Browser stays open independently.

Supports Playwright (default) and Patchright (anti-detection).
Uses persistent profile so logins survive across sessions.
"""

import sys
import json
import os
import time
import argparse
import subprocess
import signal
import urllib.request

PROFILE_DIR = os.path.expanduser("~/.browser-tool/profile")
SCREENSHOT_DIR = "/tmp/browser_screenshots"
STATE_FILE = "/tmp/browser_tool_state.json"
CDP_PORT = 9222

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(PROFILE_DIR, exist_ok=True)


def get_engine(use_patchright=False):
    if use_patchright:
        from patchright.sync_api import sync_playwright
    else:
        from playwright.sync_api import sync_playwright
    return sync_playwright


def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def is_cdp_available(port=CDP_PORT):
    """Check if a CDP endpoint is reachable."""
    try:
        urllib.request.urlopen(f"http://localhost:{port}/json/version", timeout=2)
        return True
    except Exception:
        return False


def get_chromium_path(use_patchright=False):
    """Get the Chromium executable path from Playwright/Patchright."""
    sync_pw = get_engine(use_patchright)
    pw = sync_pw().start()
    path = pw.chromium.executable_path
    pw.stop()
    return path


def cmd_install(args):
    """Install all dependencies needed for the browser tool."""
    import shutil

    errors = []

    # Step 1: Check Python 3
    print("--- Checking Python 3 ---")
    py_version = sys.version.split()[0]
    print(f"  Python {py_version} ✓")

    # Step 2: Check/install pip3
    print("\n--- Checking pip3 ---")
    pip_path = shutil.which("pip3")
    if pip_path:
        print(f"  pip3 found at {pip_path} ✓")
    else:
        print("  pip3 not found. Install Python 3 from https://python.org")
        errors.append("pip3 not found")

    # Step 3: Install Playwright
    print("\n--- Installing Playwright ---")
    try:
        import playwright
        print(f"  playwright already installed ✓")
    except ImportError:
        print("  Installing playwright...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "playwright"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print("  playwright installed ✓")
        else:
            print(f"  ERROR: {result.stderr.strip()}")
            errors.append("playwright install failed")

    # Step 4: Install Chromium browser
    print("\n--- Installing Chromium ---")
    result = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"],
                            capture_output=True, text=True)
    if result.returncode == 0:
        print("  Chromium installed ✓")
    else:
        # Check if already installed
        if "already" in result.stderr.lower() or result.returncode == 0:
            print("  Chromium already installed ✓")
        else:
            print(f"  ERROR: {result.stderr.strip()}")
            errors.append("Chromium install failed")

    # Step 5: Install Patchright (optional)
    if args.with_patchright:
        print("\n--- Installing Patchright (anti-detection) ---")
        try:
            import patchright
            print(f"  patchright already installed ✓")
        except ImportError:
            print("  Installing patchright...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", "patchright"],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                print("  patchright installed ✓")
            else:
                print(f"  ERROR: {result.stderr.strip()}")
                errors.append("patchright install failed")

        print("  Installing Patchright Chromium...")
        result = subprocess.run([sys.executable, "-m", "patchright", "install", "chromium"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print("  Patchright Chromium installed ✓")
        else:
            print(f"  WARNING: {result.stderr.strip()}")

    # Step 6: Verify
    print("\n--- Verification ---")
    try:
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start()
        path = pw.chromium.executable_path
        pw.stop()
        if os.path.exists(path):
            print(f"  Chromium binary: {path} ✓")
        else:
            print(f"  WARNING: Chromium binary not found at {path}")
            errors.append("Chromium binary missing")
    except Exception as e:
        print(f"  Verification failed: {e}")
        errors.append(f"Verification: {e}")

    print(f"\n--- Summary ---")
    print(f"  Tool location: {os.path.abspath(__file__)}")
    print(f"  Profile dir:   {PROFILE_DIR}")
    print(f"  Screenshots:   {SCREENSHOT_DIR}")

    if errors:
        print(f"\n  ⚠ {len(errors)} issue(s):")
        for e in errors:
            print(f"    - {e}")
        sys.exit(1)
    else:
        print(f"\n  All good! Run: python3 {os.path.abspath(__file__)} launch")


def cmd_launch(args):
    """Launch Chromium with CDP enabled. Runs as a detached process."""
    port = args.port or CDP_PORT
    engine_name = "patchright" if args.patchright else "playwright"

    if args.connect:
        # Just register an existing Chrome instance
        if not is_cdp_available(args.connect):
            print(f"ERROR: No Chrome found on port {args.connect}")
            print(f"Start Chrome with: chrome --remote-debugging-port={args.connect}")
            sys.exit(1)

        save_state({
            "engine": engine_name,
            "mode": "cdp",
            "cdp_port": args.connect,
        })
        print(f"Connected to existing Chrome on port {args.connect}")
        return

    # Check if already running
    if is_cdp_available(port):
        print(f"Browser already running on port {port}")
        save_state({
            "engine": engine_name,
            "mode": "launched",
            "cdp_port": port,
        })
        return

    # Get chromium path
    chromium_path = get_chromium_path(args.patchright)
    profile_dir = os.path.join(PROFILE_DIR, engine_name)
    os.makedirs(profile_dir, exist_ok=True)

    # Launch Chromium as a detached process
    chrome_args = [
        chromium_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_dir}",
        "--disable-blink-features=AutomationControlled",
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1280,800",
    ]

    proc = subprocess.Popen(
        chrome_args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setpgrp,  # Detach from parent
    )

    # Wait for CDP to be ready
    for _ in range(30):
        if is_cdp_available(port):
            break
        time.sleep(0.5)
    else:
        print("ERROR: Browser failed to start (CDP not available after 15s)")
        proc.kill()
        sys.exit(1)

    save_state({
        "engine": engine_name,
        "mode": "launched",
        "cdp_port": port,
        "pid": proc.pid,
    })

    print(f"Browser launched ({engine_name})")
    print(f"CDP: http://localhost:{port}")
    print(f"Profile: {profile_dir}")
    print(f"PID: {proc.pid}")


def _connect(state=None):
    """Connect to the running browser via CDP. Returns (pw, browser, page)."""
    if state is None:
        state = load_state()
    if not state:
        print("ERROR: No browser running. Run 'browser_tool.py launch' first.")
        sys.exit(1)

    port = state.get("cdp_port", CDP_PORT)
    engine_name = state.get("engine", "playwright")
    use_patchright = engine_name == "patchright"

    if not is_cdp_available(port):
        print(f"ERROR: Browser not reachable on port {port}. Launch it first.")
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        sys.exit(1)

    sync_pw = get_engine(use_patchright)
    pw = sync_pw().start()
    browser = pw.chromium.connect_over_cdp(f"http://localhost:{port}")
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    page = context.pages[0] if context.pages else context.new_page()

    return pw, browser, page


def cmd_navigate(args):
    pw, browser, page = _connect()
    try:
        page.goto(args.url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(1)  # Let page render
        print(f"Navigated to: {page.url}")
        print(f"Title: {page.title()}")

        path = os.path.join(SCREENSHOT_DIR, "latest.png")
        page.screenshot(path=path, full_page=False)
        print(f"Screenshot: {path}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        browser.close()
        pw.stop()


def cmd_click(args):
    pw, browser, page = _connect()
    try:
        page.click(args.selector, timeout=10000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(0.5)

        print(f"Clicked: {args.selector}")
        print(f"Current URL: {page.url}")

        path = os.path.join(SCREENSHOT_DIR, "latest.png")
        page.screenshot(path=path, full_page=False)
        print(f"Screenshot: {path}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        browser.close()
        pw.stop()


def cmd_type(args):
    pw, browser, page = _connect()
    try:
        if args.clear:
            page.fill(args.selector, args.text, timeout=10000)
        else:
            page.type(args.selector, args.text, timeout=10000)

        print(f"Typed into: {args.selector}")

        path = os.path.join(SCREENSHOT_DIR, "latest.png")
        page.screenshot(path=path, full_page=False)
        print(f"Screenshot: {path}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        browser.close()
        pw.stop()


def cmd_screenshot(args):
    pw, browser, page = _connect()
    try:
        name = args.name or "latest"
        path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
        page.screenshot(path=path, full_page=args.full)

        print(f"URL: {page.url}")
        print(f"Title: {page.title()}")
        print(f"Screenshot: {path}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        browser.close()
        pw.stop()


def cmd_evaluate(args):
    pw, browser, page = _connect()
    try:
        result = page.evaluate(args.js)
        print(f"Result: {json.dumps(result, indent=2, default=str)}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        browser.close()
        pw.stop()


def cmd_snapshot(args):
    """Return accessibility tree — structured page content optimized for LLMs."""
    pw, browser, page = _connect()
    try:
        # Get the accessibility tree
        snapshot = page.accessibility.snapshot()
        if not snapshot:
            print("ERROR: Could not get accessibility snapshot (page may be empty)")
            sys.exit(1)

        def format_node(node, indent=0):
            """Recursively format the accessibility tree as readable text."""
            lines = []
            role = node.get("role", "")
            name = node.get("name", "")
            value = node.get("value", "")

            # Skip generic/noise nodes with no useful info
            if role in ("none", "generic", "LineBreak") and not name:
                # Still recurse into children
                for child in node.get("children", []):
                    lines.extend(format_node(child, indent))
                return lines

            # Build the node description
            prefix = "  " * indent
            parts = [role]
            if name:
                parts.append(f'"{name}"')

            # Add useful properties
            props = []
            if value:
                props.append(f"value={value}")
            if node.get("checked") is not None:
                props.append(f"checked={node['checked']}")
            if node.get("disabled"):
                props.append("disabled")
            if node.get("expanded") is not None:
                props.append(f"expanded={node['expanded']}")
            if node.get("level"):
                props.append(f"level={node['level']}")
            if node.get("url"):
                props.append(f"href={node['url']}")

            if props:
                parts.append(f"[{', '.join(props)}]")

            lines.append(f"{prefix}- {' '.join(parts)}")

            for child in node.get("children", []):
                lines.extend(format_node(child, indent + 1))
            return lines

        # If selector specified, try to scope to that element
        if args.selector:
            el = page.query_selector(args.selector)
            if not el:
                print(f"ERROR: Selector '{args.selector}' not found")
                sys.exit(1)
            # Get snapshot of the specific element via aria-snapshot
            snapshot = page.accessibility.snapshot(root=el)
            if not snapshot:
                print(f"ERROR: Could not snapshot element '{args.selector}'")
                sys.exit(1)

        tree = format_node(snapshot)
        output = "\n".join(tree)

        # Truncate if too large
        if len(output) > 50000:
            output = output[:50000] + "\n... (truncated)"

        print(f"URL: {page.url}")
        print(f"Title: {page.title()}")
        print(f"--- Accessibility Tree ---")
        print(output)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        browser.close()
        pw.stop()


def cmd_html(args):
    pw, browser, page = _connect()
    try:
        if args.selector:
            el = page.query_selector(args.selector)
            if el:
                html = el.inner_html()
            else:
                print(f"ERROR: Selector '{args.selector}' not found")
                sys.exit(1)
        else:
            html = page.content()

        if len(html) > 50000:
            html = html[:50000] + "\n... (truncated)"
        print(html)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        browser.close()
        pw.stop()


def cmd_wait(args):
    pw, browser, page = _connect()
    try:
        if args.selector:
            page.wait_for_selector(args.selector, timeout=args.timeout * 1000)
            print(f"Found: {args.selector}")
        else:
            page.wait_for_load_state("networkidle", timeout=args.timeout * 1000)
            print("Page loaded (network idle)")

        path = os.path.join(SCREENSHOT_DIR, "latest.png")
        page.screenshot(path=path, full_page=False)
        print(f"Screenshot: {path}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        browser.close()
        pw.stop()


def cmd_close(args):
    state = load_state()
    if not state:
        print("No browser running.")
        return

    pid = state.get("pid")
    if pid:
        try:
            # Kill the process group to get all child processes
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            print(f"Stopped browser (PID {pid})")
        except (ProcessLookupError, PermissionError):
            # Try direct kill
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"Stopped browser (PID {pid})")
            except ProcessLookupError:
                print("Browser process already gone.")

    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    print("Browser state cleared.")


def cmd_pages(args):
    pw, browser, page = _connect()
    try:
        for ctx in browser.contexts:
            for i, p in enumerate(ctx.pages):
                print(f"[{i}] {p.url} — {p.title()}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        browser.close()
        pw.stop()


def cmd_status(args):
    """Check if browser is running."""
    state = load_state()
    if not state:
        print("No browser registered.")
        return

    port = state.get("cdp_port", CDP_PORT)
    if is_cdp_available(port):
        print(f"Browser is running on port {port}")
        print(f"Engine: {state.get('engine', 'unknown')}")
        print(f"PID: {state.get('pid', 'unknown')}")
    else:
        print(f"Browser registered but NOT reachable on port {port}")
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        print("Cleaned up stale state.")


def main():
    parser = argparse.ArgumentParser(description="Browser Control Tool for Claude Code")
    sub = parser.add_subparsers(dest="command")

    p_install = sub.add_parser("install", help="Install all dependencies (Playwright, Chromium)")
    p_install.add_argument("--with-patchright", action="store_true", help="Also install Patchright (anti-detection)")

    p_launch = sub.add_parser("launch", help="Launch browser with CDP")
    p_launch.add_argument("--patchright", action="store_true", help="Use Patchright (anti-detection)")
    p_launch.add_argument("--connect", type=int, help="Connect to existing Chrome CDP port")
    p_launch.add_argument("--port", type=int, default=CDP_PORT, help=f"CDP port (default: {CDP_PORT})")

    p_nav = sub.add_parser("navigate", help="Navigate to URL")
    p_nav.add_argument("url")

    p_click = sub.add_parser("click", help="Click element")
    p_click.add_argument("selector")

    p_type = sub.add_parser("type", help="Type into element")
    p_type.add_argument("selector")
    p_type.add_argument("text")
    p_type.add_argument("--clear", action="store_true", help="Clear field before typing")

    p_ss = sub.add_parser("screenshot", help="Take screenshot")
    p_ss.add_argument("--name", default="latest")
    p_ss.add_argument("--full", action="store_true", help="Full page screenshot")

    p_eval = sub.add_parser("evaluate", help="Run JavaScript")
    p_eval.add_argument("js")

    p_snap = sub.add_parser("snapshot", help="Get accessibility tree (AI-friendly page structure)")
    p_snap.add_argument("--selector", default=None, help="CSS selector to scope snapshot")

    p_html = sub.add_parser("html", help="Get page HTML")
    p_html.add_argument("--selector", default=None)

    p_wait = sub.add_parser("wait", help="Wait for element/load")
    p_wait.add_argument("--selector", default=None)
    p_wait.add_argument("--timeout", type=int, default=10)

    sub.add_parser("close", help="Close browser")
    sub.add_parser("pages", help="List open tabs")
    sub.add_parser("status", help="Check browser status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "install": cmd_install,
        "launch": cmd_launch,
        "navigate": cmd_navigate,
        "click": cmd_click,
        "type": cmd_type,
        "screenshot": cmd_screenshot,
        "snapshot": cmd_snapshot,
        "evaluate": cmd_evaluate,
        "close": cmd_close,
        "pages": cmd_pages,
        "html": cmd_html,
        "wait": cmd_wait,
        "status": cmd_status,
    }

    cmds[args.command](args)


if __name__ == "__main__":
    main()
