"""Parse a Markdown PRD into user stories and their acceptance criteria.

Expected shape:  ### US-101 Title  /  As a ..., I want ..., so ...  /  - criterion  - criterion
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

HEADING = re.compile(r"^#{2,4}\s+([A-Z]{2,5}-\d+)\s*[:.\-]?\s+(.*)$")


@dataclass
class Story:
    id: str
    title: str
    narrative: str = ""
    criteria: list[str] = field(default_factory=list)


def parse_text(text: str) -> tuple[str, list[Story]]:
    title, stories, current = "", [], None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        elif m := HEADING.match(line):
            current = Story(m.group(1), m.group(2).strip())
            stories.append(current)
        elif current and re.match(r"^([-*]|\d+\.)\s+", line):
            current.criteria.append(re.sub(r"^([-*]|\d+\.)\s+", "", line).strip())
        elif current and line and not current.criteria and not line.startswith("#"):
            current.narrative = f"{current.narrative} {line}".strip()
    return title, stories


def parse_prd(path: Path) -> tuple[str, list[Story]]:
    return parse_text(Path(path).read_text(encoding="utf-8"))
