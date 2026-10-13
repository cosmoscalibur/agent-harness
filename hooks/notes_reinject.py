#!/usr/bin/env python3
"""SessionStart hook: re-inject the task notes file after a compaction.

Reads the hook payload as JSON on stdin and emits the contents of
``.agent-harness/notes.md`` under the session's working directory as
additional context, when that file exists.
"""

import json
import sys
from pathlib import Path

NOTES_PATH = Path(".agent-harness") / "notes.md"


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    notes_file = Path(payload.get("cwd", ".")) / NOTES_PATH
    if not notes_file.is_file():
        return

    context = (
        f"Context was compacted. {NOTES_PATH} holds the developer's verbatim "
        "requirements, decisions, and the live plan; it takes precedence over "
        "the compaction summary (rules/agent-harness.md section 1).\n\n"
        + notes_file.read_text(encoding="utf-8")
    )
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
