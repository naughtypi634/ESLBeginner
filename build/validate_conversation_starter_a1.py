#!/usr/bin/env python3
"""Validate the A1 conversation starter source structure."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [ROOT / "MD" / "conversation starter" / "A1" / f"ConversationStarter.A1.Unit{i}.md" for i in range(1, 11)]


def sections(text: str):
    matches = list(re.finditer(r"^### STORY \d+: .+$", text, re.MULTILINE))
    return [text[m.start(): matches[i + 1].start() if i + 1 < len(matches) else len(text)]
            for i, m in enumerate(matches)]


def numbered_block(section: str, heading: str):
    start = section.find(heading)
    if start < 0:
        return []
    tail = section[start + len(heading):]
    next_heading = re.search(r"^\*\*[^\n]+\*\*$", tail, re.MULTILINE)
    if next_heading:
        tail = tail[:next_heading.start()]
    return re.findall(r"^\d+\.\s+(.+)$", tail, re.MULTILINE)


def main():
    errors = []
    total = 0
    for source in SOURCES:
        if not source.exists():
            errors.append(f"missing {source.name}")
            continue
        stories = sections(source.read_text(encoding="utf-8"))
        if len(stories) != 5:
            errors.append(f"{source.name}: expected 5 stories, got {len(stories)}")
        for index, story in enumerate(stories, 1):
            total += 1
            vocabulary = numbered_block(story, "**Key Vocabulary**")
            discussion = numbered_block(story, "**Conversation Questions**")
            for label, values, expected in (("vocabulary", vocabulary, 10), ("discussion", discussion, 10)):
                if len(values) != expected:
                    errors.append(f"{source.name} story {index}: {label} expected {expected}, got {len(values)}")
            if "**Comprehension Questions**" in story:
                errors.append(f"{source.name} story {index}: comprehension questions must be removed")
            if "**Story**" not in story:
                errors.append(f"{source.name} story {index}: missing story body")

    if errors:
        print("FAIL")
        print("\n".join(errors))
        return 1
    print(f"PASS: {total} stories across 10 units; each has 10 vocabulary and 10 conversation questions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
