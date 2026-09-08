#!/usr/bin/env python3
"""PostToolUse hook: run Ruff (fix, then format) on an edited Python file.

Reads the hook payload as JSON on stdin and acts only on .py/.pyi files.
"""

import json
import subprocess
import sys

PYTHON_SUFFIXES = (".py", ".pyi")


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    file_path = payload.get("tool_input", {}).get("file_path")
    if not file_path or not file_path.endswith(PYTHON_SUFFIXES):
        return

    _ = subprocess.run(["uvx", "ruff", "check", "--fix", "-q", file_path], check=False)
    _ = subprocess.run(["uvx", "ruff", "format", "-q", file_path], check=False)


if __name__ == "__main__":
    main()
