"""One review run, shared by the CLI and the web app."""

from dataclasses import dataclass, field

from speccheck.generate import LLM, Drafted, draft, gemini
from speccheck.lint import Gap, lint
from speccheck.parse import Story, parse_text


@dataclass
class Review:
    title: str
    stories: list[Story]
    gaps: list[Gap]
    drafts: dict[str, Drafted] = field(default_factory=dict)
    skipped: dict[str, str] = field(default_factory=dict)  # story id -> why drafting failed

    @property
    def blocking(self) -> list[Gap]:
        return [g for g in self.gaps if g.severity == "high"]


def run(text: str, use_llm: bool = True, llm: LLM = gemini) -> Review:
    title, stories = parse_text(text)
    result = Review(title or "Untitled PRD", stories, lint(stories))
    for s in stories if use_llm else []:
        try:
            result.drafts[s.id] = draft(s, llm=llm)
        except Exception as e:  # one busy/failed story must not stop the review; it is reported instead
            result.skipped[s.id] = str(e)[:200]
    return result
