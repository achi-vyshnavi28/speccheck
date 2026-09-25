"""LLM steps: draft test cases from user stories, and review requirements for defects a rule can't see.

The LLM drafts; a person reviews. Every drafted case is marked status "draft" in the test library,
and the deterministic lint in lint.py always runs regardless of the LLM.
"""

import json
import os
import re
from typing import Literal, Protocol

from pydantic import BaseModel, Field

from speccheck.parse import Story

MODELS = [m.strip() for m in os.getenv("SPECCHECK_MODELS", "gemini-3.6-flash,gemini-flash-lite-latest").split(",")]
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class TestCase(BaseModel):
    title: str
    type: Literal["positive", "negative", "boundary", "permission", "audit"]
    covers: list[int] = Field(default_factory=list, description="1-based numbers of the acceptance criteria this case tests")
    preconditions: str
    steps: list[str] = Field(min_length=1)
    expected: str
    priority: Literal["high", "medium", "low"]


class Drafted(BaseModel):
    test_cases: list[TestCase]
    ambiguities: list[str] = Field(default_factory=list, description="Anything that stopped you writing an exact expected result")


PROMPT = """You write test cases for a GxP-regulated pharmaceutical system (21 CFR Part 11).
User story {id}: {title}
{narrative}
Acceptance criteria (numbered):
{criteria}

Write 4-8 test cases covering the happy path, negative cases, boundaries (limits such as time windows),
permissions (wrong role), and audit-trail/e-signature expectations. Expected results must be exact and checkable.
Set "covers" to the numbers of the acceptance criteria each case tests.
If a criterion is too vague to write an exact expected result, do not invent one: add it to "ambiguities".
Reply with ONE JSON object: {{"test_cases": [...], "ambiguities": [...]}} matching this schema:
{schema}"""

DEFECTS = {
    "vague_term": "no pass/fail criterion (e.g. quickly, user-friendly, as needed, modern, secure)",
    "placeholder": "not decided yet (TBD, TODO, to be confirmed)",
    "weak_modal": "unclear whether mandatory (should, may, could)",
    "missing_value": "a limit, time or quantity is implied but no value is given",
    "ambiguous_reference": "starts with a pronoun whose referent is unclear",
    "missing_actor": "a human action (approve, verify, review, check...) with no role named",
    "gxp_control_missing": "a GMP-relevant change (override, delete, edit, reject, deactivate...) with no required "
                           "reason, e-signature or audit-trail entry",
}

REVIEW_PROMPT = """You review requirements for a GxP-regulated pharmaceutical software system (21 CFR Part 11).
For each numbered requirement, list the defects that would stop a tester writing an exact, checkable test.
Use only these defect types:
{types}
A vague word is NOT a defect when the same requirement gives a number (e.g. "quickly (p95 < 2 s)").
Most well-written requirements have no defects: return an empty list for them. Do not invent defects.

{items}

Reply with ONE JSON object: {{"results": [{{"i": <number>, "defects": [<types>]}}, ...]}} with one entry per requirement."""


class LLM(Protocol):
    def __call__(self, prompt: str) -> str: ...


def gemini(prompt: str, attempts: int = 3) -> str:
    """Direct REST call (no SDK). Retries busy responses with backoff, then falls back to the next model."""
    import time

    import httpx

    body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}
    last = None
    for model in MODELS:
        for attempt in range(attempts):
            r = httpx.post(GEMINI_URL.format(model=model), json=body, timeout=180,
                           headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]})
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            last = f"{model}: HTTP {r.status_code}"
            if r.status_code not in (429, 500, 502, 503, 504):
                break
            time.sleep(5 * 2 ** attempt)
    raise RuntimeError(f"All Gemini models busy or failing ({last})")


def _json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON in reply")
    return json.loads(m.group(0))


def draft(story: Story, llm: LLM = gemini) -> Drafted:
    prompt = PROMPT.format(id=story.id, title=story.title, narrative=story.narrative,
                           criteria="\n".join(f"{i}. {c}" for i, c in enumerate(story.criteria, start=1)),
                           schema=json.dumps(Drafted.model_json_schema()))
    return Drafted.model_validate(_json(llm(prompt)))


def review(texts: list[str], llm: LLM = gemini, batch: int = 10) -> list[list[str]]:
    """LLM defect labels per requirement, restricted to the known defect types."""
    out: list[list[str]] = []
    types = "\n".join(f"- {k}: {v}" for k, v in DEFECTS.items())
    for start in range(0, len(texts), batch):
        chunk = texts[start:start + batch]
        items = "\n".join(f"{i}. {t}" for i, t in enumerate(chunk))
        found = {r["i"]: r.get("defects", []) for r in _json(llm(REVIEW_PROMPT.format(types=types, items=items)))["results"]}
        out += [sorted({d for d in found.get(i, []) if d in DEFECTS}) for i in range(len(chunk))]
    return out
