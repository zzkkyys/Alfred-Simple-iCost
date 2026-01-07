#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Open one or multiple URLs on macOS.

Input can be:
- a single URL
- multiple URLs separated by newlines

It prints the original input back to stdout so downstream Alfred nodes
receive the same payload.
"""

import os
import sys
import subprocess


def _read_input() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def _split_urls(payload: str) -> list[str]:
    payload = (payload or "").strip()
    if not payload:
        return []

    # Some Alfred actions may pass literal "\\n" instead of real newlines.
    if "\\n" in payload and "\n" not in payload:
        payload = payload.replace("\\n", "\n")

    # Prefer newline-separated payload for safety (no quotes needed)
    urls = [line.strip() for line in payload.splitlines() if line.strip()]
    if len(urls) > 1:
        return urls
    return [payload]


def main() -> int:
    payload = _read_input()
    urls = _split_urls(payload)

    for url in urls:
        # macOS: open URL
        subprocess.run(["open", url], check=False)

    # Pass-through for downstream actions (e.g. habbit.py)
    sys.stdout.write(payload.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
