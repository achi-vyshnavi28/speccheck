"""Deterministic requirement checks: "if a requirement can't be turned into a test case, it isn't finished".

Each rule returns the exact text, why it can't be tested, and the question to send back to product.
Runs without any AI, so the result is repeatable and auditable. `check()` works on one requirement
(used by the evaluation); `lint()` adds story-level rules on top.
"""

import re
from dataclasses import dataclass

from speccheck.parse import Story


@dataclass
class Finding:
    rule: str
    severity: str  # high | medium | low
    why: str
    question: str


@dataclass
class Gap(Finding):
    story: str = ""
    text: str = ""


def _words(*ws: str) -> re.Pattern:
    return re.compile(r"\b(" + "|".join(re.escape(w) for w in ws) + r")\b", re.I)


VAGUE = {
    "quickly": "What response time, measured how (e.g. p95 < 2 s)?",
    "fast": "What response time, measured how?",
    "slow": "What response time counts as too slow?",
    "promptly": "Within what time?",
    "timely": "Within what time?",
    "as soon as possible": "Within what time?",
    "user-friendly": "Which usability criterion (e.g. task done in <= 3 clicks, no training)?",
    "easy": "Which measurable usability criterion?",
    "easily": "Which measurable usability criterion?",
    "intuitive": "Which measurable usability criterion?",
    "simple": "Which measurable usability criterion?",
    "seamless": "What exactly must happen, and what must not?",
    "as needed": "Under which exact conditions, and who decides?",
    "when needed": "Under which exact conditions, and who decides?",
    "if needed": "Under which exact conditions, and who decides?",
    "as required": "Under which exact conditions, and who decides?",
    "appropriate": "What is appropriate, specifically?",
    "appropriately": "What is appropriate, specifically?",
    "adequate": "What level is adequate, specifically?",
    "sufficient": "What level is sufficient, specifically?",
    "reasonable": "What is reasonable, specifically?",
    "properly": "What is the exact expected result?",
    "correctly": "What is the exact expected result?",
    "relevant": "Which items exactly?",
    "robust": "Which failure scenarios must be handled, and how?",
    "flexible": "Which variations must be supported?",
    "efficient": "Efficient by which measure, and what target?",
    "minimal": "What is the maximum allowed, as a number?",
    "periodically": "How often exactly?",
    "regularly": "How often exactly?",
    "large": "How many or how big, as a number?",
    "close to": "How close, as a number?",
    "modern": "Which concrete design standard or criterion?",
    "strong": "Which exact rules (length, character classes, expiry)?",
    "secure": "Which security controls, tested how?",
    "sensible": "By which exact rule?",
    "sensibly": "By which exact rule?",
    "user friendly": "Which usability criterion (e.g. task done in <= 3 clicks, no training)?",
    "etc": "List all items explicitly.",
    "and so on": "List all items explicitly.",
}
VAGUE_RE = _words(*VAGUE)
MEASURE = re.compile(r"\d")                     # a number anywhere makes a vague word measurable ("quickly (p95 < 2 s)")
PLACEHOLDER = re.compile(r"\b(TBD|TBC|TODO|to be (decided|confirmed|defined))\b|\?\?|\bXXX\b", re.I)
WEAK_MODAL = _words("should", "may", "could", "might", "ideally", "where possible", "if possible", "optionally")
LIMIT = _words("within", "limit", "limited", "maximum", "minimum", "max", "min", "timeout", "expire", "expires",
               "expired", "valid for", "retained for", "retain", "threshold", "tolerance", "after a period", "up to",
               "deadline")
DUE = re.compile(r"\bdue\b(?!\s+dates?\b)", re.I)  # "due" implies a limit; "due date" is just a field name
PROHIBITED = re.compile(r"\b(cannot|can't|must not|may not|never)\s+be\b", re.I)
REFERENCE = re.compile(r"^(it|this|that|they|these|those)\b", re.I)
HUMAN_PASSIVE = re.compile(r"\b(is|are|be|been|gets|get)\s+(approved|verified|reviewed|signed|checked|confirmed|"
                           r"closed|released|authori[sz]ed|investigated|assessed)\b"
                           r"|\b(needs?|requires?|requiring|after|with|pending)\s+(an?\s+|the\s+)?(\w+\s+)?"
                           r"(approval|sign-off|verification)\b", re.I)
ACTOR = _words("by", "operator", "operators", "supervisor", "supervisors", "qa", "user", "users", "admin",
               "administrator", "manager", "reviewer", "approver", "owner", "system", "analyst", "person", "role")
