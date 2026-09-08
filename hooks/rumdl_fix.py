#!/usr/bin/env python3
"""PostToolUse hook: run rumdl fmt on an edited Markdown file.

Reads the hook payload as JSON on stdin and acts only on .md files. `fmt`
applies the same fixes as `check --fix` (they share rumdl's rule engine;
only the exit-code convention differs) plus formatting, so a separate
`check --fix` call first would just repeat it.
"""

import json
import subprocess
import sys

MARKDOWN_SUFFIXES = (".md",)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    file_path = payload.get("tool_input", {}).get("file_path")
    if not file_path or not file_path.endswith(MARKDOWN_SUFFIXES):
        return

    _ = subprocess.run(["uvx", "rumdl", "fmt", "-q", file_path], check=False)


if __name__ == "__main__":
    main()
