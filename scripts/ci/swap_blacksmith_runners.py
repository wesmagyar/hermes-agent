#!/usr/bin/env python3
"""Swap Blacksmith-hosted runner labels for GitHub-hosted equivalents.

Only `runs-on:` values are touched. The Blacksmith *actions* (useblacksmith/checkout,
useblacksmith/setup-docker-builder, useblacksmith/build-push-action) are left alone:
useblacksmith/checkout needs no API key and works on any runner.

Label map:
  blacksmith-4vcpu-ubuntu-2404      -> ubuntu-latest
  blacksmith-32vcpu-ubuntu-2404     -> ubuntu-latest
  blacksmith-2vcpu-ubuntu-2404      -> ubuntu-latest
  blacksmith-32vcpu-ubuntu-2404-arm -> ubuntu-latest
  blacksmith-4vcpu-ubuntu-2404-arm  -> ubuntu-latest
  blacksmith-32vcpu-windows-2025    -> windows-latest
  blacksmith-2vcpu-windows-2025     -> windows-latest
  blacksmith-12vcpu-macos-latest    -> macos-latest
"""

import pathlib
import re

MAP = {
    "blacksmith-4vcpu-ubuntu-2404": "ubuntu-latest",
    "blacksmith-32vcpu-ubuntu-2404": "ubuntu-latest",
    "blacksmith-2vcpu-ubuntu-2404": "ubuntu-latest",
    "blacksmith-32vcpu-ubuntu-2404-arm": "ubuntu-latest",
    "blacksmith-4vcpu-ubuntu-2404-arm": "ubuntu-latest",
    "blacksmith-32vcpu-windows-2025": "windows-latest",
    "blacksmith-2vcpu-windows-2025": "windows-latest",
    "blacksmith-12vcpu-macos-latest": "macos-latest",
}

# Longest label first so "blacksmith-32vcpu-ubuntu-2404-arm" wins over
# "blacksmith-32vcpu-ubuntu-2404".
ORDERED = sorted(MAP, key=len, reverse=True)

WF = pathlib.Path(".github/workflows")
changed = {}

for path in sorted(WF.glob("*.y*ml")):
    text = original = path.read_text(encoding="utf-8-sig")
    for label in ORDERED:
        # runs-on: <label>   (optionally in a list)
        text = re.sub(
            rf"(?m)^(\s*runs-on:\s*){re.escape(label)}\s*$",
            rf"\g<1>{MAP[label]}",
            text,
        )
        # runner: <label>  (inside composite/with blocks)
        text = re.sub(
            rf"(?m)^(\s*runner:\s*){re.escape(label)}\s*$",
            rf"\g<1>{MAP[label]}",
            text,
        )
    if text != original:
        path.write_text(text, encoding="utf-8")
        n = sum(1 for a, b in zip(original.splitlines(), text.splitlines()) if a != b)
        changed[path.name] = n

for name, n in changed.items():
    print(f"  {name}: {n} line(s)")
print(f"  total files changed: {len(changed)}")