# A GMP-relevant change is a verb, not a noun ("change request", "change history"): base forms count only after a
# modal ("QA can reject"), past participles only after be ("can be modified"). A prohibition ("cannot be changed",
# "are never deleted") is itself the control, so negated actions are not flagged.
_ACTS = r"(override|delete|remove|change|edit|modify|correct|bypass|reject|void|cancel|deactivate|disable|reopen)"
_DONE = (r"(overridden|deleted|removed|changed|edited|modified|corrected|bypassed|rejected|voided|cancell?ed|"
         r"deactivated|disabled|reopened)")
GXP_ACTION = re.compile(rf"\b(can|may|must|shall|will|could|should|to|able to)\s+(also\s+)?{_ACTS}\b"
                        rf"|\b(be|is|are|been|being|get|gets)\s+{_DONE}\b"
                        rf"|\b{_ACTS}s\b(?=\s+(a|an|the|any|their|its)\b)", re.I)
GXP_NEGATED = re.compile(rf"\b(cannot|can't|not|never|no one|nobody)\s+(\w+\s+){{0,2}}({_ACTS}|{_DONE})\b", re.I)
GXP_CONTROL = _words("reason", "justification", "signature", "e-signature", "sign", "signs", "signed", "audit",
                     "audit trail", "audit-trail")
NEGATIVE = _words("not", "cannot", "can't", "refuse", "refused", "reject", "rejected", "block", "blocked", "error",
                  "invalid", "denied", "prevent", "prevented", "only", "unless", "never", "fails", "fail")


def check(text: str, context: str = "") -> list[Finding]:
    """Findings for one requirement. `context` is the rest of the story, used by the GxP-control rule."""
    out: list[Finding] = []
    has_number = bool(MEASURE.search(text))
    for m in VAGUE_RE.finditer(text):
        word = m.group(1).lower()
        if has_number and word not in ("etc", "and so on"):
            continue
        high = word in ("as needed", "when needed", "if needed", "as required")
        out.append(Finding("vague_term", "high" if high else "medium", f"'{word}' has no pass/fail criterion.",
                           VAGUE[word]))
    if PLACEHOLDER.search(text):
        out.append(Finding("placeholder", "high", "Requirement is not decided yet.",
                           "Please decide and specify before development starts."))
    if m := WEAK_MODAL.search(text):
        out.append(Finding("weak_modal", "low", f"'{m.group(1).lower()}' makes it unclear whether this is mandatory.",
                           "Is this mandatory ('must') or optional?"))
    if (m := LIMIT.search(text) or DUE.search(text)) and not has_number:
        out.append(Finding("missing_value", "medium", f"'{m.group(0).lower()}' implies a limit, but no value is given.",
                           "What is the exact value and unit?"))
    if REFERENCE.search(text.strip()):
        out.append(Finding("ambiguous_reference", "low", "Starts with a pronoun; the tester can't tell what it refers to.",
                           "Name the object explicitly."))
    prohibited = PROHIBITED.search(text)  # "cannot be closed while..." is a rule on the system, not a human action
    if HUMAN_PASSIVE.search(text) and not ACTOR.search(text) and not PLACEHOLDER.search(text) and not prohibited:
        out.append(Finding("missing_actor", "medium",
                           "A human action with no role: the record would not be attributable (ALCOA+ 'Attributable').",
                           "Which role performs this, and can the same person do the previous step?"))
    if (GXP_ACTION.search(text) and not GXP_NEGATED.search(text)
            and not GXP_CONTROL.search(f"{text} {context}")):
        out.append(Finding("gxp_control_missing", "high",
                           "A GMP-relevant action (override/delete/change/reject) without a required reason, "
                           "e-signature or audit-trail entry (21 CFR 11.10(e), 11.50).",
                           "Must this action require a reason, an e-signature and an audit-trail entry? Who may perform it?"))
    return out


def lint_story(story: Story) -> list[Gap]:
    gaps: list[Gap] = []
    if len(story.criteria) < 2:
        gaps.append(Gap("thin_acceptance_criteria", "medium",
                        f"Only {len(story.criteria)} acceptance criterion; negative and boundary behaviour are undefined.",
                        "What should happen on invalid input, wrong role, and at the limits?", story.id, story.title))
    elif not any(NEGATIVE.search(c) for c in story.criteria):
        gaps.append(Gap("no_negative_behaviour", "medium", "No criterion says what happens when a rule is broken.",
                        "What does the system do on invalid input or a wrong role (message, block, audit entry)?",
                        story.id, story.title))
    context = " ".join(story.criteria)
    for c in story.criteria:
        for f in check(c, context):
            gaps.append(Gap(f.rule, f.severity, f.why, f.question, story.id, c))
    return gaps


def lint(stories: list[Story]) -> list[Gap]:
    return [g for s in stories for g in lint_story(s)]
